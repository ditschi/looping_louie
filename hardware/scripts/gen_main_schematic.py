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
TEST_PAD = "louie:TestPad_D1.0mm"  # Unterseite, Inbetriebnahme (docs/idee-optionale-hardware.md 0.4)
TP_CONTACT = "TestPoint:TestPoint_Pad_2.0x2.0mm"  # Platzhalter, Kontaktmechanik offen


def R(ref, value, n1, n2, at, fp=R0402, **extra):
    return dict(ref=ref, lib="Device:R", value=value, fp=fp, at=at, pins={"1": n1, "2": n2}, **extra)


def C(ref, value, n1, n2, at, fp=C0402, **extra):
    return dict(ref=ref, lib="Device:C", value=value, fp=fp, at=at, pins={"1": n1, "2": n2}, **extra)


# Optionale Teile unten (docs/idee-optionale-hardware.md 0/0b): Footprint vorhanden, nicht bestückt (DNP). Die
# Stückliste führt sie mit DNP-Kennzeichen; just fab lässt sie in Bestückungsliste und JLC-Stückliste weg.
def DNP(part):
    return dict(part, dnp=True)


def TP(ref, value, net, at, fp=TP_SMALL):
    # reine Kupferfläche: nicht in der Stückliste
    return dict(ref=ref, lib="Connector:TestPoint", value=value, fp=fp, at=at, pins={"1": net}, bom=False)


def FLAG(n, net, at):
    return dict(ref=f"#FLG0{n}", lib="power:PWR_FLAG", value="PWR_FLAG", fp="", at=at, pins={"1": net})


# ---------------------------------------------------------------------------------------------
# Schaltung (Koordinaten in mm auf dem A3-Blatt, Raster 2,54 mm)
# ---------------------------------------------------------------------------------------------
BLOCKS = [
    ("USB-C (Flashen + 5-V-Betrieb), ESD-Schutz, VBUS-Erkennung", (25.4, 25.4)),
    ("Power-Path: VBUS über D2, Akku/Ladeplatine (BAT_IN) über Q1 -> VSYS", (25.4, 116.84)),
    ("3,3-V-Regler und Akkuspannung (VSYS)", (25.4, 200.66)),
    ("ESP32-C6", (139.7, 25.4)),
    ("Ausgangsstufe (DRV8213, Strommessung IPROPI, Strombegrenzung ca. 2 A)", (254, 25.4)),
    ("Hebel-Erkennung (Hebel zu = SENSE HIGH) und Kontakte an den Platinenenden", (254, 175.26)),
    ("Erweiterungs-Pads (I2C/INT) und Service-Pads, Unterseite", (139.7, 200.66)),
    ("Beschleunigungssensor (I2C 0x18, INT1 an IO2), bestückungsoptional", (254, 213.36)),
    ("Unten, DNP: Spieler-Pads J6", (350.52, 33.02)),
    ("Unten, DNP: LED-Pads J7, U6", (350.52, 116.84)),
    ("Unten: Testpunkte", (139.7, 246.38)),
]

