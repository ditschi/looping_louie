"""Variant 1b (C6 state): all components on top (single-sided machine assembly), passives in 0402.

The bottom has only copper pours and optional footprints without population (DNP): solder pads for cable and cell,
expansion/service pads, end contacts, player inputs J6, LED connector J7 with load switch,
test points (docs/idea-optional-hardware.md 0/0b). Everything on the bottom lies in the pocket of the sleeve
(|y| ≤ 5.2 mm, height ≤ 1.5 mm) and outside the antenna keepout (x > −14.6 mm).

Layout from left (antenna end) to right (docs/main-board-c6.md, chapters 2.2 and 11.3):
- ESP32-C6 module, to its right a row of 0402 directly at the module pins
- edge -y: DRV8213 at the module corner (IO18/IO19), outputs by via to the bottom; buffers C1/C2, Schottky D2
- edge +y: LDO, P-FET Q1 (BAT_IN -> VSYS), 3V3 capacitors; in between the USB lines (y = +0.9 / +1.5)
- USB-C J4 at the +y edge (opening set back 0.7 mm), ESD U5 and CC resistors in the band in front of it (-y),
  right of J4 a row of 0402, in front of it on the right the LIS2DH12 (population optional)
- bottom: J1 (charger cable) and J5 (cell) under J4, J2 (I2C) at the +y edge, J3 (service) and J6
  (players) under the module, IO5 circuitry towards the +y edge; J7 (LED) with U6/C18/R23/R24/C17 under the driver

Coordinates in mm relative to the board centre (x along the length, antenna at -x),
rotation in degrees, side "F" (top) or "B" (bottom, coordinates seen from the top).
"""

MODULE_X = -8.8   # antenna edge of the module at x = -19.84
COL1 = -1.9       # 0402 row directly at the right module pins
USB_X = 15.3      # centre of the USB-C receptacle
USB_Y = 6.05 - 3.65  # front edge 0.7 mm behind the +y edge (footprint: opening at +3.65 mm)
RC1 = 21.2  # row of 0402 (vertical) right of J4; x > 22.2 lies under the end cap of the sleeve

