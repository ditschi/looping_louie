#!/usr/bin/env python3
"""Routet die Hauptplatine automatisch mit Freerouting und füllt danach die Masseflächen.

Ablauf: Specctra-DSN exportieren → Freerouting (Java) → SES importieren → Zonen füllen.
Freerouting-JAR: Umgebungsvariable FREEROUTING_JAR oder tools/freerouting.jar (siehe setup.sh).

Aufruf (über just):  just route
Muss mit dem System-Python laufen, das das KiCad-Modul pcbnew enthält.
"""
import os
import subprocess
import sys
from pathlib import Path

import pcbnew

ROOT = Path(__file__).resolve().parent.parent.parent
PCB = ROOT / "hardware" / "main-board" / "louie-main.kicad_pcb"
WORK = ROOT / "build" / "main-board" / "route"
JAR = Path(os.environ.get("FREEROUTING_JAR", ROOT / "tools" / "freerouting.jar"))
PASSES = os.environ.get("FREEROUTING_PASSES", "40")


def main():
    if not JAR.exists():
        sys.exit(f"Freerouting nicht gefunden: {JAR}\n→ ./setup.sh ausführen oder FREEROUTING_JAR setzen")
    WORK.mkdir(parents=True, exist_ok=True)
    dsn, ses = WORK / "louie-main.dsn", WORK / "louie-main.ses"

    board = pcbnew.LoadBoard(str(PCB))
    for track in list(board.GetTracks()):  # alte, nicht gesperrte Leiterbahnen entfernen
        if not track.IsLocked():
            board.Delete(track)
    if not pcbnew.ExportSpecctraDSN(board, str(dsn)):
        sys.exit("DSN-Export fehlgeschlagen")

    subprocess.run(["java", "-jar", str(JAR), "-de", str(dsn), "-do", str(ses), "-mp", PASSES,
                    "--gui.enabled=false"], check=True)

    if not pcbnew.ImportSpecctraSES(board, str(ses)):
        sys.exit("SES-Import fehlgeschlagen")
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(PCB), board)
    print(f"geroutet: {PCB.relative_to(ROOT)} – jetzt: just drc")


if __name__ == "__main__":
    main()
