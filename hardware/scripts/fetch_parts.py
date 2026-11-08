#!/usr/bin/env python3
"""Holt Symbole, Footprints und 3D-Modelle aller LCSC-Teile aus bom/teile.csv
in die Projektbibliothek hardware/lib/lcsc.*

Aufruf (über just):  just parts            # nur fehlende Teile
                     just parts-update     # alle neu holen
"""
import csv
import re
import subprocess
import sys
import time
from pathlib import Path

HARDWARE = Path(__file__).resolve().parent.parent
BOM = HARDWARE / "bom" / "teile.csv"
LIB = HARDWARE / "lib" / "lcsc"
PAUSE_S = 3  # die EasyEDA-API sperrt bei zu schnellen Abfragen (HTTP 403)


def lcsc_ids():
    with BOM.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["bibliothek"] == "lcsc" and row["lcsc"]:
                yield row["lcsc"], row["bauteil"]


def fetch(lcsc_id, overwrite):
    cmd = ["easyeda2kicad", "--full", "--project-relative", f"--lcsc_id={lcsc_id}", "--output", str(LIB)]
    if overwrite:
        cmd.append("--overwrite")
    # cwd = hardware/, damit --project-relative "${KIPRJMOD}/lib/..." schreibt
    result = subprocess.run(cmd, cwd=HARDWARE, capture_output=True, text=True)
    output = result.stdout + result.stderr
    if "already exists" in output:
        return "vorhanden"
    if "[ERROR]" in output or result.returncode != 0:
        return "FEHLER: " + " | ".join(line for line in output.splitlines() if "ERROR" in line)
    return "geholt"


def fix_model_paths():
    """Die KiCad-Projekte liegen in hardware/<platine>/, die Bibliothek in hardware/lib/."""
    for mod in (LIB.parent / "lcsc.pretty").glob("*.kicad_mod"):
        text = mod.read_text()
        fixed = re.sub(r"\$\{KIPRJMOD\}/lib/", "${KIPRJMOD}/../lib/", text)
        if fixed != text:
            mod.write_text(fixed)


def main():
    overwrite = "--overwrite" in sys.argv
    LIB.parent.mkdir(parents=True, exist_ok=True)
    failed = False
    for i, (lcsc_id, name) in enumerate(lcsc_ids()):
        if i:
            time.sleep(PAUSE_S)
        status = fetch(lcsc_id, overwrite)
        failed |= status.startswith("FEHLER")
        print(f"{lcsc_id:<10} {name:<22} {status}")
    fix_model_paths()
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