PLACEMENT = {
    # ---- Top side ----------------------------------------------------------------------------
    "U1": (MODULE_X, 0, 90, "F"),
    # 0402 row at the right module pins (pads y = +4.8 IO0 ... -4.8 IO18)
    "R11": (COL1, -3.2, 180, "F"),      # pull-up IO8 (strapping)
    "D1": (COL1, -2.1, 0, "F"),         # LED
    "R9": (COL1, -1.0, 0, "F"),         # LED series resistor at IO14
    "R10": (COL1, 1.85, 180, "F"),      # pull-up SCL (IO7)
    "R16": (COL1, 3.1, 180, "F"),       # pull-up SDA (IO6)
    "C14": (COL1, 4.35, 0, "F"),       # filter ISEN_ADC (IO1)
    "C13": (COL1, 5.6, 0, "F"),        # filter VBAT_ADC (IO0)
    # output stage at the -y module corner: inputs towards the module, outputs towards +x
    "U2": (0.7, -4.6, 180, "F"),        # DRV8213
    "R1": (0.1, -2.55, 0, "F"),         # R_IPROPI 1.24 k
    "C4": (1.85, -2.3, 270, "F"),       # 100 nF VM, pin 1 directly above VM
    "R8": (0.1, -1.5, 0, "F"),         # filter IPROPI -> ADC
    "R3": (2.1, -0.8, 180, "F"),         # OUT_A -> GND (lever detection)
    "R5": (2.1, 0.3, 180, "F"),         # OUT_A -> SENSE
    "R4": (RC1, -1.6, 270, "F"),        # OUT_B -> 3V3: OUT_B on top by via to the OUT_B track on the bottom
    "R6": (-0.4, 5.6, 90, "F"),        # divider VSYS top, next to C13 at the ADC pin (VSYS from U3 pin 3)
    "R7": (-0.4, 3.5, 90, "F"),        # divider bottom, next to R6 (VBAT_ADC stays local, docs/main-board-c6.md 11)
    "C1": (5.45, -2.7, 0, "F"),        # 47 µF
    "C2": (5.45, -0.3, 0, "F"),        # 47 µF
    "D2": (6.9, -5.25, 0, "F"),         # SS34F: cathode (VSYS) left, anode (VBUS) right
    # edge +y: LDO, power path FET, 3V3 capacitors
    # EN pull-up and capacitor side by side at the top right module corner near J3.1 (EN). Their courtyards overlap by
    # 0.08 mm (pads 0.34 mm apart, fine for assembly); stacked horizontally instead they blocked pads 22-25 (variant
    # test 2026-11-09: 2.0 instead of 0 unconnected on average)
    "R2": (-2.62, -5.28, 90, "F"),
    "C12": (-1.68, -5.28, 90, "F"),
    "U3": (2.35, 4.8, 0, "F"),         # LDO SPX3819-3.3
    "Q1": (7.6, 4.85, 0, "F"),          # AO3401A
    "C8": (1.05, 2.3, 0, "F"),          # LDO input
    "C11": (3.05, 2.3, 0, "F"),         # LDO output
    "C9": (5.6, 2.3, 0, "F"),          # 10 µF 3V3 (0603)
    "C10": (8.3, 2.3, 0, "F"),         # 100 nF 3V3
    # USB-C and ESD
    "J4": (USB_X, USB_Y, 0, "F"),
    # USBLC6-2SC6 flow-through: receptacle side right (pin 1 D+, pin 3 D-), module side left (pin 6, pin 4)
    "U5": (16.6, -4.85, 180, "F"),
    "R12": (9.42, -1.0, 90, "F"),       # CC1: left of J4, CC1 runs under the receptacle body
    "R13": (19.7, -3.45, 0, "F"),       # CC2
    # accelerometer (population optional) right of U5
    "U4": (20.75, -5.3, 180, "F"),         # LIS2DH12
    "C15": (RC1, 1.6, 270, "F"),        # 100 nF, 3V3 on top (at R4)
    # VBUS divider in the band left of the ESD, above the VBUS track (VBUS right, VBUS_DET left)
    "R14": (11.2, -3.45, 180, "F"),     # VBUS -> VBUS_DET
    "R15": (11.2, -4.49, 0, "F"),       # VBUS_DET -> GND

    # ---- Bottom side: copper pads only ---------------------------------------------------------
    "J1": (14.5, 5.65, 270, "B"),         # charger cable under J4 at the +y edge (behind the tabs)
    "J5": (15.15, 2.55, 180, "B"),         # cell direct: BAT_IN / GND, under J4 between the tabs
    # solder pads at 2.54 mm pitch (pin header/cable possible)
    "J2": (3.4, 4.3, 180, "B"),         # expansion: 3V3, GND, SDA, SCL, INT; centre y 4.3 (pads up to 5.0 in the pocket)
    "J3": (-8.55, -3.35, 0, "B"),       # service: EN, TXD, BOOT, GND, RXD (button on BOOT+GND)
    # ---- Bottom side optional (DNP), position found with clearance check (pre-routes, vias, pads, keepouts) -------
    # J6 under the module towards the +y edge (pitch 2.0 mm, ends at x −2.9): the centre of the module and right of it
    # stay free for the vias with which the router takes the right module pads to the bottom
    "J6": (-8.63, 3.2, 0, "B"),         # players (pitch 2.0): 3V3 (x −3.63) … GND (x −13.63), towards the +y edge
    "R19": (-11.9, 0.0, 0, "B"),        # IO5 to 3V3 (between the module vias)
    "R20": (-9.8, 0.0, 0, "B"),         # IO5 to GND
    "C16": (-7.8, 0.0, 0, "B"),         # IO5 to GND
    "J7": (8.2, -4.2, 0, "B"),         # LED: VLED (x 10.74), IO23, GND (x 5.66); under D2/USB side −y, away from the driver
    "U6": (2.2, 1.2, 90, "B"),         # LDO for VLED (SPX3819 adj., enable IO15); OUT/ADJ face -y (towards C18/R23 and R24)
    "R22": (-13.7, 0.0, 90, "B"),       # IO15 → GND (U6 off in reset/deep sleep)
    "C18": (6.15, -2.65, 0, "B"),      # output capacitor U6 (former F1 place; lower part blocked by the VSYS vias)
    "R23": (6.15, -1.57, 0, "B"),      # U6 feedback top (VLED → ADJ)
    "R24": (1.5, -1.6, 0, "B"),        # U6 feedback bottom (ADJ → GND), above U6 at the ADJ pin
    "C17": (14.7, -2.05, 0, "B"),        # 10 µF at VLED (under USB-C)
    "TP1": (8.4, 2.4, 0, "B"),          # VSYS
    "TP2": (12.2, -1.4, 0, "B"),        # VBUS
    "BT1": (-21.4, 0, 0, "B"),          # end contact OUT_A (antenna end)
    "BT2": (21.4, 0, 0, "B"),           # end contact OUT_B
}
