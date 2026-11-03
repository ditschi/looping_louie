#!/usr/bin/env python3
"""Routet eine Platine (Standard: Hauptplatine) automatisch und füllt danach die Masseflächen.

Hauptplatine (4 Lagen): eigener Router route_fix.py (Standard) oder Freerouting. Ladeplatine (2 Lagen):
Freerouting – Ablauf: Specctra-DSN exportieren → Freerouting (Java) → SES importieren → Zonen füllen.
Freerouting-JAR: Umgebungsvariable FREEROUTING_JAR oder tools/freerouting.jar (siehe setup.sh).

Aufruf (über just):  just route [main-board|charger-board] [runs=N] [force=1]
  (direkt: route.py <board> [--runs N] [--force]; runs = Zahl der Versuche, Standard 6)

Keep-best-Gate (route_gate.py, docs/entwicklung.md): Der beste Versuch eines Aufrufs ersetzt die offizielle
Platine nur, wenn er für dasselbe Design besser ist als das Ergebnis in hardware/<board>/routing.json, wenn sich
das Design geändert hat oder mit force=1. Sonst landet er unter build/<board>/route/rejected/.

Umgebungsvariablen: ROUTE_RUNS (alt: FREEROUTING_ATTEMPTS), ROUTE_PARALLEL (alt: FREEROUTING_PARALLEL),
FREEROUTING_PASSES, FREEROUTING_JAR, ROUTE_VARIANTS, ROUTE_PLANE, ROUTE_GND, ROUTER (nur Hauptplatine).

Hauptplatine, 4 Lagen (main-board, docs/hauptplatine-c6.md Kapitel 11):
- ROUTER=own (Standard; veraltet: ROUTER=eigen): Labyrinth-Router route_fix.py für alle Signale auf F.Cu/In2.Cu/B.Cu, GND über die
  Lage In1 (Stitching-Vias an den GND-Pads). Die Versuche unterscheiden sich in Via- und Lagenkosten
  (ROUTER_VARIANTS); auch gleiche Varianten streuen etwas (Reihenfolge aus dem DRC, siehe route_fix.py).
  ROUTE_VARIANTS="3,4" wählt einzelne Varianten.
- ROUTER=freerouting: Freerouting wie bei der Ladeplatine, danach route_fix.py für die offenen Reste. Die GND-Lage
  In1 geht als Ebene in die DSN-Datei (ROUTE_PLANE=1, Freerouting bindet GND per Via an) oder nicht
  (ROUTE_PLANE=0, GND nur über Stitching-Vias).
Muss mit dem System-Python laufen, das das KiCad-Modul pcbnew enthält.
"""
import json
import os
import re
import shutil
import tempfile
import subprocess
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
from stitch import stitch, stitch_grid  # noqa: E402
import route_gate  # noqa: E402


def parse_args(argv):
    """board, Versuche, force aus "main-board runs=10 force=1" bzw. "main-board --runs 10 --force"."""
    board, runs, force = "main-board", None, False
    args = list(argv)
    while args:
        a = args.pop(0)
        key, _, value = a.lstrip("-").partition("=")
        if key in ("runs", "attempts"):
            runs = int(value or args.pop(0))
        elif key == "force":
            force = value.lower() not in ("0", "no", "false") if value else True
        elif not a.startswith("-") and "=" not in a:
            board = a
        else:
            sys.exit(f"Unbekannte Option: {a} (erlaubt: runs=N, force=1)")
    return board, runs, force


def env(name, old, default):
    """Englischer Name hat Vorrang, der alte bleibt als Alias."""
    return os.environ.get(name, os.environ.get(old, default))


ROOT = Path(__file__).resolve().parent.parent.parent
BOARDS = {"main-board": "louie-main", "charger-board": "louie-charger"}
# auch in den Worker-Prozessen (forkserver importiert das Modul neu, sys.argv bleibt erhalten)
BOARD, RUNS, FORCE = parse_args(sys.argv[1:])
PCB = ROOT / "hardware" / BOARD / f"{BOARDS[BOARD]}.kicad_pcb"
WORK = ROOT / "build" / BOARD / "route"
JAR = Path(os.environ.get("FREEROUTING_JAR", ROOT / "tools" / "freerouting.jar"))
PASSES = os.environ.get("FREEROUTING_PASSES", "40")
ATTEMPTS = RUNS or int(env("ROUTE_RUNS", "FREEROUTING_ATTEMPTS", "6"))
PARALLEL = int(env("ROUTE_PARALLEL", "FREEROUTING_PARALLEL", "3"))
# Freerouting ist deterministisch und bricht ab, sobald sich das Ergebnis nicht mehr verbessert; die
# Durchlaufzahl ändert daher wenig. Verschiedene Leiterbahnbreiten (Standard / Supply) liefern dagegen
# deutlich verschiedene Ergebnisse. Mindestbreite und Abstände bleiben unverändert.
PASS_VARIANTS = [40, 25, 60, 15, 100, 30]
WIDTH_VARIANTS = [(0.17, 0.2), (0.2, 0.25), (0.15, 0.2), (0.18, 0.2), (0.2, 0.2), (0.16, 0.25),
                  (0.17, 0.25), (0.18, 0.25), (0.19, 0.2)]


