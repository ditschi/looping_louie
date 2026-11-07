"""Variante 1b (C6-Stand): alle Bauteile oben (einseitig maschinell bestückt), Passive in 0402.

Unten liegen nur Kupferflächen und optionale Footprints ohne Bestückung (DNP): Lötpads für Kabel und Zelle,
Erweiterungs-/Service-Pads, Endkontakte, Spieler-Eingänge J6, LED-Anschluss J7 mit Lastschalter,
Testpunkte (docs/idee-optionale-hardware.md 0/0b). Alles unten liegt in der Tasche der Hülle (|y| ≤ 5,2 mm,
Bauhöhe ≤ 1,5 mm) und außerhalb der Antennen-Sperrfläche (x > −14,6 mm).

Aufbau von links (Antennen-Ende) nach rechts (docs/hauptplatine-c6.md, Kapitel 2.2 und 11.3):
- ESP32-C6-Modul, rechts daneben eine Reihe 0402 direkt an den Modulpins
- Kante -y: DRV8213 an der Modulecke (IO18/IO19), Ausgänge per Via nach unten; Puffer C1/C2, Schottky D2
- Kante +y: LDO, P-FET Q1 (BAT_IN -> VSYS), 3V3-Kondensatoren; dazwischen die USB-Leitungen (y = +0,9 / +1,5)
- USB-C J4 an der Kante +y (Öffnung 0,7 mm zurückgesetzt), ESD U5 und CC-Widerstände im Band davor (-y),
  rechts neben J4 eine Reihe 0402, rechts davor der LIS2DH12 (bestückungsoptional)
- unten: J1 (Kabel Ladeplatine) und J5 (Zelle) unter J4, J2 (I2C) an der Kante +y, J3 (Service) und J6
  (Spieler) unter dem Modul, IO5-Beschaltung zur Kante +y hin; J7 (LED) mit U6/F1/C17/JP1 unter dem Treiber

Koordinaten in mm relativ zur Platinenmitte (x entlang der Länge, Antenne bei -x),
Drehung in Grad, Seite "F" (oben) oder "B" (unten, Koordinaten von oben gesehen).
"""

MODULE_X = -8.8   # Antennenkante des Moduls bei x = -19.84
COL1 = -1.9       # 0402-Reihe direkt an den rechten Modulpins
USB_X = 15.3      # Mitte der USB-C-Buchse
USB_Y = 6.05 - 3.65  # Vorderkante 0,7 mm hinter der Kante +y (Footprint: Öffnung bei +3,65 mm)
RC1 = 21.2  # Reihe 0402 (senkrecht) rechts neben J4; x > 22,2 liegt unter der Endkappe der Hülle

