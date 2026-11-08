"""Variante 2: oben maschinell bestückt, unten Handlöten (nur 0603/0805, keine ICs).

Oben:  ESP32-Modul, DRV8833 mit Abblock- und Pufferkondensatoren, Shunt, LDO mit Kondensatoren,
       JST-Stecker.
Unten: Widerstände/Kondensatoren für ESP-Beschaltung, Hebel-Erkennung, ADC-Teiler und -Filter,
       LED, Testpads und Endkontakte (reine Kupferflächen).

Koordinaten in mm relativ zur Platinenmitte (x entlang der Länge, Antenne bei -x),
Drehung in Grad, Seite "F" (oben) oder "B" (unten, Koordinaten von oben gesehen).
"""

MODULE_X = -8.8  # Antennenkante des Moduls bei x = -19.84

PLACEMENT = {
    # ---- Oberseite ---------------------------------------------------------------------------
    "U1": (MODULE_X, 0, 90, "F"),
    "U2": (1.7, -3.2, 0, "F"),          # DRV8833, Ausgänge zum Modul hin, Eingänge rechts
    "R1": (-0.9, 1.6, 0, "F"),          # Shunt direkt unter den ISEN-Pins
    "C1": (4.2, 1.6, 0, "F"),           # 47 µF
    "C2": (4.2, 4.7, 0, "F"),           # 47 µF
    "C3": (-0.7, 4.7, 0, "F"),          # 47 µF
    "C4": (7.4, -4.6, 90, "F"),         # 100 nF VM
    "C7": (9.2, -4.6, 90, "F"),         # 10 nF VCP
    "C6": (11.0, -4.6, 90, "F"),        # 2,2 µF VINT
    "C5": (7.4, -1.2, 90, "F"),         # 100 nF VM
    "U3": (10.5, 0.3, 0, "F"),          # LDO
    "C8": (9.2, 3.9, 90, "F"),          # LDO Eingang
    "C11": (11.0, 3.9, 90, "F"),        # LDO Ausgang
    "J1": (17.4, 0.4, 0, "F"),          # Kabel zur Ladeplatine, Öffnung zur Seite (+y)

    # ---- Unterseite (Handlöten) ----------------------------------------------------------------
    # am Modulrand +y: 3V3, IO2, SENSE, EN
    "C9": (-12.4, 4.1, 0, "B"),         # 10 µF 3V3
    "C10": (-12.4, 2.0, 0, "B"),        # 100 nF 3V3
    "R10": (-9.0, 4.2, 0, "B"),        # Pull-up IO2
    "R2": (-5.8, 4.2, 0, "B"),          # Pull-up EN
    "C12": (-5.8, 2.4, 0, "B"),         # EN-Kondensator
    "R5": (-9.0, 2.4, 0, "B"),         # SENSE-Schutzwiderstand
    "R3": (-3.2, 0.4, 90, "B"),         # Pull-up MOT_A
    "R4": (-1.4, 0.4, 90, "B"),         # Pull-down MOT_B
    # am Modulrand rechts: VBAT_ADC, ISEN_ADC, LED
    "R6": (-0.2, 4.6, 90, "B"),         # Teiler oben
    "R7": (1.6, 4.6, 90, "B"),          # Teiler unten
    "C13": (3.4, 4.6, 90, "B"),
    "R8": (5.2, 4.6, 90, "B"),          # Filter Shunt
    "C14": (7.0, 4.6, 90, "B"),
    "R9": (0.4, 0.4, 90, "B"),         # LED-Vorwiderstand
    "D1": (2.2, 0.4, 90, "B"),
    # am Modulrand -y: IO8, BOOT, RXD, TXD
    "R11": (-4.8, -3.8, 90, "B"),       # Pull-up IO8
    "TP4": (-2.0, -4.6, 0, "B"),        # BOOT
    "TP5": (-12.0, -4.6, 0, "B"),       # TXD
    "TP6": (-9.2, -4.6, 0, "B"),        # RXD
    "TP1": (-12.6, -1.4, 0, "B"),       # 3V3
    "TP2": (-9.8, -1.4, 0, "B"),       # GND
    "TP3": (-7.0, -1.4, 0, "B"),        # EN
    # Endkontakte
    "BT1": (-21.4, 0, 0, "B"),
    "BT2": (21.4, 0, 0, "B"),
}