# Netze, die vollständig über Kupferflächen laufen und von Freerouting nicht geroutet werden sollen.
# Ladeplatine: GND wird mitgeroutet, weil die Brücke unten und die Leistungsbahnen die Flächen sonst in
# Inseln zerlegen (einzelne GND-Pads bleiben dann unverbunden).
FOUR_LAYER = BOARD == "main-board"  # Hauptplatine: 4 Lagen, GND-Lage In1
# 4 Lagen: GND-Ebene In1 an Freerouting übergeben (Standard), GND wird dann mitgeroutet (Vias zur Ebene)
PLANE_EXPORT = FOUR_LAYER and os.environ.get("ROUTE_PLANE", "1") == "1"
PLANE_NETS = [] if BOARD == "charger-board" or os.environ.get("ROUTE_GND") or PLANE_EXPORT else ["/GND"]
STITCH_NETS = ["/GND"] if FOUR_LAYER else PLANE_NETS
ROUTER = os.environ.get("ROUTER", "own") if FOUR_LAYER else "freerouting"
if ROUTER == "eigen":  # veralteter Name
    if __name__ == "__main__":
        print("Hinweis: ROUTER=eigen ist veraltet, bitte ROUTER=own verwenden", file=sys.stderr)
    ROUTER = "own"
# Varianten des eigenen Routers: (Via-Kosten in Rasterschritten, Kostenfaktor F.Cu, Kostenfaktor B.Cu)
ROUTER_VARIANTS = [(30, 1.3, 1.15), (20, 1.3, 1.15), (40, 1.3, 1.15), (30, 1.6, 1.3), (25, 1.1, 1.0), (35, 1.5, 1.1)]


def drop_nets(dsn, nets):
    """Entfernt Netze aus dem network-Abschnitt der DSN-Datei (Freerouting ignoriert sie dann)."""
    sys.path.insert(0, str(Path(__file__).parent))
    from sexpr import block_end
    text = dsn.read_text()
    for net in nets:
        start = text.find(f"(net {net}\n")
        if start < 0:
            start = text.find(f"(net {net} ")
        if start >= 0:
            text = text[:start] + text[block_end(text, start):]
        text = text.replace(f" {net}\n", "\n").replace(f" {net} ", " ").replace(f" {net})", ")")
    dsn.write_text(text)


def plane_layer_off(dsn):
    """4 Lagen: In1 (GND-Lage) für Freerouting abschalten (layer_rule active off). Freerouting ignoriert den
    Lagentyp "power"; die Sperrfläche "GND-Lage" (wire_keepout) würde es auch für Vias sperren und wird deshalb
    aus der DSN entfernt (in KiCad bleibt sie für den DRC)."""
    sys.path.insert(0, str(Path(__file__).parent))
    from sexpr import block_end
    text = dsn.read_text()
    while (start := text.find("(wire_keepout")) >= 0:
        line = text.rfind("\n", 0, start) + 1
        text = text[:line] + text[block_end(text, start):].lstrip(" ").lstrip("\n")
    i = text.find("\n", text.find("    (via \"", text.find("(structure"))) + 1  # nach den Lagen und der Via-Angabe
    text = text[:i] + "    (autoroute_settings (layer_rule In1.Cu (active off)))\n" + text[i:]
    dsn.write_text(text)


