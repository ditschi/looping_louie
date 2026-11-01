"""Variante 1b: alle Bauteile oben (einseitig maschinell bestückt), Passive in 0402.

Unten liegen nur Kupferflächen ohne Bestückung: Testpads, Lötpads für das Kabel, Endkontakte.

Aufbau von links (Antennen-Ende) nach rechts:
- ESP32-C3-Modul
- eine Reihe 0402 direkt an den rechten Modulpins (ADC-Teiler, LED, Pull-ups, EN), daneben ein Kanal
- DRV8833 (um 90° gedreht), darunter Shunt, Strommess-Filter und Erkennungswiderstände,
  VCP/VINT-Kondensatoren am Rand, Puffer-Elkos rechts
- LDO mit Kondensatoren
- unten: Kabel-Lötpads am rechten Ende

Koordinaten in mm relativ zur Platinenmitte (x entlang der Länge, Antenne bei -x),
Drehung in Grad, Seite "F" (oben) oder "B" (unten, Koordinaten von oben gesehen).
"""

MODULE_X = -8.8  # Antennenkante des Moduls bei x = -19.84
COL1, COL2 = -1.9, 0.4  # zwei Reihen 0402 neben dem Modul

PLACEMENT = {
    # ---- Oberseite ---------------------------------------------------------------------------
    "U1": (MODULE_X, 0, 90, "F"),
    # eine Reihe 0402 direkt an den rechten Modulpins, daneben ein freier Kanal zum DRV8833
    "R9": (COL1, 1.75, 0, "F"),         # LED-Vorwiderstand
    "D1": (COL1, 0.5, 0, "F"),          # LED
    "R11": (COL1, -0.75, 0, "F"),       # Pull-up IO8
    "R10": (COL1, -2.0, 0, "F"),        # Pull-up IO2
    "R2": (COL1, -3.25, 0, "F"),        # Pull-up EN
    "C12": (COL1, -4.5, 0, "F"),        # EN-Kondensator
    # 3V3-Kondensatoren
    "C10": (COL2, 4.25, 0, "F"),        # 100 nF 3V3
    "C9": (0.65, 5.6, 0, "F"),           # 10 µF 3V3 (0603)
    # Ausgangsstufe: DRV8833 um 90° gedreht – Eingangsreihe (Pins 9–16) zum Rand (-y),
    # Ausgangsreihe (Pins 1–8) zur Platinenmitte
    "U2": (4.6, -1.0, 90, "F"),
    "C6": (3.6, -5.9, 0, "F"),          # 2,2 µF VINT, direkt unter Pin 14
    "C7": (5.6, -5.9, 180, "F"),        # 10 nF VCP, direkt unter Pin 11/12
    "R1": (4.6, 5.05, 0, "F"),           # Shunt unter dem ISEN-Querbalken
    "R8": (7.7, 3.5, 0, "F"),           # Filter Shunt -> ADC
    "C14": (7.7, 4.7, 0, "F"),
    "R3": (9.7, 5.95, 0, "F"),          # Pull-up OUT_A (Erkennung)
    "R5": (7.7, 5.95, 0, "F"),          # OUT_A -> SENSE
    "R4": (20.0, 4.5, 0, "F"),          # Pull-down OUT_B, neben Endkontakt B
    "R6": (9.6, 2.4, 0, "F"),           # Akkuspannungs-Teiler oben
    "R7": (11.6, 2.4, 0, "F"),          # Teiler unten
    "C13": (11.6, 1.15, 0, "F"),        # ADC-Filter Akkuspannung
    "C4": (8.6, -1.8, 0, "F"),          # 100 nF VM
    "C5": (8.6, -0.5, 0, "F"),          # 100 nF VM
    "C1": (11.0, -3.6, 90, "F"),        # 47 µF
    "C2": (13.6, -3.6, 90, "F"),        # 47 µF
    "C3": (13.2, 4.3, 0, "F"),           # 47 µF
    # LDO
    "U3": (17.0, -3.3, 0, "F"),
    "C8": (16.0, -0.6, 0, "F"),         # LDO Eingang
    "C11": (18.2, -0.6, 0, "F"),        # LDO Ausgang

    # ---- Unterseite: nur Kupferflächen ---------------------------------------------------------
    "J1": (18.5, 0, 0, "B"),            # Lötpads Kabel zur Ladeplatine
    "TP1": (-12.7, 3.8, 0, "B"),        # 3V3
    "TP7": (-10.0, 3.8, 0, "B"),        # IO2 (frei)
    "TP3": (-7.3, 3.8, 0, "B"),         # EN
    "TP2": (-4.6, 3.8, 0, "B"),         # GND
    "TP8": (-12.7, -3.8, 0, "B"),       # IO8 (frei)
    "TP5": (-10.0, -3.8, 0, "B"),       # TXD
    "TP6": (-7.3, -3.8, 0, "B"),        # RXD
    "TP4": (-4.6, -3.8, 0, "B"),        # BOOT
    "BT1": (-21.4, 0, 0, "B"),          # Endkontakt OUT_A (Antennen-Ende)
    "BT2": (21.4, 0, 0, "B"),           # Endkontakt OUT_B
}
