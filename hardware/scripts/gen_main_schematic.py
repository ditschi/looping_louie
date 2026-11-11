#!/usr/bin/env python3
"""Generates the main board schematic from the circuit description below.

Every connected pin gets a short wire with a net label, unused pins get a
no-connect cross. Afterwards: just erc

Usage (via just):  just schematic

Warning: overwrites hardware/main-board/louie-main.kicad_sch. Once the schematic is
edited further in the KiCad GUI, this script is only a reference.
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
    "Battery_Management": KICAD_SYMBOLS / "Battery_Management.kicad_sym",
    "Power_Protection": KICAD_SYMBOLS / "Power_Protection.kicad_sym",
    "Transistor_FET": KICAD_SYMBOLS / "Transistor_FET.kicad_sym",
    "Power_Management": KICAD_SYMBOLS / "Power_Management.kicad_sym",
    "Jumper": KICAD_SYMBOLS / "Jumper.kicad_sym",
}

R0402 = "Resistor_SMD:R_0402_1005Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
C1206 = "Capacitor_SMD:C_1206_3216Metric"
TP_SMALL = "TestPoint:TestPoint_Pad_D1.5mm"
TEST_PAD = "louie:TestPad_D1.0mm"  # bottom side, bring-up (docs/idea-optional-hardware.md 0.4)
TP_CONTACT = "TestPoint:TestPoint_Pad_2.0x2.0mm"  # placeholder, contact mechanics open


def R(ref, value, n1, n2, at, fp=R0402, **extra):
    return dict(ref=ref, lib="Device:R", value=value, fp=fp, at=at, pins={"1": n1, "2": n2}, **extra)


def C(ref, value, n1, n2, at, fp=C0402, **extra):
    return dict(ref=ref, lib="Device:C", value=value, fp=fp, at=at, pins={"1": n1, "2": n2}, **extra)


# Optional parts on the bottom (docs/idea-optional-hardware.md 0/0b): footprint present, not populated (DNP). The
# BOM lists them with a DNP flag; just fab leaves them out of the placement file and the JLC BOM.
def DNP(part):
    return dict(part, dnp=True)


def TP(ref, value, net, at, fp=TP_SMALL):
    # bare copper pad: not in the BOM
    return dict(ref=ref, lib="Connector:TestPoint", value=value, fp=fp, at=at, pins={"1": net}, bom=False)


def FLAG(n, net, at):
    return dict(ref=f"#FLG0{n}", lib="power:PWR_FLAG", value="PWR_FLAG", fp="", at=at, pins={"1": net})


# ---------------------------------------------------------------------------------------------
# Circuit (coordinates in mm on the A3 sheet, grid 2.54 mm)
# ---------------------------------------------------------------------------------------------
BLOCKS = [
    ("USB-C (flashing + 5 V operation), ESD protection, VBUS detection", (25.4, 25.4)),
    ("Power path: VBUS via D2, battery/charger board (BAT_IN) via Q1 -> VSYS", (25.4, 116.84)),
    ("3.3 V buck converter and battery voltage (VSYS)", (25.4, 200.66)),
    ("ESP32-C6", (139.7, 25.4)),
    ("Output stage (DRV8213, current sensing IPROPI, current limit approx. 2 A)", (254, 25.4)),
    ("Lever detection (lever closed = SENSE HIGH) and contacts at the board ends", (254, 175.26)),
    ("Expansion pads (I2C/INT) and service pads, bottom side", (139.7, 200.66)),
    ("Accelerometer (I2C 0x18, INT1 to IO2), population optional", (254, 213.36)),
    ("Bottom, DNP: player pads J6", (350.52, 33.02)),
    ("Bottom, DNP: LED pads J7, U6", (350.52, 116.84)),
    ("Bottom: test points", (139.7, 246.38)),
]

PARTS = [
    # --- USB-C: sink (CC 5.1 k), data directly to IO12/IO13 -----------------------------------------
    dict(ref="J4", lib="Connector:USB_C_Receptacle_USB2.0_16P", value="TYPE-C-31-M-12", lcsc="C165948",
         fp="louie:USB_C_Receptacle_HRO_TYPE-C-31-M-12", at=(45.72, 60.96), ref_at=(-10.16, -24.13),
         val_at=(2.54, 26.67),
         pins={"A4": "VBUS_J4", "A9": "VBUS_J4", "B4": "VBUS_J4", "B9": "VBUS_J4", "A5": "CC1", "B5": "CC2",
               "A6": "USB_D+", "B6": "USB_D+", "A7": "USB_D-", "B7": "USB_D-",
               "A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND", "S1": "GND"}),
    R("R12", "5.1k", "CC1", "GND", (83.82, 40.64)),
    R("R13", "5.1k", "CC2", "GND", (96.52, 40.64)),
    dict(ref="U5", lib="Power_Protection:USBLC6-2SC6", value="USBLC6-2SC6", lcsc="C7519",
         fp="Package_TO_SOT_SMD:SOT-23-6", at=(96.52, 71.12), ref_at=(-7.62, -8.89), val_at=(2.54, 10.16),
         # Flow-through (ST DS4260 Rev 5, Fig. 1/7/18): I/O1 = pins 1 and 6, I/O2 = pins 3 and 4 are each
         # the same node. The line comes from J4 to pin 1/3 and continues under the package to pin 6/4
         # towards the module (no branch/stub).
         pins={"1": "USB_D+", "6": "USB_D+", "3": "USB_D-", "4": "USB_D-", "5": "VBUS_J4", "2": "GND"}),
    # VBUS_DET: divider 100k/100k to IO4 (5 V -> 2.5 V), also gate pull-down of Q1, discharges VBUS
    R("R14", "100k", "VBUS_J4", "VBUS_DET", (83.82, 101.6)),
    R("R15", "100k", "VBUS_DET", "GND", (106.68, 101.6)),
    FLAG(3, "VBUS_J4", (114.3, 40.64)),

    # --- Power path (Microchip AN1149 without charge controller) -------------------------------------
    dict(ref="D2", lib="Device:D_Schottky", value="SS34F", lcsc="C60396", fp="lcsc:SMAF_L3.5-W2.6-LS4.7-RD",
         at=(50.8, 134.62), pins={"2": "VBUS_J4", "1": "VSYS"}),
    # Gate to VBUS: with USB, Q1 blocks (no charging of the cell from VBUS), without USB it conducts (gate via
    # R14+R15 to GND). Body diode BAT_IN -> VSYS; cell reversed -> Q1 blocks (reverse polarity protection).
    dict(ref="Q1", lib="Transistor_FET:AO3401A", value="AO3401A", lcsc="C15127",
         fp="Package_TO_SOT_SMD:SOT-23", at=(78.74, 152.4), ref_at=(5.08, -2.54), val_at=(5.08, 2.54),
         pins={"1": "VBUS_J4", "2": "VSYS", "3": "BAT_IN"}),
    # Bottom side: cable to the charger board (1 BAT_IN, 4 GND; 2/3 free) and battery pads (cell direct)
    dict(ref="J1", lib="Connector_Generic:Conn_01x04", value="Charger cable",
         fp="louie:SolderPads_1x04_P2.00mm", bom=False,  # solder pads for stranded wires, not populated
         # Only BAT_IN and GND: flashing exclusively via J4 (client decision). Pads 2/3 stay without
         # a net so that the cable pinout of charger board v0.1 (1 VSYS, 2 D+, 3 D-, 4 GND) fits
         at=(45.72, 175.26), pins={"1": "BAT_IN", "4": "GND"}),
    dict(ref="J5", lib="Connector_Generic:Conn_01x02", value="Battery +/-",
         fp="louie:SolderPads_1x02_2.5x3.5mm", bom=False,
         at=(91.44, 177.8), pins={"1": "BAT_IN", "2": "GND"}),
    FLAG(1, "VSYS", (101.6, 129.54)),
    FLAG(2, "GND", (114.3, 129.54)),
    FLAG(4, "BAT_IN", (101.6, 162.56)),

    # --- 3.3 V buck (rev B, docs/proposal-supply-buck.md): TPS62162 fixed 3.3 V, 3-17 V in, 1 A, 17 uA, WSON-8 2x2
    # (same DSG package as the DRV8213). EN tied to VIN, FB to AGND (fixed version), PG open, VOS at the output
    # capacitor. L1 2.2 uH (Murata DFE201612P, 2016), CIN 10 uF, COUT 22 uF. Replaces the LDO SPX3819 (rev A).
    dict(ref="U3", lib="louie:TPS62162DSG", value="TPS62162DSGR", lcsc="C40256",
         fp="Package_SON:WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm", at=(63.5, 228.6), ref_at=(-10.16, -8.89),
         val_at=(2.54, 10.16),
         pins={"2": "VSYS", "3": "VSYS", "1": "GND", "4": "GND", "9": "GND", "5": "GND", "6": "+3V3", "7": "SW3V3"}),
    dict(ref="L1", lib="Device:L", value="2.2uH", lcsc="C79317", fp="Inductor_SMD:L_Murata_DFE201610P",
         at=(91.44, 220.98), pins={"1": "SW3V3", "2": "+3V3"}),
    C("C8", "10u 10V", "VSYS", "GND", (38.1, 228.6)),
    FLAG(5, "+3V3", (114.3, 220.98)),  # the buck output (inductor) drives +3V3; the ERC needs a power flag

    # --- Battery voltage: 680k/470k, VSYS up to 6.6 V (4 x AA fresh) -> 2.7 V (C6 ADC up to 3.3 V) --------
    R("R6", "680k", "VSYS", "VBAT_ADC", (38.1, 264.16)),
    R("R7", "470k", "VBAT_ADC", "GND", (50.8, 264.16)),
    C("C13", "100n", "VBAT_ADC", "GND", (76.2, 264.16)),

    # --- ESP32-C6 -----------------------------------------------------------------------------
    dict(ref="U1", lib="louie:ESP32-C6-MINI-1", value="ESP32-C6-MINI-1-H8", lcsc="C42403058",
         fp="lcsc:WIFIM-SMD_ESP32-C6-MINI-1", at=(177.8, 73.66), ref_at=(-12.7, -24.13), val_at=(2.54, 24.13),
         pins={"3": "+3V3", "8": "EN", "1": "GND", "12": "VBAT_ADC", "13": "ISEN_ADC", "5": "INT", "6": "SENSE",
               "9": "VBUS_DET", "10": "IO5", "15": "SDA", "16": "SCL", "22": "IO8", "23": "BOOT",
               "17": "USB_D-", "18": "USB_D+", "19": "LED", "24": "MOT_IN1", "25": "MOT_IN2", "31": "TXD",
               # expansions on the bottom (all optional): IO15 LED supply on, IO20/IO21 player inputs,
               # IO23 LED data, RXD console (J3-5); IO22 free (spare)
               "20": "IO15", "26": "IO20", "27": "IO21", "29": "IO23", "30": "RXD"}),
    C("C9", "22u 10V", "+3V3", "GND", (152.4, 139.7), fp=C0805),  # buck output capacitor (rev B)
    C("C10", "100n", "+3V3", "GND", (165.1, 139.7)),
    R("R2", "10k", "+3V3", "EN", (177.8, 139.7)),
    C("C12", "1u", "EN", "GND", (190.5, 139.7)),
    R("R16", "10k", "+3V3", "SDA", (203.2, 139.7)),  # I2C, breakouts often have no pull-ups
    R("R10", "10k", "+3V3", "SCL", (215.9, 139.7)),
    R("R11", "10k", "+3V3", "IO8", (228.6, 139.7)),  # strapping pin, 1 during download
    R("R9", "1k", "LED", "LED_A", (152.4, 165.1)),
    dict(ref="D1", lib="Device:LED", value="green", fp="LED_SMD:LED_0402_1005Metric",
         at=(170.18, 175.26), pins={"2": "LED_A", "1": "GND"}),
    # Bottom side: solder pads at 2.54 mm pitch (pin header/cable), not populated
    dict(ref="J2", lib="Connector_Generic:Conn_01x05", value="I2C expansion", bom=False,
         fp="louie:SolderPads_1x05_P2.54mm", at=(165.1, 228.6),
         pins={"1": "+3V3", "2": "GND", "3": "SDA", "4": "SCL", "5": "INT"}),   # sensor breakout/switch
    # Service: full UART0 console (TXD, RXD), EN, BOOT, GND – e.g. pogo adapter; button on 3+4
    dict(ref="J3", lib="Connector_Generic:Conn_01x05", value="Service", bom=False,
         fp="louie:SolderPads_1x05_P2.54mm", at=(203.2, 228.6),
         pins={"1": "EN", "2": "TXD", "3": "BOOT", "4": "GND", "5": "RXD"}),

    # --- Output stage -------------------------------------------------------------------------------
    # GAINSEL to GND: 205 µA/A; R1 = R_IPROPI: ITRIP = 0.51 V / (1.24 k × 205 µA/A) ≈ 2 A
    dict(ref="U2", lib="louie:DRV8213DSG", value="DRV8213DSG", lcsc="C22407186",
         fp="Package_SON:WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm",  # = Texas DSG0008A, with 3D model
         at=(304.8, 76.2), ref_at=(-10.16, -8.89), val_at=(2.54, 10.16),
         pins={"1": "VSYS", "2": "OUT_A", "3": "OUT_B", "4": "GND", "9": "GND", "5": "MOT_IN2", "6": "MOT_IN1",
               "7": "GND", "8": "ISEN"}),
    C("C1", "47u 16V", "VSYS", "GND", (269.24, 124.46), fp=C1206),
    C("C2", "47u 16V", "VSYS", "GND", (281.94, 124.46), fp=C1206),
    C("C4", "100n", "VSYS", "GND", (294.64, 124.46)),
    R("R1", "1.24k 1%", "ISEN", "GND", (269.24, 147.32)),
    # capacitor not directly at IPROPI (delays the current limit), but behind R8
    R("R8", "1k", "ISEN", "ISEN_ADC", (284.48, 147.32)),
    C("C14", "100n", "ISEN_ADC", "GND", (299.72, 147.32)),

    # --- Lever detection: open -> SENSE 0 V, closed -> approx. 3.0 V (WAKEUP_ANY_HIGH) ----------------
    R("R3", "100k", "OUT_A", "GND", (269.24, 198.12)),
    R("R4", "10k", "OUT_B", "+3V3", (284.48, 198.12)),
    # 470 k (was 100 k): limits the current into the IO3 clamp diodes while OUT_A switches up to VSYS 6.6 V to approx. 6 µA
    R("R5", "470k", "OUT_A", "SENSE", (299.72, 198.12)),
    TP("BT1", "Contact A", "OUT_A", (322.58, 198.12), fp=TP_CONTACT),
    TP("BT2", "Contact B", "OUT_B", (337.82, 198.12), fp=TP_CONTACT),

    # --- Accelerometer: population optional (DNP possible), INT1 wakes from deep sleep via IO2 ---------
    dict(ref="U4", lib="louie:LIS2DH12", value="LIS2DH12TR", lcsc="C110926",
         fp="Package_LGA:LGA-12_2x2mm_P0.5mm", at=(304.8, 233.68), ref_at=(-7.62, -8.89), val_at=(2.54, 11.43),
         # SA0 (pin 3) on 3V3: address 0x19, no current through the internal SA0 pull-up (on GND approx. 150 µA)
         pins={"9": "+3V3", "10": "+3V3", "2": "+3V3", "3": "+3V3", "5": "GND", "6": "GND",
               "1": "SCL", "4": "SDA", "12": "INT"}),
    C("C15", "100n", "+3V3", "GND", (266.7, 233.68)),

    # --- Bottom side, optional (docs/idea-optional-hardware.md 0b.4): none of this is populated ---------------------
    # J6 "Players": S1 = IO5 (deep-sleep wake-up, ADC), S2 = IO20, S3 = IO21, S4 = IO8 (R11 10 k present);
    # button/reed to GND with internal pull-up (45 k) and 1 kΩ in series in the cable; no RC footprints
    dict(ref="J6", lib="Connector_Generic:Conn_01x06", value="Players S1-S4", bom=False,
         fp="louie:SolderPads_1x06_P2.00mm", at=(355.6, 66.04),
         pins={"1": "+3V3", "2": "IO5", "3": "IO20", "4": "IO21", "5": "IO8", "6": "GND"}),
    # IO5: R to 3V3 (pull-up, resistor ladder), R and C to GND (NTC, piezo bleed, filter)
    DNP(R("R19", "10k", "IO5", "+3V3", (370.84, 48.26), lcsc="C25744")),
    DNP(R("R20", "1M", "IO5", "GND", (383.54, 48.26))),
    DNP(C("C16", "10n", "IO5", "GND", (396.24, 48.26), lcsc="C15195")),

    # J7 "LED": 1 VLED, 2 IO23 (NeoPixel data/LED/button), 3 GND. VLED from LDO U6 (adjustable, approx. 3.95 V; enable
    # IO15, R22 keeps it off in reset and deep sleep; switch, voltage and current limit for VSYS up to 6.6 V), C18 at its
    # output, C17 as buffer. No PTC: U6 limits at approx. 0.8-0.95 A and has thermal shutdown. The 330 Ω series resistor
    # belongs at the LED end of the cable.
    dict(ref="J7", lib="Connector_Generic:Conn_01x03", value="LED", bom=False,
         fp="louie:SolderPads_1x03_P2.54mm", at=(355.6, 154.94), pins={"1": "VLED", "2": "IO23", "3": "GND"}),
    # SPX3819 adjustable (EN V_IH 2.0 V): VOUT = 1.235 V × (1 + R23/R24) = 3.95 V. At 3.95 V the V5 LED types need
    # V_IH 0.63 × 3.95 = 2.49 V, below the guaranteed ESP32 V_OH (2.64 V); at 5.0 V (3.15 V) the 3.3 V data line
    # would be out of spec without a level shifter, and there is no room for one on the bottom.
    DNP(dict(ref="U6", lib="Regulator_Linear:SPX3819M5-L", value="SPX3819M5-L (adj. 3.95 V)",
             fp="Package_TO_SOT_SMD:SOT-23-5", at=(383.54, 144.78), ref_at=(-7.62, -8.89), val_at=(2.54, 10.16),
             pins={"1": "VSYS", "2": "GND", "3": "IO15", "4": "VLED_ADJ", "5": "VLED"})),
    DNP(R("R23", "220k", "VLED", "VLED_ADJ", (401.32, 139.7))),
    DNP(R("R24", "100k", "VLED_ADJ", "GND", (401.32, 152.4))),
    DNP(C("C18", "2.2u", "VLED", "GND", (414.02, 144.78))),
    DNP(C("C17", "10u", "VLED", "GND", (401.32, 167.64), fp=C0805, lcsc="C1713")),
    DNP(R("R22", "100k", "IO15", "GND", (370.84, 170.18), lcsc="C25741")),

    # test points (probe tip, test adapter)
    TP("TP1", "VSYS", "VSYS", (152.4, 254.0), fp=TEST_PAD),
    TP("TP2", "VBUS", "VBUS_J4", (165.1, 254.0), fp=TEST_PAD),
]

# ---------------------------------------------------------------------------------------------


def uid(*name):
    """Fixed UUIDs (uuid5 from project and name or sequence number): re-running just schematic does not change
    the symbol ↔ footprint link (path in the .kicad_pcb), the schematic parity check in the DRC stays valid."""
    key = "/".join(name) if name else f"item/{next(_SEQ)}"
    return str(uuid.uuid5(_NS, f"{_PROJECT}/{key}"))


_NS = uuid.UUID("7d3c1d52-4f1e-4a8e-9a55-1f0c2b6e9a10")
_PROJECT = "louie-main"
_SEQ = iter(range(1, 10 ** 9))


def fmt(v):
    return f"{round(v, 4):g}"


def embedded_symbol(lib_id):
    """Fetch a symbol from the library, resolve derived symbols, prefix it with the library name."""
    lib, name = lib_id.split(":")
    text = LIBS[lib].read_text()
    sym = find_symbol(text, name)
    parent = re.search(r'\(extends "([^"]+)"\)', sym)
    if parent:
        # like KiCad: graphics and pins from the base symbol, fields from the derived symbol
        base = find_symbol(text, parent.group(1)).replace(f'"{parent.group(1)}', f'"{name}')
        for key, block in properties(sym).items():
            old = properties(base).get(key)
            base = base.replace(old, block) if old else base.replace("\n", "\n" + block, 1)
        sym = base
    return sym.replace(f'(symbol "{name}"', f'(symbol "{lib_id}"', 1), symbol_pins(sym)


def properties(sym_text):
    """Top-level property blocks of a symbol: {name: text}."""
    result = {}
    for m in re.finditer(r'\(property "([^"]+)"', sym_text):
        result.setdefault(m.group(1), sym_text[m.start():block_end(sym_text, m.start())])
    return result


def label_effects(angle):
    justify = "left" if angle in (0, 90) else "right"
    return f"(effects (font (size 1.27 1.27)) (justify {justify} bottom))"


TITLE = "Looping Louie Wi-Fi upgrade – main board"
COMMENT = "AA-format board, see docs/hardware-concept.md"


def main(sch=SCH, parts=PARTS, blocks=BLOCKS, title=TITLE, comment=COMMENT, project="louie-main",
         generator="gen_main_schematic.py"):
    """Writes the schematic. Other boards (gen_charger_schematic.py) call this with their own data."""
    global _PROJECT, _SEQ
    _PROJECT, _SEQ = project, iter(range(1, 10 ** 9))
    root = uid("root")
    lib_symbols, pin_cache = {}, {}
    items = []

    for part in parts:
        if part["lib"] not in lib_symbols:
            lib_symbols[part["lib"]], pin_cache[part["lib"]] = embedded_symbol(part["lib"])
        pins = pin_cache[part["lib"]]
        x, y = part["at"]
        is_power = part["ref"].startswith("#")
        in_bom = part.get("bom", True) and not is_power
        dnp = part.get("dnp", False)

        # component
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
            f'\t\t(exclude_from_sim no) (in_bom {"yes" if in_bom else "no"}) (on_board {"no" if is_power else "yes"}) (dnp {"yes" if dnp else "no"})\n'
            f'\t\t(uuid "{uid("symbol", part["ref"])}")\n{prop_text}{pin_text}'
            f'\t\t(instances (project "{project}" (path "/{root}" (reference "{part["ref"]}") (unit 1))))\n'
            '\t)\n')

        # wires, labels, no-connects
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
            if is_power:  # PWR_FLAG: pin at the origin, label directly below
                angle, length = 270, 2.54
            else:
                angle, length = (p["rot"] + 180) % 360, 2.54
            ex = px + length * math.cos(math.radians(angle))
            ey = py - length * math.sin(math.radians(angle))
            items.append(f'\t(wire (pts (xy {fmt(px)} {fmt(py)}) (xy {fmt(ex)} {fmt(ey)}))\n'
                         f'\t\t(stroke (width 0) (type default)) (uuid "{uid()}"))\n')
            items.append(f'\t(label "{net}" (at {fmt(ex)} {fmt(ey)} {int(angle)}) {label_effects(int(angle))}\n'
                         f'\t\t(uuid "{uid()}"))\n')

    for block, (tx, ty) in blocks:
        items.append(f'\t(text "{block}" (exclude_from_sim no) (at {fmt(tx)} {fmt(ty)} 0)\n'
                     '\t\t(effects (font (size 2 2) (bold yes)) (justify left bottom))\n'
                     f'\t\t(uuid "{uid()}"))\n')

    sch.write_text(
        '(kicad_sch\n'
        '\t(version 20250114)\n'
        '\t(generator "eeschema")\n'
        '\t(generator_version "9.0")\n'
        f'\t(uuid "{root}")\n'
        '\t(paper "A3")\n'
        '\t(title_block\n'
        f'\t\t(title "{title}")\n'
        '\t\t(rev "0.1")\n'
        f'\t\t(comment 1 "{comment}")\n'
        f'\t\t(comment 2 "Generated with hardware/scripts/{generator}")\n'
        '\t)\n'
        '\t(lib_symbols\n' + "".join("\t\t" + s.replace("\n", "\n\t\t") + "\n" for s in lib_symbols.values()) + '\t)\n'
        + "".join(items) +
        '\t(sheet_instances (path "/" (page "1")))\n'
        '\t(embedded_fonts no)\n'
        ')\n'
    )
    print(f"{sch.relative_to(HARDWARE.parent)}: {len(parts)} components")


if __name__ == "__main__":
    main()
