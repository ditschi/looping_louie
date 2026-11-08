#!/usr/bin/env python3
"""Generates the project symbol library hardware/lib/louie.kicad_sym.

Contains symbols for which neither KiCad nor LCSC has a usable one (ESP32-C6-MINI-1,
DRV8213DSG; C3, DRV8833 and LIS2DH12 remain as fallback or for board B)
(LCSC symbols have no pin types, which would make the ERC check worthless).

Also the solder pad footprints at 2.54 mm pitch (hardware/lib/louie.pretty/SolderPads_1x0N_P2.54mm, N from
SOLDER_PADS), because KiCad only has pin headers with drill holes for that.

Usage (via just):  just symbols
"""
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "lib" / "louie.kicad_sym"
FOOTPRINTS = LIB.parent / "louie.pretty"
SOLDER_PADS = (3, 4, 5)  # pads per row at 2.54 mm pitch (J7, –, J2/J3)
FONT = "(effects (font (size 1.27 1.27)))"
HIDDEN = "(effects (font (size 1.27 1.27)) (hide yes))"

# ESP modules: (pin name, pad number, pin type). Per Espressif datasheet, table "Pin Definitions".
ESP_C3 = dict(
    left=[("3V3", "3", "power_in"), ("EN", "8", "input"),
          ("IO0", "12", "bidirectional"), ("IO1", "13", "bidirectional"), ("IO2", "5", "bidirectional"),
          ("IO3", "6", "bidirectional"), ("IO4", "18", "bidirectional"), ("IO5", "19", "bidirectional"),
          ("IO6", "20", "bidirectional"), ("IO7", "21", "bidirectional")],
    right=[("IO8", "22", "bidirectional"), ("IO9", "23", "bidirectional"), ("IO10", "16", "bidirectional"),
           ("IO18/USB_D-", "26", "bidirectional"), ("IO19/USB_D+", "27", "bidirectional"),
           ("RXD0/IO20", "30", "bidirectional"), ("TXD0/IO21", "31", "bidirectional")],
    gnd=["1", "2", "11", "14"] + [str(n) for n in range(36, 54)],
    nc=["4", "7", "9", "10", "15", "17", "24", "25", "28", "29", "32", "33", "34", "35"],
    footprint="lcsc:WIFIM-SMD_ESP32-C3-MINI-1", lcsc="C2838502",
    datasheet="https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf",
    description="Wi-Fi/BLE module ESP32-C3, 4 MB flash, PCB antenna",
)
# ESP32-C6-MINI-1: same pads as C3, pinout as KiCad RF_Module:ESP32-C6-MINI-1 (verified)
ESP_C6 = dict(
    left=[("3V3", "3", "power_in"), ("EN", "8", "input")]
    + [(f"IO{n}", pad, "bidirectional") for n, pad in
       [(0, "12"), (1, "13"), (2, "5"), (3, "6"), (4, "9"), (5, "10"), (6, "15"), (7, "16")]],
    right=[(name, pad, "bidirectional") for name, pad in
           [("IO8", "22"), ("IO9", "23"), ("IO12/USB_D-", "17"), ("IO13/USB_D+", "18"), ("IO14", "19"),
            ("IO15", "20"), ("IO18", "24"), ("IO19", "25"), ("IO20", "26"), ("IO21", "27"), ("IO22", "28"),
            ("IO23", "29"), ("RXD0/IO17", "30"), ("TXD0/IO16", "31")]],
    gnd=["1", "2", "11", "14"] + [str(n) for n in range(36, 54)],
    nc=["4", "7", "21", "32", "33", "34", "35"],
    footprint="lcsc:WIFIM-SMD_ESP32-C6-MINI-1", lcsc="C42403058",
    datasheet="https://documentation.espressif.com/esp32-c6-mini-1_mini-1u_datasheet_en.html",
    description="Wi-Fi 6/BLE 5.3/802.15.4 module ESP32-C6, H8 = 8 MB flash (N4 = 4 MB pin-compatible), PCB antenna",
)


def pin(ptype, x, y, rot, name, number, hidden=False):
    hide = " (hide yes)" if hidden else ""
    return (f'\t\t\t(pin {ptype} line (at {x} {y} {rot}) (length 2.54){hide}\n'
            f'\t\t\t\t(name "{name}" {FONT}) (number "{number}" {FONT}))\n')


