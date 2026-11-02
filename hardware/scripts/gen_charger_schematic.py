#!/usr/bin/env python3
"""Erzeugt den Schaltplan der Ladeplatine aus der Schaltungsbeschreibung unten.

Die Ladeplatine hat das Format der Hauptplatine (AA) und ersetzt im zweiten AA-Fach die Brücke:
USB-C (liegend, Stecker kommt quer zur Zellachse von oben), Laderegler MCP73831 mit Load-Sharing
(Spielen beim Laden), ESD-Schutz, Ladeanzeige, Akku-Anschluss, Kabel-Lötpads zur Hauptplatine und
eine Kupferbrücke zwischen den Endkontakten. Alternativ wird sie in die Basis geklebt.

Aufruf (über just):  just charger-schematic

Achtung: überschreibt hardware/charger-board/louie-charger.kicad_sch.
"""
from pathlib import Path

import gen_main_schematic as base
from gen_main_schematic import C, FLAG, R, TP, TP_CONTACT

SCH = base.HARDWARE / "charger-board" / "louie-charger.kicad_sch"
R0603 = "Resistor_SMD:R_0603_1608Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"


def R6(*args):
    return R(*args, fp=R0603)


BLOCKS = [
    ("USB-C (Laden + Daten zur Hauptplatine) und ESD-Schutz", (25.4, 25.4)),
    ("Laderegler 1S-LiPo, 500 mA (R103 = 1000 V / I_Lade)", (139.7, 25.4)),
    ("Load-Sharing: mit USB versorgt VBUS über D102 das System, sonst der Akku über Q101", (139.7, 111.76)),
    ("Akku, Kabel zur Hauptplatine", (25.4, 175.26)),
    ("Brücke zwischen den Endkontakten (ersetzt die Brückenplatine im zweiten AA-Fach)", (139.7, 175.26)),
]

PARTS = [
    # --- USB-C ---------------------------------------------------------------------------------
    dict(ref="J101", lib="Connector:USB_C_Receptacle_USB2.0_16P", value="TYPE-C-31-M-12", lcsc="C165948",
         fp="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", at=(50.8, 76.2), ref_at=(-10.16, -24.13),
         val_at=(2.54, 26.67),
         pins={"A4": "VBUS", "A9": "VBUS", "B4": "VBUS", "B9": "VBUS", "A5": "CC1", "B5": "CC2",
               "A6": "USB_D+", "B6": "USB_D+", "A7": "USB_D-", "B7": "USB_D-",
               "A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND", "S1": "GND"}),
    # 5,1 k an CC1/CC2: Gerät (Senke), jedes USB-C-Netzteil liefert dann 5 V
    R6("R101", "5.1k", "CC1", "GND", (88.9, 50.8)),
    R6("R102", "5.1k", "CC2", "GND", (101.6, 50.8)),
    dict(ref="U102", lib="Power_Protection:USBLC6-2SC6", value="USBLC6-2SC6", lcsc="C7519",
         fp="Package_TO_SOT_SMD:SOT-23-6", at=(88.9, 127), ref_at=(-7.62, -8.89), val_at=(2.54, 10.16),
         pins={"1": "USB_D+", "6": "USB_D+", "3": "USB_D-", "4": "USB_D-", "5": "VBUS", "2": "GND"}),
    FLAG(1, "VBUS", (114.3, 43.18)),
    FLAG(2, "GND", (127, 43.18)),

    # --- Laderegler ----------------------------------------------------------------------------
    dict(ref="U101", lib="Battery_Management:MCP73831-2-OT", value="MCP73831T-2ACI/OT", lcsc="C424093",
         fp="Package_TO_SOT_SMD:SOT-23-5", at=(190.5, 66.04), ref_at=(-7.62, -8.89), val_at=(2.54, 10.16),
         pins={"4": "VBUS", "2": "GND", "3": "BAT", "5": "PROG", "1": "STAT"}),
    C("C101", "4.7u 10V", "VBUS", "GND", (160.02, 66.04), fp=C0603),
    C("C102", "4.7u 10V", "BAT", "GND", (233.68, 66.04), fp=C0603),
    R6("R103", "2k", "PROG", "GND", (215.9, 88.9)),
    # Ladeanzeige: STAT zieht beim Laden nach GND -> LED an; voll oder ohne USB -> aus
    R6("R104", "1k", "VBUS", "LED_A", (160.02, 88.9)),
    dict(ref="D101", lib="Device:LED", value="rot", lcsc="C2286", fp="LED_SMD:LED_0603_1608Metric",
         at=(177.8, 93.98), pins={"2": "LED_A", "1": "STAT"}),

    # --- Load-Sharing (Microchip AN1149) -------------------------------------------------------
    dict(ref="Q101", lib="Transistor_FET:AO3401A", value="AO3401A", lcsc="C15127",
         fp="Package_TO_SOT_SMD:SOT-23", at=(190.5, 142.24), ref_at=(5.08, -2.54), val_at=(5.08, 2.54),
         pins={"1": "VBUS", "2": "VSYS", "3": "BAT"}),
    dict(ref="D102", lib="Device:D_Schottky", value="SS34", lcsc="C8678", fp="Diode_SMD:D_SMA",
         at=(165.1, 132.08), pins={"2": "VBUS", "1": "VSYS"}),
    R6("R105", "100k", "VBUS", "GND", (160.02, 152.4)),      # zieht das Gate ohne USB auf GND -> Q101 leitet
    C("C103", "10u 10V", "VSYS", "GND", (231.14, 142.24), fp=C0805),

    # --- Akku und Kabel ------------------------------------------------------------------------
    dict(ref="J102", lib="Connector_Generic:Conn_01x02", value="LiPo JST-PH", lcsc="C295747",
         fp="Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
         at=(50.8, 200.66), pins={"1": "BAT", "2": "GND"}),
    TP("TP101", "Akku +", "BAT", (76.2, 198.12), fp=TP_CONTACT),       # Lötpads statt Stecker
    TP("TP102", "Akku -", "GND", (88.9, 198.12), fp=TP_CONTACT),
    dict(ref="J103", lib="Connector_Generic:Conn_01x04", value="Kabel Hauptplatine",
         fp="louie:SolderPads_1x04_P2.00mm", bom=False,  # gleiche Belegung wie J1 der Hauptplatine
         at=(50.8, 236.22), pins={"1": "VSYS", "2": "USB_D+", "3": "USB_D-", "4": "GND"}),

    # --- Brücke --------------------------------------------------------------------------------
    TP("BT101", "Kontakt", "BRUECKE", (165.1, 198.12), fp=TP_CONTACT),
    TP("BT102", "Kontakt", "BRUECKE", (180.34, 198.12), fp=TP_CONTACT),
]


if __name__ == "__main__":
    base.main(sch=SCH, parts=PARTS, blocks=BLOCKS,
              title="Looping Louie WLAN-Upgrade – Ladeplatine",
              comment="AA-Format (Fach 2 statt Brücke) oder in die Basis geklebt, siehe docs/ladeplatine.md",
              project="louie-charger", generator="gen_charger_schematic.py")