PARTS = [
    # --- USB-C: Senke (CC 5,1 k), Daten direkt an IO12/IO13 ---------------------------------------
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
         # Durchgeschleift (ST DS4260 Rev 5, Fig. 1/7/18): I/O1 = Pin 1 und 6, I/O2 = Pin 3 und 4 sind je
         # derselbe Knoten. Die Leitung kommt von J4 an Pin 1/3 und läuft unter dem Gehäuse zu Pin 6/4 weiter
         # zum Modul (kein Abzweig/Stich).
         pins={"1": "USB_D+", "6": "USB_D+", "3": "USB_D-", "4": "USB_D-", "5": "VBUS_J4", "2": "GND"}),
    # VBUS_DET: Teiler 100k/100k an IO4 (5 V -> 2,5 V), zugleich Gate-Pull-down von Q1, entlädt VBUS
    R("R14", "100k", "VBUS_J4", "VBUS_DET", (83.82, 101.6)),
    R("R15", "100k", "VBUS_DET", "GND", (106.68, 101.6)),
    FLAG(3, "VBUS_J4", (114.3, 40.64)),

    # --- Power-Path (Microchip AN1149 ohne Laderegler) -----------------------------------------------
    dict(ref="D2", lib="Device:D_Schottky", value="SS34F", lcsc="C60396", fp="lcsc:SMAF_L3.5-W2.6-LS4.7-RD",
         at=(50.8, 134.62), pins={"2": "VBUS_J4", "1": "VSYS"}),
    # Gate an VBUS: mit USB sperrt Q1 (keine Ladung der Zelle aus VBUS), ohne USB leitet er (Gate über
    # R14+R15 an GND). Body-Diode BAT_IN -> VSYS; Zelle verpolt -> Q1 sperrt (Verpolschutz).
    dict(ref="Q1", lib="Transistor_FET:AO3401A", value="AO3401A", lcsc="C15127",
         fp="Package_TO_SOT_SMD:SOT-23", at=(78.74, 152.4), ref_at=(5.08, -2.54), val_at=(5.08, 2.54),
         pins={"1": "VBUS_J4", "2": "VSYS", "3": "BAT_IN"}),
    # Unterseite: Kabel zur Ladeplatine (1 BAT_IN, 4 GND; 2/3 frei) und Akku-Pads (Zelle direkt)
    dict(ref="J1", lib="Connector_Generic:Conn_01x04", value="Kabel Ladeplatine",
         fp="louie:SolderPads_1x04_P2.00mm", bom=False,  # Lötpads für Litzen, keine Bestückung
         # Nur BAT_IN und GND: Flashen ausschließlich über J4 (Entscheidung Auftraggeber). Pads 2/3 bleiben
         # ohne Netz, damit die Kabelbelegung der Ladeplatine v0.1 (1 VSYS, 2 D+, 3 D-, 4 GND) passt
         at=(45.72, 175.26), pins={"1": "BAT_IN", "4": "GND"}),
    dict(ref="J5", lib="Connector_Generic:Conn_01x02", value="Akku +/-",
         fp="louie:SolderPads_1x02_2.5x3.5mm", bom=False,
         at=(91.44, 177.8), pins={"1": "BAT_IN", "2": "GND"}),
    FLAG(1, "VSYS", (101.6, 129.54)),
    FLAG(2, "GND", (114.3, 129.54)),
    FLAG(4, "BAT_IN", (101.6, 162.56)),

    # --- LDO ----------------------------------------------------------------------------------
    dict(ref="U3", lib="Regulator_Linear:AP2112K-3.3", value="AP2112K-3.3", lcsc="C51118",
         fp="Package_TO_SOT_SMD:SOT-23-5", at=(63.5, 228.6), ref_at=(-5.08, -6.35), val_at=(1.27, 7.62),
         pins={"1": "VSYS", "3": "VSYS", "2": "GND", "5": "+3V3"}),
    C("C8", "1u", "VSYS", "GND", (38.1, 228.6)),
    C("C11", "1u", "+3V3", "GND", (88.9, 228.6)),

    # --- Akkuspannung: 470k/470k, VSYS bis 5,5 V -> 2,75 V (ADC des C6 bis 3,3 V) --------------------
    R("R6", "470k", "VSYS", "VBAT_ADC", (38.1, 264.16)),
    R("R7", "470k", "VBAT_ADC", "GND", (50.8, 264.16)),
    C("C13", "100n", "VBAT_ADC", "GND", (76.2, 264.16)),

    # --- ESP32-C6 -----------------------------------------------------------------------------
    dict(ref="U1", lib="louie:ESP32-C6-MINI-1", value="ESP32-C6-MINI-1-H8", lcsc="C42403058",
         fp="lcsc:WIFIM-SMD_ESP32-C6-MINI-1", at=(177.8, 73.66), ref_at=(-12.7, -24.13), val_at=(2.54, 24.13),
         pins={"3": "+3V3", "8": "EN", "1": "GND", "12": "VBAT_ADC", "13": "ISEN_ADC", "5": "INT", "6": "SENSE",
               "9": "VBUS_DET", "10": "IO5", "15": "SDA", "16": "SCL", "22": "IO8", "23": "BOOT",
               "17": "USB_D-", "18": "USB_D+", "19": "LED", "24": "MOT_IN1", "25": "MOT_IN2", "31": "TXD",
               # Erweiterungen unten (alle optional): IO15 LED-Versorgung ein, IO20/IO21 Spieler-Eingänge,
               # IO23 LED-Daten, RXD Konsole (J3-5); IO22 frei (Reserve)
               "20": "IO15", "26": "IO20", "27": "IO21", "29": "IO23", "30": "RXD"}),
    C("C9", "10u", "+3V3", "GND", (152.4, 139.7), fp=C0603),
    C("C10", "100n", "+3V3", "GND", (165.1, 139.7)),
    R("R2", "10k", "+3V3", "EN", (177.8, 139.7)),
    C("C12", "1u", "EN", "GND", (190.5, 139.7)),
    R("R16", "10k", "+3V3", "SDA", (203.2, 139.7)),  # I2C, Breakouts haben oft keine Pull-ups
    R("R10", "10k", "+3V3", "SCL", (215.9, 139.7)),
    R("R11", "10k", "+3V3", "IO8", (228.6, 139.7)),  # Strapping-Pin, beim Download 1
    R("R9", "1k", "LED", "LED_A", (152.4, 165.1)),
    dict(ref="D1", lib="Device:LED", value="grün", fp="LED_SMD:LED_0402_1005Metric",
         at=(170.18, 175.26), pins={"2": "LED_A", "1": "GND"}),
    # Unterseite: Lötpads im 2,54-mm-Raster (Stiftleiste/Kabel), keine Bestückung
    dict(ref="J2", lib="Connector_Generic:Conn_01x05", value="Erweiterung I2C", bom=False,
         fp="louie:SolderPads_1x05_P2.54mm", at=(165.1, 228.6),
         pins={"1": "+3V3", "2": "GND", "3": "SDA", "4": "SCL", "5": "INT"}),   # Sensor-Breakout/Schalter
    # Service: vollständige UART0-Konsole (TXD, RXD), EN, BOOT, GND – z. B. Pogo-Adapter; Taster an 3+4
    dict(ref="J3", lib="Connector_Generic:Conn_01x05", value="Service", bom=False,
         fp="louie:SolderPads_1x05_P2.54mm", at=(203.2, 228.6),
         pins={"1": "EN", "2": "TXD", "3": "BOOT", "4": "GND", "5": "RXD"}),

    # --- Ausgangsstufe ---------------------------------------------------------------------------
    # GAINSEL an GND: 205 µA/A; R1 = R_IPROPI: ITRIP = 0,51 V / (1,24 k × 205 µA/A) ≈ 2 A
    dict(ref="U2", lib="louie:DRV8213DSG", value="DRV8213DSG", lcsc="C22407186",
         fp="Package_SON:WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm",  # = Texas DSG0008A, mit 3D-Modell
         at=(304.8, 76.2), ref_at=(-10.16, -8.89), val_at=(2.54, 10.16),
         pins={"1": "VSYS", "2": "OUT_A", "3": "OUT_B", "4": "GND", "9": "GND", "5": "MOT_IN2", "6": "MOT_IN1",
               "7": "GND", "8": "ISEN"}),
    C("C1", "47u 10V", "VSYS", "GND", (269.24, 124.46), fp=C1206),
    C("C2", "47u 10V", "VSYS", "GND", (281.94, 124.46), fp=C1206),
    C("C4", "100n", "VSYS", "GND", (294.64, 124.46)),
    R("R1", "1.24k 1%", "ISEN", "GND", (269.24, 147.32)),
    # Kondensator nicht direkt an IPROPI (verzögert die Strombegrenzung), sondern hinter R8
    R("R8", "1k", "ISEN", "ISEN_ADC", (284.48, 147.32)),
    C("C14", "100n", "ISEN_ADC", "GND", (299.72, 147.32)),

    # --- Hebel-Erkennung: offen -> SENSE 0 V, zu -> ca. 3,0 V (WAKEUP_ANY_HIGH) ----------------------
    R("R3", "100k", "OUT_A", "GND", (269.24, 198.12)),
    R("R4", "10k", "OUT_B", "+3V3", (284.48, 198.12)),
    R("R5", "100k", "OUT_A", "SENSE", (299.72, 198.12)),
    TP("BT1", "Kontakt A", "OUT_A", (322.58, 198.12), fp=TP_CONTACT),
    TP("BT2", "Kontakt B", "OUT_B", (337.82, 198.12), fp=TP_CONTACT),

    # --- Beschleunigungssensor: bestückungsoptional (DNP möglich), INT1 weckt über IO2 aus Deep Sleep ---
    dict(ref="U4", lib="louie:LIS2DH12", value="LIS2DH12TR", lcsc="C110926",
         fp="Package_LGA:LGA-12_2x2mm_P0.5mm", at=(304.8, 233.68), ref_at=(-7.62, -8.89), val_at=(2.54, 11.43),
         pins={"9": "+3V3", "10": "+3V3", "2": "+3V3", "3": "GND", "5": "GND", "6": "GND",
               "1": "SCL", "4": "SDA", "12": "INT"}),
    C("C15", "100n", "+3V3", "GND", (266.7, 233.68)),

    # --- Unterseite, optional (docs/idee-optionale-hardware.md 0b.4): nichts davon ist bestückt ---------------------
    # J6 „Spieler“: S1 = IO5 (Deep-Sleep-Wecken, ADC), S2 = IO20, S3 = IO21, S4 = IO8 (R11 10 k vorhanden);
    # Taster/Reed gegen GND mit internem Pull-up (45 k) und 1 kΩ in Reihe im Kabel; keine RC-Footprints
    dict(ref="J6", lib="Connector_Generic:Conn_01x06", value="Spieler S1-S4", bom=False,
         fp="louie:SolderPads_1x06_P2.00mm", at=(355.6, 66.04),
         pins={"1": "+3V3", "2": "IO5", "3": "IO20", "4": "IO21", "5": "IO8", "6": "GND"}),
    # IO5: R nach 3V3 (Pull-up, Widerstandsleiter), R und C nach GND (NTC, Piezo-Ableitung, Filter)
    DNP(R("R19", "10k", "IO5", "+3V3", (370.84, 48.26), lcsc="C25744")),
    DNP(R("R20", "1M", "IO5", "GND", (383.54, 48.26))),
    DNP(C("C16", "10n", "IO5", "GND", (396.24, 48.26), lcsc="C15195")),

    # J7 „LED“: 1 VLED, 2 IO23 (NeoPixel-Daten/LED/Taster), 3 GND. VLED über Lastschalter U6 (Freigabe IO15,
    # R22 hält ihn im Reset und Deep Sleep aus) oder über JP1 (Lötbrücke, Standard offen); dahinter PTC F1 0,5 A
    # (VSYS ist sonst ungesichert) und C17 als Puffer. Serienwiderstand 330 Ω gehört ans LED-Ende des Kabels.
    dict(ref="J7", lib="Connector_Generic:Conn_01x03", value="LED", bom=False,
         fp="louie:SolderPads_1x03_P2.54mm", at=(355.6, 154.94), pins={"1": "VLED", "2": "IO23", "3": "GND"}),
    # TPS22918 (DBV): CT offen = schnellste Flanke; QOD offen = keine Ausgangsentladung (TI: zulässig). An VOUT
    # meldet der ERC Stromausgang an offenem Kollektor, an VLED fand der Router keinen Weg; die LEDs entladen VLED.
    DNP(dict(ref="U6", lib="Power_Management:TPS22917DBV", value="TPS22918DBVR", lcsc="C131941",
             fp="Package_TO_SOT_SMD:SOT-23-6", at=(383.54, 144.78), ref_at=(-7.62, -8.89), val_at=(2.54, 10.16),
             pins={"1": "VSYS", "2": "GND", "3": "IO15", "6": "VLED_SW"})),
    # Lötbrücke als 0603-Pads (Lot oder 0-Ω-Widerstand): der SolderJumper-Footprint fand unten keinen Platz mehr
    dict(ref="JP1", lib="Jumper:SolderJumper_2_Open", value="VSYS->VLED", bom=False,
         fp="Resistor_SMD:R_0603_1608Metric", at=(383.54, 127.0),
         pins={"1": "VSYS", "2": "VLED_SW"}),
    DNP(dict(ref="F1", lib="Device:Polyfuse", value="0.5A 6V", lcsc="C883108",
             fp="Fuse:Fuse_0805_2012Metric", at=(401.32, 144.78), pins={"1": "VLED_SW", "2": "VLED"})),
    DNP(C("C17", "10u", "VLED", "GND", (401.32, 167.64), fp=C0805, lcsc="C1713")),
    DNP(R("R22", "100k", "IO15", "GND", (370.84, 170.18), lcsc="C25741")),

    # Testpunkte (Messspitze, Prüfadapter)
    TP("TP1", "VSYS", "VSYS", (152.4, 254.0), fp=TEST_PAD),
    TP("TP2", "VBUS", "VBUS_J4", (165.1, 254.0), fp=TEST_PAD),
]

