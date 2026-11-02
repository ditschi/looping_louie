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


# Eigene Footprints, abgeleitet von geholten: (neuer Name, Vorlage, 3D-Modell, LCSC-Nummer).
# ESP32-C6-MINI-1: EasyEDA liefert die Pads um bis zu 20 µm neben dem 0,8-mm-Raster; die Pads des
# C3-MINI-1 sind identisch zum C6 (KiCad RF_Module:ESP32-C6-MINI-1, max. 5 µm), deshalb die C3-Datei
# mit dem 3D-Modell des C6 (siehe docs/hauptplatine-c6.md 2.1). Den KiCad-Footprint nicht verwenden:
# sein Courtyard enthält eine 43 × 20 mm große Antennen-Sperrzone.
DERIVED = [
    ("WIFIM-SMD_ESP32-C6-MINI-1", "WIFIM-SMD_ESP32-C3-MINI-1",
     "WIFIM-SMD_61P-L16.6-W13.2-P0.80-ESP32-C6-MINI-1-N4", "C42403058"),
]


def derive_footprints():
    pretty = LIB.parent / "lcsc.pretty"
    for name, template, model, lcsc in DERIVED:
        src = pretty / f"{template}.kicad_mod"
        if not src.exists() or not (LIB.parent / "lcsc.3dshapes" / f"{model}.wrl").exists():
            print(f"{name}: Vorlage oder 3D-Modell fehlt")
            continue
        text = src.read_text().replace(template, name)
        text = re.sub(r'\(property "LCSC Part" "[^"]*"\)', f'(property "LCSC Part" "{lcsc}")', text)
        text = re.sub(r'lcsc\.3dshapes/[^"]+\.wrl', f"lcsc.3dshapes/{model}.wrl", text)
        (pretty / f"{name}.kicad_mod").write_text(text)


# KiCad-Footprints mit fehlendem 3D-Modell: Kopie nach louie.pretty mit dem Modell eines LCSC-Teils.
# (KiCad-Footprint, Ziel, Modell, Versatz x/y/z, Drehung z, Bestückungsdruck entfernen)
# HRO TYPE-C-31-M-12: Modell um 0,85 mm verschoben, damit die Vorderkante wie im KiCad-Footprint bei
# +3,7 mm liegt (Modell-Y zeigt zur Footprint-Rückseite); der Umriss im
# Bestückungsdruck läuft über die Platinenkante.
KICAD_DERIVED = [
    ("Connector_USB/USB_C_Receptacle_HRO_TYPE-C-31-M-12", "USB_C_Receptacle_HRO_TYPE-C-31-M-12",
     "USB-C_SMD-TYPE-C-31-M-12_1", (0, -0.85, 0), 180, True),
]
KICAD_FP = Path("/usr/share/kicad/footprints")


def derive_kicad_footprints():
    sys.path.insert(0, str(Path(__file__).parent))
    from sexpr import block_end
    for src, name, model, (ox, oy, oz), rz, no_silk in KICAD_DERIVED:
        lib, fp = src.split("/")
        path = KICAD_FP / f"{lib}.pretty" / f"{fp}.kicad_mod"
        if not path.exists():
            print(f"{name}: {path} fehlt")
            continue
        text = path.read_text().replace(f'(footprint "{fp}"', f'(footprint "{name}"', 1)
        m = text.find("(model ")
        if m >= 0:
            text = text[:m] + text[block_end(text, m):]
        if no_silk:
            for kind in ("fp_line", "fp_arc", "fp_poly", "fp_rect", "fp_circle"):
                i = 0
                while (i := text.find(f"({kind}", i)) >= 0:
                    end = block_end(text, i)
                    if '(layer "F.SilkS")' in text[i:end]:
                        text = text[:i] + text[end:]
                    else:
                        i = end
        model_block = (f'\t(model "${{KIPRJMOD}}/../lib/lcsc.3dshapes/{model}.wrl"\n'
                       f'\t\t(offset (xyz {ox} {oy} {oz}))\n\t\t(scale (xyz 1 1 1))\n'
                       f'\t\t(rotate (xyz 0 0 {rz}))\n\t)\n')
        end = text.rstrip().rfind(")")
        text = text[:end] + model_block + ")\n"
        (LIB.parent / "louie.pretty" / f"{name}.kicad_mod").write_text(text)


def fix_courtyards():
    """EasyEDA-Courtyards sind teils kleiner als die Pads (z. B. SMAF). Rechteckiges Courtyard auf
    Pads + 0,25 mm erweitern, damit Platzierungsprüfung und DRC stimmen."""
    for mod in (LIB.parent / "lcsc.pretty").glob("*.kicad_mod"):
        text = mod.read_text()
        crt = re.findall(r"\(fp_line \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\) \(layer F\.CrtYd\)", text)
        if len(crt) != 4:
            continue
        xs = [float(v) for c in crt for v in (c[0], c[2])]
        ys = [float(v) for c in crt for v in (c[1], c[3])]
        box = [min(xs), min(ys), max(xs), max(ys)]
        new = list(box)
        for m in re.finditer(r"\(pad \S+ smd rect \(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\) \(size ([\d.]+) ([\d.]+)\)", text):
            x, y, rot, w, h = (float(m.group(i) or 0) for i in range(1, 6))
            if round(rot) % 180 == 90:
                w, h = h, w
            new = [min(new[0], x - w / 2 - 0.25), min(new[1], y - h / 2 - 0.25),
                   max(new[2], x + w / 2 + 0.25), max(new[3], y + h / 2 + 0.25)]
        if new == box:
            continue
        x0, y0, x1, y1 = (f"{v:.2f}" for v in new)
        rect = [(x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)]
        lines = iter(f"(fp_line (start {a} {b}) (end {c} {d}) (layer F.CrtYd)" for a, b, c, d in rect)
        text = re.sub(r"\(fp_line \(start [-\d.]+ [-\d.]+\) \(end [-\d.]+ [-\d.]+\) \(layer F\.CrtYd\)",
                      lambda _m: next(lines), text)
        mod.write_text(text)


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
    fix_courtyards()
    derive_footprints()
    derive_kicad_footprints()
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
