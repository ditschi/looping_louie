#!/usr/bin/env python3
"""Generates the charger board schematic from the circuit description below.

The charger board has the format of the main board (AA) and replaces the bridge in the second AA compartment:
USB-C (horizontal, the plug comes from above across the cell axis), charge controller MCP73831 with load sharing
(play while charging), ESD protection, charge indicator, battery connection, cable solder pads to the main board and
a copper bridge between the end contacts. Alternatively it is glued into the base.

Usage (via just):  just charger-schematic

Warning: overwrites hardware/charger-board/louie-charger.kicad_sch.
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
    ("USB-C (charging + data to the main board) and ESD protection", (25.4, 25.4)),
    ("Charge controller 1S LiPo, 500 mA (R103 = 1000 V / I_charge)", (139.7, 25.4)),
    ("Load sharing: with USB, VBUS supplies the system via D102, otherwise the battery via Q101", (139.7, 111.76)),
    ("Battery, cable to the main board", (25.4, 175.26)),
    ("Bridge between the end contacts (replaces the bridge board in the second AA compartment)", (139.7, 175.26)),
]

PARTS = [
    # --- USB-C ---------------------------------------------------------------------------------
    dict(ref="J101", lib="Connector:USB_C_Receptacle_USB2.0_16P", value="TYPE-C-31-M-12", lcsc="C165948",
         fp="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", at=(50.8, 76.2), ref_at=(-10.16, -24.13),
         val_at=(2.54, 26.67),
         pins={"A4": "VBUS", "A9": "VBUS", "B4": "VBUS", "B9": "VBUS", "A5": "CC1", "B5": "CC2",
               "A6": "USB_D+", "B6": "USB_D+", "A7": "USB_D-", "B7": "USB_D-",
               "A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND", "S1": "GND"}),
    # 5.1 k at CC1/CC2: device (sink), every USB-C power supply then delivers 5 V
    R6("R101", "5.1k", "CC1", "GND", (88.9, 50.8)),
    R6("R102", "5.1k", "CC2", "GND", (101.6, 50.8)),
    dict(ref="U102", lib="Power_Protection:USBLC6-2SC6", value="USBLC6-2SC6", lcsc="C7519",
         fp="Package_TO_SOT_SMD:SOT-23-6", at=(88.9, 127), ref_at=(-7.62, -8.89), val_at=(2.54, 10.16),
         pins={"1": "USB_D+", "6": "USB_D+", "3": "USB_D-", "4": "USB_D-", "5": "VBUS", "2": "GND"}),
    FLAG(1, "VBUS", (114.3, 43.18)),
    FLAG(2, "GND", (127, 43.18)),

    # --- Charge controller ----------------------------------------------------------------------
    dict(ref="U101", lib="Battery_Management:MCP73831-2-OT", value="MCP73831T-2ACI/OT", lcsc="C424093",
         fp="Package_TO_SOT_SMD:SOT-23-5", at=(190.5, 66.04), ref_at=(-7.62, -8.89), val_at=(2.54, 10.16),
         pins={"4": "VBUS", "2": "GND", "3": "BAT", "5": "PROG", "1": "STAT"}),
    C("C101", "4.7u 10V", "VBUS", "GND", (160.02, 66.04), fp=C0603),
    C("C102", "4.7u 10V", "BAT", "GND", (233.68, 66.04), fp=C0603),
    R6("R103", "2k", "PROG", "GND", (215.9, 88.9)),
    # charge indicator: STAT pulls to GND while charging -> LED on; full or without USB -> off
    R6("R104", "1k", "VBUS", "LED_A", (160.02, 88.9)),
    dict(ref="D101", lib="Device:LED", value="red", lcsc="C2286", fp="LED_SMD:LED_0603_1608Metric",
         at=(177.8, 93.98), pins={"2": "LED_A", "1": "STAT"}),

    # --- Load sharing (Microchip AN1149) -------------------------------------------------------
    dict(ref="Q101", lib="Transistor_FET:AO3401A", value="AO3401A", lcsc="C15127",
         fp="Package_TO_SOT_SMD:SOT-23", at=(190.5, 142.24), ref_at=(5.08, -2.54), val_at=(5.08, 2.54),
         pins={"1": "VBUS", "2": "VSYS", "3": "BAT"}),
    dict(ref="D102", lib="Device:D_Schottky", value="SS34", lcsc="C8678", fp="Diode_SMD:D_SMA",
         at=(165.1, 132.08), pins={"2": "VBUS", "1": "VSYS"}),
    R6("R105", "100k", "VBUS", "GND", (160.02, 152.4)),      # pulls the gate to GND without USB -> Q101 conducts
    C("C103", "10u 10V", "VSYS", "GND", (231.14, 142.24), fp=C0805),

    # --- Battery and cable ---------------------------------------------------------------------
    dict(ref="J102", lib="Connector_Generic:Conn_01x02", value="LiPo JST-PH", lcsc="C295747",
         fp="Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
         at=(50.8, 200.66), pins={"1": "BAT", "2": "GND"}),
    TP("TP101", "Battery +", "BAT", (76.2, 198.12), fp=TP_CONTACT),       # solder pads instead of connector
    TP("TP102", "Battery -", "GND", (88.9, 198.12), fp=TP_CONTACT),
    dict(ref="J103", lib="Connector_Generic:Conn_01x04", value="Main board cable",
         fp="louie:SolderPads_1x04_P2.00mm", bom=False,  # same pinout as J1 of the main board
         at=(50.8, 236.22), pins={"1": "VSYS", "2": "USB_D+", "3": "USB_D-", "4": "GND"}),

    # --- Bridge --------------------------------------------------------------------------------
    TP("BT101", "Contact", "BRIDGE", (165.1, 198.12), fp=TP_CONTACT),
    TP("BT102", "Contact", "BRIDGE", (180.34, 198.12), fp=TP_CONTACT),
]


if __name__ == "__main__":
    base.main(sch=SCH, parts=PARTS, blocks=BLOCKS,
              title="Looping Louie Wi-Fi upgrade – charger board",
              comment="AA format (compartment 2 instead of the bridge) or glued into the base, see docs/charger-board.md",
              project="louie-charger", generator="gen_charger_schematic.py")
