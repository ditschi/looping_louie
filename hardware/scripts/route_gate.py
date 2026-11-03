#!/usr/bin/env python3
"""Keep-best-Gate für das Routing (docs/entwicklung.md, Abschnitt „Routing: bestes Ergebnis behalten“).

Jede Platine hat eine eingecheckte Ergebnisdatei hardware/<platine>/routing.json mit dem Fingerabdruck des
Designs, den Kennzahlen des offiziellen Routings und Angaben zu Router und Werkzeugen. Ein neuer Routing-Lauf
ersetzt die offizielle .kicad_pcb nur, wenn er für dasselbe Design besser ist (oder das Design sich geändert hat).

Fingerabdruck (fingerprint): SHA-256 über den normalisierten Inhalt der *ungerouteten* Platine (Ausgabe von
`just pcb`: Platzierung, Vorrouten, Flächen-Umrisse, Sperrflächen, Regeln, Netze) plus die Regeln aus der
Projektdatei (board.design_settings, net_settings) und der .kicad_dru. Normalisiert heißt: ohne UUIDs (auch in
Pfaden), ohne Generator-/Versionskennung, ohne Plot-Einstellungen, ohne Flächenfüllungen; Elemente sortiert
(KiCad sortiert beim Speichern nach UUID, die Reihenfolge ist also zufällig).

Weil die Router (route_fix.py, stitch.py) ihre Bahnen und Vias genauso sperren wie die Vorrouten, lässt sich
aus einer gerouteten Platine nicht ablesen, was Vorroute ist. Deshalb steht in routing.json zusätzlich der
normalisierte Inhalts-Hash der offiziellen gerouteten Platine (board_hash). Startet ein Lauf von genau dieser
Platine (erneutes `just route` ohne `just pcb`), gilt der gespeicherte Fingerabdruck; sonst wird der Start
als ungeroutete Platine betrachtet und ihr Inhalts-Hash ist der Fingerabdruck.

Rangfolge (lexikografisch, kleiner ist besser): drc_violations, unconnected, gnd_islands, via_count,
track_length_mm.

Aufruf:
  route_gate.py fingerprint <platine.kicad_pcb>          Inhalts-Hash ausgeben
  route_gate.py measure <platine.kicad_pcb> [projekt.kicad_pro]   Kennzahlen ausgeben
  route_gate.py init <board> [--preroute DATEI]          routing.json aus der offiziellen Platine anlegen
  route_gate.py check <board> <kandidat> [--start DATEI] [--force] [--apply]
                                                         Kandidat durch das Gate schicken; ohne --apply nur
                                                         Probelauf (nichts wird geändert). Start des simulierten
                                                         Laufs: Standard die offizielle Platine
Muss für measure/init/check mit dem System-Python laufen, das pcbnew enthält.
"""
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BOARDS = {"main-board": "louie-main", "charger-board": "louie-charger"}
METRICS = ["drc_violations", "unconnected", "gnd_islands", "via_count", "track_length_mm"]
UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
TOKEN_RE = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
# Knoten, die nicht zum Design gehören (erzeugt, zufällig oder Ausgabe-Einstellungen)
DROP = {"uuid", "tstamp", "filled_polygon", "fill_segments", "generator", "generator_version", "version",
        "pcbplotparams"}
TRACK_KINDS = {"segment", "arc", "via"}
# Bibliotheksabgleich der Footprints: hängt nur davon ab, ob fp-lib-table neben der Datei liegt (in den
# Arbeitsordnern von route.py nicht), nicht vom Routing; just drc prüft ihn weiterhin.
LIB_CHECKS = {"lib_footprint_issues", "lib_footprint_mismatch"}
# Listen, deren Kinder KiCad nach UUID sortiert schreibt: Kinder für den Hash sortieren
SORTED = {"kicad_pcb", "footprint", "group"}


def pcb_path(board):
    return ROOT / "hardware" / board / f"{BOARDS[board]}.kicad_pcb"


def record_path(board):
    return ROOT / "hardware" / board / "routing.json"


# --- Fingerabdruck -----------------------------------------------------------------------------------------

