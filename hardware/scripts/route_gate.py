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

Entscheidung (route_score.py, hardware/routing-score.toml, docs/routing-score.md): harte Bedingungen (DRC-Fehler,
offene Verbindungen, Kupfer in der Antennen-Sperrfläche, zu schmale Strompfade) → Regel nach Deb → gewichteter
Score S mit Schwelle (ΔS ≤ −min_improvement) und Veto. routing.json speichert Kennzahlen, Score, Hash der
Konfiguration und Kennzahlen-Version; passen Hash oder Version nicht mehr, wird die offizielle Platine neu gemessen.

Aufruf:
  route_gate.py fingerprint <platine.kicad_pcb>          Inhalts-Hash ausgeben
  route_gate.py measure <platine.kicad_pcb> [projekt.kicad_pro] [--board B]   Kennzahlen ausgeben (JSON)
  route_gate.py init <board> [--preroute DATEI]          routing.json aus der offiziellen Platine anlegen
  route_gate.py check <board> <kandidat> [--start DATEI] [--force] [--apply]
                                                         Kandidat durch das Gate schicken; ohne --apply nur
                                                         Probelauf (nichts wird geändert). Start des simulierten
                                                         Laufs: Standard die offizielle Platine
  route_gate.py score [board] [kandidat …]               Score-Tabelle der offiziellen Platine und der Kandidaten
                                                         (z. B. build/<board>/keep/*.kicad_pcb), Bericht je
                                                         Kandidat, Pareto-Sicht; ändert nichts
  route_gate.py explain [board] <kandidat>               Entscheidung mit Beiträgen, Kipp-Faktoren, Robustheit
Muss für measure/init/check/score/explain mit dem System-Python laufen, das pcbnew enthält.
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

sys.path.insert(0, str(Path(__file__).parent))
import route_score  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
BOARDS = {"main-board": "louie-main", "charger-board": "louie-charger"}
UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
TOKEN_RE = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
# Knoten, die nicht zum Design gehören (erzeugt, zufällig oder Ausgabe-Einstellungen)
DROP = {"uuid", "tstamp", "filled_polygon", "fill_segments", "generator", "generator_version", "version",
        "pcbplotparams"}
TRACK_KINDS = {"segment", "arc", "via"}
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

def measure(pcb, project=None, board="main-board"):
    """Kennzahlen einer Platine (route_score.measure_all) → dict(metrics=…, details=…). project: .kicad_pro, deren
    Regeln (samt .kicad_dru) gelten sollen; liegt die Platine nicht daneben, wird sie dafür in einen temporären
    Ordner kopiert (sonst prüft der DRC mit Standardregeln)."""
    m, d = route_score.measure_all(pcb, route_score.load_config(board), project)
    return {"metrics": m, "details": d}


def short(m, cfg=None, details=None):
    """Kurzzeile; mit cfg zusätzlich harte Verletzung und Score S."""
    text = (f"{m['unconnected']} offen, DRC {m['drc_violations']}, Inseln {m['gnd_islands']}, "
            f"{m['via_count']} Vias, {m['track_length_mm']:.1f} mm")
    if cfg is not None and "drc_errors" in m:
        e = route_score.evaluate(cfg, m, details)
        text += f", hart {e['hard_total']}" + (f" ({', '.join(e['hard'])})" if e["hard"] else "") + f", S {e['S']:.2f}"
    return text


def slug(m, cfg=None, details=None):
    text = (f"drc{m['drc_violations']}-open{m['unconnected']}-isl{m['gnd_islands']}-via{m['via_count']}"
            f"-len{m['track_length_mm']:.0f}")
    if cfg is not None and "drc_errors" in m:
        e = route_score.evaluate(cfg, m, details)
        text += f"-hard{e['hard_total']}-S{e['S']:.1f}"
    return text


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


def write_record(board, fingerprint, board_hash, meas, info):
    cfg = route_score.load_config(board)
    m, d = meas["metrics"], meas.get("details", {})
    e = route_score.evaluate(cfg, m, d)
    record = {"board": board, "fingerprint": fingerprint, "board_hash": board_hash, "metrics": m,
              "score": {"S": e["S"], "hard": e["hard"], "hard_total": e["hard_total"], "under_mm": e["under_mm"],
                        "parts": e["parts"]},
              "decision": "hard+weighted", "score_config_sha256": route_score.config_hash(),
              "metrics_version": route_score.METRICS_VERSION, "details": d,
              "router": info.get("router"), "variant": info.get("variant"),
              "runs": info.get("runs"), "note": info.get("note"),
              "timestamp": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
              "tools": tool_versions(info.get("router"))}
    record_path(board).write_text(json.dumps({k: v for k, v in record.items() if v is not None}, indent=2,
                                             ensure_ascii=False) + "\n")


def refresh_record(board, record, meas):
    """Score der offiziellen Platine neu eintragen (neue Konfiguration/Kennzahlen-Version), sonst nichts ändern."""
    info = {k: record.get(k) for k in ("router", "variant", "runs", "note")}
    write_record(board, record["fingerprint"], record["board_hash"], meas, info)
    saved = json.loads(record_path(board).read_text())
    saved["timestamp"], saved["tools"] = record.get("timestamp"), record.get("tools")
    saved["rescored"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    record_path(board).write_text(json.dumps(saved, indent=2, ensure_ascii=False) + "\n")


def record_current(record):
    """Passen gespeicherte Kennzahlen zu Konfiguration und Kennzahlen-Version?"""
    return bool(record) and record.get("score_config_sha256") == route_score.config_hash() \
        and record.get("metrics_version") == route_score.METRICS_VERSION and "drc_errors" in record.get("metrics", {})


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

def official_measurement(board, record, project, log=print):
    """Kennzahlen der offiziellen Platine: aus routing.json, wenn Konfigurations-Hash und Kennzahlen-Version passen;
    sonst neu gemessen (offizielle Datei, falls sie noch das Ergebnis aus routing.json ist, sonst die Kopie aus
    build/<board>/keep/ oder Git). → (Messung oder None, neu gemessen?)"""
    if record_current(record):
        return {"metrics": record["metrics"], "details": record.get("details", {})}, False
    official = pcb_path(board)
    source = official if content_hash(official, project) == record["board_hash"] else \
        find_copy(board, record["board_hash"], project)
    if source is None:
        return None, False
    why = "Kennzahlen-Version geändert" if record.get("metrics_version") not in (None, route_score.METRICS_VERSION) \
        else "Score-Konfiguration geändert" if record.get("score_config_sha256") else "noch kein Score in routing.json"
    log(f"Offizielle Platine neu gemessen ({why}): {source.relative_to(ROOT)}")
    return measure(source, project, board), True


def gate(board, candidate, fingerprint, metrics=None, info=None, force=False, log=print, dry_run=False):
    """Entscheidet, ob candidate die offizielle Platine wird. Gibt True zurück, wenn übernommen.
    metrics: Messung des Kandidaten (dict(metrics, details), sonst wird gemessen).
    dry_run=True: nur entscheiden und melden, keine Datei ändern."""
    info = dict(info or {})
    official = pcb_path(board)
    project = official.with_suffix(".kicad_pro")
    cfg = route_score.load_config(board)
    meas = metrics or measure(candidate, project, board)
    m = meas["metrics"]
    record = load_record(board)

    def accept(reason):
        if dry_run:
            log(f"Probelauf: würde übernehmen ({reason}): {short(m, cfg, meas.get('details'))}")
            return True
        shutil.copy(candidate, official)
        shutil.copy(candidate, keep_dir(board) / f"accepted-{stamp()}-{slug(m, cfg, meas.get('details'))}.kicad_pcb")
        write_record(board, fingerprint, content_hash(official, project), meas, info)
        log(f"Neuer Lauf: {short(m, cfg, meas.get('details'))} → übernommen ({reason}); "
            f"{official.relative_to(ROOT)} und {record_path(board).relative_to(ROOT)} aktualisiert")
        return True

    if force:
        info["note"] = "mit --force übernommen"
        return accept("--force")
    if record is None:
        return accept("noch kein routing.json")
    if record["fingerprint"] != fingerprint:
        old = record["metrics"]
        info["note"] = f"Design geändert, Basis neu gesetzt (vorher {short(old)})"
        return accept(f"Design geändert, Fingerabdruck {record['fingerprint'][:10]} → {fingerprint[:10]}, "
                      f"bisheriger Stand {short(old)}")
    off, refreshed = official_measurement(board, record, project, log)
    if off is None:
        info["note"] = "bisheriges Ergebnis nicht auffindbar, neuer Lauf übernommen"
        log("  bisheriges Ergebnis (board_hash aus routing.json) weder in build/<platine>/keep/ noch in Git "
            "gefunden – übernehme den neuen Lauf")
        return accept("Ersatz")
    ok, why, drivers = route_score.decide(cfg, meas, off)
    report = route_score.explain(cfg, "neu", meas, "offiziell", off)
    if not dry_run:
        out = ROOT / "build" / board / "route"
        out.mkdir(parents=True, exist_ok=True)
        (out / "score-report.txt").write_text("\n".join(report) + "\n")
    for line in report:
        log(line)
    eo, ec = route_score.evaluate(cfg, off["metrics"], off.get("details")), \
        route_score.evaluate(cfg, m, meas.get("details"))
    summary = (f"S {ec['S']:.2f} ({ec['S'] - eo['S']:+.2f}), hart {ec['hard_total']} (bisher {eo['hard_total']})")
    if ok:
        return accept(f"{why}; {summary}; Haupttreiber {drivers}")
    if dry_run:
        log(f"Probelauf: würde verwerfen ({why}): {summary}; Haupttreiber {drivers}")
        return False
    if refreshed:
        refresh_record(board, record, off)
        log(f"  {record_path(board).relative_to(ROOT)}: Score der offiziellen Platine aktualisiert")
    rejected = ROOT / "build" / board / "route" / "rejected"
    rejected.mkdir(parents=True, exist_ok=True)
    target = rejected / f"{stamp()}-{slug(m, cfg, meas.get('details'))}.kicad_pcb"
    shutil.copy(candidate, target)
    log(f"Neuer Lauf: {summary} → verworfen ({why}; Haupttreiber {drivers}), "
        f"abgelegt unter {target.relative_to(ROOT)}")
    log(f"  neu:    {short(m, cfg, meas.get('details'))}\n  bisher: {short(off['metrics'], cfg, off.get('details'))}")
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
    meas = measure(official, board=board)
    old = load_record(board) or {}
    write_record(board, fp, content_hash(official), meas,
                 {"router": old.get("router") or ("own" if board == "main-board" else "freerouting"),
                  "variant": old.get("variant"), "note": "aus der offiziellen Platine angelegt (route_gate.py init)"})
    print(f"{record_path(board).relative_to(ROOT)}: {short(meas['metrics'], route_score.load_config(board), meas['details'])}")


def split_board(args):
    """[board] [rest …] → (board, rest); ohne Platinennamen gilt main-board."""
    if args and args[0] in BOARDS:
        return args[0], args[1:]
    return "main-board", list(args)


def score_cmd(args, explain_only=False):
    board, files = split_board(args)
    cfg = route_score.load_config(board)
    official = pcb_path(board)
    record = load_record(board)
    project = official.with_suffix(".kicad_pro")
    if record and content_hash(official, project) != record.get("board_hash"):
        print(f"Hinweis: {official.relative_to(ROOT)} ist nicht die Platine aus routing.json (z. B. nach just pcb)")
    boards = [(f"offiziell ({official.name})", measure(official, project, board))]
    for f in files:
        boards.append((Path(f).name, measure(f, project, board)))
    if not explain_only:
        for line in route_score.table(cfg, boards):
            print(line)
        print()
    for name, b in boards[1:]:
        for line in route_score.explain(cfg, name, b, boards[0][0], boards[0][1]):
            print(line)
        print()
    if not explain_only:
        for line in route_score.pareto(cfg, boards):
            print(line)
        if len(boards) == 1:
            m, e = boards[0][1]["metrics"], route_score.evaluate(cfg, boards[0][1]["metrics"], boards[0][1]["details"])
            print("\nBeiträge (Punkte):")
            for k, v in sorted(e["parts"].items(), key=lambda kv: -abs(kv[1])):
                print(f"  {k:24} {route_score.fmt(m.get(k)):>10} {v:>+8.2f}")
            for p in boards[0][1]["details"].get("paths", []):
                print(f"  Pfad {p['name']}: " + (f"{p['drop_mv']} mV, min. {p['min_width_mm']} mm, {p['vias']} Vias, "
                                                 f"zu schmal {p['under_width_mm']} mm" if p.get("connected")
                                                 else "nicht verbunden"))


def main(argv):
    if len(argv) < 1:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "fingerprint":
        print(content_hash(args[0], *(args[1:2])))
    elif cmd == "measure":
        board = args[args.index("--board") + 1] if "--board" in args else "main-board"
        rest = [a for i, a in enumerate(args) if a != "--board" and (i == 0 or args[i - 1] != "--board")]
        meas = measure(rest[0], *(rest[1:2]), board=board)
        meas["evaluation"] = route_score.evaluate(route_score.load_config(board), meas["metrics"], meas["details"])
        print(json.dumps(meas, indent=2, ensure_ascii=False))
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
    elif cmd == "score":
        score_cmd(args)
    elif cmd == "explain":
        board, files = split_board(args)
        if len(files) != 1:
            sys.exit("explain [board] <kandidat>")
        score_cmd([board] + files, explain_only=True)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
