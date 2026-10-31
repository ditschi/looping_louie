#!/usr/bin/env python3
"""Erzeugt die projekteigene Symbolbibliothek hardware/lib/louie.kicad_sym.

Enthält Symbole, für die es weder in KiCad noch bei LCSC ein brauchbares gibt
(LCSC-Symbole haben keine Pin-Typen, damit wäre die ERC-Prüfung wertlos).

Aufruf (über just):  just symbols
"""
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "lib" / "louie.kicad_sym"
FONT = "(effects (font (size 1.27 1.27)))"
HIDDEN = "(effects (font (size 1.27 1.27)) (hide yes))"

# ESP32-C3-MINI-1: (Pinname, Padnummer, Pintyp). Laut Datenblatt Espressif, Tabelle "Pin Definitions".
ESP_LEFT = [
    ("3V3", "3", "power_in"), ("EN", "8", "input"),
    ("IO0", "12", "bidirectional"), ("IO1", "13", "bidirectional"), ("IO2", "5", "bidirectional"),
    ("IO3", "6", "bidirectional"), ("IO4", "18", "bidirectional"), ("IO5", "19", "bidirectional"),
    ("IO6", "20", "bidirectional"), ("IO7", "21", "bidirectional"),
]
ESP_RIGHT = [
    ("IO8", "22", "bidirectional"), ("IO9", "23", "bidirectional"), ("IO10", "16", "bidirectional"),
    ("IO18/USB_D-", "26", "bidirectional"), ("IO19/USB_D+", "27", "bidirectional"),
    ("RXD0/IO20", "30", "bidirectional"), ("TXD0/IO21", "31", "bidirectional"),
]
ESP_GND = ["1", "2", "11", "14"] + [str(n) for n in range(36, 54)]
ESP_NC = ["4", "7", "9", "10", "15", "17", "24", "25", "28", "29", "32", "33", "34", "35"]


def pin(ptype, x, y, rot, name, number, hidden=False):
    hide = " (hide yes)" if hidden else ""
    return (f'\t\t\t(pin {ptype} line (at {x} {y} {rot}) (length 2.54){hide}\n'
            f'\t\t\t\t(name "{name}" {FONT}) (number "{number}" {FONT}))\n')


def esp32_c3_mini_1():
    rows = max(len(ESP_LEFT), len(ESP_RIGHT))
    top = (rows - 1) * 2.54 / 2 + 2.54
    top = round(top / 2.54) * 2.54
    half_w = 12.7
    bottom = top - (rows + 1) * 2.54
    pins = []
    for i, (name, num, ptype) in enumerate(ESP_LEFT):
        pins.append(pin(ptype, -half_w - 2.54, round(top - 2.54 * (i + 1), 2), 0, name, num))
    for i, (name, num, ptype) in enumerate(ESP_RIGHT):
        pins.append(pin(ptype, half_w + 2.54, round(top - 2.54 * (i + 1), 2), 180, name, num))
    gnd_y = round(bottom - 2.54, 2)
    for i, num in enumerate(ESP_GND):
        pins.append(pin("power_in" if i == 0 else "passive", 0, gnd_y, 90, "GND", num, hidden=i > 0))
    for num in ESP_NC:
        pins.append(pin("no_connect", half_w, round(bottom + 2.54, 2), 180, "NC", num, hidden=True))
    return (
        '\t(symbol "ESP32-C3-MINI-1"\n'
        '\t\t(pin_names (offset 1.016))\n'
        '\t\t(exclude_from_sim no) (in_bom yes) (on_board yes)\n'
        f'\t\t(property "Reference" "U" (at {-half_w} {top + 1.27} 0) (effects (font (size 1.27 1.27)) (justify left)))\n'
        f'\t\t(property "Value" "ESP32-C3-MINI-1" (at {half_w} {top + 1.27} 0) (effects (font (size 1.27 1.27)) (justify right)))\n'
        f'\t\t(property "Footprint" "lcsc:WIFIM-SMD_ESP32-C3-MINI-1" (at 0 0 0) {HIDDEN})\n'
        '\t\t(property "Datasheet" "https://www.espressif.com/sites/default/files/documentation/'
        f'esp32-c3-mini-1_datasheet_en.pdf" (at 0 0 0) {HIDDEN})\n'
        f'\t\t(property "Description" "WLAN/BLE-Modul ESP32-C3, 4 MB Flash, PCB-Antenne" (at 0 0 0) {HIDDEN})\n'
        f'\t\t(property "LCSC Part" "C2838502" (at 0 0 0) {HIDDEN})\n'
        '\t\t(symbol "ESP32-C3-MINI-1_0_1"\n'
        f'\t\t\t(rectangle (start {-half_w} {top}) (end {half_w} {round(bottom, 2)})\n'
        '\t\t\t\t(stroke (width 0.254) (type default)) (fill (type background)))\n'
        '\t\t)\n'
        '\t\t(symbol "ESP32-C3-MINI-1_1_1"\n'
        + "".join(pins) +
        '\t\t)\n'
        '\t\t(embedded_fonts no)\n'
        '\t)\n'
    )


