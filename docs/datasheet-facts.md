# Datasheet facts: verified fact sheets

Status: 2026-11-09 · Basis for the [wiring review](wiring-review.md). Documents and revisions:
[datasheets.md](datasheets.md) (PDFs in the gitignored `datasheets/`, `just datasheets`).

**How this was made:** Agent A extracted the facts per part group from the PDFs (paraphrased, with page/table
references). Agent B, an independent agent without A's context, checked every item against the PDFs, including
rendered pages for pinout drawings and land patterns, and tagged it:

- **[verified]** matches the PDF
- **[corrected]** value or reference fixed by B (B's reference given)
- **[unverifiable]** not confirmable from the documents
- **[added]** item added by B because it matters for the wiring review

Result: 218 verified, 21 corrected (mostly page references and package dimensions; no pinout of a fitted part had to be
corrected), 0 unverifiable, 40 added. Anything marked "(derived)" is a calculation, not a datasheet value. Datasheets
are copyrighted: values are paraphrased; see the PDF for the authoritative wording.

Groups: G1 = MCU and load switch (U1, U6, F1) · G2 = motor driver, LDO, accelerometer, P-MOSFET (U2, U3, U4, Q1/Q101) ·
G3 = USB, diodes, LEDs, charger IC, connectors (U5/U102, J4/J101, D2, D102, D1, D101, U101, J102) ·
G4 = delta 2026-11-09 for VSYS up to 6.6 V: SPX3819 (new U3/U6), all VSYS parts at 6.6 V, F1 PTC candidates (proposals).

G1–G3 describe the design state at commit `32a3535`; the AP2112K (G2), TPS22918 and BSMD0805-050-6V (G1) sections are kept
for reference but are superseded on the main board by G4.


---

## Fact sheet G1 – MCU and load switch (VERIFIED by Agent B)

Verification method: every item re-checked against the PDFs (pdftotext -layout per page, plus visual rendering of MOD Figs 3-1, 8-1, 9-1 (zoomed at 300 dpi), 10-1 (zoomed), 11-1, HDG Fig 24/25, PTC p.7). Page-offset claims checked: MOD and SOC PDF page = printed page (confirmed); HDG PDF page = printed + 3 (confirmed, e.g. PDF 8 = printed 5); TPS PDF = printed for 1-22, mechanical PDF 23-30 (confirmed); PTC n/10 footer = PDF page (confirmed).

Tags: **[verified]** matches PDF; **[corrected]** value or reference fixed (my reference given); **[unverifiable]** cannot be confirmed from the documents; **[added]** new item by Agent B.

Documents (all in `datasheets/`):
- **MOD** = ESP32-C6-MINI-1 & MINI-1U Datasheet v1.5 (`ESP32-C6-MINI-1_datasheet_en.pdf`). PDF page = printed page.
- **SOC** = ESP32-C6 Series Datasheet v1.5 (`ESP32-C6_datasheet_en.pdf`). PDF page = printed page.
- **HDG** = ESP32-C6 Hardware Design Guidelines, release master, built 2026-11-09 (`ESP32-C6_hardware_design_guidelines_en.pdf`). **PDF page = printed page + 3.** Both are given as "p.X (PDF Y)".
- **TPS** = TI SLVSD76C TPS22918 (`TPS22918_datasheet.pdf`). PDF page = printed page for pp.1-22; mechanical pages are PDF-only (23-30).
- **PTC** = BHFUSE BSMD0805 Series approval sheet, Revision 2025 (`BSMD0805-050-6V_datasheet.pdf`). Page = "n / 10" footer = PDF page.

Values are paraphrased. Anything I worked out myself rather than read from a document is marked "(derived)".

---

### ESP32-C6-MINI-1-H8 (U1)

**Pinout (module, 53 pads)**

G1-ESP32-1. **[verified]** Pad pattern, top view: 11 pads down the left edge (1 to 11, top to bottom), 13 along the bottom edge (12 to 24, left to right), 11 up the right edge (25 to 35, bottom to top) and 13 along the top edge under the antenna (36 to 48, right to left). There are 4 corner GND pads: 50 top-right, 51 bottom-right, 52 bottom-left, 53 top-left. Pad 49 is the central GND/EPAD, drawn as a 3×3 array of squares. Pin 1 is the top-left side pad, next to the antenna area. [source: MOD, p.10, Figure 3-1; p.44, Figure 11-1; p.38, Figure 8-1 pin-out symbol]

G1-ESP32-2. **[corrected]** GND pads: 1, 2, 11, 14, and 36 to 53 (pad list verified). Count corrected: 4 side/bottom pads + 13 top-row pads (36-48) + EPAD 49 + 4 corners (50-53) = **22 GND pads, not 23** (36..53 inclusive is 18 pads). [Agent B: MOD p.10, Table 3-1 row GND; Figure 3-1] All of them are type P. [source: MOD, p.10, Table 3-1]

G1-ESP32-3. **[verified]** Full pad table (name, pad, type, functions):

| Pad | Name | Type | Function(s) |
|---|---|---|---|
| 1 | GND | P | Ground |
| 2 | GND | P | Ground |
| 3 | 3V3 | P | Power supply |
| 4 | NC | – | not connected |
| 5 | IO2 | I/O/T | GPIO2, LP_GPIO2, LP_UART_RTSN, ADC1_CH2, FSPIQ |
| 6 | IO3 | I/O/T | GPIO3, LP_GPIO3, LP_UART_CTSN, ADC1_CH3 |
| 7 | NC | – | not connected |
| 8 | EN | I | High enables the chip, low powers it off. Must not float. |
| 9 | IO4 | I/O/T | MTMS, GPIO4, LP_GPIO4, LP_UART_RXD, ADC1_CH4, FSPIHD (strapping MTMS) |
| 10 | IO5 | I/O/T | MTDI, GPIO5, LP_GPIO5, LP_UART_TXD, ADC1_CH5, FSPIWP (strapping MTDI) |
| 11 | GND | P | Ground |
| 12 | IO0 | I/O/T | GPIO0, XTAL_32K_P, LP_GPIO0, LP_UART_DTRN, ADC1_CH0 |
| 13 | IO1 | I/O/T | GPIO1, XTAL_32K_N, LP_GPIO1, LP_UART_DSRN, ADC1_CH1 |
| 14 | GND | P | Ground |
| 15 | IO6 | I/O/T | MTCK, GPIO6, LP_GPIO6, LP_I2C_SDA, ADC1_CH6, FSPICLK |
| 16 | IO7 | I/O/T | MTDO, GPIO7, LP_GPIO7, LP_I2C_SCL, FSPID |
| 17 | IO12 | I/O/T | GPIO12, USB_D- |
| 18 | IO13 | I/O/T | GPIO13, USB_D+ |
| 19 | IO14 | I/O/T | GPIO14 |
| 20 | IO15 | I/O/T | GPIO15 (strapping: JTAG source) |
| 21 | NC | – | not connected |
| 22 | IO8 | I/O/T | GPIO8 (strapping: boot mode / ROM print) |
| 23 | IO9 | I/O/T | GPIO9 (strapping: boot mode) |
| 24 | IO18 | I/O/T | GPIO18, SDIO_CMD, FSPICS2 |
| 25 | IO19 | I/O/T | GPIO19, SDIO_CLK, FSPICS3 |
| 26 | IO20 | I/O/T | GPIO20, SDIO_DATA0, FSPICS4 |
| 27 | IO21 | I/O/T | GPIO21, SDIO_DATA1, FSPICS5 |
| 28 | IO22 | I/O/T | GPIO22, SDIO_DATA2 |
| 29 | IO23 | I/O/T | GPIO23, SDIO_DATA3 |
| 30 | RXD0 | I/O/T | U0RXD, GPIO17, FSPICS1 |
| 31 | TXD0 | I/O/T | U0TXD, GPIO16, FSPICS0 |
| 32-35 | NC | – | not connected |
| 36-48 | GND | P | Ground (top row, under the antenna side) |
| 49 | GND (EPAD) | P | Central exposed ground pad (3×3 sub-pads) |
| 50-53 | GND | P | Corner ground pads |

[source: MOD, pp.10-11, Table 3-1 and Figure 3-1]

G1-ESP32-4. **[verified]** (Agent B note: Fig 8-1 also shows an ESD diode D1 on VDD33 inside the module, see G1-ESP32-A2.) Module-internal wiring: EN goes straight to the chip's CHIP_PU pin, with no internal pull-up or RC drawn. Inside the module, the 3V3 rail has 10 µF, 1 µF, 10 nF and several 0.1 µF capacitors. GPIO16 (U0TXD) goes through a 499 Ω series resistor inside the module, and GPIO19 (SDIO_CLK) through 0 Ω. [source: MOD, p.38, Figure 8-1 Module Schematics]

**Absolute maximum ratings / recommended operating conditions**

G1-ESP32-5. **[verified]** Absolute maximum for module VDD33: -0.3 V to 3.6 V. [source: MOD, p.26, Table 6-1]

G1-ESP32-6. **[corrected]** Recommended VDD33 is 3.0 / 3.3 / 3.6 V (min/typ/max). The external supply must be able to deliver at least 0.5 A. Ambient temperature is -40 to +105 °C for the 105 °C versions, and the H8 is one of them (Table 1-1 lists -H4/-H8 as -40 to 105 °C). [source: MOD, p.26, Table 6-2; p.7 (printed 3), Table 1-1] — **[corrected] reference only:** Table 1-1 is on MOD **p.4** (PDF 4 = printed 4); p.7 is the List of Tables. Values are correct.

G1-ESP32-7. **[verified]** Chip level: the input power pins have an absolute maximum of -0.3 to 3.6 V. Cumulative IO output current is 1000 mA max. Storage temperature is -40 to 150 °C. Recommended VDDA/VDDPST1/VDDPST2 is 3.0 to 3.6 V, cumulative input current at least 0.5 A, TA -40 to 105 °C. Note 3: when writing eFuses, VDDPST2 should not exceed 3.3 V. [source: SOC, p.64, Tables 5-1 and 5-2]

G1-ESP32-8. **[verified]** IO levels (3.3 V, 25 °C): VIH min 0.75×VDD and max VDD+0.3. VIL max 0.25×VDD. VOH min 0.8×VDD, VOL max 0.1×VDD. IOH is 40 mA typ and IOL 28 mA typ at drive strength 3. Internal pull-up and pull-down are 45 kΩ typ. **IO pins are not 5 V tolerant**: VIH max is VDD+0.3, about 3.6 V. [source: MOD, p.26, Table 6-3; SOC, p.65, Table 5-4]

G1-ESP32-9. **[verified]** EN/CHIP_PU thresholds: reset is released at VIH_nRST ≥ 0.75×VDD (2.475 V at 3.3 V, derived). The chip is held in reset at VIL_nRST ≤ 0.25×VDD (0.825 V at 3.3 V, derived). [source: MOD, pp.26-27, Table 6-3; SOC, p.65, Table 5-4]

G1-ESP32-10. **[verified]** Peak supply current at 3.3 V: Wi-Fi TX 802.11b at 20.5 dBm is 382 mA peak. BLE TX at 19 dBm is 309 mA peak. [source: MOD, p.27, Tables 6-4 and 6-5]

G1-ESP32-11. **[verified]** **5.5 V question:** 5.5 V on 3V3 (pad 3) is **outside the absolute maximum** (3.6 V) and outside the recommended range (3.0-3.6 V). 5.5 V on any IO or EN is also outside the limits (VIH max VDD+0.3). U1 may only connect to the 3V3 rail. Any VBUS/VSYS sensing needs a divider or clamp so the pin stays at or below about 3.6 V. [source: MOD, p.26, Tables 6-1, 6-2 and 6-3]

**External components / placement**

G1-ESP32-12. **[corrected]** Espressif's peripheral reference schematic shows: 22 µF + 0.1 µF on 3V3 (C1, C2), an EN pull-up R1 to VDD33 (value "TBD") with C3 to GND ("TBD"), a reset button SW1 through R2 = 0 Ω with C4 = 0.1 µF, R8 = 10 kΩ pull-up from VDD33 to IO8, a 2-pin "Boot Option" jumper JP2 to GND at the IO9/IO8 area, and USB_D+/USB_D- series resistors R6/R7 plus capacitors to GND C7/C8. **Correction:** only C7/C8 are drawn grey (= not populated, "NC: No component"); R6/R7 are drawn black, i.e. populated with value TBD (cf. HDG §1.3.13: 22/33 Ω start value). **JP2 confirmed visually at 300 dpi: JP2 pin 1 = IO9 (module pad 23), JP2 pin 2 = GND.** R8 10 kΩ goes from VDD33 to the IO8 net (pad 22), confirmed. [Agent B: MOD p.40, Figure 9-1, zoomed render] [source: MOD, p.40, Figure 9-1 Peripheral Schematics]

G1-ESP32-13. **[verified]** RC on EN: an RC delay at EN is recommended, usually **R = 10 kΩ, C = 1 µF**, adjusted to the actual supply ramp. [source: MOD, p.40, text below Figure 9-1; HDG, p.7 (PDF 10), §1.3.3 Attention box]

G1-ESP32-14. **[verified]** Keep the CHIP_PU/EN trace as short as possible so that interference cannot cause resets. CHIP_PU must not be left floating. Neither MOD nor HDG explicitly says to place the RC "close to the EN pin". The "short trace" rule implies it (derived). [source: HDG, p.7 (PDF 10), §1.3.3; MOD, p.11, Table 3-1 EN note]

G1-ESP32-15. **[verified]** HDG adds that the RC alone may not meet timing when the supply rises or falls slowly (e.g. **during battery charging**), when power is cycled often, or when the supply is unstable. In those cases, reserve a supply supervisor (reset IC) with a threshold of about 3.0 V. **This applies to our 1S LiPo + charger design.** [source: HDG, p.7 (PDF 10), §1.3.3 Attention box]

G1-ESP32-16. **[verified]** Power-entry recommendations: a 3.3 V single supply rated at least 500 mA. An ESD diode and at least 10 µF where power enters the PCB. Per the chip-level guide, 0.1 µF close to the digital supply pins and 10 µF on the analog rail. The 10 µF at the power entrance can be merged with that one when the two are close together. For the module, the internal caps (G1-ESP32-4) plus the external 22 µF + 0.1 µF from Figure 9-1 apply. [source: HDG, pp.5-6 (PDF 8-9), §1.3.2; MOD, p.40, Figure 9-1]

G1-ESP32-17. **[verified]** (wording note: HDG says "close to the chip" / "close to the chip side"; for a module design that means at the module pads) USB on IO12/IO13: reserve series resistors (22-33 Ω to start) and capacitors to GND (unpopulated to start) close to the module. Route as a 90 Ω ±10 % differential pair with a continuous GND reference and few vias. USB_D+ toggles at power-up, so add an external pull-up if a stable initial level is needed. By default, GPIO12/13 are USB pins with the USB pull-up (USB_PU) active. [source: HDG, p.15 (PDF 18), §1.3.13; p.24 (PDF 27), §1.4.8; p.14 (PDF 17), Table 6 notes]

G1-ESP32-18. **[verified]** ADC (GPIO0-6 = ADC1_CH0-6): 0.1 µF filter capacitor at the pin is recommended. Calibrated range at ATTEN=3 is 0-3300 mV with ±40 mV total error. [source: HDG, p.14 (PDF 17), §1.3.11]

G1-ESP32-19. **[verified]** UART0: a 499 Ω series resistor on U0TXD is recommended. The module already contains it (G1-ESP32-4). Keep UART0 available for download, because the RF test firmware supports UART only. [source: HDG, p.12 (PDF 15), §1.3.7; p.27 (PDF 30), Download notes; MOD, p.38, Figure 8-1]

**Power-up / EN timing**

G1-ESP32-20. **[verified]** tSTBL ≥ 50 µs: the time the supply rails need to be stable (above about 2.8 V in the figure) before CHIP_PU goes high. tRST ≥ 50 µs: the minimum time CHIP_PU must stay below VIL_nRST for a reset. [source: MOD, pp.15-16, Figure 4-2 and Table 4-8; SOC, pp.30-31, Figure 2-4 and Table 2-15; HDG, p.7 (PDF 10), Table 1]

G1-ESP32-21. **[verified]** Strapping timing: tSU ≥ 0 ms (rails stable before CHIP_PU rises). tH ≥ 3 ms: strapping levels must stay valid for at least 3 ms after CHIP_PU is high. [source: MOD, p.13, Table 4-2 and Figure 4-1; SOC, p.34, Table 3-2; HDG, p.13 (PDF 16), Table 5]

G1-ESP32-22. **[verified]** RC timing (derived, not from the documents): 10 kΩ × 1 µF gives τ = 10 ms. With an ideal 3.3 V step, EN reaches 0.75×VDD after about 1.39 τ, roughly 14 ms. That satisfies tSTBL ≥ 50 µs by a wide margin.

**Strapping pins**

G1-ESP32-23. **[verified]** Default levels at reset: MTMS, MTDI, GPIO8 and GPIO15 float (no internal pull). GPIO9 has a weak pull-up, so it reads 1. [source: MOD, p.12, Table 4-1; SOC, p.33, Table 3-1]

G1-ESP32-24. **[verified]** Boot mode: GPIO9 = 1 selects SPI boot (normal) whatever GPIO8 is. GPIO8 = 1 with GPIO9 = 0 selects joint download boot (USB-Serial-JTAG, UART or SDIO). **GPIO8 = 0 with GPIO9 = 0 is an invalid combination that HDG says causes unexpected behaviour.** So IO8 must be high whenever IO9 is pulled low. [source: MOD, p.13, Table 4-3; SOC, p.34, Table 3-3; HDG, p.12 (PDF 15), Table 4 and footnote 1]

G1-ESP32-25. **[verified]** HDG recommends an external pull-up on GPIO9 and **no large capacitor on GPIO9**, because the chip may otherwise enter download mode. [source: HDG, p.13 (PDF 16), Attention box]

G1-ESP32-26. **[verified]** GPIO8 also controls ROM messages on UART0. With the default eFuse EFUSE_UART_PRINT_CONTROL = 0, GPIO8 is ignored and printing is enabled. [source: MOD, p.14, Table 4-5]

G1-ESP32-27. **[verified]** GPIO15 selects the JTAG signal source, but only when EFUSE_JTAG_SEL_ENABLE = 1. With default eFuses (all 0), GPIO15 is ignored and JTAG comes from the USB Serial/JTAG controller. GPIO15 has no internal pull, and when it is used as a strap the external circuit must drive it to a defined level (not Hi-Z). [source: MOD, p.15, §4.4 and Table 4-7; SOC, §3 (p.33 list)]

G1-ESP32-28. **[verified]** MTMS (IO4) and MTDI (IO5) strap the SDIO sampling and driving edge only. They float by default, and this matters only if the SDIO slave is used. [source: MOD, p.14, Table 4-4]

G1-ESP32-29. **[verified]** Strapping values are latched at chip reset and kept until power-down. After reset the pins work as normal GPIOs. [source: MOD, pp.12-13, §4; SOC, p.33]

G1-ESP32-30. **[verified]** Download over USB: an empty flash needs the joint download strap (IO9 low). Afterwards IO9 must be high or floating for SPI boot. USB auto-download stops working if the application disables the USB PHY, reconfigures USB, or remaps the USB IOs. In that case the strap must be used, so HDG recommends keeping control of the strapping pins. [source: HDG, pp.26-27 (PDF 29-30), Download Guidelines]

G1-ESP32-31. **[verified]** Deep sleep: only GPIOs in the VDDPST1 domain can be controlled in deep sleep. These are LP GPIOs: XTAL_32K_P/N = GPIO0/1, GPIO2-GPIO7. This matters for any enable line, such as TPS22918 ON or DRV8213 nSLEEP, that must hold its level in deep sleep (relevance derived). [source: HDG, p.14 (PDF 17), GPIO bullet list; SOC, p.29, Table 2-13 (LP IO = VDDPST1 domain)]

G1-ESP32-32. **[verified]** GPIO13 (USB_D+) has USB_PU active at reset. When USB is disabled, its weak pull-up is off at reset and on after reset. GPIO9 has a WPU both at and after reset. GPIO8 and GPIO15 are input-enabled only (no pull) at and after reset. [source: SOC, pp.17-18, Table 2-2 QFN32 Pin Overview, "At Reset/After Reset" columns; HDG, pp.14-15 (PDF 17-18)]

**Polarity / orientation**

G1-ESP32-33. **[corrected]** Pin 1 is the top-left side pad next to the antenna area (top view). The recommended land pattern marks "Pin 1" with a leader line. The central 3×3 GND pad array has a chamfered top-left sub-pad on the pin-1 side. The shield top shows a Ø0.50 mm circular mark (Figure 10-1), but the document does not say whether it marks pin 1. **Agent B clarification (zoomed Fig 10-1 top view, and HDG Fig 24 module drawings): the Ø0.50 dot sits at the lower-left corner of the shield, i.e. at the end AWAY from the antenna (near pads 11/12/52), not next to pin 1. Do not use it as a pin-1 locator; pin 1 is the topmost left-side pad directly below corner pad 53, adjacent to the antenna area.** Shield can is 11.95 × 9.95 mm. Module outline is 13.2 × 16.6 × 2.4 mm (±0.2, ±0.15 for height) — verified. **Reference corrected:** Table 1-1 is on MOD p.4, not p.7. [Agent B: MOD p.41 Fig 10-1; p.44 Fig 11-1; p.4 Table 1-1; HDG p.25 (PDF 28) Fig 24]

**Land pattern / EPAD**

G1-ESP32-34. **[corrected]** (interpretation only) Land pattern: 48 signal/GND pads 0.40 mm wide on 0.80 mm pitch. The 4 corner pads are 0.70 × 0.70 mm. Outer pad span is 11.80/11.90 mm horizontally, and the side-pad row length is 9.80/9.90 mm. The central GND array is 3×3 squares of 1.45 mm with 0.60 mm gaps, inside a 5.40 mm reference square. Other dimensions shown: 1.60, 11.20 and 0.80 mm offsets from the module edge, and 16.60 mm total length including the antenna area. Espressif provides source files (Autodesk Viewer link) for dimensions not shown. [source: MOD, p.44, Figure 11-1; p.41, Figure 10-1 bottom view] — **Agent B:** all numbers are transcribed correctly, but reading 0.60 as the gap between the 1.45 mm squares does not add up: 3×1.45 + 2×0.60 = 5.55 mm ≠ 5.40 mm. The 0.60 dimension is ambiguous in the drawing (could be an offset); the pad length of the perimeter pads is not explicitly dimensioned either. Take the EPAD array geometry and pad length from Espressif's land-pattern source file / KiCad footprint, not from this figure. Pin-1 chamfer on the top-left EPAD sub-pad confirmed (Fig 11-1, top view; mirrored to top-right in the Fig 10-1 bottom view).

G1-ESP32-35. **[verified]** EPAD (pad 49): soldering it to base-board GND is optional but improves thermal performance. Use the correct amount of paste, because too much lifts the module and weakens the other joints. **NOT FOUND in MOD/HDG**: a required number of thermal vias or a paste-window/stencil pattern for the EPAD. [source: MOD, p.40, first bullet below Figure 9-1]

G1-ESP32-36. **[verified]** Antenna placement: put the PCB antenna outside the base board, or at a board edge with the feed point close to the edge. The keepout drawing shows a board cut-out beside the antenna of at least 15 mm (on the side away from the module) and 6.00 mm deep along the antenna. Edge overhangs are max 2 mm on the side and max 1 mm, as drawn. Do not place the module in the middle of the board with a cut-out on all four sides. Provide ground copper and dense GND vias near the antenna. Keep at least 15 mm clearance to the housing in all directions. MOD Figure 3-1 marks the area above pins 36-48 as a "Keepout Zone". [source: HDG, pp.23-25 (PDF 26-28), §1.4.7, Figures 23-25; MOD, p.10, Figure 3-1; p.45, §11.2]

G1-ESP32-37. **[verified]** MSL 3: once the bag is opened, solder within 168 h at 25±5 °C / 60 %RH, otherwise bake. [source: MOD, p.46, §12.1]

G1-ESP32-38. **[verified]** Flash: the H8 has 8 MB quad-SPI flash inside the chip package (ESP32-C6FH8). Flash pins are not brought out, and up to 22 GPIOs are available. [source: MOD, p.4, Table 1-1; p.17, §5.1; HDG, p.8 (PDF 11), §1.3.4]


**Added by Agent B (ESP32-C6-MINI-1-H8)**

G1-ESP32-A1. **[added]** Module ESD: HBM ±2000 V, CDM ±500 V. Solder in a **single reflow**; module peak 235-250 °C, >217 °C for 60-90 s, MSL 3. [MOD, p.46, §12.2, §12.3 Fig 12-1] (relevance: USB D+/D- and any connector-facing IO need external ESD protection; F1's 260 °C max peak is compatible with the module's 250 °C max peak profile.)

G1-ESP32-A2. **[added]** The module already contains an ESD diode (D1) on VDD33 and 10 µF + 1 µF + 10 nF + 4×0.1 µF on the 3V3 rail (C3-C7, C10, C12). [MOD, p.38, Fig 8-1]

G1-ESP32-A3. **[added]** Default pin states (QFN32 = ESP32-C6FH8, relevant for enable lines such as TPS22918 ON / DRV8213 nSLEEP and for current leakage):
- GPIO0/1 (XTAL_32K), GPIO7 (MTDO), GPIO12, GPIO14: no pull at reset (GPIO12/14 IE after reset; GPIO13 USB_PU).
- GPIO2, GPIO3, GPIO4 (MTMS), GPIO5 (MTDI), GPIO8, GPIO15: IE, no pull at and after reset.
- **GPIO6 (MTCK): internal weak pull-up enabled after reset** (with default EFUSE_DIS_PAD_JTAG = 0) → an active-high enable on IO6 would be pulled HIGH after reset until firmware reconfigures it.
- **GPIO18-GPIO23 (SDIO pins): weak pull-up enabled DURING reset** → same issue for active-high enables.
- GPIO9: WPU at and after reset; GPIO16 (U0TXD) output-enabled + WPU after reset; GPIO17 (U0RXD) IE + WPU after reset.
Consequence (derived): for a load-switch ON or driver nSLEEP line use an LP GPIO without default pull (GPIO0-5, GPIO7) plus an external pull-down. [SOC, pp.17-18, Table 2-2 and notes 4-6; HDG p.14 (PDF 17) Table 6]

G1-ESP32-A4. **[added]** Default drive strength is 20 mA for all GPIOs except GPIO12/13 (40 mA). Input leakage IIH/IIL max 50 nA (useful for sizing high-value ADC dividers on VBUS/VBAT sensing). [SOC, p.18, Table 2-2 note 3; MOD p.26, Table 6-3]

G1-ESP32-A5. **[added]** Unused GPIOs that are Hi-Z without internal pull should get an external pull or have the internal pull enabled in firmware, to avoid extra current. [HDG, p.14 (PDF 17), §1.3.10 bullet 2]

G1-ESP32-A6. **[added]** Antenna feed side (derived from drawing): in the MOD top view the meander antenna's two vertical legs (feed + ground) drop down at the LEFT end, i.e. the pin-1 side. This corresponds to HDG Fig 24 ("antenna feed point on the left") for placement choices; Fig 25 shows the mirror case. [MOD p.41, Fig 10-1 top view; HDG pp.24-25 (PDF 27-28), Figs 23-25]

---

### TPS22918DBVR (U6)

**Pinout**

G1-TPS22918-1. **[verified]** SOT-23-6 (DBV), top view:

| Pin | Name | I/O | Function |
|---|---|---|---|
| 1 | VIN | I | Switch input. Needs a ceramic bypass cap to GND. |
| 2 | GND | – | Device ground |
| 3 | ON | I | Active-high enable. **Must not float.** |
| 4 | CT | O | Slew-rate (rise-time) capacitor to GND. May be left floating. |
| 5 | QOD | O | Quick output discharge: tie to VOUT (internal RPD), connect to VOUT through REXT, or leave floating (no discharge) |
| 6 | VOUT | O | Switch output |

[source: TPS, p.3, Pin Configuration and Pin Functions table]

**Absolute maximum ratings / recommended operating conditions**

G1-TPS22918-2. **[verified]** Absolute maximum: VIN, VOUT and VON are each -0.3 to 6 V. IMAX is 2 A continuous (at TA = 70 °C). IPLS is 2.5 A (pulses under 300 µs, 2 % duty). TJ max 125 °C. Tstg -65 to 150 °C. ESD is ±2 kV HBM and ±1 kV CDM. [source: TPS, p.4, §6.1 and §6.2]

G1-TPS22918-3. **[verified]** Recommended operating conditions: VIN 0-5.5 V (the features list and §10 give 1-5.5 V as the operating range). VON 0-5.5 V, independent of VIN. VOUT up to VIN. VIH,ON is 1 to 5.5 V and VIL,ON is 0 to 0.5 V (for VIN 1-5.5 V). TA -40 to 105 °C. CIN at least 1 µF. [source: TPS, p.4, §6.3; p.1, Features; p.20, §10]

G1-TPS22918-4. **[verified]** **5.5 V question:** VIN = 5.5 V is **within the absolute maximum** (6 V, 0.5 V margin) and **within the recommended range**, but exactly at its 5.5 V upper limit. ON may sit at 3.3 V GPIO level whatever VIN is (VIH min is 1 V). [source: TPS, p.4, §6.1 and §6.3]

G1-TPS22918-5. **[verified]** Electrical: RON is typically 52 mΩ at 5 V and 53 mΩ at 3.3 V. At 25 °C, the maximum is 59 mΩ at 5 V and 79 mΩ over -40 to 105 °C. Quiescent current is typically 8.7 µA at 5 V (max 16 µA). Shutdown current is typically 0.5 µA (max 4.5 µA at 5 V, 5 µA at 5.5 V). ON-pin leakage is at most 0.1 µA. ON hysteresis is typically 107 mV. RPD (QOD internal) is typically 24 Ω at 5 V (max 30 Ω), 25 Ω at 3.3 V (max 35 Ω) and 45 Ω at 1.8 V (max 60 Ω). [source: TPS, p.5, §6.5]

G1-TPS22918-6. **[verified]** Thermal: RθJA 183.2 °C/W, RθJB 34.1 °C/W. PD(max) = (125 °C - TA) / θJA. [source: TPS, p.4, §6.4; p.21, §11.3 Eq. 14]

**ON threshold / QOD / CT**

G1-TPS22918-7. **[verified]** ON is active high with a low threshold and works with GPIO levels of 1 V and up. It must be driven high or low and must not float. Neither the pin table nor §8.3.1 mentions an internal pull-down, so an external pull-down is needed if the GPIO can be Hi-Z, for example during ESP32 reset or boot (derived). [source: TPS, p.13, §8.3.1; p.3, Pin Functions]

G1-TPS22918-8. **[verified]** QOD options and resulting VOUT state when ON = L: QOD tied to VOUT gives discharge through RPD. QOD to VOUT through REXT gives discharge through RPD+REXT. QOD open leaves VOUT floating. With ON = H, VOUT = VIN in every QOD configuration. RQOD = RPD + REXT. The fall time follows VCAP = VIN·e^(-t/(RQOD·CL)). [source: TPS, p.13, §8.3.2 Eqs. 1-2; p.15, Table 4]

G1-TPS22918-9. **[verified]** Internal RPD limit: when QOD is tied directly to VOUT, the total load capacitance must be **at most 200 µF**. Above that, add REXT so that TJ stays at or below 125 °C. The output must not be actively driven during discharge. [source: TPS, p.14, §8.3.2.2]

G1-TPS22918-10. **[verified]** QOD fall times (90-10 %, QOD = VOUT, 25 °C): at 5 V, 43 µs with 1 µF, 200 µs with 10 µF and about 1.9 ms with 100 µF. At 3.3 V, 47 / 230 / 2150 µs. [source: TPS, p.13, Table 1]

G1-TPS22918-11. **[verified]** CT: slew rate SR [µs/V] ≈ 0.55 × CT [pF] + 30, valid for CT > 0. Rise time ≈ VIN × SR. Typical 10-90 % rise times at 5 V: CT 0 pF gives 135 µs, 220 pF gives 650 µs, 470 pF 1260 µs, 1000 pF 2540 µs, 2200 pF 5435 µs. At 3.3 V: 95 / 455 / 850 / 1680 / 3580 µs. [source: TPS, p.14, §8.3.3 Eq. 3 and Table 2]

G1-TPS22918-12. **[verified]** CT capacitor voltage rating: 10 V for VIN 1-1.2 V, 16 V for 1.2-4 V, **20 V for 4-5.5 V**. These guard against DC-bias capacitance loss. Table 2 was characterised with a 25 V X7R. [source: TPS, p.15, Table 3; p.14, Table 2 note]

G1-TPS22918-13. **[verified]** Switching at 5 V (CIN 1 µF, CL 0.1 µF, CT 1000 pF, RL 10 Ω): tON 1950 µs, tR 2540 µs, tD 690 µs, tOFF 2 µs. These hold only if VIN is already stable before ON goes high. If ON is applied before VIN, the VOUT slew rate is not controlled. [source: TPS, p.6, §6.6; p.20, §10]

G1-TPS22918-14. **[verified]** Inrush: I = CL × dVOUT/dt, where dVOUT is 80 % of VOUT for the 10-90 % rise time. [source: TPS, p.19, §9.2.2.5 Eq. 9]

**External components / placement**

G1-TPS22918-15. **[verified]** CIN: 1 µF ceramic (X5R/X7R) from VIN to GND, **as close to the pins as possible**. When switching heavy loads, use CIN about 10× CL. Add bulk capacitance if the source is more than a few inches away. [source: TPS, p.17, §9.2.2.1; p.20, §10 and §11.1]

G1-TPS22918-16. **[verified]** CL is optional, but **CIN should be larger than CL**. The NMOS has a body diode, so if CL > CIN, VOUT can rise above VIN when the supply is removed, and current then flows from VOUT back to VIN. The recommended CIN:CL ratio is 10:1. There is **no reverse-current blocking** (derived from the body-diode statement). [source: TPS, p.17, §9.2.2.2]

G1-TPS22918-17. **[verified]** Layout: VIN and VOUT traces short and wide, with caps close to the device. Wide VIN, VOUT and GND copper also lowers thermal impedance. The layout example uses a via to the power ground plane at GND. [source: TPS, pp.20-21, §11.1-11.3 and Figure 32]

**Polarity / orientation / land pattern**

G1-TPS22918-18. **[verified]** Pin 1 is marked by a pin-1 index area (shaded corner) on the package top. Pins 1-3 are on one side and 4-6 opposite, counter-clockwise from the top view. Leads 1-3 may be wider than 4-6 to show orientation. Body is 2.6-3.0 × 2.75-3.05 mm (with leads) and 1.45 mm max height. Pitch 0.95 mm, 1.9 mm between pins 1 and 3. Device marking: **13MW**. [source: TPS, PDF p.27, DBV0006A Package Outline and notes 4-5; PDF p.23, Package Option Addendum "Device Marking"]

G1-TPS22918-19. **[verified]** Land pattern (DBV0006A example): 6 pads of 1.1 × 0.6 mm. Row pitch 0.95 mm, pad-centre-to-pad-centre across the body 2.6 mm (ref). Non-solder-mask-defined (NSMD) pads are preferred, with the mask opening at most 0.07 mm around each pad. **No exposed or thermal pad.** [source: TPS, PDF p.28, Example Board Layout; PDF p.27]


**Added by Agent B (TPS22918)**

G1-TPS22918-A1. **[added]** RON at VIN = 4.2 V (fully charged LiPo on VSYS): 52 mΩ typ, 59 mΩ max at 25 °C, 71 mΩ max -40..85 °C, 79 mΩ max -40..105 °C. Quiescent at 3.3 V: 8.3 µA typ, 15 µA max. [TPS, p.5, §6.5]

G1-TPS22918-A2. **[added]** MSL Level 2, 260 °C peak; DBVR = 3000/reel; orderable marking 13MW (also for DBVT). Also exists as automotive TPS22918-Q1. [TPS, PDF p.23-24, Package Option Addendum]

G1-TPS22918-A3. **[added]** Power-sequencing: any order of VIN and ON is safe within abs max; ON before VIN only loses slew-rate control. [TPS, p.20, §10]

G1-TPS22918-A4. **[added]** Package body width (without leads) 1.45-1.75 mm; lead span 2.6-3.0 mm; length 2.75-3.05 mm; mold flash up to 0.25 mm per side not included. Example stencil based on 0.125 mm thickness. [TPS, PDF p.27 notes 3-5; PDF p.29]

---

### BSMD0805-050-6V (F1)

**Pinout / polarity**

G1-BSMD0805-1. **[verified]** Two-terminal 0805 (2012 metric) polymer PTC with end terminations. It is **non-polarised**: no polarity is defined, and the drawing shows two identical terminals. Body marking code for -050 parts is "**5**". [source: PTC, p.7, Physical Dimensions drawing; p.8, dimension table row BSMD0805-050-6V]

**Ratings**

G1-BSMD0805-2. **[verified]** (Rmin per p.3 vocabulary = un-soldered initial state; R1max = 1 h after trip or after 260 °C/20 s reflow) Electrical, 25 °C: Ihold 0.50 A, Itrip 1.00 A, Vmax 6 Vdc, Imax 40 A, Pd typ 0.5 W (tripped). Time to trip is at most 0.10 s at 8.00 A. Rmin 0.100 Ω (initial, before soldering). R1max 0.850 Ω, measured 1 h after tripping or after reflow. [source: PTC, p.2, Electrical Characteristics table]

G1-BSMD0805-3. **[verified]** Definitions: Ihold is the largest current the part carries without tripping in 25 °C still air. Itrip is the smallest current at which it trips. Vmax is the highest voltage it survives at Imax, and Imax the highest fault current it survives at Vmax. [source: PTC, p.3, definitions under table]

G1-BSMD0805-4. **[verified]** Hold-current derating for the -050 series: -40 °C 0.68 A, -20 °C 0.62 A, 0 °C 0.55 A, 25 °C 0.50 A, 40 °C 0.40 A, 50 °C 0.37 A, 60 °C 0.33 A, 70 °C 0.29 A, 85 °C 0.23 A. The derating curve is on p.4. [source: PTC, p.5, Thermal Derating Chart; p.4, Thermal Derating Curve]

G1-BSMD0805-5. **[verified]** Ambient operating range is -40 to +85 °C. Maximum surface temperature when tripped is 125 °C. [source: PTC, p.5, Environmental Specifications]

G1-BSMD0805-6. **[verified]** **5.5 V question:** 5.5 V (VBUS upper USB tolerance) is **within Vmax = 6 Vdc**, a margin of 0.5 V (8 %). The sheet gives no separate "recommended operating voltage". Vmax is the only voltage rating. Warning 3 says not to use the part where Vmax or Imax could be exceeded in a fault. [source: PTC, p.2 table; p.3 definitions; p.10, Warning item 3]

G1-BSMD0805-7. **[verified]** Voltage drop (derived): R1max 0.85 Ω × 0.5 A gives up to about 0.43 V across F1 at Ihold after a trip or reflow. At Rmin, 0.1 Ω × 0.5 A gives 0.05 V. [from PTC, p.2 values]

G1-BSMD0805-8. **[corrected]** (wording) Usage warnings: the part is not a switch, and repeated trips reduce the hold current. Keep it away from heat sources. The hold-current figures are 1-hour ratings after a single reflow, not long-term charge or discharge currents. Rework heat (extra soldering, potting) degrades the parameters. Hand soldering is not recommended, and a **heat gun is not allowed** during rework (stronger than "not recommended"). If an iron is used nearby, stay more than 1.5 mm away, below 350 °C, for no more than 3 s. [source: PTC, p.10, Warning items 1-6]

**Land pattern**

G1-BSMD0805-9. **[verified]** Recommended pads: two pads of 1.00 ± 0.1 mm (along the length) × 1.50 ± 0.1 mm, with a 1.20 ± 0.1 mm gap between them, giving about 3.2 mm overall (derived). Body for -050-6V: A (length) 2.00-2.30 mm, B (width) 1.20-1.50 mm, C (height) 0.50-1.10 mm, D (termination) at least 0.20 mm, E at least 0.10 mm. Reel quantity 5000. [source: PTC, p.7, Recommended Pad Layout drawing; p.8, table row BSMD0805-050-6V]

G1-BSMD0805-10. **[verified]** Reflow: 260 °C peak, 60-150 s above 217 °C, preheat 150-200 °C for 60-180 s, ramp up at most 3 °C/s, ramp down at most 6 °C/s. Recommended maximum paste thickness 0.25 mm. [source: PTC, p.6, Soldering Parameters]

G1-BSMD0805-11. **[verified]** No exposed pad and no thermal-via requirement: NOT FOUND in PTC, not applicable to a 2-terminal chip. [source: PTC, p.7]


**Added by Agent B (BSMD0805-050-6V)**

G1-BSMD0805-A1. **[added]** Moisture sensitivity grade 2 (sealed packaging; reseal leftovers). Storage 0-30 °C, 30-60 %RH. Reflow methods IR / vapour phase / hot air. [PTC, p.10 Warning 11; p.6]

G1-BSMD0805-A2. **[added]** Environmental drift: passive aging (85 °C, 1000 h) and humidity aging ±5 % typ; thermal shock (85/-40 °C ×20) ±33 % typ resistance change. [PTC, p.5, Environmental Specifications]

G1-BSMD0805-A3. **[added]** Do not expose to cleaning solvents/potting without verification (ethers, ketones, aromatic solvents named as harmful); allow 24 h for solvent residue to evaporate. [PTC, p.10 Warnings 7-8]

---

### Gaps / NOT FOUND
- NOT FOUND in MOD/HDG: EPAD thermal-via count or stencil pattern for the ESP32-C6-MINI-1 (only "soldering optional, mind the paste amount").
- NOT FOUND in MOD/HDG: an explicit "place the EN RC close to the pin" rule. Only "keep the CHIP_PU trace short".
- NOT FOUND in MOD: whether the Ø0.50 mm shield mark means pin 1. **[Agent B]** The mark is at the corner away from the antenna, not next to pin 1 (see G1-ESP32-33).
- Value of the EN pull-up R1 and capacitor C3 in MOD Figure 9-1 is "TBD". Only the text gives 10 kΩ / 1 µF.
- NOT FOUND in TPS: an internal pull-down on ON.
- NOT FOUND in PTC: a recommended operating voltage separate from Vmax, and a maximum initial resistance (only Rmin and R1max are given).

---

## Fact sheet G2 – VERIFIED – Motor driver, LDO, accelerometer, P-MOSFET

Agent B (independent verification), 2026-11-09. Every numbered item was checked against the PDFs (text layer via pdftotext -layout per page, figures/land patterns/pinout drawings visually at 300–800 dpi). Quick-answer table: all rows verified (DRV PDF p.5; AP p.3, p.8; LIS p.12, p.15; AO p.1).

Agent A (fact extraction), 2026-11-09. All facts are paraphrased from the documents named below. Page numbers are PDF page numbers; they match the printed page numbers in all four documents, except where "PDF p." is written (DRV8213 mechanical addendum).

Documents:
- [DRV] TI DRV8213 datasheet, SLVSGV9 (Aug 2023), `datasheets/DRV8213_datasheet_en.pdf`
- [AP] Diodes AP2112 datasheet, DS39724 Rev. 2-2 (Jun 2017), `datasheets/AP2112_datasheet_en.pdf`
- [LIS] ST LIS2DH12 datasheet, DocID025056 Rev 6 (May 2017), `datasheets/LIS2DH12_datasheet_LCSC.pdf`
- [AO] AOS AO3401A datasheet, Rev 3.1 (Dec 2023), `datasheets/AO3401A_datasheet_en.pdf`

Quick answer to the 5.5 V question:

| Part | Pin | Abs max | Recommended | 5.5 V within abs max? | 5.5 V within recommended range? |
|---|---|---|---|---|---|
| DRV8213DSG | VM | 12 V | 1.65–11 V | YES | YES |
| DRV8213DSG | IN1/IN2/GAINSEL (logic) | 5.75 V | 0–5.5 V | YES | YES (at the limit) |
| AP2112K-3.3 | VIN | 6.5 V | 2.5–6.0 V | YES | YES |
| AP2112K-3.3 | EN | NOT FOUND as a separate abs max; VIH max 6.0 V | – | (no separate rating) | YES (VIH max 6.0 V) |
| LIS2DH12 | Vdd / Vdd_IO | 4.8 V | 1.71–3.6 V | **NO** | **NO** – must run from 3V3 |
| AO3401A | VDS / VGS | -30 V / ±12 V | no ROC table in the doc | YES (both) | NOT FOUND (no ROC table) |

---

### DRV8213DSGR (U2)

**Pinout**

- **G2-DRV8213-1** **[verified]** The DSG package is WSON-8, 2.0 × 2.0 mm body, plus an exposed thermal pad (the land pattern numbers it pad 9). Top-view pin order: pins 1–4 run down the left side, pins 5–8 run up the right side (pin 8 is opposite pin 1). [source: DRV, p.3, Figure 6-1; PDF p.53–54, DSG0008A outline/land pattern]
- **G2-DRV8213-2** **[verified]** DSG pin table: Note: Table 6-1 lists PAD with pin number "—"; the number 9 exists only in the DSG0008A mechanical drawings (PDF p.53–55).

  | Pin | Name | Type | Function |
  |---|---|---|---|
  | 1 | VM | PWR | Motor supply, and the device's only supply in DSG. Bypass to GND with 0.1 µF ceramic plus bulk capacitance. |
  | 2 | OUT1 | O | H-bridge output to the motor |
  | 3 | OUT2 | O | H-bridge output to the motor |
  | 4 | GND | PWR | Device ground |
  | 5 | IN2 | I | Bridge control input, internal pulldown |
  | 6 | IN1 | I | Bridge control input, internal pulldown |
  | 7 | GAINSEL | I (tri-level) | Selects the IPROPI gain / current range: Low, High-Z or High |
  | 8 | IPROPI | PWR (analog out) | Current output proportional to the load current; needs a resistor to GND |
  | PAD (9) | Thermal pad | – | Connect to board ground. Use large GND planes on several layers and many vias nearby. |

  [source: DRV, p.3–4, Figure 6-1 and Table 6-1]
- **G2-DRV8213-3** **[verified]** These pins **do not exist on the DSG package**: nSLEEP, VREF, VCC, nFAULT, nSTALL, IMODE, SMODE, TINRUSH and PGND. They are RTE-only (WQFN-16). On the DSG, VREF is fixed internally at 510 mV and there is no sleep pin; sleep is entered automatically ("auto-sleep") when IN1 = IN2 = 0 for tAUTOSLEEP. The abs-max table lists "nSLEEP" among the logic pins, but no package in this datasheet has an nSLEEP pin. (This corrects the download note, which says the DSG pinout has VREF and nSLEEP.) [source: DRV, p.3–4, Table 6-1; p.5, section 7.1; p.11, section 8.1]

**Absolute maximum / recommended operating conditions**

- **G2-DRV8213-4** **[verified]** Abs max: VM -0.5 to 12 V. VCC -0.5 to 5.75 V (RTE only). Supply ramp on VM/VCC at most 2 V/µs. Logic pins (IN1, IN2, GAINSEL, …) -0.3 to 5.75 V. IPROPI: -0.3 to VVM + 0.3 V when VM < 5.45 V, or -0.3 to 5.75 V when VM ≥ 5.45 V. OUTx: -VSD to VVM + VSD. TA -40 to 125 °C, TJ -40 to 150 °C, Tstg -65 to 150 °C. [source: DRV, p.5, section 7.1] Note: the VREF abs-max row prints MIN as "0.3" (presumably -0.3, RTE only, irrelevant for DSG).
- **G2-DRV8213-5** **[verified]** Recommended: VVM (DSG) 1.65–11 V. Logic input voltage 0–5.5 V. fPWM 0–100 kHz. Peak OUTx current 0–4 A (power and thermal limits still apply). IPROPI output current 0–1 mA. VVREF up to min(3.3 V, VVM - 1.25 V), which matters for RTE only. TA -40 to 125 °C. [source: DRV, p.5–6, section 7.3]
- **G2-DRV8213-6** **[verified]** **5.5 V on VM is within abs max (12 V) AND within the recommended range (1.65–11 V).** 5.5 V on the IN pins is within abs max (5.75 V) and exactly at the recommended maximum (5.5 V). 3.3 V logic levels from the ESP32 are within range. [source: DRV, p.5, sections 7.1 and 7.3]
- **G2-DRV8213-7** **[corrected]** Label only: the 0–2 V/µs limit is the abs-max row "Power supply transient voltage ramp" (VM, VCC), not an ESD item; ESD is a separate table (7.2: HBM ±2000 V, CDM ±500 V). Value 2 V/µs and the hot-plug inference stand. [own ref: DRV p.5, 7.1 and 7.2]
  - original claim: The ESD/supply ramp limit of 2 V/µs on VM is an abs-max item. A hot-plug of USB or the battery through a switch with fast edges could exceed it unless VM has enough capacitance or a slew-controlled load switch. [source: DRV, p.5, section 7.1]
- **G2-DRV8213-8** **[verified]** Logic thresholds for IN1/IN2: VIL max 0.4 V, VIH min 1.45 V, hysteresis 40 mV, internal pulldown 200 kΩ typ. Tri-level thresholds (the table names only IMODE/SMODE): Low ≤ 0.4 V, High-Z 0.75–1.05 V, High ≥ 1.45 V. Tri-level pins have an 83 kΩ pulldown and a 10.5 µA pullup, which explains the mid-level when floating. The datasheet does not list GAINSEL thresholds separately; it describes GAINSEL only as a "tri-level input". [source: DRV, p.6–7, section 7.5] Note: in the PDF the symbol column of the tri-level rows is shifted (VTHYS/ITIL/ITIZ labels), the values are as stated. The 10.5 µA pull-up is specified "to VCC", which has no pin on DSG (internal rail).
- **G2-DRV8213-9** **[verified]** UVLO on VM (DSG): rising max 1.65 V, falling min 1.30 V, hysteresis 150 mV typ. Thermal shutdown 165/175/185 °C with 17 °C hysteresis. Fault retry 1.5 ms. [source: DRV, p.8, section 7.5]

**External components**

- **G2-DRV8213-10** **[verified]** Recommended parts: CVM1 = 0.1 µF low-ESR ceramic, VM to GND, VM-rated. CVM2 = bulk capacitor VM to GND, sized per section 10.1. RIPROPI = resistor from IPROPI to GND that sets the current-regulation level. (CVCC, CINRUSH, RnFAULT and RnSTALL apply to RTE only.) [source: DRV, p.13, Table 8-1]
- **G2-DRV8213-11** **[corrected]** Figure 9-1 content verified (VM 1.65–11 V, 100 nF + CBULK, IN1/IN2 from MCU PWM, IPROPI–RIPROPI–ADC, PPAD). But the 47 µF bulk value is NOT in the design-parameter table (Table 9-1, p.26, which lists no bulk capacitor); it appears only in the RTE schematic Figure 9-3 (p.27, 100 nF / 100 nF / 47 µF). [own ref: DRV p.26 Table 9-1, Fig. 9-1; p.27 Fig. 9-3]
  - original claim: Typical DSG circuit: VM 1.65–11 V with 100 nF plus CBULK. IN1/IN2 driven by MCU PWM pins. GAINSEL driven by the MCU (or strapped). IPROPI goes through RIPROPI to GND and is read by the MCU ADC. The thermal pad (PPAD) goes to GND. The design-example table (an RTE example) uses 47 µF bulk. [source: DRV, p.26, Figure 9-1; p.27, Figure 9-3]
- **G2-DRV8213-12** **[verified]** Layout: use X5R/X7R low-ESR ceramic for VM bypass. Place the VM bypass and bulk capacitors as close to the device as possible (small loop). Use wide copper for VM, OUT1, OUT2 and GND. [source: DRV, p.39, section 11.1]
- **G2-DRV8213-13** **[verified]** If transients last longer than the deglitch time, a 10 nF capacitor on IPROPI placed close to the device helps against false current-regulation triggering. Larger values slow down the regulation response. [source: DRV, p.17, section 8.4.2.2]
- **G2-DRV8213-14** **[verified]** The bulk capacitor's voltage rating should exceed the operating voltage, because the motor can push energy back into the supply. TI gives no fixed value; size it by system test. [source: DRV, p.38, section 10.1]

**IPROPI / GAINSEL / ITRIP / sleep**

- **G2-DRV8213-15** **[verified]** IPROPI current = (ILS1 + ILS2) × AIPROPI. Only low-side FET current flowing drain to source is counted. In coast (High-Z), the current cannot be sensed. It is sensed in drive and in brake (slow decay). VIPROPI = IIPROPI × RIPROPI. [source: DRV, p.15–16, Equations 1 and 2, section 8.4.2.1]
- **G2-DRV8213-16** **[verified]** GAINSEL settings:

  | GAINSEL | AIPROPI | Recommended range | Low-side RDS(on) typ | Min OCP |
  |---|---|---|---|---|
  | Low | 205 µA/A | 350 mA–2 A | 120 mΩ | 4 A |
  | High-Z | 1050 µA/A | 60–350 mA | 460 mΩ | 0.8 A |
  | High | 4900 µA/A | 10–60 mA | 2100 mΩ | 0.16 A |

  Mirror error is ±6 % in each range. GAINSEL also changes the low-side RDS(on) and the OCP trip point, not only the sense gain. [source: DRV, p.15, Table 8-3; p.7, section 7.5 (AIPROPI, AERR, RDS(ON)_LS); p.8 (IOCP)]
- **G2-DRV8213-17** **[verified]** ITRIP (the current-regulation chopping threshold): ITRIP × AIPROPI = VVREF / RIPROPI, and on the DSG VVREF is fixed at 510 mV (470–550 mV). So ITRIP = 0.51 V / (RIPROPI × AIPROPI). My examples (not from the datasheet): GAINSEL Low with RIPROPI 1.24 kΩ gives about 2.0 A. GAINSEL High-Z with 1.0 kΩ gives about 0.49 A. GAINSEL Low with 2.49 kΩ gives about 1.0 A. Above ITRIP, the bridge brakes (slow decay) for tOFF = 20 µs, with tBLANK 1.8 µs and tDEG 2 µs. [source: DRV, p.17, Equation 3, section 8.4.2.2; p.7–8, section 7.5 (VREF_INT, tOFF, tBLANK, tDEG)]
- **G2-DRV8213-18** **[verified]** The IPROPI voltage clamp is tied to VVREF, which is 510 mV on the DSG. TI recommends at least 1.25 V headroom between VVM and the largest VIPROPI the ADC has to measure. On the DSG, VIPROPI ≈ 0.51 V is where regulation starts, so the useful ADC range is about 0–0.5 V. The datasheet has no IMODE equivalent on the DSG: it does not state that DSG current regulation can be disabled. Fig. 8-1 (DSG block diagram) shows the VREF/IPROPI comparator permanently present. **NOT FOUND in DRV:** an explicit statement that DSG regulation is always on, or how to disable it. Consequence (inference): a very large or missing RIPROPI makes ITRIP tiny, so IPROPI must always have a resistor of the right size. [source: DRV, p.16, section 8.4.2.1; p.12, Figure 8-1; p.17]
- **G2-DRV8213-19** **[verified]** Bridge truth table: IN1/IN2 = 0/0 → both outputs High-Z (coast), and the device enters sleep after tAUTOSLEEP. 0/1 → reverse (OUT1 L, OUT2 H). 1/0 → forward (OUT1 H, OUT2 L). 1/1 → brake (both low-side on). Recommended PWM is drive/brake alternation. The IN pins may be driven before VM is present. [source: DRV, p.14, Table 8-2, section 8.4.1]
- **G2-DRV8213-20** **[verified]** Sleep/wake: auto-sleep after IN1 = IN2 = 0 for 0.7–1.3 ms (DSG). Sleep current 20 nA typ, 60 nA max (VM = 5 V, 27 °C). Wake after 250 µs max (tWAKE) once any IN goes high. Active VM current 1.2 mA typ, 1.9 mA max. Charge pump at 6 MHz with internal capacitors, so no external charge-pump parts are needed. [source: DRV, p.6, section 7.5; p.23, sections 8.5.1–8.5.2]
- **G2-DRV8213-21** **[verified]** OCP is independent of IPROPI/VREF. Both high-side and low-side FETs are monitored. Deglitch tOCP is 4.2 µs, then auto-retry after 1.5 ms. TSD also auto-retries. Hardware stall detection is RTE-only; on the DSG, stall detection is done in software through IPROPI and the MCU ADC. [source: DRV, p.22, section 8.4.4; p.27, section 9.2.1.3]
- **G2-DRV8213-22** **[verified]** H-bridge RDS(on): HS 120 mΩ typ (280 max). LS 120/460/2100 mΩ typ depending on GAINSEL. Body diode VSD 0.9 V. Rise/fall time 70/40 ns. Propagation delay 450 ns. Dead time 500 ns. [source: DRV, p.7, section 7.5]

**Polarity / pin 1**

- **G2-DRV8213-23** **[corrected]** Content verified (pin-1 index area dotted on top, 45° × 0.25 chamfer on the exposed pad at pin 1, marking "8213", DRV8213DSGR 3000 pcs large T&R, MSL Level-1-260C-UNLIM, -40 to 125 °C), but the Package Option Addendum is PDF p.49 ("Addendum-Page 1"), not p.48 (p.48 is the tape-and-reel box dimensions table). [own ref: DRV PDF p.49; PDF p.53]
  - original claim: On the top side, pin 1 is a dotted "pin 1 index area" in one corner. On the bottom, the exposed pad has a 45° × 0.25 mm chamfer on the pin-1 corner. Device marking is "8213". Orderable part: DRV8213DSGR, 3000 pcs T&R, MSL 1 / 260 °C, -40 to 125 °C. [source: DRV, PDF p.53, DSG0008A outline; p.48 (PDF), Package Option Addendum]

**Land pattern / thermal pad**

- **G2-DRV8213-24** **[verified]** Package: 2.0 × 2.0 mm (±0.1), 0.7–0.8 mm high, pitch 0.5 mm. Terminals 0.18–0.32 mm wide and 0.2–0.4 mm long. Exposed pad 0.9 ± 0.1 × 1.6 ± 0.1 mm. [source: DRV, PDF p.53, DSG0008A Package Outline]
- **G2-DRV8213-25** **[corrected]** Minor: for the preferred non-solder-mask-defined pads the mask opening is 0.07 mm MAX all around the copper (the 0.07 mm MIN applies to the SMD variant, mask over metal). All other values verified: pads (0.5) × (0.25), 0.5 pitch, rows (1.9) centre-to-centre, thermal land (0.9) × (1.6), two optional Ø0.2 vias at (0.55) from centre, R0.05 corners, note 5 on filled/plugged/tented vias. [own ref: DRV PDF p.54]
  - original claim: Example land pattern: pads 0.5 × 0.25 mm at 0.5 mm pitch. Pad rows at 1.9 mm center-to-center. Thermal land 0.9 × 1.6 mm with two optional Ø0.2 mm vias at ±0.55 mm from center along the long axis. Non-solder-mask-defined pads are preferred, with a 0.07 mm mask opening all around. Vias are optional; if used, fill, plug or tent them when they sit under paste. [source: DRV, PDF p.54, Example Board Layout, notes 4–5]
- **G2-DRV8213-26** **[verified]** Stencil: 0.125 mm thick, with the thermal pad split into two apertures giving 87 % paste coverage. [source: DRV, PDF p.55, Example Stencil Design]
- **G2-DRV8213-27** **[verified]** The thermal pad **must be soldered** to the PCB. Connect it to the GND plane on top (and inner layers) with thermal vias and as much copper as possible. RθJA (JEDEC) is 65.9 °C/W, RθJB 28.7 °C/W, RθJC(bot) 12.0 °C/W. TI's own simulation used only 2 vias (0.3 mm, 1.2 mm spacing) under the pad. [source: DRV, PDF p.53 note 3; p.39, section 11.1; p.6, section 7.4; p.32–33, section 9.2.1.5]

---

### AP2112K-3.3TRG1 (U3)

**Pinout**

- **G2-AP2112K-1** **[verified]** In the part number, "K" means the SOT25 package (Diodes' new name for SOT-23-5). The other packages are M = SO-8 and R5/R5A = SOT89-5. (Note: the download note says "S" for SO-8; the ordering table actually says **M**.) The 3.3 V SOT25 part is AP2112K-3.3TRG1, marking ID **G3P**, 3000 pcs on a 7" reel, -40 to +85 °C. [source: AP, p.12, Ordering Information]
- **G2-AP2112K-2** **[verified]** SOT25 (K) pinout, top view:

  | Pin | Name | Function |
  |---|---|---|
  | 1 | VIN | Input voltage |
  | 2 | GND | Ground |
  | 3 | EN | Chip enable; High = on, Low = output off |
  | 4 | NC | No connection |
  | 5 | VOUT | Output voltage |

  Pins 1–3 are on one long side and pins 4–5 on the other, with pin 5 opposite pin 1. [source: AP, p.1, Pin Assignments (SOT25); p.2, Pin Descriptions]
- **G2-AP2112K-3** **[verified]** The pin order is different on the other packages, so a footprint or symbol from another variant is wrong for K. SO-8: 1 VOUT, 2/3/4 NC, 5 EN, 6/7 GND, 8 VIN. SOT89-5 R5: 1 NC, 2 GND, 3 EN, 4 VIN, 5 VOUT. SOT89-5 R5A: 1 EN, 2 GND, 3 NC, 4 VIN, 5 VOUT. Watch out: the common "SOT-23-5 LDO" pinout used by several other vendors (1 VIN, 2 GND, 3 EN, 4 NC/BYP, 5 VOUT) matches the AP2112K, but some other LDO families (for example ones with VOUT on pin 1) do not. Check against this table only. [source: AP, p.1–2, Pin Assignments and Pin Descriptions] Note: the remark about other vendors' SOT-23-5 LDO pinouts is general knowledge, not from the AP datasheet; the AP2112 pinouts for SOT25, SO-8, R5 and R5A are verified against p.1–2.

**Absolute maximum / recommended operating conditions**

- **G2-AP2112K-4** **[verified]** Abs max: VCC (supply) 6.5 V. TJ +150 °C. Tstg -65 to +150 °C. Lead temperature 260 °C for 10 s. ESD 400 V MM / 4000 V HBM. θJA SOT25 184 °C/W (no heatsink). No separate abs-max rating is given for EN. [source: AP, p.3, Absolute Maximum Ratings]
- **G2-AP2112K-5** **[verified]** Recommended: VIN 2.5–6.0 V, TA -40 to +85 °C. [source: AP, p.3, Recommended Operating Conditions]
- **G2-AP2112K-6** **[verified]** **5.5 V on VIN is within abs max (6.5 V) AND within the recommended range (2.5–6.0 V).** EN high is specified from 1.5 V up to 6.0 V, so EN tied to VIN at 5.5 V is allowed. [source: AP, p.3; p.8, AP2112-3.3 Electrical Characteristics (VIH)]
- **G2-AP2112K-7** **[verified]** 3.3 V version, measured at VIN = 4.3 V: VOUT 3.3 V ±1.5 % (1–30 mA). IOUT(max) at least 600 mA. Dropout 5/8 mV at 10 mA, 125/200 mV at 300 mA and 250/400 mV at 600 mA (typ/max). IQ 55 µA typ, 80 µA max. Standby current 0.01 µA typ, 1 µA max. Line regulation is specified for 4.3–6 V. Short-circuit (foldback) current 50 mA. Start-up 20 µs. OTSD 160 °C with 25 °C hysteresis. θJC (SOT25) 96 °C/W. [source: AP, p.8, AP2112-3.3 Electrical Characteristics]
- **G2-AP2112K-8** **[verified]** Relevance for VSYS 3.0–5.5 V (my inference from G2-AP2112K-7): below about 3.3 V + VDROP (≈3.5–3.7 V at 300–600 mA), the output is in dropout and follows VIN minus the dropout. At a battery voltage of 3.0–3.5 V, 3V3 will be below 3.3 V. [source: AP, p.8 (VDROP)]
- **G2-AP2112K-9** **[verified]** Thermal (my calculation from the datasheet's θJA of 184 °C/W): at 5.5 V in and 3.3 V out, dissipation is 2.2 V × IOUT. TJ = 150 °C at TA = 25 °C allows about 0.68 W, i.e. about 0.31 A continuous, and less at higher TA. OTSD (160 °C) protects the part. [source: AP, p.3 (θJA, TJ); p.8 (TOTSD)]

**External components**

- **G2-AP2112K-10** **[verified]** Typical circuit: CIN = 1 µF on VIN and COUT = 1 µF on VOUT, both to GND. If 1 µF ceramics are used, X7R or X5R dielectric is recommended. The part is stable with 1 µF ceramic, tantalum or aluminium electrolytic. [source: AP, p.2, Typical Applications Circuit and Note 4; p.1, Features]
- **G2-AP2112K-11** **[verified]** EN has an internal 3 MΩ pull-down, so a floating EN means the regulator is off. VIH min 1.5 V, VIL max 0.4 V. With EN low, VOUT is discharged through 60 Ω (auto discharge). [source: AP, p.8 (RPD, VIH/VIL, RDCHG); p.1, Description]
- **G2-AP2112K-12** **[verified]** Application note: if a load already draws current from the output before the part is enabled (for example a current source, or a back-feed from another supply), the foldback current limit can stop the part from starting. With a normal resistive load there is no problem. [source: AP, p.11, Application Note]
- **G2-AP2112K-13** **[verified]** NOT FOUND in AP: explicit capacitor placement or distance rules, or other layout guidance (only the typical circuit is given).

**Polarity / pin 1**

- **G2-AP2112K-14** **[verified]** The SOT25 marking is the Diodes logo plus "G3P". The marking drawing shows no pin-1 dot; pin 1 is found from the package outline (3-lead side, pin 1 at the end opposite pin 4). NOT FOUND in AP: an explicit pin-1 marker on the SOT25 package. [source: AP, p.13, Marking Information (1) SOT25; p.1, Pin Assignments] Addition: in the marking drawing the 2-lead side is up and the 3-lead side down with the text upright; per the top-view pin assignment pin 1 (VIN) is then bottom-left, pin 3 (EN) bottom-right, pin 4 (NC) top-right, pin 5 (VOUT) top-left – inferred, no marker.

**Land pattern**

- **G2-AP2112K-15** **[verified]** SOT25 package: body 1.50–1.70 × 2.90–3.10 mm, 2.70–3.00 mm over leads, pitch 0.95 mm, leads 0.35–0.50 mm wide, height 1.00–1.30 mm. Suggested pad layout: Z = 3.20, G = 1.60, X = 0.55, Y = 0.80, C1 = 2.40 (pad-row center spacing), C2 = 0.95 (pitch), all in mm. Add 0.2 mm to Z for wave soldering. There is no exposed pad. [source: AP, p.14, Package Outline Dimensions and Suggested Pad Layout (SOT25)]

---

### LIS2DH12TR (U4)

**Pinout**

- **G2-LIS2DH12-1** **[verified]** Package: LGA-12, 2.0 × 2.0 × 1.0 mm (max height). Pin table:

  | Pin | Name | Function |
  |---|---|---|
  | 1 | SCL / SPC | I2C clock / SPI clock |
  | 2 | CS | Mode select: 1 = I2C enabled (SPI idle), 0 = SPI enabled (I2C off) |
  | 3 | SDO / SA0 | SPI data out / I2C address LSB; internal pull-up |
  | 4 | SDA / SDI / SDO | I2C data / SPI data in / 3-wire data out |
  | 5 | Res | Connect to GND |
  | 6 | GND | 0 V |
  | 7 | GND | 0 V |
  | 8 | GND | 0 V |
  | 9 | Vdd | Power supply |
  | 10 | Vdd_IO | I/O supply |
  | 11 | INT2 | Interrupt 2 |
  | 12 | INT1 | Interrupt 1 |

  There is no exposed pad. [source: LIS, p.9, Table 2; p.8, Figure 2; p.49, Figure 12]
- **G2-LIS2DH12-2** **[verified]** Pad layout as seen from the bottom (Figure 12): the top row from left to right is 10, 11, 12, 1. The right column from top is 1, 2, 3, 4. The bottom row from right is 4, 5, 6, 7. The left column from bottom is 7, 8, 9, 10. Pins 1, 4, 7 and 10 are the corners. In **top view** this is mirrored: pin 1 is top-left. [source: LIS, p.49, Figure 12 (bottom view); p.8, Figure 2]

**Absolute maximum / recommended operating conditions**

- **G2-LIS2DH12-3** **[verified]** Abs max: Vdd -0.3 to 4.8 V. Vdd_IO -0.3 to 4.8 V. Control pins (CS, SCL, SDA, SA0) -0.3 to Vdd_IO + 0.3 V. Shock 3000 g / 0.5 ms and 10000 g / 0.2 ms. TOP -40 to +85 °C. Tstg -40 to +125 °C. ESD 2 kV HBM. The datasheet states that no pin may ever see more than 4.8 V. [source: LIS, p.15, Table 9 and note]
- **G2-LIS2DH12-4** **[verified]** Operating: Vdd 1.71–3.6 V (2.5 V typ; factory-calibrated at 2.5 V). Vdd_IO 1.71 V to Vdd + 0.1 V. Top -40 to +85 °C. VIH ≥ 0.8 × Vdd_IO, VIL ≤ 0.2 × Vdd_IO, VOH ≥ 0.9 × Vdd_IO, VOL ≤ 0.1 × Vdd_IO. Current: 2 µA at 1 Hz ODR and 11 µA at 50 Hz in normal mode, 0.5 µA in power-down. [source: LIS, p.12, Table 6 and footnote c]
- **G2-LIS2DH12-5** **[verified]** **5.5 V on Vdd or Vdd_IO is NOT within abs max (4.8 V) and NOT within the recommended range (≤ 3.6 V).** The LIS2DH12 must run from 3V3. Vdd_IO must not be higher than Vdd + 0.1 V. Any pull-up on CS, SDA, SCL, SA0 or the INT lines must go to a rail at or below Vdd_IO + 0.3 V, so 3V3, never VSYS or VBUS. [source: LIS, p.12, Table 6; p.15, Table 9]
- **G2-LIS2DH12-6** **[verified]** All supplies and grounds should be present at the same time. Vdd may be removed while Vdd_IO stays up without blocking the bus; the measurement chain is then off. [source: LIS, p.20, section 4; p.12, Table 6 note 2]

**External components**

- **G2-LIS2DH12-7** **[verified]** Decoupling: 100 nF ceramic plus 10 µF aluminium, as close as possible to pin 9 (Vdd). Figure 5 also shows a separate 100 nF on Vdd_IO (pin 10). [source: LIS, p.20, section 4 and Figure 5]
- **G2-LIS2DH12-8** **[verified]** I2C needs external pull-up resistors on SDA and SCL to Vdd_IO. Standard (100 kHz) and fast mode (400 kHz) are supported. [source: LIS, p.24, section 6.1; p.14, Table 8]
- **G2-LIS2DH12-9** **[verified]** Pin 5 (Res) must be connected to GND. [source: LIS, p.9, Table 2]

**I2C mode, address, interrupts**

- **G2-LIS2DH12-10** **[verified]** I2C mode: tie CS high (to Vdd_IO). CS = 0 enables SPI and disables I2C. CS has no internal pull: by default it is a high-impedance input, so it must be driven or tied. [source: LIS, p.20, section 4; p.24, section 6; p.21, Table 13]
- **G2-LIS2DH12-11** **[verified]** I2C 7-bit address is 001100x: **SA0 = 0 (to GND) gives 0x18; SA0 = 1 (to supply) gives 0x19.** As 8-bit read/write bytes: 0x30/0x31 for SA0 = 0 and 0x32/0x33 for SA0 = 1. [source: LIS, p.25, section 6.1.1 and Table 16]
- **G2-LIS2DH12-12** **[verified]** SDO/SA0 has an internal pull-up (typ. 54.4 kΩ at 1.7 V, 49.2 kΩ at 1.8 V, 30.4 kΩ at 2.5 V, 20.4 kΩ at 3.6 V Vdd_IO). If SA0 is left floating, the address is 0x19. If SA0 is tied to GND, the pull-up draws about 3.3 V / ~22 kΩ ≈ 150 µA continuously (my estimate) unless it is disabled by writing 0x90 to CTRL_REG0 (0x1E). Bits 0–6 of CTRL_REG0 must keep their default value (0x10). [source: LIS, p.9, Table 3; p.21, Table 13 note 1; p.33, Tables 25–26]
- **G2-LIS2DH12-13** **[verified]** WHO_AM_I (0x0F) reads 0x33. [source: LIS, p.33, Table 24; p.31, Table 21]
- **G2-LIS2DH12-14** **[verified]** Interrupt polarity is set by bit 1 of CTRL_REG6 (0x25), named **INT_POLARITY** in this datasheet (other ST parts call it H_LACTIVE). Default 0 = active-high, 1 = active-low. It applies to INT1 and INT2 together. CTRL_REG6 resets to 0x00. Register bit layout: b7 I2_CLICK, b6 I2_IA1, b5 I2_IA2, b4 I2_BOOT, b3 I2_ACT, b2 –, b1 INT_POLARITY, b0 –. [source: LIS, p.38, Tables 42–43; p.31, Table 21]
- **G2-LIS2DH12-15** **[verified]** INT1 and INT2 are push-pull outputs, driven to GND by default. No open-drain option appears in Table 13. Latching of INT1 is set by LIR_INT1 in CTRL_REG5 (0x24). [source: LIS, p.21, Table 13; p.38, Table 41]

**Polarity / pin 1 / land pattern**

- **G2-LIS2DH12-16** **[verified]** On the top side, a dot marks the pin-1 corner. On the bottom, pad 1 has a chamfered corner ("Pin 1 indicator"). The soldering note says to leave the "Pin 1 indicator" unconnected when soldering. [source: LIS, p.8, Figure 2; p.49, Figure 12; p.21, section 4.1]
- **G2-LIS2DH12-17** **[verified]** Package dimensions: L = W = 2.00 ± 0.15 mm, H = 1.0 mm max. Pad pitch 0.5 mm, 1.5 mm between outer pad centers. Pads are about 0.25 × 0.275 mm, 0.1 mm from the package edge. General tolerance ±0.1 mm. There is no exposed or thermal pad. [source: LIS, p.49, Figure 12 (read from the drawing at 400 dpi)]
- **G2-LIS2DH12-18** **[verified]** NOT FOUND in LIS: a recommended PCB land pattern. The datasheet only refers to www.st.com for land pattern and soldering recommendations. Soldering heat resistance is per JEDEC J-STD-020. [source: LIS, p.21, section 4.1]

---

### AO3401A (Q1, Q101)

**Pinout**

- **G2-AO3401A-1** **[verified]** Package SOT23. Top-view drawing: the single lead on one side is **D**. On the opposite side, the lead next to the dot is **G** and the other is **S**. The drawing labels leads only by name, not by number. Assuming the standard JEDEC SOT-23 numbering (pin 1 at the dot, pin 2 beside it, pin 3 the single lead), the order is **1 = G, 2 = S, 3 = D**. NOT FOUND in AO: explicit pin numbers. [source: AO, p.1, SOT23 Top View / Bottom View drawing] Visual check (300/800 dpi): top view shows the dot beside the G lead; G and S share one side, D is alone opposite – consistent with 1 = G, 2 = S, 3 = D.
- **G2-AO3401A-2** **[corrected]** Symbol and diode direction verified: the drawn body diode has its anode at D and cathode at S (conducts D→S), consistent with a P-channel device. The consequence sentence is wrong as a general rule: in a high-side load switch S goes to the supply and D to the load (body diode then blocks supply→load when off); in a P-FET reverse-polarity / ideal-diode circuit the FET is deliberately mounted the other way round (D to the source/battery side, S to the protected rail) so the body diode conducts in the forward direction and the FET bypasses it. Check orientation per circuit function, not by the rule "S faces the blocked side". [own ref: AO p.1 schematic symbol; p.2 VSD]
  - original claim: Symbol: P-channel enhancement MOSFET, D at the top and S at the bottom, with the body diode drawn across D–S. For a P-channel FET, the body diode's anode is at D and its cathode at S, so it conducts from D to S. The body-diode spec (VSD -0.7 V typ at IS = -1 A) is consistent with that. Consequence: in a load-switch or reverse-polarity circuit, S must face the side that has to be blocked when the FET is off; if D and S are swapped, the FET leaks through the body diode. [source: AO, p.1, schematic symbol; p.2, VSD]

**Absolute maximum / ratings**

- **G2-AO3401A-3** **[verified]** Abs max (TA = 25 °C): VDS -30 V. VGS ±12 V. ID -4.0 A (25 °C) / -3.2 A (70 °C). IDM -27 A. PD 1.4 W (25 °C) / 0.9 W (70 °C). TJ and Tstg -55 to 150 °C. RθJA 70/90 °C/W (t ≤ 10 s), 100/125 °C/W steady state (typ/max). RθJL 63/80 °C/W. [source: AO, p.1, Absolute Maximum Ratings and Thermal Characteristics]
- **G2-AO3401A-4** **[verified]** **5.5 V across D-S is within abs max (|VDS| 30 V). A gate pulled to GND with the source at up to 5.5 V gives VGS = -5.5 V, within abs max (±12 V).** NOT FOUND in AO: a recommended operating conditions table, so "within recommended range" cannot be answered from the document. The RDS(on) specs at -4.5 V and -2.5 V cover the gate-drive range used here. [source: AO, p.1]
- **G2-AO3401A-5** **[verified]** Electrical (TJ = 25 °C): BVDSS ≥ -30 V. IDSS ≤ -1 µA (-5 µA at 55 °C). IGSS ±100 nA at ±12 V. VGS(th) -0.5 / -0.9 / -1.3 V (min/typ/max). RDS(on): 41/50 mΩ at -10 V, 47/60 mΩ at -4.5 V, 60/85 mΩ at -2.5 V (typ/max). Body diode VSD -0.7 V typ / -1 V max at 1 A, IS max -2 A. Ciss 645 pF. Qg 7 nC at 4.5 V. Rg 4–12 Ω. [source: AO, p.2, Electrical Characteristics] Note: IDSS units print as "mA" in the text layer (symbol-font µ), the value is -1 µA / -5 µA. Qg(4.5V) 7 nC is listed under the VGS = -10 V, VDS = -15 V, ID = -4 A test-condition block.
- **G2-AO3401A-6** **[verified]** Relevance (my inference): at the lowest VSYS of 3.0 V, VGS ≈ -3.0 V is between the -2.5 V and -4.5 V test points, so RDS(on) is roughly 60–85 mΩ max. The gate turns on well (VGS(th) max is -1.3 V). [source: AO, p.2; p.3, Figure 5]

**External components**

- **G2-AO3401A-7** **[verified]** NOT FOUND in AO: recommended external parts (gate resistor, gate pull-up). The datasheet gives only characteristics and test circuits. [source: AO, p.1–5]

**Polarity / pin 1 / land pattern**

- **G2-AO3401A-8** **[verified]** The top-view drawing shows a dot near the G lead (pin-1 corner) and the AOS logo on top. NOT FOUND in AO: the device marking code. [source: AO, p.1, SOT23 drawing]
- **G2-AO3401A-9** **[verified]** NOT FOUND in AO: package dimensions and recommended land pattern (the 5-page datasheet has no mechanical page; AOS publishes them separately). There is no exposed pad. [source: AO, p.1–5]

---

### Discrepancies with the download notes (for the verifier)

1. DRV8213 DSG has **no nSLEEP pin and no VREF pin**. Sleep is automatic (IN1 = IN2 = 0 for about 1 ms), and VREF is fixed at 510 mV internally (G2-DRV8213-3).
2. In the AP2112 ordering code, SO-8 is "M", not "S" (G2-AP2112K-1). This does not affect the K part.
3. The LIS2DH12 polarity bit is called INT_POLARITY (CTRL_REG6 bit 1), not H_LACTIVE. Its default 0 = active-high (G2-LIS2DH12-14).
4. AO3401A pin numbers are inferred from the standard SOT-23 convention; the datasheet labels leads only by name (G2-AO3401A-1).

---

### Added items (wiring-review relevant, not in Agent A's sheet)

### DRV8213DSGR
- **G2-DRV8213-A1** **[added]** GAINSEL High-Z from a floating MCU pin: the tri-level input has an internal 83 kΩ pull-down and a 10.5 µA pull-up, so left open it settles around 10.5 µA × 83 kΩ ≈ 0.87 V (my calculation), inside the 0.75–1.05 V High-Z window. An ESP32 GPIO used for GAINSEL must be truly Hi-Z (input, no internal pull-up/down) to select High-Z; any external resistor or GPIO pull shifts this level. Thresholds are only tabulated for IMODE/SMODE; GAINSEL is assumed to share them. [source: DRV p.7, 7.5 tri-level inputs; p.4 Table 6-1 GAINSEL "tri-level input"]
- **G2-DRV8213-A2** **[added]** INx input current: IIH 15–35 µA at VINx = 5 V; IIL ±1 µA at 0 V; 50 ns input deglitch. Negligible load for ESP32 GPIOs. [source: DRV p.6–7, 7.5]
- **G2-DRV8213-A3** **[added]** The ±6 % IPROPI accuracy (AERR) is specified only for VIPROPI ≤ min(VVM − 1.25 V, 3.3 V); example in text: VVM = 3.3 V → good accuracy up to 2.05 V. On DSG the 510 mV clamp/ITRIP is the practical ceiling anyway. [source: DRV p.7, 7.5 AERR rows; p.16, 8.4.2.1]
- **G2-DRV8213-A4** **[added]** DSG UVLO behaviour: VVM < 1.65 V → UVLO, IPROPI not available; 1.65 V to VVM_MAX → normal operation. UVLO deglitch tUVLO 10 µs; in UVLO all logic is reset. [source: DRV p.22, 8.4.4.3; p.23, Table 8-7; p.8, 7.5]
- **G2-DRV8213-A5** **[added]** ESD: HBM ±2000 V, CDM ±500 V (motor leads leaving the board may need external protection – inference). [source: DRV p.5, 7.2]
- **G2-DRV8213-A6** **[added]** Thermal-via guidance: section 11.1 says to tie the thermal pad to the top-layer and internal ground planes through thermal vias, maximise copper on the pad, and use the via positions from the package drawing (two Ø0.2 mm vias at ±0.55 mm). [source: DRV p.39, 11.1; PDF p.54]
- **G2-DRV8213-A7** **[added]** Brake/slow-decay with IPROPI: in brake, IPROPI reflects the current in only one low-side FET (the other conducts source→drain and counts as zero), so the reading still equals the motor current. During coast it reads zero. [source: DRV p.15, 8.4.2.1 paragraph before Eq. 1; p.16]

### AP2112K-3.3TRG1
- **G2-AP2112K-A1** **[added]** The functional block diagram confirms the 3 MΩ EN pull-down to GND and gives the SOT25 pin numbers in square brackets: EN [3], VIN [1], VOUT [5], GND [2]. [source: AP p.2, Functional Block Diagram]
- **G2-AP2112K-A2** **[added]** NOT FOUND in AP: any reverse-current / reverse-battery protection statement (no "reverse" in the document). If VOUT can be held up while VIN collapses (e.g. 3V3 back-fed via USB-UART or a debug probe), the AP datasheet gives no guarantee; treat as unprotected. [source: full-text search of AP, all 18 pages]
- **G2-AP2112K-A3** **[added]** Line regulation and IOUT(max) for the 3.3 V version are specified at VIN = 4.3 V (IOUT(max) ≥ 600 mA with VOUT 3.251–3.350 V); no guaranteed output tolerance is given for VIN below 4.3 V other than via the dropout spec. [source: AP p.8]

### LIS2DH12TR
- **G2-LIS2DH12-A1** **[added]** With Vdd_IO = 3.3 V the logic thresholds become VIH ≥ 2.64 V, VIL ≤ 0.66 V (calculated from 0.8/0.2 × Vdd_IO). ESP32 3.3 V push-pull and I2C pull-ups to 3V3 satisfy this; pull-ups to a lower rail would not. [source: LIS p.12, Table 6]
- **G2-LIS2DH12-A2** **[added]** INT1/INT2 are push-pull by default (driven to GND), so they need no pull-up and must not be wire-ORed with other open-drain IRQ lines. Their high level is referenced to Vdd_IO. [source: LIS p.21, Table 13; p.12 VOH]
- **G2-LIS2DH12-A3** **[added]** Figure 5 reference connection (visually checked): RES (pin 5) and GND pins 6/7/8 all tied to GND; Vdd_IO (10) with 100 nF; Vdd (9) with 10 µF + 100 nF; CS driven by the controller in the drawing (for I2C it must be tied high, p.20 text). [source: LIS p.20, Figure 5]
- **G2-LIS2DH12-A4** **[added]** I2C timing (fast mode): fSCL ≤ 400 kHz, tLOW ≥ 1.3 µs, tHIGH ≥ 0.6 µs, data hold 0–0.9 µs; measured at 0.2/0.8 × Vdd_IO. [source: LIS p.14, Table 8]
- **G2-LIS2DH12-A5** **[added]** Low-power mode current 6 µA typ at 50 Hz ODR (in addition to the normal-mode values in item 4). [source: LIS p.12, Table 6]

### AO3401A
- **G2-AO3401A-A1** **[added]** The PD ratings (1.4 W / 0.9 W) are based on the t ≤ 10 s RθJA; RθJA itself is measured on 1 in² of 2 oz copper on FR-4. For steady state use RθJA 125 °C/W max → about 1.0 W at 25 °C (my calculation), less on a small board with minimal copper. [source: AO p.2, notes A, B, D; p.1 Thermal Characteristics]
- **G2-AO3401A-A2** **[added]** Dynamic data for gate-drive sizing: Ciss 645 pF, Coss 80 pF, Crss 55 pF at VDS = -15 V; Qg 14 nC (10 V) / 7 nC (4.5 V); switching at RGEN 3 Ω: td(on) 6.5 ns, tr 3.5 ns, td(off) 41 ns, tf 9 ns. [source: AO p.2]
- **G2-AO3401A-A3** **[added]** The datasheet's top-view drawing shows the dot next to G on the two-lead side; the bottom view mirrors it (D top-left, G right, S bottom). Do not use the bottom-view drawing for footprint orientation. [source: AO p.1, SOT23 drawings]

---

### Verifier summary
- Verified: 64 · Corrected: 5 · Unverifiable: 0 · Added: 18
- Agent A's four "discrepancies with the download notes" are all confirmed: DSG has no nSLEEP/VREF pins (DRV p.3–4 Table 6-1); SO-8 code is "M" (AP p.12); polarity bit is INT_POLARITY, CTRL_REG6 bit 1, default 0 = active-high, reset 0x00 (LIS p.38 Tables 42–43, p.31 Table 21); AO3401A pin numbers are not printed, only lead names (AO p.1).

---

## Fact sheet G3 – VERIFIED (Agent B) – USB, diodes, LEDs, charger IC, connectors

Agent B checked every item against the PDFs themselves. Pages were rendered at 300–600 dpi and read visually, so the check did not rely only on the text extracts.
Legend: **[verified]** matches the PDF · **[corrected]** wrong or misleading; corrected value and own page reference given · **[unverifiable]** cannot be checked from the document · **[added]** new item relevant to a wiring review.
Page numbers are PDF page numbers. Document short names are the same as in facts-G3.md:

- [ST-USBLC6] = datasheets/USBLC6-2SC6_datasheet_LCSC.pdf (ST Doc ID 11265 Rev 5, Oct 2011)
- [HRO-C31] = datasheets/HRO_TYPE-C-31-M-12_datasheet_LCSC.pdf (HRO drawing rev A, 2020-12-08, 1 sheet)
- [MDD-SS34F] = datasheets/MDD_SS34F_datasheet_LCSC.pdf (SS32F–SS3200F, Rev 2024A3)
- [MDD-SS34] = datasheets/MDD_SS34_datasheet_LCSC.pdf (SS32–SS3200, Rev 2024A5)
- [KENTO] = datasheets/KENTO_KT-0603R_datasheet_LCSC.pdf
- [NS-0402G] = datasheets/NATIONSTAR_NCD0402G1_datasheet_LCSC_representative.pdf – REPRESENTATIVE ONLY
- [MCP] = datasheets/MCP73831_datasheet_en.pdf (DS20001984H)
- [JST-PH] = datasheets/JST_PH_catalog_en.pdf
- [JST-PH-old] = datasheets/JST_S2B-PH-SM4-TB_datasheet_LCSC.pdf

---

### USBLC6-2SC6 (U5, U102)

**Pinout**
- **[verified]** G3-USBLC6-1: SOT23-6L, top view: pin 1 = I/O1, pin 2 = GND, pin 3 = I/O2, pin 4 = I/O2, pin 5 = VBUS, pin 6 = I/O1. [source: ST-USBLC6, p.1, Figure 1]
- **[verified]** G3-USBLC6-2: Pins 1 and 6 are the two ends of I/O1, and pins 3 and 4 the two ends of I/O2. They are tied together inside the device: Fig. 1 shows one line between 1 and 6. In Fig. 18, D+in goes to pin 1 and D+out to pin 6, D−in to pin 3 and D−out to pin 4. Each line has steering diodes to VBUS and to GND, plus a Zener between VBUS and GND. *Note:* Fig. 18 and Fig. 16 support this item. Fig. 7, which A also cites, deals with the VBUS track (see item 3). [source: ST-USBLC6, p.1 Fig.1; p.9 Figs.16, 18]
- **[corrected]** G3-USBLC6-3: Fig. 7 is not about the data lines. It compares two ways of connecting the **VCC/VBUS supply track to pin 5**. The "unsuitable" version reaches pin 5 through a long stub. The "optimized" version runs the supply track straight past pin 5, so there is no stub. The flow-through routing of the data lines (1→6, 3→4) comes from Fig. 18. The datasheet never says that either pin of a pair may serve as the connector side. That only follows from the internal 1–6 and 3–4 connection in Fig. 1, and ST always draws "in" on pins 1 and 3. [source: ST-USBLC6, p.5 §2.3 and Fig.7; p.9 Fig.18]

**Absolute maximum / operating**
- **[verified]** G3-USBLC6-4: Table 1 lists VPP 15 kV air, 15 kV contact (IEC 61000-4-2) and 25 kV (MIL-STD-883G method 3015-7). Tstg is −55..+150 °C, Tj −40..+125 °C, and TL is 260 °C for 10 s. The front page claims IEC level 4 compliance at 15 kV air and 8 kV contact. [source: ST-USBLC6, p.2 Table 1; p.1]
- **[verified]** G3-USBLC6-5: The datasheet gives no DC abs-max for the VBUS pin and has no recommended-operating table. [source: ST-USBLC6, p.2]
- **[verified]** G3-USBLC6-6: Table 2 at 25 °C:
  - IRM: typ 10 nA, max 150 nA at VRM = 5.25 V.
  - VBR: min 6 V at 1 mA.
  - VF: max 1.1 V at 10 mA.
  - VCL: max 12 V at 1 A and 17 V at 5 A (8/20 µs).
  - C(I/O–GND): typ 2.5 pF, max 3.5 pF at 1.65 V. ΔC(I/O–GND) is 0.015 pF.
  - C(I/O–I/O): typ 1.2 pF, max 1.7 pF. ΔC(I/O–I/O) is 0.04 pF; A did not list this value.

  [source: ST-USBLC6, p.2 Table 2]
- **[verified]** G3-USBLC6-7: 5.5 V on VBUS is below the 6 V minimum VBR, which leaves about 0.5 V of margin. Leakage is specified only at 5.25 V. Section 2.1 uses VBR = 6.1 V as a typical value in its worked example. [source: ST-USBLC6, p.2 Table 2; p.4 §2.1]
- **[verified]** G3-USBLC6-8: Fig. 2 plots capacitance against line voltage from 0 to 5 V. Fig. 3 states a line voltage of 0 to 3.3 V. Fig. 4 (leakage against Tj) is drawn at VBUS = 5 V. [source: ST-USBLC6, p.3 Figs.2–4]

**External components / placement**
- **[verified]** G3-USBLC6-9: Fig. 18 shows CBUS = 100 nF from VBUS to GND. Fig. 15 shows 100 nF on +VCC. [source: ST-USBLC6, p.9 Fig.18; p.8 Fig.15]
- **[verified]** G3-USBLC6-10: Place the device as close to the connector as possible. Keep the I/O, VBUS and GND tracks short. ST's example: a track 10 mm long and 0.5 mm wide has about 6 nH. At 24 A/ns (8 kV contact discharge) that adds 144 V per inductance, giving roughly +319 V and −301 V in total. [source: ST-USBLC6, p.4 §2.2; p.5 §2.3; p.6 "Important"]
- **[verified]** G3-USBLC6-11: The VBUS pin connects to the protected supply rail; Fig. 14 shows it tied to connector VBUS. [source: ST-USBLC6, p.8 Fig.14; p.4 §2.1]

**Polarity / pin 1**
- **[verified]** G3-USBLC6-12: The top marking reads "UL26". A dot marks pin 1, at bottom left when the text reads upright. [source: ST-USBLC6, p.12 Fig.23; p.13 Table 5]

**Land pattern**
- **[verified]** G3-USBLC6-13: Footprint pads are 0.60 × 1.20 mm at 0.95 mm pitch. The gap between pad rows is 1.10 mm and the outer extent is 3.50 mm, so the row centre spacing is 2.30 mm (1.20 + 1.10 + 1.20 = 3.50). There is no exposed pad. [source: ST-USBLC6, p.12 Fig.22]
- **[verified]** G3-USBLC6-14: D 2.80–3.05, E 1.50–1.75, H 2.60–3.00 (overall, including leads), A 0.90–1.45, e 0.95 mm. Also b 0.35–0.50 and L 0.10–0.60 mm. [source: ST-USBLC6, p.12 Table 4]

**Relevant to our use**
- **[verified]** G3-USBLC6-15: The applications list includes USB 2.0 up to 480 Mb/s. Route D+ through 1↔6 and D− through 3↔4. Pin 2 goes to GND and pin 5 to VBUS with 100 nF. [source: ST-USBLC6, p.1; p.9 Fig.18]
- **[verified]** G3-USBLC6-16: The document is Rev 5, dated 24 Oct 2011. Rev 4 updated the leakage specification at 5.25 V. Whether later ST revisions exist cannot be checked offline. [source: ST-USBLC6, p.13 Table 6]
- **[added]** G3-USBLC6-17: Ordering: USBLC6-2SC6, marking UL26, SOT23-6L, 3000 pcs per tape and reel. [source: ST-USBLC6, p.13 Table 5]
- **[added]** G3-USBLC6-18: The VBUS pin is the positive rail of the clamp. With pin 5 left unconnected, positive ESD on I/O would be clamped only through the floating Zener rail. So pin 5 must be tied to VBUS, ideally with the 100 nF capacitor next to the pin. [source: ST-USBLC6, p.4 §2.1 (VCL+ = VTRANSIL + VF); p.9 Fig.18]

---

### TYPE-C-31-M-12 (J4, J101)

Single-sheet CAD drawing. All items refer to [HRO-C31] p.1, re-rendered at 400 dpi.

**Pinout**
- **[verified]** G3-HROC31-1: A1, A12, B1 and B12 are GND. A4, A9, B4 and B9 are VBUS. A5 = CC1, B5 = CC2, A6 = DP1, A7 = DN1, B6 = DP2, B7 = DN2, A8 = SBU1, B8 = SBU2. This is a 16-contact USB 2.0 part with no SuperSpeed pins. [source: HRO-C31, p.1 pin table]
- **[verified]** G3-HROC31-2: The layout pad row, left to right (component side, PCB edge at the bottom), is A1/B12, A4/B9, B8, A5, B7, A6, A7, B6, A8, B5, B4/A9, B1/A12. That makes 12 pads, with the GND and VBUS pads shared between A and B contacts. [source: HRO-C31, p.1 "Recommend P.C.B layout"]
- **[verified]** G3-HROC31-3: The four shell tabs carry no net name, so their net is not given in the drawing. [source: HRO-C31, p.1]

**Ratings**
- **[verified]** G3-HROC31-4: Electrical (Note 4): 5 A, 20 V, insulation at least 100 MΩ, 100 VAC for 1 min, and no contact resistance given. Mechanical and environmental (Notes 3, 5, 6): operating −30..+80 °C, reflow peak 260 °C held for 10 s, insertion 0.5–2.0 kgf, removal 0.8–2.0 kgf, 10 000 cycles. [source: HRO-C31, p.1 Notes 3–6]
- **[verified]** G3-HROC31-5: 5.5 V on VBUS is far below the 20 V rating. [source: HRO-C31, p.1 Note 4-1]

**External components**
- **[verified]** G3-HROC31-6: The drawing does not give CC Rd values (5.1 kΩ), ESD protection or shield termination. [source: HRO-C31, p.1]

**Orientation / pin 1**
- **[verified]** G3-HROC31-7: Looking into the opening, A1 is at top left, A12 top right, B12 bottom left and B1 bottom right. [source: HRO-C31, p.1 front view]
- **[corrected]** G3-HROC31-8: The opening faces the PCB edge. However, **5.79 mm is not measured from the pad row**. The dimension chain on the right of the layout gives 1.64 mm from the rear edge of the pads to the centre line of the locating holes. It then gives **5.79 mm from that hole centre line to the PCB edge**. The rear edge of the pads therefore sits 1.64 + 5.79 ≈ **7.43 mm** from the PCB edge. [source: HRO-C31, p.1 layout, right-hand dimension stack "1.64 / 0.50 / 4.18 / 5.79"]

**Land pattern**
- **[corrected]** G3-HROC31-9: Pitch is 0.50 mm. The 8 inner pads are 0.30 mm wide ("8-0.30") and the 4 outer pads 0.60 mm wide ("4-0.60"); layout tolerance is ±0.05. **Pad length is about 1.14 mm. It is not 1.64 mm.** The 1.64 dimension runs from the rear edge of the pads to the hole centre line, and 0.50 runs from the front edge of the pads to the same line, so length = 1.64 − 0.50. The span dimensions are pad centre to pad centre:
  - 1.50 = B7↔B6
  - 2.50 = A5↔A8
  - 3.50 = B8↔B5
  - 4.80 = A4/B9↔B4/A9
  - 6.40 = A1/B12↔B1/A12

  [source: HRO-C31, p.1 layout]
- **[verified]** G3-HROC31-10: The two locating holes are Ø0.60 mm with centres 5.78 mm apart. They are drawn without a copper ring, i.e. NPTH. The part's pegs are "2-Ø0.50" at 5.78 mm. 6.40 mm is the centre spacing of the outer pads. [source: HRO-C31, p.1 layout and front view]
- **[verified]** G3-HROC31-11: Shell tabs:
  - Rear pair: slot 0.60 × 1.70 mm, copper 0.90 × 2.00 mm.
  - Front pair: slot 0.60 × 1.40 mm, copper 0.90 × 1.70 mm.
  - Rear-to-front centre spacing is 4.18 mm and left-right centre spacing 8.65 mm. The front view gives 8.64 mm for the shell legs.
  - The 0.60/0.90 widths are dimensioned only at the front-left slot.

  [source: HRO-C31, p.1 layout]
- **[verified]** G3-HROC31-12: The body is 8.94 mm wide and 7.35 mm deep, with contacts 16 × 0.20 ±0.05 mm. The opening is 8.34 mm wide (+0.06/−0.02). [source: HRO-C31, p.1 top and front views]
- **[verified]** G3-HROC31-13: The title "DETECTOR SWITCHS" is a template error; the part number is TYPE-C-31-M-12. Housing is UL94V-0 and contacts copper alloy. Plating is nickel underplate, gold on the contact area and gold flash on the solder area. The mid plate is stainless steel. [source: HRO-C31, p.1 title block, Notes 1–2]
- **[added]** G3-HROC31-14: The rear shell-tab slot centres sit roughly level with the front edge of the signal pads. The 4.18 mm dimension starts on the same line where the 0.50 dimension begins. The locating holes are 0.50 mm in front of the pads, toward the PCB edge. [source: HRO-C31, p.1 layout]

---

### SS34F (D2)

- **[verified]** G3-SS34F-1: Two terminals; the colour band marks the cathode. [source: MDD-SS34F, p.1 Mechanical Data]
- **[verified]** G3-SS34F-2: SS34F: VRRM 40 V, VRMS 28 V, VDC 40 V, I(AV) 3.0 A, IFSM 80 A. [source: MDD-SS34F, p.1 table]
- **[verified]** G3-SS34F-3: VF max 0.55 V at 3.0 A, from the merged cell for SS32F–SS34F. [source: MDD-SS34F, p.1 table]
- **[verified]** G3-SS34F-4: Fig. 3, SS32F/SS345F trace, typical, read from the graph: about 0.35 V at 0.1 A, 0.44 V at 1 A and 0.50 V at 2 A. [source: MDD-SS34F, p.2 Fig.3]
- **[verified]** G3-SS34F-5: IR max: 0.5 mA at 25 °C and 5.0 mA at 100 °C. Fig. 2, solid trace at about 10 % of VR: roughly 1.4 µA at 25 °C, 75 µA at 75 °C and 500 µA at 100 °C. At 100 % of VR and 25 °C the typical value is only about 4 µA. [source: MDD-SS34F, p.1; p.2 Fig.2]
- **[verified]** G3-SS34F-6: CJ 250 pF (1 MHz, 4 V). RθJA 70 °C/W and RθJC 18 °C/W on 2.0″ × 2.0″ (5 × 5 cm) copper. TJ −55..+125 °C, Tstg −55..+150 °C, terminals 260 °C for 10 s. [source: MDD-SS34F, p.1]
- **[verified]** G3-SS34F-7: Derating against case temperature: 3 A up to 100 °C, falling linearly to 0 A at 150 °C. [source: MDD-SS34F, p.2 Fig.1]
- **[verified]** G3-SS34F-8: 5.5 V reverse is far below 40 V. [source: MDD-SS34F, p.1]
- **[verified]** G3-SS34F-9: Body length 3.30–3.70 mm, overall 4.40–4.90 mm, width 2.40–2.70 mm, height 0.90–1.20 mm, terminal width 1.30–1.60 mm. Also lead length 0.80–1.20 mm and lead thickness 0.12–0.20 mm. [source: MDD-SS34F, p.1 outline]
- **[verified]** G3-SS34F-10: Pads A 1.8 × B 1.6 mm, gap D 2.2 mm, centre-to-centre C 3.8 mm, overall E 5.4 mm. These are consistent: E = D + 2B and C = D + B. [source: MDD-SS34F, p.3 Suggested Pad Layout]
- **[verified]** G3-SS34F-11: No exposed pad. [source: MDD-SS34F, p.1]
- **[corrected]** G3-SS34F-12: The "Marking Code" row is not blank. It shares its cells with the column headers ("MDD SS34F"), because the headers span both the "Parameter" and "Marking Code" rows. That implies the marking is the type designation SS34F, with the MDD logo. No separate short code exists. Reel: 3000 pcs on a 7″ reel. [source: MDD-SS34F, p.1 table header; p.3 Reel packing]

---

### SS34 (D102)

- **[verified]** G3-SS34-1: The colour band marks the cathode. [source: MDD-SS34, p.1]
- **[verified]** G3-SS34-2: VRRM 40 V, VRMS 28 V, VDC 40 V, I(AV) 3.0 A ("at TL, see Fig.1"), IFSM 80 A. [source: MDD-SS34, p.1]
- **[verified]** G3-SS34-3: VF max 0.55 V at 3.0 A (SS32–SS34). [source: MDD-SS34, p.1]
- **[verified]** G3-SS34-4: Fig. 3, SS32~SS35 trace, read from the graph: about 0.40–0.42 V at 1 A and 0.48 V at 2 A. [source: MDD-SS34, p.2 Fig.3]
- **[verified]** G3-SS34-5: IR max: 0.5 mA at 25 °C and 5 mA at 125 °C. Fig. 2 (legend SS32~SS36) shows the same typical curve shape as the SMAF part. [source: MDD-SS34, p.1; p.2 Fig.2]
- **[verified]** G3-SS34-6: CJ 250 pF and RθJA 70 °C/W; this sheet gives no RθJC. Note 2 reads "0.2x0.2″ (5.0x5.0mm)", which is inconsistent as A says. TJ −55..+125 °C, Tstg −55..+150 °C, terminals 250 °C for 10 s. [source: MDD-SS34, p.1]
- **[verified]** G3-SS34-7: Derating against lead temperature: 3 A up to 100 °C, falling to 0 A at 125 °C. [source: MDD-SS34, p.2 Fig.1]
- **[verified]** G3-SS34-8: 5.5 V reverse is far below 40 V. [source: MDD-SS34, p.1]
- **[corrected]** G3-SS34-9: **Body length is 3.80–4.50 mm (0.150–0.177″)**, not 3.90–4.50. The other values are correct: overall 4.70–5.30, width 2.30–2.80, height 1.85–2.45 mm. Also terminal width 1.30–1.70, lead length 0.75–1.55 and lead thickness 0.15–0.31 mm. [source: MDD-SS34, p.1 outline]
- **[verified]** G3-SS34-10: Pads A 1.68 × B 1.52 mm, C 3.93 mm, D 2.41 mm, E 5.45 mm. These are consistent: 2 × 1.52 + 2.41 = 5.45. [source: MDD-SS34, p.3]
- **[verified]** G3-SS34-11: This is the family sheet, with no exposed pad. Reels hold 2000 (7″), 5000 (11″) or 7500 (13″) pcs. [source: MDD-SS34, p.1; p.3]

---

### KT-0603R red LED (D101)

- **[verified]** G3-KT0603R-1: The symbol has the triangle pointing toward ②, with the bar at ②, and "+" next to ①. So ① is the anode and ② the cathode. [source: KENTO, p.2 §2, checked at 400 dpi]
- **[verified]** G3-KT0603R-2: The top view has a green corner mark at the ② (cathode) end. The second view has a T or funnel mark and shows the electrodes in red (0.41 mm). Its pads are not numbered, so use the top view and the symbol. [source: KENTO, p.2 §2]
- **[verified]** G3-KT0603R-3: 1.6 × 0.8 × 0.6 mm. Electrodes are 0.30 mm on the top view, 1.00 mm apart, with ±0.10 mm tolerance. [source: KENTO, p.2 §1–2]
- **[verified]** G3-KT0603R-4: Two pads, 0.70 × 0.70 mm, with a 0.70 mm gap. [source: KENTO, p.2 §2]
- **[verified]** G3-KT0603R-5: Pd 40 mW, IF 25 mA, IFP 60 mA (1/10 duty, 0.1 ms), VR 5 V. Topr and Tstg both −40..+85 °C. Reflow 260 °C for 10 s, hand soldering 300 °C for 3 s. The ESD field is blank. [source: KENTO, p.3 §4]
- **[verified]** G3-KT0603R-6: At 20 mA: VF 1.8–2.4 V, IV 145–300 mcd, λd 615–630 nm, λp 625–645 nm, viewing angle 120°. IR max 5 µA at 5 V; Δλ typ 20 nm. [source: KENTO, p.3 §5]
- **[verified]** G3-KT0603R-7: VF bins VE..VJ cover 1.8–2.4 V (±0.05 V). IV bins run from P22 to P24. The table has typos: "P23" appears twice, for 175–210 and 210–250, and the unit column says "V" instead of mcd. [source: KENTO, p.4 §6]
- **[verified]** G3-KT0603R-8: VR abs max is 5 V, so the LED must never see 5–5.5 V in reverse. [source: KENTO, p.3 §4]
- **[verified]** G3-KT0603R-9: Reflow profile: preheat 180–200 °C for up to 120 s, at most 60 s above 220 °C, peak 260 °C for at most 10 s, ramps 1–5 °C/s. [source: KENTO, p.2 §3]

---

### Generic green 0402 LED (D1) – representative NCD0402G1 only

- **[verified]** G3-LED0402-1: Polarity: ① is "−" (cathode) and ② is "+" (anode); the symbol's triangle points toward ①. [source: NS-0402G, p.2 Polarity]
- **[corrected]** G3-LED0402-2: The green cathode mark, on the bottom view where the pads are visible, does **not** sit next to pad ①. It is a T-shape **centred between the pads**: a full-height vertical bar with a short horizontal arm **pointing toward pad ①** (cathode). [source: NS-0402G, p.2 "Cathode Mark", checked at 500 dpi]
- **[verified]** G3-LED0402-3: 1.0 × 0.5 × 0.35 mm; 0.16 mm is the electrode height. [source: NS-0402G, p.2]
- **[verified]** G3-LED0402-4: Pads 0.35 × 0.5 mm, 0.4 mm gap, 1.1 mm overall. [source: NS-0402G, p.2]
- **[verified]** G3-LED0402-5: IF 20 mA, IFP 50 mA, VR 5 V, Topr −30..+85 °C, Tstg −40..+100 °C, PD 72 mW. [source: NS-0402G, p.1]
- **[verified]** G3-LED0402-6: VF 2.5 / 2.8 / 3.6 V, λp 520 nm, λd 513 / 522 / 532 nm, Δλ 30 nm, IV 100 / 150 / 300 mcd. IR max 10 µA at 5 V; viewing angle 130°. A single merged cell gives **IF = 5 mA** as the test condition for VF, λp, λd, Δλ and IV; this is clearly drawn, not just implied. [source: NS-0402G, p.1]
- **[verified]** G3-LED0402-7: This is an inference. With 3V3 supply and VF up to 3.6 V at 5 mA, a worst-case part may not light usefully. [source: NS-0402G, p.1]
- **[verified]** G3-LED0402-8: VR max is 5 V. [source: NS-0402G, p.1]

---

### MCP73831T-2ACI/OT (U101)

**Pinout**
- **[verified]** G3-MCP73831-1: SOT-23-5: 1 STAT, 2 VSS, 3 VBAT, 4 VDD, 5 PROG. Pin 5 is opposite pin 1 and pin 4 opposite pin 3. The exposed pad exists only on the DFN. [source: MCP, p.11 Table 3-1; p.1 Package Types]

**Absolute maximum / operating**
- **[verified]** G3-MCP73831-2: VDD 7.0 V; all other pins −0.3 V to VDD + 0.3 V. Tstg −65..+150 °C. ESD 4 kV HBM and 400 V MM. [source: MCP, p.3]
- **[verified]** G3-MCP73831-3: The DC table gives VDD 3.75–6 V. Limits apply from VREG + 1 V (5.2 V) up to 6 V. §3.1 recommends VREG + 0.3 V (4.5 V) up to 6 V. [source: MCP, p.3; p.11 §3.1]
- **[verified]** G3-MCP73831-4: 5.5 V is within both the abs max and the spec range. [source: MCP, p.3]
- **[verified]** G3-MCP73831-5: VSTART 3.3 / 3.45 / 3.6 V, VSTOP 3.2 / 3.38 / 3.5 V, hysteresis 70 mV, tSTART at most 5 ms. [source: MCP, p.3; p.5]
- **[verified]** G3-MCP73831-6: TA −40..+85 °C, TJ −40..+125 °C, TSD 150 °C with 10 °C hysteresis. θJA is 230 °C/W on JC51-7, or 130 °C/W or better with large copper. *The θJA source is p.5 Note 2;* Fig. 4-2 on p.14 shows thermal regulation, with current falling from about 110 °C TJ. [source: MCP, p.5; p.14 §4.9–4.10]
- **[verified]** G3-MCP73831-7: Output reverse leakage typ 0.15 / 0.25 / 0.15 µA, max 2 µA, for PROG floating, VDD floating and VDD < VSTOP respectively. [source: MCP, p.3; p.4 "Battery Discharge Current"]

**-2AC option values**
- **[verified]** G3-MCP73831-8: "-2" gives VREG 4.20 V (4.168–4.232 V). [source: MCP, p.3; p.26]
- **[verified]** G3-MCP73831-9: AC option: IPREG 10 %, VPTH 66.5 %, ITERM 7.5 %, VRTH 96.5 %. Marking KDNN. [source: MCP, p.26 Options table; p.19]

**External components**
- **[verified]** G3-MCP73831-10: At least 4.7 µF on VDD and at least 4.7 µF on VBAT. The typical application uses 470 Ω on STAT and 2 kΩ on PROG. [source: MCP, p.11 §3.1–3.2; p.18 §6.1.1.4; p.1]
- **[verified]** G3-MCP73831-11: IREG [mA] = 1000 V / RPROG [kΩ], valid for RPROG 2–67 kΩ. Specified points: 90/100/110 mA at 10 kΩ, 450/505/550 mA at 2 kΩ (by design) and 12.5/14.5/16.5 mA at 67 kΩ. [source: MCP, p.15 §5.1.2; p.3]
- **[corrected]** G3-MCP73831-12: Floating PROG or a logic-high on PROG disables the charger, and supply current then falls to about 25 µA typ. **The 70–200 kΩ "Minimum Shutdown Impedance" is a min/max spec of the shutdown threshold, not a "disable range".** Below 70 kΩ the charger is guaranteed enabled. Shutdown is only guaranteed with more than 200 kΩ, or with PROG floating. A resistor between 70 and 200 kΩ gives an undefined state. [source: MCP, p.4 PROG Input; p.15 §5.2.2; p.18 §6.1.1.6]
- **[verified]** G3-MCP73831-13: Input protection must be used with hot-plug sources such as USB cables. A transzorb from the input to 0 V is recommended; Fig. 6-1 uses SMAJ5.0A/AC. [source: MCP, p.18 §6.1.1.2; p.17 Fig.6-1]
- **[verified]** G3-MCP73831-14: Place the battery close to VBAT and VSS, and use a copper heat-sink area with vias. [source: MCP, p.18 §6.2]
- **[verified]** G3-MCP73831-15: Pdiss = (VDDmax − VPTHmin) × IREGmax. The example gives (5.5 − 2.7) V × 550 mA = 1.54 W, which leads to thermal regulation in SOT-23-5. [source: MCP, p.18 §6.1.1.3]

**STAT**
- **[verified]** G3-MCP73831-16: STAT states: shutdown Hi-Z, no battery Hi-Z, precharge L, CC L, CV L, complete H. [source: MCP, p.15 Table 5-1]
- **[verified]** G3-MCP73831-17: Sink 25 mA, source 35 mA. VOL 0.4 V typ and 1 V max at 4 mA; VOH VDD − 0.4 V typ and VDD − 1 V min at 4 mA. Hi-Z leakage 1 µA max. tON and tOFF at most 200 µs. [source: MCP, p.4; p.5]
- **[verified]** G3-MCP73831-18: This is an inference. STAT high is about VDD (≈5 V), so it needs a divider or clamp before a 3.3 V GPIO. [source: MCP, p.4 VOH]

**Polarity / land pattern**
- **[verified]** G3-MCP73831-19: Drawing C04-091-OT Rev F: D 2.90, E1 1.60, E 2.80 BSC, e 0.95, e1 1.90, A at most 1.45, b 0.20–0.51 mm. [source: MCP, p.22–23]
- **[verified]** G3-MCP73831-20: Land pattern: X 0.60, Y 1.10, E 0.95, C 2.80, G at least 1.70, GX at least 0.35, Z 3.90. [source: MCP, p.24, C04-2091-OT Rev F]
- **[added]** G3-MCP73831-21: Automatic power-down: entry when VDD falls below VBAT + 50 mV typ (+20 mV min); exit when VDD rises above VBAT + 150 mV typ (+200 mV max), for 3.5 V ≤ VBAT ≤ VREG. This matters if VDD can sag toward the battery voltage, e.g. a VBUS sag, or VDD fed from VSYS behind the Schottky. [source: MCP, p.4–5 Automatic Power Down]
- **[added]** G3-MCP73831-22: Battery detection: source current 6 µA typ (0.6 min). The device detects "no battery" when VBAT ≥ VREG + 100 mV or the VBAT impedance is at least 7 MΩ. In Charge Complete, IDISCHARGE is −5.5 µA typ (−15 µA max). [source: MCP, p.4]
- **[added]** G3-MCP73831-23: VSS connects to battery negative and to input-supply ground. The RDSON of the pass transistor is 350 mΩ typ at VDD = 3.75 V and TJ = 105 °C. [source: MCP, p.11 §3.4; p.4]
- **[added]** G3-MCP73831-24: Supply current in charge-complete or no-battery state is 53 µA typ (200 max). In charging it is 510 µA typ (1500 max). With VDD < VBAT − 50 mV it is 1 µA typ (5 max). [source: MCP, p.3]

---

### S2B-PH-SM4-TB (J102)

- **[verified]** G3-JSTPH-1: 2 circuits, A = 2.0 mm, B = 7.9 mm, 1000 per reel. Height 5.5 mm, depth 6 mm, plus 2.6 mm of lead tails. [source: JST-PH, p.4 side-entry table and drawing]
- **[verified]** G3-JSTPH-2: "Mark of No. 1 circuit" is at the left end of the side-entry drawing. [source: JST-PH, p.4]
- **[verified]** G3-JSTPH-3: 2 A (AWG24), 100 V, −40..+105 °C. Contact resistance 10 mΩ initial and 20 mΩ after test. Insulation at least 1000 MΩ, withstand 800 VAC for 1 min, wire AWG32–24. [source: JST-PH, p.1]
- **[verified]** G3-JSTPH-4: 5.5 V is far below 100 V. [source: JST-PH, p.1]
- **[corrected]** G3-JSTPH-5: As A states, the view is from the mounting surface. Signal pitch is 2 ±0.05 mm (non-accumulating), pad width at least 1 mm, and No. 1 is the leftmost pad. **The signal pad length follows from the dimensions: 9 min − 5.5 max ≥ 3.5 mm.** A measurement by scale also gives about 3.5 mm. A's "≈3.4 mm" confused it with the 3.4 mm reinforcement-pad length. The signal pads extend past the rear of the connector outline (lead tails). The reinforcement pads sit at the mating side. [source: JST-PH, p.2 side-entry SMT layout, checked at 600 dpi]
- **[verified]** G3-JSTPH-6: Reinforcement pads are 1.5 ±0.1 mm wide × 3.4 ±0.1 mm long. Their inner edge is 1.6 ±0.1 mm from the outermost signal-pad centre, so the pad centre is ≈3.35 mm from the connector centre line for 2 circuits. Pattern height is at least 9 mm and the signal-pad inner edge to reinforcement-pad outer edge distance at most 5.5 mm. The reinforcement pads extend 0.2 mm beyond the connector outline. The chain was confirmed at 600 dpi: 1.6 runs from the signal-pad centre to the pad inner edge, and 1.5 across the pad. JST-PH-old gives the same "1.5 / 1.6 / 2 / 3.4". [source: JST-PH, p.2; JST-PH-old p.1]
- **[verified]** G3-JSTPH-7: No net is given for the reinforcement pads. Reinforcement material is tin-plated copper alloy. [source: JST-PH, p.4 Material]
- **[verified]** G3-JSTPH-8: Mating housing PHR-2 with SPH-002T-P0.5S (AWG30–24) or SPH-002T-P0.5L (AWG28–24) contacts. PCB thickness 0.8–1.6 mm, given for the series in the through-hole context. [source: JST-PH, p.1–3]
- **[verified]** G3-JSTPH-9: JST defines no battery polarity. [source: JST-PH]

---

### Gaps / NOT FOUND summary (updated)
- USBLC6: no VBUS abs-max DC voltage and no recommended-operating table.
- HRO: shell tab net, CC resistor values and contact resistance are not given. Pad length (≈1.14 mm) and pad-to-edge distance (≈7.43 mm) are derived from the dimension chain, not dimensioned directly.
- SS34F/SS34: no short marking code; the type name is in the merged header cell.
- KT-0603R: ESD rating is blank and the bin table has typos.
- NCD0402G1: representative only.
- MCP73831: STAT high = VDD (≈5 V). A PROG impedance of 70–200 kΩ gives an undefined state.
- JST: no reinforcement pad net and no battery polarity.

---

## Fact sheet G4 – verified (Agent B, 2026-11-09)

Agent B checked each item in `facts-G4.md` against the PDFs in `datasheets/`. Agent B read all 13 pages of SPX3819 Rev 2.0.5 visually. Figs. 3, 5, 7 and 17 were also rendered at 250 dpi and cropped. All PTC sheets were read in full. Netlist facts were rechecked in `v2/main.net`. LCSC part pages were fetched with WebFetch. The LCSC product API was not reachable from this session, so stock and price figures could not be confirmed.

Tags: **[verified]**, **[corrected]** (with reference), **[unverifiable]**, **[added]**.

### Documents
- [SPX] Rev 2.0.5, December 2019, 13 pages, 1 217 248 bytes: **[verified]** (p.1 header, p.13 revision table; pdfinfo creation date 2019-12-07).
- [TF] approval sheet, 4 pages, dated 10-Apr-13: **[verified]** (p.1).
- [BN] 3 pages: **[corrected]** The document says "Version 1.0, effective date 2018-12-27" (p.1 header). The 2019-11 date is only the PDF creation timestamp.
- [RO] Rev 1.2, 6 pages: **[verified]**.
- Design state, netlist: **[verified]** in v2/main.net:
  - U3: pins 1 and 3 on VSYS, pin 5 on 3V3, pin 4 unconnected.
  - U6: pin 1 on VSYS, pin 3 on IO15 together with R22, pin 5 on VLED_SW.
  - VLED_SW connects only to F1.1 and U6.5. C17 sits on VLED with F1.2 and J7.
  - F1 value "0.5A 16V".
  - C8's value field says only "1u". The 16 V rating is not in the netlist value field (not checked further).
- Quick table, 6.6 V: **[verified]** (p.2 abs max and operating ratings).

### SPX3819

- **G4-SPX3819-1** **[verified]** p.3 Fig. 2 and Pin Description.
- **G4-SPX3819-2** **[verified]** p.3. EN "logic low or open = shutdown". BYP is for the fixed version only, with 10 nF to ground to reduce noise.
- **G4-SPX3819-3** **[verified]** Matches G2-AP2112K-2 (1 VIN, 2 GND, 3 EN, 4 NC, 5 VOUT).
- **G4-SPX3819-4** **[verified]** p.4. The SOT-23-5 list also contains -1-2. The "-L" decoding is derived, as stated.
- **G4-SPX3819-5** **[verified]** p.12, POD-00000025 rev B:
  - D 2.90, E 2.80, E1 1.60, A max 1.45, e 0.95, e1 1.90 mm.
  - Land pattern ("for reference only"): pads 0.69 × 0.99, spacing 2.59, outer pitch 1.90.
- **G4-SPX3819-6** **[verified]** p.2.
- **G4-SPX3819-7** **[verified]** p.2, Note 1.
- **G4-SPX3819-8** **[verified]** p.1 Fig. 1, p.8 Fig. 18 ("ENABLE may be tied directly to VIN"), p.2 line-regulation rows.
- **G4-SPX3819-9** **[verified]** The operating rating is EN 0.0 V to VIN (p.2). The rest is derived and plausible.
- **G4-SPX3819-10** **[verified]** (derived from p.2).
- **G4-SPX3819-11** **[verified]** p.3 table. VIL max 0.4 V, VIH min 2 V; EN current 0.01/2 µA and 3/20 µA. Fig. 13 (p.6) reads about 1.18 V at 4.5 V and about 1.11 V at 16 V.
- **G4-SPX3819-12** **[verified]** (derived; G1-ESP32-8 confirms VOH 0.8 × VDD).
- **G4-SPX3819-13** **[verified]** (derived arithmetic; G1-ESP32-23/31/32 confirm IO15 floats and is not an LP GPIO).
- **G4-SPX3819-14** **[verified]** p.2.
  - Line regulation 0.04 typ / 0.1 max with VEN ≤ 6 V.
  - The 0.2 %/V row "VIN = VEN up to 8 V" carries the full-TJ bullet.
  - The 16 V row is specified for TA 25–85 °C.
  - Load regulation 0.05 / 0.4 %. PSRR 70 dB, no frequency given.
- **G4-SPX3819-15** **[verified]** p.2 table and Note 2 (p.3). Fig. 7 (p.5) at 250 dpi: about 115–120 mV at 30 mA, about 205 mV at 200 mA, about 330 mV at 500 mA.
- **G4-SPX3819-16** **[corrected]** The 3.45 V figure (3.0 V + 450 mV full-TJ max at 150 mA) is correct. "3.35 V typ at 25 °C" is wrong:
  - 350 mV is the **25 °C maximum**, so 3.35 V is the 25 °C worst case.
  - The typical dropout at 150 mA is 180 mV, which gives about 3.18 V (p.2, dropout rows).
  - The conclusion is unchanged.
- **G4-SPX3819-17** **[corrected]** The Fig. 3 regulation value at 200 mA is about **1.3 mA**, not 1.5 mA (p.5 Fig. 3 at 250 dpi: 0.8 mA at 150 mA, 1.8 mA at 250 mA). The 350 mA (about 3.4 mA) and 500 mA (about 6.2 mA) values are verified.
  - Fig. 5 is verified: about 2.0 mA at 200 mA, about 6.5–7 mA at 350 mA, about 12.9 mA at 500 mA.
  - Fig. 12 (p.6) is verified: 11.0–12.5 mA.
  - **[added]** Fig. 3, Fig. 5 and Fig. 12 are all labelled VIN = 4.3 V for a 3.3 V device. The dropout condition of Fig. 5 is not otherwise defined.
- **G4-SPX3819-18** **[verified]** p.2.
- **G4-SPX3819-19** **[verified]** p.5 Fig. 4: about 80 µA at 4.5 V, about 88–90 µA at 6.6 V, about 142 µA at 16 V.
- **G4-SPX3819-20** **[verified]** p.3: 800 typ, 950 max (full-TJ bullet), at VOUT = 0 V. No minimum is given.
- **G4-SPX3819-21** **[verified]** p.3.
- **G4-SPX3819-22** **[verified]** p.1: reverse battery protection and zero off-mode current appear in the Features list. Current limit and thermal shutdown appear in the General Description. No threshold, UVLO, soft-start, discharge or reverse-current specification exists anywhere in pp.1–13.
- **G4-SPX3819-23** **[verified]** p.7, Application Information.
- **G4-SPX3819-24** **[corrected]** in detail:
  - Fig. 15 legends do say "uFT" (tantalum).
  - Fig. 17 (p.7) gives only "CL = 10uF". The capacitor type is not stated, so not every characterised capacitor is explicitly tantalum. Fig. 16 (line transient) uses CL = 1 µF, type also not stated.
  - Fig. 17 deviation read at 250 dpi is about **-170 mV / +120 mV**, followed by a slow undershoot of about -50 mV. The sheet said -200 / +150 mV.
  - The conclusion (MLCC stability not confirmed, bench test needed) still holds.
- **G4-SPX3819-25** **[verified]** The netlist confirms that VLED_SW connects only to U6.5 and F1.1, and that C17 is on VLED. The remaining statements are derived.
- **G4-SPX3819-26** **[verified]** p.3 noise conditions and p.7 Fig. 15 (CIN = 1 µF T). The netlist confirms C1, C2, C4 and C8 on VSYS.
- **G4-SPX3819-27** **[verified]** p.7–8, with "(Opt.)" in Figs. 1 and 18.
- **G4-SPX3819-28** **[verified]** p.3 and p.7 Fig. 15:
  - About 300 µV with no CBYP, about 225 µV with Cout 10 µF T.
  - About 60–70 µV at 10 nF.
  - At 1 µF CBYP, Fig. 15 shows about 40 µV (Cout 10 µF) to about 55–60 µV (Cout 1 µF). The 40 µV table value corresponds to the lower curve.
- **G4-SPX3819-29** **[verified]** Arithmetic checked: 0.495 W gives +95 K, TJ about 135 °C; 0.445 W corresponds to 135 mA; (6.4 - 3.3) × 0.1 A = 0.31 W.
- **G4-SPX3819-30** **[verified]** Arithmetic checked: 187 mA, 278 mA, about 0.11 W.
- **G4-SPX3819-31** **[verified]** Nothing found on pp.1–13.
- **G4-SPX3819-32** **[verified]** (derived, plausible).
- **G4-SPX3819-33** **[verified]** Arithmetic checked: 0.33 mA and 0.22 mA. The netlist shows R4.2 on 3V3.
- **[added] G4-SPX3819-34** The revision history (p.13) says Rev 2.0.5 "corrected table alignment on last 5 specs" of the electrical table. Those rows are current limit, noise, VIL, VIH and EN current. The LCSC copy of C13417 is Rev 2.0.2, which predates this fix, so take those rows from Rev 2.0.5 only.
- **[added] G4-SPX3819-35** The General Description (p.1) gives a ground current of 800 µA at 100 mA output. This is consistent with Fig. 3 (about 0.5 mA at 100 mA) only as an approximate figure.

### G4-66V table
- **G4-66V-1 … -17** **[verified]** against the cited verified items. Abs-max and recommended values match:
  - G2-DRV8213-4/-5, G2-AO3401A-3/-4/-5, G3-SS34F-2/-5/-8
  - G3-USBLC6-5/-6/-7, G1-ESP32-5/-6/-8/-11/-18
  - G2-LIS2DH12-3/-5, G3-MCP73831-2/-3
  - G1-TPS22918-2/-3, G1-BSMD0805-2/-6, G2-AP2112K-4/-5
- The derived 6.6 V verdicts are correct.
- G4-66V-12: the 16 V rating comes from the C1/C2 values "47u 16V". For C8 the netlist value is only "1u", so its 16 V rating comes from the task context, not the netlist.
- Notes a–d **[verified]** (derived; arithmetic checked: 30 µA and 19 µA; 2.70 V; VGS about -1.0 V lies inside -0.5 to -1.3 V).

### G4-F1 – PTC candidates
- Common line, "Ihold ≈ 0.40 A at 50 °C, 0.37 A at 60 °C, 0.29 A at 85 °C": **[corrected]** The values are shifted by one temperature column. All three sheets give **0.40 A at 40 °C, 0.37 A at 50 °C, 0.33 A at 60 °C, 0.29 A at 70 °C, 0.23 A at 85 °C**. Sources: [TF] p.2 table "Ihold versus temperature", [BN] p.2 "Thermal Derating", [RO] p.3 "Thermal Derating Chart", row SMD0805-050.
- Common line, other values **[verified]**: Ihold 0.50 A, Itrip 1.00 A, Vmax 16 V, Pd 0.5 W, 0.10 s at 8 A.
- Operating range -40 to +85 °C: verified for [TF] p.2 and [RO] p.3. [BN] states no explicit operating range; the derating table only spans -40…85 °C.
- **G4-F1-1** (TF): **[verified]** Imax 100 A; Rmin 0.150 Ω; R1max 0.850 Ω (p.2); height C 0.30–0.60 mm (p.3). The LCSC page confirms the MPN SMD0805-050-16V by TECHFUSE, 0805, for C2833485. Stock and price **[unverifiable]**.
- **G4-F1-2** (BN): **[verified]** Imax 40 A; Rmin 0.10 Ω; R1max 0.85 Ω; C 0.50–1.10 mm (p.1); derating on p.2. The LCSC page confirms the MPN and C2760262. Stock and price **[unverifiable]**.
- **G4-F1-3** (RO): **[verified]** Marking N, Imax 40 A, Rmin 0.10 Ω, R1max 0.85 Ω (p.2). The C 0.50–1.10 mm dimension for -050-16 is in the **p.5** table, not on p.4. The LCSC page confirms the MPN, C46640986, and height 1.1 mm. Stock and price **[unverifiable]**.
- Also-seen parts: **[verified]** on the LCSC pages.
  - C49073064: BORN SMD0805-050/16N, 16 V, height 1.15 mm.
  - C438897: PTTC SMD0805P050TF, 6 V.
  - C434721: Littelfuse PICOSMDC050S-2 (zero stock not confirmed: **[unverifiable]**).
- Recommendation text: "LCSC Time to Trip 8 s is a parsing error" is **[verified]**. The LCSC page shows "8 s"; the sheet says 0.10 s at 8.0 A.
- Recommendation text, pads: **[corrected]** It is not true that all three sheets have a pad recommendation:
  - [TF] p.3: pads 1.0 × 1.5 mm, gap 1.2 mm.
  - [RO] p.4: pads 1.0 × 1.5 mm, gap 1.1 mm.
  - **[BN] has no pad layout.**
- Recommendation text, drop **[verified]**: 0.85 Ω × 0.5 A = 0.425 V.
- **[added]** [RO] p.4 lists MPQ 4 500 per reel for -050-16. [TF] and [BN] list 5 000 per reel ([TF] p.4, [BN] p.3).
- **[added]** The [TF] applications text (p.2) says "low voltage power supply, up to 15V". The rating table still says Vmax 16 V.

### G4-LCSC – SPX3819
- C9055 = MaxLinear SPX3819M5-L-3-3/TR, SOT-23-5: **[verified]** (LCSC page). Stock and price **[unverifiable]**.
- C13417 = MaxLinear SPX3819M5-L-5-0/TR, SOT-23-5, 5 V fixed: **[verified]** (LCSC page). Stock and price **[unverifiable]**. The Rev 2.0.2 claim about the LCSC PDF was not rechecked: **[unverifiable]**.
- HXY clone C41381857: **[unverifiable]** (not fetched).

### Open points
Open points 1–6 are confirmed. Point 3 should read "3.45 V worst case over temperature at 150 mA (3.35 V worst case at 25 °C, about 3.18 V typical)".