def esp32_mini_1(name, d):
    rows = max(len(d["left"]), len(d["right"]))
    top = (rows - 1) * 2.54 / 2 + 2.54
    top = round(top / 2.54) * 2.54
    half_w = 12.7
    bottom = top - (rows + 1) * 2.54
    pins = []
    for i, (pname, num, ptype) in enumerate(d["left"]):
        pins.append(pin(ptype, -half_w - 2.54, round(top - 2.54 * (i + 1), 2), 0, pname, num))
    for i, (pname, num, ptype) in enumerate(d["right"]):
        pins.append(pin(ptype, half_w + 2.54, round(top - 2.54 * (i + 1), 2), 180, pname, num))
    gnd_y = round(bottom - 2.54, 2)
    for i, num in enumerate(d["gnd"]):
        pins.append(pin("power_in" if i == 0 else "passive", 0, gnd_y, 90, "GND", num, hidden=i > 0))
    for num in d["nc"]:
        pins.append(pin("no_connect", half_w, round(bottom + 2.54, 2), 180, "NC", num, hidden=True))
    return (
        f'\t(symbol "{name}"\n'
        '\t\t(pin_names (offset 1.016))\n'
        '\t\t(exclude_from_sim no) (in_bom yes) (on_board yes)\n'
        f'\t\t(property "Reference" "U" (at {-half_w} {top + 1.27} 0) (effects (font (size 1.27 1.27)) (justify left)))\n'
        f'\t\t(property "Value" "{name}" (at {half_w} {top + 1.27} 0) (effects (font (size 1.27 1.27)) (justify right)))\n'
        f'\t\t(property "Footprint" "{d["footprint"]}" (at 0 0 0) {HIDDEN})\n'
        f'\t\t(property "Datasheet" "{d["datasheet"]}" (at 0 0 0) {HIDDEN})\n'
        f'\t\t(property "Description" "{d["description"]}" (at 0 0 0) {HIDDEN})\n'
        f'\t\t(property "LCSC Part" "{d["lcsc"]}" (at 0 0 0) {HIDDEN})\n'
        f'\t\t(symbol "{name}_0_1"\n'
        f'\t\t\t(rectangle (start {-half_w} {top}) (end {half_w} {round(bottom, 2)})\n'
        '\t\t\t\t(stroke (width 0.254) (type default)) (fill (type background)))\n'
        '\t\t)\n'
        f'\t\t(symbol "{name}_1_1"\n'
        + "".join(pins) +
        '\t\t)\n'
        '\t\t(embedded_fonts no)\n'
        '\t)\n'
    )


def drv8213dsg():
    """TI DRV8213DSG (WSON-8 2 × 2 mm): H-bridge with current sensing (IPROPI), autosleep, without nSLEEP/nFAULT.
    Pinout per datasheet SLVSGV9 or LCSC C22407186: 1 VM, 2 OUT1, 3 OUT2, 4 GND, 5 IN2, 6 IN1,
    7 GAINSEL, 8 IPROPI, 9 thermal pad (GND)."""
    half_w, top, bottom = 10.16, 5.08, -7.62
    pins = []
    left = [("IN1", "6", "input"), ("IN2", "5", "input"), ("GAINSEL", "7", "input")]
    right = [("OUT1", "2", "power_out"), ("OUT2", "3", "power_out"), ("IPROPI", "8", "output")]
    for i, (name, num, ptype) in enumerate(left):
        pins.append(pin(ptype, -half_w - 2.54, round(top - 2.54 * (i + 1), 2), 0, name, num))
    for i, (name, num, ptype) in enumerate(right):
        pins.append(pin(ptype, half_w + 2.54, round(top - 2.54 * (i + 1), 2), 180, name, num))
    pins.append(pin("power_in", 0, top + 2.54, 270, "VM", "1"))
    pins.append(pin("power_in", 0, bottom - 2.54, 90, "GND", "4"))
    pins.append(pin("passive", 0, bottom - 2.54, 90, "GND", "9", hidden=True))
    return (
        '\t(symbol "DRV8213DSG"\n'
        '\t\t(pin_names (offset 1.016))\n'
        '\t\t(exclude_from_sim no) (in_bom yes) (on_board yes)\n'
        f'\t\t(property "Reference" "U" (at {-half_w} {top + 1.27} 0) (effects (font (size 1.27 1.27)) (justify left)))\n'
        f'\t\t(property "Value" "DRV8213DSG" (at {half_w} {bottom - 1.27} 0) (effects (font (size 1.27 1.27)) (justify right)))\n'
        '\t\t(property "Footprint" "Package_SON:Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm"'
        f' (at 0 0 0) {HIDDEN})\n'
        f'\t\t(property "Datasheet" "https://www.ti.com/lit/gpn/drv8213" (at 0 0 0) {HIDDEN})\n'
        f'\t\t(property "Description" "H-bridge 4 A, current sensing IPROPI, current limit, autosleep" (at 0 0 0) {HIDDEN})\n'
        f'\t\t(property "LCSC Part" "C22407186" (at 0 0 0) {HIDDEN})\n'
        '\t\t(symbol "DRV8213DSG_0_1"\n'
        f'\t\t\t(rectangle (start {-half_w} {top}) (end {half_w} {bottom})\n'
        '\t\t\t\t(stroke (width 0.254) (type default)) (fill (type background)))\n'
        '\t\t)\n'
        '\t\t(symbol "DRV8213DSG_1_1"\n'
        + "".join(pins) +
        '\t\t)\n'
        '\t\t(embedded_fonts no)\n'
        '\t)\n'
    )