PLACEMENT = {
    # ---- Oberseite ---------------------------------------------------------------------------
    "U1": (MODULE_X, 0, 90, "F"),
    # 0402-Reihe an den rechten Modulpins (Pads y = +4,8 IO0 ... -4,8 IO18)
    "R11": (COL1, -3.2, 180, "F"),      # Pull-up IO8 (Strapping)
    "D1": (COL1, -2.1, 0, "F"),         # LED
    "R9": (COL1, -1.0, 0, "F"),         # LED-Vorwiderstand an IO14
    "R10": (COL1, 1.85, 180, "F"),      # Pull-up SCL (IO7)
    "R16": (COL1, 3.1, 180, "F"),       # Pull-up SDA (IO6)
    "C14": (COL1, 4.35, 0, "F"),       # Filter ISEN_ADC (IO1)
    "C13": (COL1, 5.6, 0, "F"),        # Filter VBAT_ADC (IO0)
    # Ausgangsstufe an der Modulecke -y: Eingänge zum Modul, Ausgänge nach +x
    "U2": (0.7, -4.6, 180, "F"),        # DRV8213
    "R1": (0.1, -2.55, 0, "F"),         # R_IPROPI 1,24 k
    "C4": (1.85, -2.3, 270, "F"),       # 100 nF VM, Pin 1 direkt über VM
    "R8": (0.1, -1.5, 0, "F"),         # Filter IPROPI -> ADC
    "R3": (2.1, -0.8, 180, "F"),         # OUT_A -> GND (Hebel-Erkennung)
    "R5": (2.1, 0.3, 180, "F"),         # OUT_A -> SENSE
    "R4": (RC1, -1.6, 270, "F"),        # OUT_B -> 3V3: OUT_B oben per Via auf die OUT_B-Bahn unten
    "R6": (0.1, -0.45, 180, "F"),           # Teiler VSYS oben
    "R7": (8.33, -1.0, 90, "F"),        # Teiler unten
    "C1": (5.45, -2.7, 0, "F"),        # 47 µF
    "C2": (5.45, -0.3, 0, "F"),        # 47 µF
    "D2": (6.9, -5.25, 0, "F"),         # SS34F: Kathode (VSYS) links, Anode (VBUS) rechts
    # Kante +y: LDO, Power-Path-FET, 3V3-Kondensatoren
    "R2": (-0.4, 5.6, 90, "F"),        # Pull-up EN
    "C12": (-0.4, 3.5, 90, "F"),       # EN-Kondensator
    "U3": (2.35, 4.8, 0, "F"),         # AP2112K
    "Q1": (7.6, 4.85, 0, "F"),          # AO3401A
    "C8": (1.05, 2.3, 0, "F"),          # LDO Eingang
    "C11": (3.05, 2.3, 0, "F"),         # LDO Ausgang
    "C9": (5.6, 2.3, 0, "F"),          # 10 µF 3V3 (0603)
    "C10": (8.3, 2.3, 0, "F"),         # 100 nF 3V3
    # USB-C und ESD
    "J4": (USB_X, USB_Y, 0, "F"),
    # USBLC6-2SC6 durchgeschleift: Buchsenseite rechts (Pin 1 D+, Pin 3 D-), Modulseite links (Pin 6, Pin 4)
    "U5": (16.6, -4.85, 180, "F"),
    "R12": (9.42, -1.0, 90, "F"),       # CC1: links neben J4, CC1 läuft unter dem Buchsenkörper
    "R13": (19.7, -3.45, 0, "F"),       # CC2
    # Beschleunigungssensor (bestückungsoptional) rechts neben U5
    "U4": (20.75, -5.3, 180, "F"),         # LIS2DH12
    "C15": (RC1, 1.6, 270, "F"),        # 100 nF, 3V3 oben (an R4)
    # VBUS-Teiler im Band links der ESD, über der VBUS-Bahn (VBUS rechts, VBUS_DET links)
    "R14": (11.2, -3.45, 180, "F"),     # VBUS -> VBUS_DET
    "R15": (11.2, -4.49, 0, "F"),       # VBUS_DET -> GND

    # ---- Unterseite: nur Kupferflächen ---------------------------------------------------------
    "J1": (14.5, 5.65, 270, "B"),         # Kabel Ladeplatine unter J4 an der Kante +y (hinter den Laschen)
    "J5": (15.15, 2.55, 180, "B"),         # Zelle direkt: BAT_IN / GND, unter J4 zwischen den Laschen
    # Lötpads im 2,54-mm-Raster (Stiftleiste/Kabel möglich)
    "J2": (3.4, 4.3, 180, "B"),         # Erweiterung: 3V3, GND, SDA, SCL, INT; Mitte y 4,3 (Pads bis 5,0 in der Tasche)
    "J3": (-8.55, -3.35, 0, "B"),       # Service: EN, TXD, BOOT, GND, RXD (Taster an BOOT+GND)
    # ---- Unterseite optional (DNP), Lage mit Abstandsprüfung gesucht (Vorrouten, Vias, Pads, Sperrflächen) -------
    # J6 unter dem Modul zur Kante +y hin (Raster 2,0 mm, endet bei x −2,9): Mitte des Moduls und rechts davon bleiben
    # frei für die Vias, mit denen der Router die rechten Modulpads nach unten führt
    "J6": (-8.63, 3.2, 0, "B"),         # Spieler (Raster 2,0): 3V3 (x −3,63) … GND (x −13,63), zur Kante +y hin
    "R19": (-11.9, 0.0, 0, "B"),        # IO5 nach 3V3 (zwischen den Modul-Vias)
    "R20": (-9.8, 0.0, 0, "B"),         # IO5 nach GND
    "C16": (-7.8, 0.0, 0, "B"),         # IO5 nach GND
    "J7": (8.2, -4.2, 0, "B"),         # LED: VLED (x 10,74), IO23, GND (x 5,66); unter D2/USB-Seite −y, weg vom Treiber
    "U6": (2.2, 1.5, 0, "B"),          # Lastschalter TPS22918 (unter USB-C kein Platz für U6 mit F1/JP1)
    "R22": (-13.7, 0.0, 90, "B"),       # IO15 → GND (U6 aus im Reset/Deep Sleep)
    "JP1": (6.2, 1.8, 90, "B"),         # Brücke VSYS (Nord) → VLED_SW (Süd), 0603-Pads (Lot oder 0 Ω), zwischen VSYS- und VBUS-Bahn
    "F1": (6.2, -1.5, 90, "B"),        # PTC 0,5 A: VLED_SW (Nord, zu JP1) → VLED (Süd, zu J7)
    "C17": (14.7, -2.05, 0, "B"),        # 10 µF an VLED (unter USB-C)
    "TP1": (8.4, 2.4, 0, "B"),          # VSYS
    "TP2": (12.2, -1.4, 0, "B"),        # VBUS
    "BT1": (-21.4, 0, 0, "B"),          # Endkontakt OUT_A (Antennen-Ende)
    "BT2": (21.4, 0, 0, "B"),           # Endkontakt OUT_B
}