def parse(text):
    stack, cur = [], []
    for tok in TOKEN_RE.findall(text):
        if tok == "(":
            stack.append(cur)
            cur = []
        elif tok == ")":
            done, cur = cur, stack.pop()
            cur.append(done)
        else:
            cur.append(tok)
    return cur[0]


def canon(node, drop_tracks=False, top=True):
    """Normalisierte Textform eines Knotens (siehe Modulbeschreibung)."""
    if not isinstance(node, list):
        return UUID_RE.sub("~", node)
    head = node[0] if node and isinstance(node[0], str) else ""
    atoms, lists = [], []
    for child in node:
        if isinstance(child, list):
            h = child[0] if child and isinstance(child[0], str) else ""
            if h in DROP or (top and drop_tracks and h in TRACK_KINDS):
                continue
            lists.append(canon(child, drop_tracks, top=False))
        else:
            atoms.append(canon(child))
    if head == "fill":  # Zone: "(fill yes …)" heißt nur „ist gefüllt“
        atoms = [a for a in atoms if a not in ("yes", "no")]
    if head in SORTED:
        lists.sort()
    return "(" + " ".join(atoms + lists) + ")"


def project_rules(pcb, project=None):
    """Regeln aus .kicad_pro (board.design_settings, net_settings ohne Farben) und .kicad_dru.
    project: Pfad der .kicad_pro (Standard: neben der Platine, gleicher Name)."""
    pro = Path(project) if project else Path(pcb).with_suffix(".kicad_pro")
    dru = pro.with_suffix(".kicad_dru")
    out = ""
    if pro.exists():
        data = json.loads(pro.read_text())
        net = {k: v for k, v in data.get("net_settings", {}).items() if k not in ("net_colors", "meta")}
        out += json.dumps({"design_settings": data.get("board", {}).get("design_settings"), "net_settings": net},
                          sort_keys=True)
    if dru.exists():
        out += "\n" + dru.read_text()
    return out


def content_hash(pcb, project=None, drop_tracks=False):
    """Normalisierter Inhalts-Hash einer Platine samt Projektregeln. drop_tracks=True: ohne Bahnen und Vias
    (nur zum Vergleich von Platzierung, Flächen und Regeln zwischen ungerouteter und gerouteter Platine)."""
    text = canon(parse(Path(pcb).read_text()), drop_tracks)
    rules = project_rules(pcb, project)
    return hashlib.sha256((text + "\n" + rules).encode()).hexdigest()


def track_items(pcb):
    """Bahnen und Vias als normalisierte Texte (Vergleich ungeroutet ⊆ geroutet)."""
    tree = parse(Path(pcb).read_text())
    return {canon(c, top=False) for c in tree if isinstance(c, list) and c and c[0] in TRACK_KINDS}


def run_fingerprint(start, record, project):
    """Fingerabdruck des Designs, von dem ein Lauf startet (siehe Modulbeschreibung)."""
    h = content_hash(start, project)
    if record and h == record.get("board_hash"):
        return record["fingerprint"], "Start = offizielle geroutete Platine, Fingerabdruck aus routing.json"
    return h, "Start = ungeroutete Platine"


# --- Kennzahlen ---------------------------------------------------------------------------------------------

def drc(pcb):
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "drc.json"
        subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "-o", str(report), str(pcb)],
                       capture_output=True)
        return json.loads(report.read_text())


def gnd_islands(board):
    """Flächeninseln (gefüllte Polygone der Kupferflächen) ohne Via und ohne Durchsteckpad: hängen nur über
    Bahnen/SMD-Pads am Netz. Füllt die Flächen im Speicher neu (Datei bleibt unverändert)."""
    import pcbnew
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    count = 0
    for zone in board.Zones():
        if zone.GetIsRuleArea():
            continue
        code = zone.GetNetCode()
        vias = [t.GetPosition() for t in board.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetCode() == code]
        tht = [p.GetPosition() for p in board.GetPads() if p.GetNetCode() == code and p.GetDrillSize().x > 0]
        for layer in zone.GetLayerSet().CuStack():
            polys = zone.GetFilledPolysList(layer)
            for i in range(polys.OutlineCount()):
                outline = polys.Outline(i)
                if not any(outline.PointInside(v) for v in vias + tht):
                    count += 1
    return count