def freerouting_round(dsn, ses, keep_tracks, passes=None, pcb=None, work=None):
    """Eine Freerouting-Runde. keep_tracks=False: vorher alle ungesperrten Bahnen entfernen."""
    PCB, WORK = pcb or globals()["PCB"], work or globals()["WORK"]
    board = pcbnew.LoadBoard(str(PCB))
    if not keep_tracks:
        for track in list(board.GetTracks()):
            if not track.IsLocked():
                board.Delete(track)
        pcbnew.SaveBoard(str(PCB), board)

    # Für Freerouting ohne Kupferflächen exportieren: sonst gelten die flächigen Zonen als
    # belegtes Kupfer und blockieren das Routing. Die Flächen werden nach dem Import gefüllt.
    export = pcbnew.LoadBoard(str(PCB))
    for zone in list(export.Zones()):
        if not zone.GetIsRuleArea() and not (PLANE_EXPORT and zone.GetLayer() == pcbnew.In1_Cu):
            export.Delete(zone)
    if not pcbnew.ExportSpecctraDSN(export, str(dsn)):
        sys.exit("DSN-Export fehlgeschlagen")
    drop_nets(dsn, PLANE_NETS)
    if FOUR_LAYER:
        plane_layer_off(dsn)

    result = subprocess.run(["java", "-jar", str(JAR), "-de", str(dsn), "-do", str(ses), "-mp", str(passes or PASSES),
                             "--gui.enabled=false", "--router.automatic_neckdown=false"], capture_output=True, text=True)
    log = result.stdout + result.stderr
    (WORK / "freerouting.log").write_text(log)
    m = re.findall(r"final score: [\d.]+ \((\d+) unrouted", log)
    unrouted = int(m[-1]) if m else -1

    board = pcbnew.LoadBoard(str(PCB))
    if not pcbnew.ImportSpecctraSES(board, str(ses)):
        sys.exit("SES-Import fehlgeschlagen")
    # Freerouting verjüngt Bahnen an kleinen Pads; nichts unter die Mindestbreite der Designregeln
    min_w = board.GetDesignSettings().m_TrackMinWidth
    for track in board.GetTracks():
        if track.GetClass() == "PCB_TRACK" and track.GetWidth() < min_w:
            track.SetWidth(min_w)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(PCB), board)
    return unrouted


def remove_dangling_vias(PCB=PCB):
    """Vias und Leiterbahnstücke, die Freerouting ohne Anschluss zurückgelassen hat (DRC: via_dangling,
    track_dangling), entfernen; mehrfach, weil danach neue lose Enden entstehen können."""
    removed = 0
    for _ in range(4):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "drc.json"
            subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "-o", str(report), str(PCB)],
                           capture_output=True)
            data = json.loads(report.read_text())
        spots = {v["type"]: [] for v in data.get("violations", [])}
        for v in data.get("violations", []):
            if v["type"] in ("via_dangling", "track_dangling"):
                spots[v["type"]] += [(item["pos"]["x"], item["pos"]["y"]) for item in v["items"]]
        if not spots.get("via_dangling") and not spots.get("track_dangling"):
            break
        board = pcbnew.LoadBoard(str(PCB))
        n = 0
        for t in [t for t in board.GetTracks() if not t.IsLocked()]:
            kind = "via_dangling" if t.GetClass() == "PCB_VIA" else "track_dangling"
            ends = [t.GetPosition()] if kind == "via_dangling" else [t.GetStart(), t.GetEnd()]
            if any(abs(pcbnew.ToMM(e.x) - sx) < 0.01 and abs(pcbnew.ToMM(e.y) - sy) < 0.01
                   for e in ends for sx, sy in spots.get(kind, [])):
                board.Delete(t)
                n += 1
        if not n:
            break
        removed += n
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        pcbnew.SaveBoard(str(PCB), board)
    return removed


def attempt(n, start, project):
    """Ein Routing-Versuch in eigenem Ordner (läuft parallel zu anderen)."""
    work = WORK / f"attempt_{n}"
    work.mkdir(parents=True, exist_ok=True)
    pcb = work / PCB.name
    shutil.copy(start, pcb)
    for f in (project, project.with_suffix(".kicad_dru")):
        if f.exists():
            shutil.copy(f, work / f.name)
    if ROUTER == "own":
        return attempt_own(n, pcb)
    passes = PASS_VARIANTS[(n - 1) % len(PASS_VARIANTS)]
    track, supply = WIDTH_VARIANTS[(n - 1) % len(WIDTH_VARIANTS)]
    if BOARD == "main-board":
        board = pcbnew.LoadBoard(str(pcb))
        ns = board.GetDesignSettings().m_NetSettings
        ns.GetDefaultNetclass().SetTrackWidth(pcbnew.FromMM(track))
        if ns.HasNetclass("Supply"):
            ns.GetNetClassByName("Supply").SetTrackWidth(pcbnew.FromMM(supply))
        pcbnew.SaveBoard(str(pcb), board)
    dsn, ses = work / f"{BOARDS[BOARD]}.dsn", work / f"{BOARDS[BOARD]}.ses"
    unrouted = freerouting_round(dsn, ses, keep_tracks=False, passes=passes, pcb=pcb, work=work)
    if FOUR_LAYER:  # Reste mit dem eigenen Router
        import route_fix
        with open(work / "route_fix.log", "w") as log:
            route_fix.fix(pcb, log=lambda m: print(m, file=log, flush=True))
    for _ in range(2 if STITCH_NETS else 0):  # GND-Pads ohne Flächenkontakt per Via anbinden
        done, _failed = stitch(pcb, STITCH_NETS)
        if not done:
            break
    grid = stitch_grid(pcb)  # GND-Flächen oben/unten im Raster verbinden
    removed = remove_dangling_vias(pcb)
    label = f"{passes} Durchläufe, Bahn {track}/{supply} mm" if BOARD == "main-board" else f"{passes} Durchläufe"
    return n, label, unrouted, route_gate.measure(pcb), grid, removed, pcb


