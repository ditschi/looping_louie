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
# Freerouting ist deterministisch; unterschiedliche Durchlaufzahlen liefern verschiedene Ergebnisse
PASS_VARIANTS = [40, 25, 60, 15, 100, 30]


# Netze, die vollständig über Kupferflächen laufen und von Freerouting nicht geroutet werden sollen.
# Ladeplatine: GND wird mitgeroutet, weil die Brücke unten und die Leistungsbahnen die Flächen sonst in
# Inseln zerlegen (einzelne GND-Pads bleiben dann unverbunden).
PLANE_NETS = [] if BOARD == "charger-board" else ["/GND"]


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


def freerouting_round(dsn, ses, keep_tracks, passes=None):
    """Eine Freerouting-Runde. keep_tracks=False: vorher alle ungesperrten Bahnen entfernen."""
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
                             "--gui.enabled=false"], capture_output=True, text=True)
    log = result.stdout + result.stderr
    (WORK / "freerouting.log").write_text(log)
    m = re.findall(r"final score: [\d.]+ \((\d+) unrouted", log)
    unrouted = int(m[-1]) if m else -1

    board = pcbnew.LoadBoard(str(PCB))
    if not pcbnew.ImportSpecctraSES(board, str(ses)):
        sys.exit("SES-Import fehlgeschlagen")
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(PCB), board)
    return unrouted


def unconnected_count():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "drc.json"
        subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "-o", str(report), str(PCB)],
                       capture_output=True)
        data = json.loads(report.read_text())
    return len(data.get("unconnected_items", [])), len(data.get("violations", []))


def remove_dangling_vias():
    """Vias, die Freerouting ohne Anschluss zurückgelassen hat (DRC: via_dangling), entfernen."""
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "drc.json"
        subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "-o", str(report), str(PCB)],
                       capture_output=True)
        data = json.loads(report.read_text())
    spots = [(item["pos"]["x"], item["pos"]["y"]) for v in data.get("violations", [])
             if v["type"] == "via_dangling" for item in v["items"]]
    if not spots:
        return 0
    board = pcbnew.LoadBoard(str(PCB))
    removed = 0
    for via in [t for t in board.GetTracks() if t.GetClass() == "PCB_VIA" and not t.IsLocked()]:
        x, y = pcbnew.ToMM(via.GetPosition().x), pcbnew.ToMM(via.GetPosition().y)
        if any(abs(x - sx) < 0.01 and abs(y - sy) < 0.01 for sx, sy in spots):
            board.Delete(via)
            removed += 1
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(PCB), board)
    return removed


def main():
    if not JAR.exists():
        sys.exit(f"Freerouting nicht gefunden: {JAR}\n→ ./setup.sh ausführen oder FREEROUTING_JAR setzen")
    WORK.mkdir(parents=True, exist_ok=True)
    dsn, ses = WORK / f"{BOARDS[BOARD]}.dsn", WORK / f"{BOARDS[BOARD]}.ses"
    start = WORK / "start.kicad_pcb"
    best_file = WORK / "best.kicad_pcb"
    shutil.copy(PCB, start)

    best = None
    for attempt in range(1, ATTEMPTS + 1):
        shutil.copy(start, PCB)
        passes = PASS_VARIANTS[(attempt - 1) % len(PASS_VARIANTS)]
        unrouted = freerouting_round(dsn, ses, keep_tracks=False, passes=passes)
        for _ in range(2 if PLANE_NETS else 0):  # GND-Pads ohne Flächenkontakt per Via anbinden
            done, _failed = stitch(PCB, PLANE_NETS)
            if not done:
                break
        grid = stitch_grid(PCB)  # GND-Flächen oben/unten im Raster verbinden
        open_items, violations = unconnected_count()
        print(f"Versuch {attempt} ({passes} Durchläufe): Freerouting {unrouted} offen → nach Stitching {open_items} unverbunden, "
              f"{violations} DRC-Meldungen, {grid} Stitching-Vias")
        if best is None or (open_items, violations) < best:
            best = (open_items, violations)
            shutil.copy(PCB, best_file)
        if open_items == 0:
            break
    shutil.copy(best_file, PCB)
    removed = remove_dangling_vias()
    if removed:
        print(f"{removed} unangeschlossene Vias entfernt")
    print(f"bestes Ergebnis übernommen: {best[0]} unverbunden – jetzt: just drc")


if __name__ == "__main__":
    main()
