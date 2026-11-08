#!/usr/bin/env python3
"""Erzeugt den Schaltplan der Hauptplatine aus der Schaltungsbeschreibung unten.

Jeder angeschlossene Pin bekommt einen kurzen Draht mit Netz-Label, unbenutzte Pins
ein No-Connect-Kreuz. Danach: just erc

Aufruf (über just):  just schematic

Achtung: überschreibt hardware/main-board/louie-main.kicad_sch. Sobald der Schaltplan
im KiCad-GUI weiterbearbeitet wird, ist dieses Skript nur noch Referenz.
"""
import math
import re
import uuid
from pathlib import Path

from sexpr import block_end, find_symbol, symbol_pins

HARDWARE = Path(__file__).resolve().parent.parent
SCH = HARDWARE / "main-board" / "louie-main.kicad_sch"
KICAD_SYMBOLS = Path("/usr/share/kicad/symbols")
LIBS = {
    "louie": HARDWARE / "lib" / "louie.kicad_sym",
    "Device": KICAD_SYMBOLS / "Device.kicad_sym",
    "Driver_Motor": KICAD_SYMBOLS / "Driver_Motor.kicad_sym",
    "Regulator_Linear": KICAD_SYMBOLS / "Regulator_Linear.kicad_sym",
    "Connector": KICAD_SYMBOLS / "Connector.kicad_sym",
    "Connector_Generic": KICAD_SYMBOLS / "Connector_Generic.kicad_sym",
    "power": KICAD_SYMBOLS / "power.kicad_sym",
}

R0402 = "Resistor_SMD:R_0402_1005Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
C1206 = "Capacitor_SMD:C_1206_3216Metric"
TP_SMALL = "TestPoint:TestPoint_Pad_D1.5mm"
TP_CONTACT = "TestPoint:TestPoint_Pad_2.0x2.0mm"  # Platzhalter, Kontaktmechanik offen


def R(ref, value, n1, n2, at, fp=R0402):
    return dict(ref=ref, lib="Device:R", value=value, fp=fp, at=at, pins={"1": n1, "2": n2})


def C(ref, value, n1, n2, at, fp=C0402):
    return dict(ref=ref, lib="Device:C", value=value, fp=fp, at=at, pins={"1": n1, "2": n2})


def TP(ref, value, net, at, fp=TP_SMALL):
    # reine Kupferfläche: nicht in der Stückliste
    return dict(ref=ref, lib="Connector:TestPoint", value=value, fp=fp, at=at, pins={"1": net}, bom=False)


def FLAG(n, net, at):
    return dict(ref=f"#FLG0{n}", lib="power:PWR_FLAG", value="PWR_FLAG", fp="", at=at, pins={"1": net})


# ---------------------------------------------------------------------------------------------
# Schaltung (Koordinaten in mm auf dem A3-Blatt, Raster 2,54 mm)
# ---------------------------------------------------------------------------------------------
BLOCKS = [
    ("Versorgung und Kabel zur Ladeplatine", (25.4, 25.4)),
    ("3,3-V-Regler", (25.4, 111.76)),
    ("ESP32-C3", (139.7, 25.4)),
    ("Ausgangsstufe (DRV8833, beide Kanäle parallel, Strombegrenzung ca. 2 A)", (254, 25.4)),
    ("Schalter-/Last-Erkennung und Kontakte an den Platinenenden", (254, 175.26)),
    ("Akkuspannung", (25.4, 175.26)),
    ("Beschleunigungssensor (I2C 0x18, INT1 an RXD)", (25.4, 228.6)),
]