# ---------------------------------------------------------------------------------------------


def uid(*name):
    """Feste UUIDs (uuid5 aus Projekt und Name bzw. laufender Nummer): ein erneutes just schematic ändert die
    Verknüpfung Symbol ↔ Footprint (Pfad in der .kicad_pcb) nicht, der Schaltplan-Abgleich im DRC bleibt gültig."""
    key = "/".join(name) if name else f"item/{next(_SEQ)}"
    return str(uuid.uuid5(_NS, f"{_PROJECT}/{key}"))


_NS = uuid.UUID("7d3c1d52-4f1e-4a8e-9a55-1f0c2b6e9a10")
_PROJECT = "louie-main"
_SEQ = iter(range(1, 10 ** 9))


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


TITLE = "Looping Louie WLAN-Upgrade – Hauptplatine"
COMMENT = "Platine im AA-Format, siehe docs/hardware-konzept.md"


def main(sch=SCH, parts=PARTS, blocks=BLOCKS, title=TITLE, comment=COMMENT, project="louie-main",
         generator="gen_main_schematic.py"):
    """Schreibt den Schaltplan. Andere Platinen (gen_charger_schematic.py) rufen das mit eigenen Daten auf."""
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
            f'\t\t(exclude_from_sim no) (in_bom {"yes" if in_bom else "no"}) (on_board {"no" if is_power else "yes"}) (dnp {"yes" if dnp else "no"})\n'
            f'\t\t(uuid "{uid("symbol", part["ref"])}")\n{prop_text}{pin_text}'
            f'\t\t(instances (project "{project}" (path "/{root}" (reference "{part["ref"]}") (unit 1))))\n'
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
        f'\t\t(comment 2 "Erzeugt mit hardware/scripts/{generator}")\n'
        '\t)\n'
        '\t(lib_symbols\n' + "".join("\t\t" + s.replace("\n", "\n\t\t") + "\n" for s in lib_symbols.values()) + '\t)\n'
        + "".join(items) +
        '\t(sheet_instances (path "/" (page "1")))\n'
        '\t(embedded_fonts no)\n'
        ')\n'
    )
    print(f"{sch.relative_to(HARDWARE.parent)}: {len(parts)} Bauteile")


if __name__ == "__main__":
    main()
