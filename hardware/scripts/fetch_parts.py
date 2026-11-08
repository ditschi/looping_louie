#!/usr/bin/env python3
"""Fetches symbols, footprints and 3D models of all LCSC parts from bom/parts.csv
into the project library hardware/lib/lcsc.*

Usage (via just):  just parts            # missing parts only
                   just parts-update     # fetch all again
"""
import csv
import re
import subprocess
import sys
import time
from pathlib import Path

HARDWARE = Path(__file__).resolve().parent.parent
BOM = HARDWARE / "bom" / "parts.csv"
LIB = HARDWARE / "lib" / "lcsc"
PAUSE_S = 3  # the EasyEDA API blocks requests that come too fast (HTTP 403)


def lcsc_ids():
    with BOM.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["library"] == "lcsc" and row["lcsc"]:
                yield row["lcsc"], row["part"]


def fetch(lcsc_id, overwrite):
    cmd = ["easyeda2kicad", "--full", "--project-relative", f"--lcsc_id={lcsc_id}", "--output", str(LIB)]
    if overwrite:
        cmd.append("--overwrite")
    # cwd = hardware/, so that --project-relative writes "${KIPRJMOD}/lib/..."
    result = subprocess.run(cmd, cwd=HARDWARE, capture_output=True, text=True)
    output = result.stdout + result.stderr
    if "already exists" in output:
        return "present"
    if "[ERROR]" in output or result.returncode != 0:
        return "ERROR: " + " | ".join(line for line in output.splitlines() if "ERROR" in line)
    return "fetched"


def fix_model_paths():
    """The KiCad projects live in hardware/<board>/, the library in hardware/lib/."""
    for mod in (LIB.parent / "lcsc.pretty").glob("*.kicad_mod"):
        text = mod.read_text()
        fixed = re.sub(r"\$\{KIPRJMOD\}/lib/", "${KIPRJMOD}/../lib/", text)
        if fixed != text:
            mod.write_text(fixed)


# Own footprints derived from fetched ones: (new name, template, 3D model, LCSC number).
# ESP32-C6-MINI-1: EasyEDA delivers the pads up to 20 µm off the 0.8 mm grid; the pads of the
# C3-MINI-1 are identical to the C6 (KiCad RF_Module:ESP32-C6-MINI-1, max. 5 µm), hence the C3 file
# with the 3D model of the C6 (see docs/main-board-c6.md 2.1). Do not use the KiCad footprint:
# its courtyard contains a 43 × 20 mm antenna keepout zone.
DERIVED = [
    ("WIFIM-SMD_ESP32-C6-MINI-1", "WIFIM-SMD_ESP32-C3-MINI-1",
     "WIFIM-SMD_61P-L16.6-W13.2-P0.80-ESP32-C6-MINI-1-N4", "C42403058"),
]


def derive_footprints():
    pretty = LIB.parent / "lcsc.pretty"
    for name, template, model, lcsc in DERIVED:
        src = pretty / f"{template}.kicad_mod"
        if not src.exists() or not (LIB.parent / "lcsc.3dshapes" / f"{model}.wrl").exists():
            print(f"{name}: template or 3D model missing")
            continue
        text = src.read_text().replace(template, name)
        text = re.sub(r'\(property "LCSC Part" "[^"]*"\)', f'(property "LCSC Part" "{lcsc}")', text)
        text = re.sub(r'lcsc\.3dshapes/[^"]+\.wrl', f"lcsc.3dshapes/{model}.wrl", text)
        (pretty / f"{name}.kicad_mod").write_text(text)


# KiCad footprints with a missing 3D model: copy to louie.pretty with the model of an LCSC part.
# (KiCad footprint, target, model, offset x/y/z, rotation z, remove silkscreen)
# HRO TYPE-C-31-M-12: model shifted by 0.85 mm so that the front edge lies at +3.7 mm as in the KiCad
# footprint (model Y points to the footprint rear side); the outline in the
# silkscreen runs over the board edge.
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
            print(f"{name}: {path} missing")
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
    """EasyEDA courtyards are sometimes smaller than the pads (e.g. SMAF). Extend the rectangular courtyard to
    pads + 0.25 mm so that the placement check and the DRC are correct."""
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
        failed |= status.startswith("ERROR")
        print(f"{lcsc_id:<10} {name:<22} {status}")
    fix_model_paths()
    fix_courtyards()
    derive_footprints()
    derive_kicad_footprints()
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