def measure(pcb, project=None):
    """Kennzahlen einer Platine. project: .kicad_pro, deren Regeln (samt .kicad_dru) gelten sollen; liegt die
    Platine nicht daneben, wird sie dafür in einen temporären Ordner kopiert (sonst prüft der DRC mit
    Standardregeln)."""
    pcb = Path(pcb)
    project = Path(project) if project else pcb.with_suffix(".kicad_pro")
    if project != pcb.with_suffix(".kicad_pro"):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / f"{project.stem}.kicad_pcb"
            shutil.copy(pcb, copy)
            for f in (project, project.with_suffix(".kicad_dru")):
                if f.exists():
                    shutil.copy(f, Path(tmp) / f.name)
            return measure(copy)
    import pcbnew
    data = drc(pcb)
    board = pcbnew.LoadBoard(str(pcb))
    vias = length = 0
    for t in board.GetTracks():
        if t.GetClass() == "PCB_VIA":
            vias += 1
        else:
            length += t.GetLength()
    violations = [v for v in data.get("violations", []) if v["type"] not in LIB_CHECKS]
    return {"drc_violations": len(violations),
            "unconnected": len(data.get("unconnected_items", [])),
            "gnd_islands": gnd_islands(board),
            "via_count": vias,
            "track_length_mm": round(pcbnew.ToMM(length), 2)}


def rank(metrics):
    return tuple(metrics[k] for k in METRICS)


def short(m):
    return (f"{m['unconnected']} offen, DRC {m['drc_violations']}, Inseln {m['gnd_islands']}, "
            f"{m['via_count']} Vias, {m['track_length_mm']:.1f} mm")


def slug(m):
    return (f"drc{m['drc_violations']}-open{m['unconnected']}-isl{m['gnd_islands']}-via{m['via_count']}"
            f"-len{m['track_length_mm']:.0f}")


# --- Werkzeuge, Ergebnisdatei ----------------------------------------------------------------------------

def tool_versions(router):
    out = {}
    try:
        out["kicad"] = subprocess.run(["kicad-cli", "--version"], capture_output=True, text=True).stdout.strip()
    except OSError:
        pass
    jar = Path(os.environ.get("FREEROUTING_JAR", ROOT / "tools" / "freerouting.jar"))
    if router == "freerouting" and jar.exists():
        # Version steht im Log (das JAR-Manifest sagt "unspecified"), dazu Build-Datum/-Revision des JARs
        logs = sorted((ROOT / "build").glob("*/route/**/freerouting.log"), key=lambda f: f.stat().st_mtime)
        m = re.search(r"Freerouting v(\S+)", logs[-1].read_text(errors="replace")) if logs else None
        version = m.group(1) if m else "?"
        try:
            manifest = zipfile.ZipFile(jar).read("META-INF/MANIFEST.MF").decode(errors="replace")
            date = re.search(r"Build-Date: *(\S+)", manifest)
            rev = re.search(r"Build-Revision: *(\S+)", manifest)
            version += f" (Build {date.group(1) if date else '?'} {rev.group(1)[:8] if rev else ''})".rstrip()
        except (OSError, KeyError, zipfile.BadZipFile):
            pass
        out["freerouting"] = version
    git = subprocess.run(["git", "-C", str(ROOT), "describe", "--always", "--dirty"], capture_output=True, text=True)
    if git.returncode == 0:
        out["repo"] = git.stdout.strip()
    return out


def load_record(board):
    p = record_path(board)
    return json.loads(p.read_text()) if p.exists() else None


def write_record(board, fingerprint, board_hash, metrics, info):
    record = {"board": board, "fingerprint": fingerprint, "board_hash": board_hash, "metrics": metrics,
              "ranking": METRICS, "router": info.get("router"), "variant": info.get("variant"),
              "runs": info.get("runs"), "note": info.get("note"),
              "timestamp": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
              "tools": tool_versions(info.get("router"))}
    record_path(board).write_text(json.dumps({k: v for k, v in record.items() if v is not None}, indent=2,
                                             ensure_ascii=False) + "\n")


def stamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def keep_dir(board):
    d = ROOT / "build" / board / "keep"
    d.mkdir(parents=True, exist_ok=True)
    return d


def find_copy(board, board_hash, project):
    """Datei mit dem Inhalts-Hash board_hash: build/<board>/keep/*.kicad_pcb oder Git (HEAD)."""
    for f in sorted(keep_dir(board).glob("*.kicad_pcb"), key=lambda f: f.stat().st_mtime, reverse=True):
        if content_hash(f, project) == board_hash:
            return f
    rel = pcb_path(board).relative_to(ROOT)
    git = subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:{rel}"], capture_output=True)
    if git.returncode == 0:
        f = keep_dir(board) / f"git-head-{stamp()}.kicad_pcb"
        f.write_bytes(git.stdout)
        if content_hash(f, project) == board_hash:
            return f
        f.unlink()
    return None


# --- Gate ---------------------------------------------------------------------------------------------------

def gate(board, candidate, fingerprint, metrics=None, info=None, force=False, log=print, dry_run=False):
    """Entscheidet, ob candidate die offizielle Platine wird. Gibt True zurück, wenn übernommen.
    dry_run=True: nur entscheiden und melden, keine Datei ändern."""
    info = dict(info or {})
    official = pcb_path(board)
    project = official.with_suffix(".kicad_pro")
    metrics = metrics or measure(candidate, project)
    record = load_record(board)

    def accept(reason):
        if dry_run:
            log(f"Probelauf: würde übernehmen ({reason}): {short(metrics)}")
            return True
        shutil.copy(candidate, official)
        shutil.copy(candidate, keep_dir(board) / f"accepted-{stamp()}-{slug(metrics)}.kicad_pcb")
        write_record(board, fingerprint, content_hash(official, project), metrics, info)
        log(f"Neuer Lauf: {short(metrics)} → übernommen ({reason}); "
            f"{official.relative_to(ROOT)} und {record_path(board).relative_to(ROOT)} aktualisiert")
        return True

    if force:
        info["note"] = "mit --force übernommen"
        return accept("--force")
    if record is None:
        return accept("noch kein routing.json")
    if record["fingerprint"] != fingerprint:
        old = record["metrics"]
        info["note"] = f"Design geändert, Basis neu gesetzt (vorher {old['unconnected']} offen)"
        return accept(f"Design geändert, Fingerabdruck {record['fingerprint'][:10]} → {fingerprint[:10]}, "
                      f"bisheriger Stand {short(old)}")
    old = record["metrics"]
    if rank(metrics) < rank(old):
        decisive = next(k for k in METRICS if metrics[k] != old[k])
        return accept(f"besser bei {decisive}, bisher: {short(old)}")

    decisive = next((k for k in METRICS if metrics[k] != old[k]), None)
    if dry_run:
        log(f"Probelauf: würde verwerfen ({'schlechter bei ' + decisive if decisive else 'gleich gut'}): "
            f"neu {short(metrics)}, bisher {short(old)}")
        return False
    rejected = ROOT / "build" / board / "route" / "rejected"
    rejected.mkdir(parents=True, exist_ok=True)
    target = rejected / f"{stamp()}-{slug(metrics)}.kicad_pcb"
    shutil.copy(candidate, target)
    why = f"schlechter bei {decisive}" if decisive else "gleich gut"
    log(f"Neuer Lauf: {metrics['unconnected']} offen, bisher {old['unconnected']} → verworfen ({why}), "
        f"abgelegt unter {target.relative_to(ROOT)}")
    log(f"  neu:    {short(metrics)}\n  bisher: {short(old)}")
    # Die offizielle Datei muss das bisherige Ergebnis sein (just pcb überschreibt sie mit der ungerouteten)
    if content_hash(official, project) != record["board_hash"]:
        source = find_copy(board, record["board_hash"], project)
        if source:
            shutil.copy(source, official)
            log(f"  bisheriges Ergebnis wiederhergestellt aus {source.relative_to(ROOT)}")
        else:
            info["note"] = "bisheriges Ergebnis nicht auffindbar, schlechterer Lauf übernommen"
            log("  bisheriges Ergebnis (board_hash aus routing.json) weder in build/<platine>/keep/ noch in Git "
                "gefunden – übernehme den neuen Lauf, damit keine ungeroutete Platine liegen bleibt")
            return accept("Ersatz")
    return False