PARTS = [
    # --- Kabel zur Ladeplatine: 1 VSYS, 2 D+, 3 D-, 4 GND --------------------------------------
    dict(ref="J1", lib="Connector_Generic:Conn_01x04", value="Kabel Ladeplatine",
         fp="louie:SolderPads_1x04_P2.00mm", bom=False,  # Lötpads für Litzen, keine Bestückung
         at=(50.8, 50.8), pins={"1": "VSYS", "2": "USB_D+", "3": "USB_D-", "4": "GND"}),
    FLAG(1, "VSYS", (76.2, 43.18)),
    FLAG(2, "GND", (88.9, 43.18)),

    # --- LDO ----------------------------------------------------------------------------------
    dict(ref="U3", lib="Regulator_Linear:AP2112K-3.3", value="AP2112K-3.3", lcsc="C51118",
         fp="Package_TO_SOT_SMD:SOT-23-5", at=(63.5, 137.16), ref_at=(-5.08, -6.35), val_at=(1.27, 7.62),
         pins={"1": "VSYS", "3": "VSYS", "2": "GND", "5": "+3V3"}),
    C("C8", "1u", "VSYS", "GND", (38.1, 137.16)),
    C("C11", "1u", "+3V3", "GND", (88.9, 137.16)),

    # --- Akkuspannung: 470k/470k, 4,2 V -> 2,1 V ------------------------------------------------
    R("R6", "470k", "VSYS", "VBAT_ADC", (38.1, 195.58)),
    R("R7", "470k", "VBAT_ADC", "GND", (50.8, 195.58)),
    C("C13", "100n", "VBAT_ADC", "GND", (63.5, 195.58)),

    # --- ESP32-C3 -----------------------------------------------------------------------------
    dict(ref="U1", lib="louie:ESP32-C3-MINI-1", value="ESP32-C3-MINI-1-N4", lcsc="C2838502",
         fp="lcsc:WIFIM-SMD_ESP32-C3-MINI-1", at=(177.8, 76.2), ref_at=(-12.7, -16.51), val_at=(2.54, 15.24),
         pins={"3": "+3V3", "8": "EN", "12": "VBAT_ADC", "13": "ISEN_ADC", "5": "IO2", "6": "SENSE",
               "18": "DRV_IN1", "19": "DRV_IN2", "20": "DRV_nSLEEP", "21": "DRV_nFAULT",
               "22": "IO8", "23": "BOOT", "16": "LED", "26": "USB_D-", "27": "USB_D+",
               "30": "RXD", "31": "TXD", "1": "GND"}),
    C("C9", "10u", "+3V3", "GND", (152.4, 127), fp=C0603),
    C("C10", "100n", "+3V3", "GND", (165.1, 127)),
    R("R2", "10k", "+3V3", "EN", (190.5, 127)),
    C("C12", "1u", "EN", "GND", (203.2, 127)),
    R("R10", "10k", "+3V3", "IO2", (215.9, 127)),   # Strapping-Pin
    R("R11", "10k", "+3V3", "IO8", (228.6, 127)),   # Strapping-Pin
    R("R9", "1k", "LED", "LED_A", (152.4, 162.56)),
    dict(ref="D1", lib="Device:LED", value="grün", fp="LED_SMD:LED_0402_1005Metric",
         at=(170.18, 172.72), pins={"2": "LED_A", "1": "GND"}),
    # Unterseite: Lötpads im 2,54-mm-Raster (Stiftleiste/Kabel), keine Bestückung
    dict(ref="J2", lib="Connector_Generic:Conn_01x05", value="Erweiterung I2C", bom=False,
         fp="louie:SolderPads_1x05_P2.54mm", at=(203.2, 172.72),
         pins={"1": "+3V3", "2": "GND", "3": "IO8", "4": "IO2", "5": "RXD"}),   # 3V3 GND SDA SCL INT
    dict(ref="J3", lib="Connector_Generic:Conn_01x04", value="Service Taster", bom=False,
         fp="louie:SolderPads_1x04_P2.54mm", at=(228.6, 172.72),
         pins={"1": "EN", "2": "TXD", "3": "BOOT", "4": "GND"}),                # Taster an 3+4

    # --- Ausgangsstufe ---------------------------------------------------------------------------
    dict(ref="U2", lib="louie:DRV8833PWP_parallel", value="DRV8833PWP", lcsc="C50506",
         fp="Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.46x2.31mm",  # Vias selbst setzen (0,3 mm)
         at=(304.8, 76.2), ref_at=(-10.16, -8.89), val_at=(2.54, 10.16),
         pins={"1": "DRV_nSLEEP", "11": "VCP", "3": "ISEN", "16": "DRV_IN1", "15": "DRV_IN2",
               "13": "GND", "14": "VINT", "12": "VSYS", "8": "DRV_nFAULT", "2": "OUT_A", "4": "OUT_B"}),
    C("C1", "47u 10V", "VSYS", "GND", (269.24, 124.46), fp=C1206),
    C("C2", "47u 10V", "VSYS", "GND", (281.94, 124.46), fp=C1206),
    C("C3", "47u 10V", "VSYS", "GND", (294.64, 124.46), fp=C1206),
    C("C4", "100n", "VSYS", "GND", (307.34, 124.46)),
    C("C5", "100n", "VSYS", "GND", (320.04, 124.46)),
    C("C6", "2.2u", "VINT", "GND", (332.74, 124.46)),
    C("C7", "10n", "VCP", "VSYS", (345.44, 124.46)),
    R("R1", "0.1 1%", "ISEN", "GND", (269.24, 147.32), fp="Resistor_SMD:R_0805_2012Metric"),
    R("R8", "1k", "ISEN", "ISEN_ADC", (284.48, 147.32)),
    C("C14", "100n", "ISEN_ADC", "GND", (299.72, 147.32)),

    # --- Schalter-/Last-Erkennung: Schalter offen -> SENSE 3,3 V, zu -> ca. 0,3 V --------------------
    R("R3", "100k", "+3V3", "OUT_A", (269.24, 198.12)),
    R("R4", "10k", "OUT_B", "GND", (284.48, 198.12)),
    R("R5", "100k", "OUT_A", "SENSE", (299.72, 198.12)),
    # --- Beschleunigungssensor ----------------------------------------------------------------
    dict(ref="U4", lib="louie:LIS2DH12", value="LIS2DH12TR", lcsc="C110926",
         fp="Package_LGA:LGA-12_2x2mm_P0.5mm", at=(76.2, 246.38), ref_at=(-7.62, -8.89), val_at=(2.54, 11.43),
         pins={"9": "+3V3", "10": "+3V3", "2": "+3V3", "3": "GND", "5": "GND", "6": "GND",
               "1": "IO2", "4": "IO8", "12": "RXD"}),
    C("C15", "100n", "+3V3", "GND", (38.1, 246.38)),
    TP("BT1", "Kontakt A", "OUT_A", (322.58, 198.12), fp=TP_CONTACT),
    TP("BT2", "Kontakt B", "OUT_B", (337.82, 198.12), fp=TP_CONTACT),
]