def drv8833_parallel():
    """DRV8833PWP with both H-bridges in parallel (datasheet section 8.3.5): AIN1+BIN1, AIN2+BIN2,
    AOUT1+BOUT1, AOUT2+BOUT2, AISEN+BISEN. The paralleled pins are stacked on top of each other.
    VINT is the output of the internal regulator (capacitor only), hence passive."""
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
        '\t\t(property "Footprint" "Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.46x2.31mm"'
        f' (at 0 0 0) {HIDDEN})\n'
        f'\t\t(property "Datasheet" "https://www.ti.com/lit/ds/symlink/drv8833.pdf" (at 0 0 0) {HIDDEN})\n'
        f'\t\t(property "Description" "Dual H-bridge, here in parallel mode (up to approx. 3 A)" (at 0 0 0) {HIDDEN})\n'
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


def lis2dh12():
    """ST LIS2DH12 accelerometer, LGA-12 2×2 mm (pinout per datasheet/LCSC C110926)."""
    half_w, top, bottom = 7.62, 7.62, -7.62
    left = [("VDD", ["9"], "power_in"), ("VDD_IO", ["10"], "power_in"), ("CS", ["2"], "input"),
            ("SDO/SA0", ["3"], "input"), ("RES", ["5"], "passive")]
    right = [("SCL/SPC", ["1"], "input"), ("SDA/SDI", ["4"], "bidirectional"),
             ("INT1", ["12"], "output"), ("INT2", ["11"], "output")]
    pins = []
    for i, (name, nums, ptype) in enumerate(left):
        pins.append(pin(ptype, -half_w - 2.54, round(top - 2.54 * (i + 1), 2), 0, name, nums[0]))
    for i, (name, nums, ptype) in enumerate(right):
        pins.append(pin(ptype, half_w + 2.54, round(top - 2.54 * (i + 1), 2), 180, name, nums[0]))
    for i, num in enumerate(["6", "7", "8"]):
        pins.append(pin("power_in" if i == 0 else "passive", 0, bottom - 2.54, 90, "GND", num, hidden=i > 0))
    return (
        '\t(symbol "LIS2DH12"\n'
        '\t\t(pin_names (offset 1.016))\n'
        '\t\t(exclude_from_sim no) (in_bom yes) (on_board yes)\n'
        f'\t\t(property "Reference" "U" (at {-half_w} {top + 1.27} 0) (effects (font (size 1.27 1.27)) (justify left)))\n'
        f'\t\t(property "Value" "LIS2DH12" (at {half_w} {top + 1.27} 0) (effects (font (size 1.27 1.27)) (justify right)))\n'
        f'\t\t(property "Footprint" "Package_LGA:LGA-12_2x2mm_P0.5mm" (at 0 0 0) {HIDDEN})\n'
        f'\t\t(property "Datasheet" "https://www.st.com/resource/en/datasheet/lis2dh12.pdf" (at 0 0 0) {HIDDEN})\n'
        f'\t\t(property "Description" "3-axis accelerometer, I2C/SPI, 2 µA" (at 0 0 0) {HIDDEN})\n'
        f'\t\t(property "LCSC Part" "C110926" (at 0 0 0) {HIDDEN})\n'
        '\t\t(symbol "LIS2DH12_0_1"\n'
        f'\t\t\t(rectangle (start {-half_w} {top}) (end {half_w} {bottom})\n'
        '\t\t\t\t(stroke (width 0.254) (type default)) (fill (type background)))\n'
        '\t\t)\n'
        '\t\t(symbol "LIS2DH12_1_1"\n'
        + "".join(pins) +
        '\t\t)\n'
        '\t\t(embedded_fonts no)\n'
        '\t)\n'
    )