def attempt_own(n, pcb):
    """4 Lagen: alle Signale mit dem eigenen Router (route_fix.py), dann GND-Stitching."""
    import route_fix
    via_cost, f_cost, b_cost = ROUTER_VARIANTS[(n - 1) % len(ROUTER_VARIANTS)]
    route_fix.VIA_COST = via_cost
    route_fix.LAYER_COST[pcbnew.F_Cu] = f_cost
    route_fix.LAYER_COST[pcbnew.B_Cu] = b_cost
    board = pcbnew.LoadBoard(str(pcb))
    for track in list(board.GetTracks()):
        if not track.IsLocked():
            board.Delete(track)
    pcbnew.SaveBoard(str(pcb), board)
    with open(pcb.parent / "route_fix.log", "w") as log:
        out = lambda m: print(m, file=log, flush=True)  # noqa: E731
        done, still_open = route_fix.route_all(pcb, log=out)
        for _ in range(2):  # GND-Pads ohne Flächenkontakt per Via an die GND-Lage In1
            stitched, _failed = stitch(pcb, STITCH_NETS)
            if not stitched:
                break
        grid = stitch_grid(pcb)
        out(f"GND-Inseln angebunden: {route_fix.gnd_islands(pcb, log=out)}")
        grid += stitch_grid(pcb)
    removed = remove_dangling_vias(pcb)
    label = f"eigener Router, Via-Kosten {via_cost}, F {f_cost}, B {b_cost}"
    return n, label, still_open, route_gate.measure(pcb), grid, removed, pcb


def main():
    if ROUTER != "own" and not JAR.exists():
        sys.exit(f"Freerouting nicht gefunden: {JAR}\n→ ./setup.sh ausführen oder FREEROUTING_JAR setzen")
    WORK.mkdir(parents=True, exist_ok=True)
    start = WORK / "start.kicad_pcb"
    best_file = WORK / "best.kicad_pcb"
    shutil.copy(PCB, start)
    project = PCB.with_suffix(".kicad_pro")
    # Fingerabdruck des Designs am Start (vor dem Routing), siehe route_gate.py
    fingerprint, why = route_gate.run_fingerprint(start, route_gate.load_record(BOARD), project)
    print(f"Design-Fingerabdruck {fingerprint[:12]} ({why})", flush=True)

    from concurrent.futures import ProcessPoolExecutor
    best = None
    with ProcessPoolExecutor(max_workers=PARALLEL) as pool:
        # ROUTE_VARIANTS="3,4": nur diese Versuche (Wiederholung/Streuung), sonst 1..runs
        numbers = [int(x) for x in os.environ["ROUTE_VARIANTS"].split(",")] if os.environ.get("ROUTE_VARIANTS") \
            else list(range(1, ATTEMPTS + 1))
        for n, label, unrouted, metrics, grid, removed, pcb in pool.map(
                attempt, numbers, [start] * len(numbers), [project] * len(numbers)):
            first = "Router" if ROUTER == "own" else "Freerouting"
            extra = f", {removed} lose Vias/Bahnstücke entfernt" if removed else ""
            print(f"Versuch {n} ({label}): {first} {unrouted} offen → nach Stitching {route_gate.short(metrics)}, "
                  f"{grid} Stitching-Vias{extra}", flush=True)
            if best is None or route_gate.rank(metrics) < route_gate.rank(best[0]):
                best = (metrics, n, label)
                shutil.copy(pcb, best_file)
    print(f"bester Versuch dieses Aufrufs: {best[1]} ({best[2]})")
    info = {"router": ROUTER, "variant": f"Versuch {best[1]}: {best[2]}", "runs": len(numbers)}
    route_gate.gate(BOARD, best_file, fingerprint, best[0], info, force=FORCE)
    print(f"jetzt: just drc {BOARD}")


if __name__ == "__main__":
    main()