# ---------------------------------------------------------------------------------------------


def uid():
    return str(uuid.uuid4())


def fmt(v):
    return f"{round(v, 4):g}"


def embedded_symbol(lib_id):
    """Symbol aus der Bibliothek holen, abgeleitete Symbole auflösen, mit Bibliotheksnamen versehen."""
    lib, name = lib_id.split(":")
    text = LIBS[lib].read_text()
    sym = find_symbol(text, name)
    parent = re.search(r'\(extends "([^"]+)"\)', sym)
    if parent:
        # wie KiCad: Grafik und Pins vom Basissymbol, Felder vom abgeleiteten Symbol
        base = find_symbol(text, parent.group(1)).replace(f'"{parent.group(1)}', f'"{name}')
        for key, block in properties(sym).items():
            old = properties(base).get(key)
            base = base.replace(old, block) if old else base.replace("\n", "\n" + block, 1)
        sym = base
    return sym.replace(f'(symbol "{name}"', f'(symbol "{lib_id}"', 1), symbol_pins(sym)


def properties(sym_text):
    """Property-Blöcke der obersten Ebene eines Symbols: {Name: Text}."""
    result = {}
    for m in re.finditer(r'\(property "([^"]+)"', sym_text):
        result.setdefault(m.group(1), sym_text[m.start():block_end(sym_text, m.start())])
    return result


def label_effects(angle):
    justify = "left" if angle in (0, 90) else "right"
    return f"(effects (font (size 1.27 1.27)) (justify {justify} bottom))"