def solder_pads(n, pitch=2.54, size=1.4):
    """Footprint with n SMD solder pads in a row (pad 1 square), not populated (not in BOM/placement)."""
    half = round((n - 1) * pitch / 2 + 0.85, 2)
    name = f"SolderPads_1x{n:02d}_P{pitch:.2f}mm"
    pitch_text = f"{pitch:.2f}"
    pads = []
    for k in range(n):
        x = round(-(n - 1) * pitch / 2 + k * pitch, 2)
        shape = "rect" if k == 0 else "circle"
        pads.append(f'\t(pad "{k + 1}" smd {shape} (at {x if x else "0.0"} 0) (size {size} {size}) '
                    '(layers "F.Cu" "F.Mask"))\n')
    return name, (
        f'(footprint "{name}"\n'
        '\t(version 20241229)\n'
        '\t(generator "louie")\n'
        '\t(layer "F.Cu")\n'
        f'\t(descr "{n} SMD solder pads at {pitch_text} mm pitch (pin header or stranded wires). Not populated.")\n'
        '\t(tags "solder pad header")\n'
        '\t(property "Reference" "REF**" (at 0 -1.6 0) (layer "F.Fab") (effects (font (size 0.5 0.5) (thickness 0.08))))\n'
        f'\t(property "Value" "SolderPads_1x{n:02d}" (at 0 1.6 0) (layer "F.Fab") (hide yes) '
        '(effects (font (size 0.5 0.5) (thickness 0.08))))\n'
        '\t(attr smd exclude_from_pos_files exclude_from_bom)\n'
        f'\t(fp_rect (start -{half} -0.95) (end {half} 0.95) (stroke (width 0.05) (type default)) (fill no) '
        '(layer "F.CrtYd"))\n'
        + "".join(pads) +
        '\t(embedded_fonts no)\n'
        ')\n')


def test_pad(d=1.0, courtyard=0.65):
    """Round test point (probe tip/pogo pin), copper only; courtyard tighter than KiCad's TestPoint_Pad_D1.0mm
    (r = 1.0 mm), so that it fits between the optional components on the bottom."""
    name = f"TestPad_D{d:.1f}mm"
    return name, (
        f'(footprint "{name}"\n'
        '\t(version 20241229)\n'
        '\t(generator "louie")\n'
        '\t(layer "F.Cu")\n'
        f'\t(descr "Round SMD test point {d:.1f} mm (probe tip, pogo pin). Not populated.")\n'
        '\t(tags "test point pad")\n'
        '\t(property "Reference" "REF**" (at 0 -1.0 0) (layer "F.Fab") (effects (font (size 0.5 0.5) (thickness 0.08))))\n'
        f'\t(property "Value" "{name}" (at 0 1.0 0) (layer "F.Fab") (hide yes) '
        '(effects (font (size 0.5 0.5) (thickness 0.08))))\n'
        '\t(attr smd exclude_from_pos_files exclude_from_bom)\n'
        f'\t(fp_circle (center 0 0) (end {courtyard} 0) (stroke (width 0.05) (type default)) (fill no) '
        '(layer "F.CrtYd"))\n'
        f'\t(pad "1" smd circle (at 0 0) (size {d} {d}) (layers "F.Cu" "F.Mask"))\n'
        '\t(embedded_fonts no)\n'
        ')\n')


def main():
    name, text = test_pad()
    (FOOTPRINTS / f"{name}.kicad_mod").write_text(text)
    for n, pitch in [(n, 2.54) for n in SOLDER_PADS] + [(6, 2.0)]:  # 1x06 2.0 mm: J6 (shorter, 11.7)
        name, text = solder_pads(n, pitch)
        (FOOTPRINTS / f"{name}.kicad_mod").write_text(text)
    LIB.write_text(
        '(kicad_symbol_lib\n'
        '\t(version 20241209)\n'
        '\t(generator "louie_gen_symbols")\n'
        '\t(generator_version "1.0")\n'
        + esp32_mini_1("ESP32-C3-MINI-1", ESP_C3) + esp32_mini_1("ESP32-C6-MINI-1", ESP_C6)
        + drv8213dsg() + drv8833_parallel() + lis2dh12() +
        ')\n'
    )
    print(f"{LIB.relative_to(LIB.parent.parent.parent)} written")


if __name__ == "__main__":
    main()