def drv8833_parallel():
    """DRV8833PWP mit beiden H-Brücken parallel (Datenblatt Kap. 8.3.5): AIN1+BIN1, AIN2+BIN2,
    AOUT1+BOUT1, AOUT2+BOUT2, AISEN+BISEN. Die zusammengeschalteten Pins liegen übereinander.
    VINT ist der Ausgang des internen Reglers (nur Kondensator), daher passiv."""
    left = [("~{SLEEP}", ["1"], "input"), ("VCP", ["11"], "passive"), ("ISEN", ["3", "6"], "passive"),
            ("IN1", ["16", "9"], "input"), ("IN2", ["15", "10"], "input")]
    right = [("~{FAULT}", ["8"], "open_collector"), ("OUT1", ["2", "7"], "power_out"),
             ("OUT2", ["4", "5"], "power_out")]
    half_w, top, bottom = 10.16, 7.62, -7.62
    pins = []

    def stacked(x, y, rot, name, numbers, ptype):
        for i, num in enumerate(numbers):
            pins.append(pin(ptype if i == 0 else "passive", x, y, rot, name, num, hidden=i > 0))

    for i, (name, nums, ptype) in enumerate(left):
        stacked(-half_w - 2.54, round(top - 2.54 * (i + 1), 2), 0, name, nums, ptype)
    for i, (name, nums, ptype) in enumerate(right):
        stacked(half_w + 2.54, round(top - 2.54 * (i + 1), 2), 180, name, nums, ptype)
    stacked(-2.54, top + 2.54, 270, "VM", ["12"], "power_in")
    stacked(2.54, top + 2.54, 270, "VINT", ["14"], "passive")
    stacked(0, bottom - 2.54, 90, "GND", ["13", "17"], "power_in")
    return (
        '\t(symbol "DRV8833PWP_parallel"\n'
        '\t\t(pin_names (offset 1.016))\n'
        '\t\t(exclude_from_sim no) (in_bom yes) (on_board yes)\n'
        f'\t\t(property "Reference" "U" (at {-half_w} {top + 1.27} 0) (effects (font (size 1.27 1.27)) (justify left)))\n'
        f'\t\t(property "Value" "DRV8833PWP" (at {half_w} {bottom - 1.27} 0) (effects (font (size 1.27 1.27)) (justify right)))\n'
        '\t\t(property "Footprint" "Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.46x2.31mm_ThermalVias"'
        f' (at 0 0 0) {HIDDEN})\n'
        f'\t\t(property "Datasheet" "https://www.ti.com/lit/ds/symlink/drv8833.pdf" (at 0 0 0) {HIDDEN})\n'
        f'\t\t(property "Description" "Dual-H-Brücke, hier im Parallelbetrieb (bis ca. 3 A)" (at 0 0 0) {HIDDEN})\n'
        f'\t\t(property "LCSC Part" "C50506" (at 0 0 0) {HIDDEN})\n'
        '\t\t(symbol "DRV8833PWP_parallel_0_1"\n'
        f'\t\t\t(rectangle (start {-half_w} {top}) (end {half_w} {bottom})\n'
        '\t\t\t\t(stroke (width 0.254) (type default)) (fill (type background)))\n'
        '\t\t)\n'
        '\t\t(symbol "DRV8833PWP_parallel_1_1"\n'
        + "".join(pins) +
        '\t\t)\n'
        '\t\t(embedded_fonts no)\n'
        '\t)\n'
    )


def main():
    LIB.write_text(
        '(kicad_symbol_lib\n'
        '\t(version 20241209)\n'
        '\t(generator "louie_gen_symbols")\n'
        '\t(generator_version "1.0")\n'
        + esp32_c3_mini_1() + drv8833_parallel() +
        ')\n'
    )
    print(f"{LIB.relative_to(LIB.parent.parent.parent)} geschrieben")


if __name__ == "__main__":
    main()