def main():
    root = uid()
    lib_symbols, pin_cache = {}, {}
    items = []

    for part in PARTS:
        if part["lib"] not in lib_symbols:
            lib_symbols[part["lib"]], pin_cache[part["lib"]] = embedded_symbol(part["lib"])
        pins = pin_cache[part["lib"]]
        x, y = part["at"]
        is_power = part["ref"].startswith("#")
        in_bom = part.get("bom", True) and not is_power

        # Bauteil
        rx, ry = part.get("ref_at", (2.54, -1.27))
        vx, vy = part.get("val_at", (2.54, 1.27))
        props = [("Reference", part["ref"], (x + rx, y + ry), is_power),
                 ("Value", part["value"], (x + vx, y + vy), False),
                 ("Footprint", part["fp"], (x, y), True),
                 ("Datasheet", "~", (x, y), True),
                 ("Description", "", (x, y), True)]
        if part.get("lcsc"):
            props.append(("LCSC Part", part["lcsc"], (x, y), True))
        prop_text = "".join(
            f'\t\t(property "{k}" "{v}" (at {fmt(px)} {fmt(py)} 0) (effects (font (size 1.27 1.27))'
            f'{" (justify left)" if not hide else ""}{" (hide yes)" if hide else ""}))\n'
            for k, v, (px, py), hide in props)
        pin_text = "".join(f'\t\t(pin "{p["number"]}" (uuid "{uid()}"))\n' for p in pins)
        items.append(
            f'\t(symbol (lib_id "{part["lib"]}") (at {fmt(x)} {fmt(y)} 0) (unit 1)\n'
            f'\t\t(exclude_from_sim no) (in_bom {"yes" if in_bom else "no"}) (on_board {"no" if is_power else "yes"}) (dnp no)\n'
            f'\t\t(uuid "{uid()}")\n{prop_text}{pin_text}'
            f'\t\t(instances (project "louie-main" (path "/{root}" (reference "{part["ref"]}") (unit 1))))\n'
            '\t)\n')

        # Drähte, Labels, No-Connects
        seen_positions = set()
        for p in pins:
            if p["hidden"] or p["type"] == "no_connect":
                continue
            px, py = x + p["x"], y - p["y"]
            if (px, py) in seen_positions:
                continue
            seen_positions.add((px, py))
            net = part["pins"].get(p["number"])
            if net is None:
                items.append(f'\t(no_connect (at {fmt(px)} {fmt(py)}) (uuid "{uid()}"))\n')
                continue
            if is_power:  # PWR_FLAG: Pin liegt im Ursprung, Label direkt darunter
                angle, length = 270, 2.54
            else:
                angle, length = (p["rot"] + 180) % 360, 2.54
            ex = px + length * math.cos(math.radians(angle))
            ey = py - length * math.sin(math.radians(angle))
            items.append(f'\t(wire (pts (xy {fmt(px)} {fmt(py)}) (xy {fmt(ex)} {fmt(ey)}))\n'
                         f'\t\t(stroke (width 0) (type default)) (uuid "{uid()}"))\n')
            items.append(f'\t(label "{net}" (at {fmt(ex)} {fmt(ey)} {int(angle)}) {label_effects(int(angle))}\n'
                         f'\t\t(uuid "{uid()}"))\n')

    for title, (tx, ty) in BLOCKS:
        items.append(f'\t(text "{title}" (exclude_from_sim no) (at {fmt(tx)} {fmt(ty)} 0)\n'
                     '\t\t(effects (font (size 2 2) (bold yes)) (justify left bottom))\n'
                     f'\t\t(uuid "{uid()}"))\n')

    SCH.write_text(
        '(kicad_sch\n'
        '\t(version 20250114)\n'
        '\t(generator "eeschema")\n'
        '\t(generator_version "9.0")\n'
        f'\t(uuid "{root}")\n'
        '\t(paper "A3")\n'
        '\t(title_block\n'
        '\t\t(title "Looping Louie WLAN-Upgrade – Hauptplatine")\n'
        '\t\t(rev "0.1")\n'
        '\t\t(comment 1 "Platine im AA-Format, siehe docs/hardware-konzept.md")\n'
        '\t\t(comment 2 "Erzeugt mit hardware/scripts/gen_main_schematic.py")\n'
        '\t)\n'
        '\t(lib_symbols\n' + "".join("\t\t" + s.replace("\n", "\n\t\t") + "\n" for s in lib_symbols.values()) + '\t)\n'
        + "".join(items) +
        '\t(sheet_instances (path "/" (page "1")))\n'
        '\t(embedded_fonts no)\n'
        ')\n'
    )
    print(f"{SCH.relative_to(HARDWARE.parent)}: {len(PARTS)} Bauteile")


if __name__ == "__main__":
    main()
