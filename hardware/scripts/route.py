#!/usr/bin/env python3
"""Routet eine Platine (Standard: Hauptplatine) automatisch mit Freerouting und füllt danach die Masseflächen.

Ablauf: Specctra-DSN exportieren → Freerouting (Java) → SES importieren → Zonen füllen.
Freerouting-JAR: Umgebungsvariable FREEROUTING_JAR oder tools/freerouting.jar (siehe setup.sh).

Aufruf (über just):  just route [main-board|charger-board]
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

ROOT = Path(__file__).resolve().parent.parent.parent
BOARDS = {"main-board": "louie-main", "charger-board": "louie-charger"}
BOARD = sys.argv[1] if len(sys.argv) > 1 else "main-board"
PCB = ROOT / "hardware" / BOARD / f"{BOARDS[BOARD]}.kicad_pcb"
WORK = ROOT / "build" / BOARD / "route"
JAR = Path(os.environ.get("FREEROUTING_JAR", ROOT / "tools" / "freerouting.jar"))
PASSES = os.environ.get("FREEROUTING_PASSES", "40")
ATTEMPTS = int(os.environ.get("FREEROUTING_ATTEMPTS", "6"))
PARALLEL = int(os.environ.get("FREEROUTING_PARALLEL", "3"))
# Freerouting ist deterministisch und bricht ab, sobald sich das Ergebnis nicht mehr verbessert; die
# Durchlaufzahl ändert daher wenig. Verschiedene Leiterbahnbreiten (Standard / Supply) liefern dagegen
# deutlich verschiedene Ergebnisse. Mindestbreite und Abstände bleiben unverändert.
PASS_VARIANTS = [40, 25, 60, 15, 100, 30]
WIDTH_VARIANTS = [(0.17, 0.2), (0.2, 0.25), (0.15, 0.2), (0.18, 0.2), (0.2, 0.2), (0.16, 0.25),
                  (0.17, 0.25), (0.18, 0.25), (0.19, 0.2)]


# Netze, die vollständig über Kupferflächen laufen und von Freerouting nicht geroutet werden sollen.
# Ladeplatine: GND wird mitgeroutet, weil die Brücke unten und die Leistungsbahnen die Flächen sonst in
# Inseln zerlegen (einzelne GND-Pads bleiben dann unverbunden).
PLANE_NETS = [] if BOARD == "charger-board" or os.environ.get("ROUTE_GND") else ["/GND"]


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
        if not zone.GetIsRuleArea():
            export.Delete(zone)
    if not pcbnew.ExportSpecctraDSN(export, str(dsn)):
        sys.exit("DSN-Export fehlgeschlagen")
    drop_nets(dsn, PLANE_NETS)

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


def unconnected_count(PCB=PCB):
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "drc.json"
        subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "-o", str(report), str(PCB)],
                       capture_output=True)
        data = json.loads(report.read_text())
    return len(data.get("unconnected_items", [])), len(data.get("violations", []))


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
    work = WORK / f"versuch_{n}"
    work.mkdir(parents=True, exist_ok=True)
    pcb = work / PCB.name
    shutil.copy(start, pcb)
    if project.exists():
        shutil.copy(project, work / project.name)
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
    for _ in range(2 if PLANE_NETS else 0):  # GND-Pads ohne Flächenkontakt per Via anbinden
        done, _failed = stitch(pcb, PLANE_NETS)
        if not done:
            break
    grid = stitch_grid(pcb)  # GND-Flächen oben/unten im Raster verbinden
    open_items, violations = unconnected_count(pcb)
    label = f"{passes} Durchläufe, Bahn {track}/{supply} mm" if BOARD == "main-board" else f"{passes} Durchläufe"
    return n, label, unrouted, open_items, violations, grid, pcb


def main():
    if not JAR.exists():
        sys.exit(f"Freerouting nicht gefunden: {JAR}\n→ ./setup.sh ausführen oder FREEROUTING_JAR setzen")
    WORK.mkdir(parents=True, exist_ok=True)
    start = WORK / "start.kicad_pcb"
    best_file = WORK / "best.kicad_pcb"
    shutil.copy(PCB, start)
    project = PCB.with_suffix(".kicad_pro")

    from concurrent.futures import ProcessPoolExecutor
    best = None
    with ProcessPoolExecutor(max_workers=PARALLEL) as pool:
        for n, label, unrouted, open_items, violations, grid, pcb in pool.map(
                attempt, range(1, ATTEMPTS + 1), [start] * ATTEMPTS, [project] * ATTEMPTS):
            print(f"Versuch {n} ({label}): Freerouting {unrouted} offen → nach Stitching {open_items} unverbunden, "
                  f"{violations} DRC-Meldungen, {grid} Stitching-Vias", flush=True)
            if best is None or (open_items, violations) < best[:2]:
                best = (open_items, violations, n)
                shutil.copy(pcb, best_file)
    shutil.copy(best_file, PCB)
    removed = remove_dangling_vias()
    if removed:
        print(f"{removed} lose Vias/Leiterbahnstücke entfernt")
    print(f"bestes Ergebnis (Versuch {best[2]}) übernommen: {best[0]} unverbunden – jetzt: just drc")


if __name__ == "__main__":
    main()