def preroute_board(board, out_dir):
    """Ungeroutete Platine wie `just pcb` erzeugen, aber nach out_dir (offizielle Dateien unverändert)."""
    if board != "main-board":
        sys.exit(f"{board}: ungeroutete Platine bitte mit --preroute angeben")
    out = Path(out_dir) / pcb_path(board).name
    out.parent.mkdir(parents=True, exist_ok=True)
    for f in pcb_path(board).parent.iterdir():  # Projektdatei, Regeln, Bibliothekstabellen wie im Original
        if f.suffix in (".kicad_pro", ".kicad_dru") or f.name in ("fp-lib-table", "sym-lib-table"):
            shutil.copy(f, out.parent / f.name)
    python = os.environ.get("KICAD_PYTHON", sys.executable)
    subprocess.run([python, str(Path(__file__).parent / "gen_main_pcb.py")],
                   check=True, env=dict(os.environ, PCB_OUT=str(out)), capture_output=True)
    return out


def init(board, preroute=None, accept_mismatch=False):
    official = pcb_path(board)
    with tempfile.TemporaryDirectory() as tmp:
        pre = Path(preroute) if preroute else preroute_board(board, tmp)
        # Projektregeln: beim erzeugten Stand die mit erzeugte .kicad_pro, sonst die offizielle
        project = official.with_suffix(".kicad_pro") if preroute else pre.with_suffix(".kicad_pro")
        fp = content_hash(pre, project)
        # Passt die offizielle (geroutete) Platine zu dieser ungerouteten? Platzierung/Flächen/Regeln gleich und
        # alle Vorrouten unverändert enthalten.
        same_design = (content_hash(pre, project, drop_tracks=True)
                       == content_hash(official, drop_tracks=True))
        missing = track_items(pre) - track_items(official)
    print(f"{board}: Fingerabdruck {fp[:16]}…, Platzierung/Flächen/Regeln gleich: {same_design}, "
          f"fehlende Vorrouten: {len(missing)}")
    if not (same_design and not missing) and not accept_mismatch:
        sys.exit("offizielle Platine passt nicht zur ungerouteten – routing.json nicht geschrieben "
                 "(--accept-mismatch erzwingt es)")
    metrics = measure(official)
    old = load_record(board) or {}
    write_record(board, fp, content_hash(official), metrics,
                 {"router": old.get("router") or ("own" if board == "main-board" else "freerouting"),
                  "variant": old.get("variant"), "note": "aus der offiziellen Platine angelegt (route_gate.py init)"})
    print(f"{record_path(board).relative_to(ROOT)}: {short(metrics)}")


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "fingerprint":
        print(content_hash(args[0], *(args[1:2])))
    elif cmd == "measure":
        print(json.dumps(measure(args[0], *(args[1:2])), indent=2))
    elif cmd == "init":
        pre = args[args.index("--preroute") + 1] if "--preroute" in args else None
        init(args[0], pre, "--accept-mismatch" in args)
    elif cmd == "check":
        board, cand = args[0], Path(args[1])
        record = load_record(board)
        # Start des simulierten Laufs: Standard die offizielle Platine (erneutes just route), sonst --start
        start = Path(args[args.index("--start") + 1]) if "--start" in args else pcb_path(board)
        fp, why = run_fingerprint(start, record, pcb_path(board).with_suffix(".kicad_pro"))
        print(f"Fingerabdruck {fp[:16]}… ({why})")
        gate(board, cand, fp, info={"router": "manual", "variant": f"route_gate.py check {cand.name}"},
             force="--force" in args, dry_run="--apply" not in args)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
