# Wiring review: datasheets vs. design (main board and charger board)

Status: 2026-11-09 · Review only; no schematic, layout or generator was changed. Design state: schematics and
PCBs as of commit `32a3535` (main board routing unfinished, see F15). Facts: [datasheet-facts.md](datasheet-facts.md),
documents: [datasheets.md](datasheets.md). Open decisions from this review: [open-items.md](open-items.md) F19–F27.

**Update 2026-11-09 (evening):** the main board power path was changed for VSYS up to 6.6 V (4 × AA; U3/U6 now
SPX3819, see [main-board-c6.md](main-board-c6.md) 2.7). Sections 1–6 describe the state at `32a3535`; section 7 is the
delta review of the new state (uncommitted in the main checkout at review time) and supersedes the U3, U6 and F1 rows
and the 5.5 V table.

**Note 2026-11-11:** rev B replaces U3 by the buck converter TPS62162 with L1, C8 and C9 ([main-board-c6.md](main-board-c6.md) 2.7);
the delta review of this block against TI SLVSAM2E is being done separately and is not part of this document yet.

## 1. Method

| Step | Who | What |
|---|---|---|
| Download | 3 agents | 18 PDFs for all active and polarized parts into `datasheets/` (gitignored), index in [datasheets.md](datasheets.md) |
| A: extraction | 3 agents (one per part group) | fact sheets: pinout, abs max / recommended, external parts, polarity, land pattern, use-specific items, explicit "5.5 V OK?" per part |
| B: verification | 3 agents without A's context | every item checked against the PDF (rendered pages for drawings): 218 verified, 21 corrected, 40 added, 0 unverifiable. No correction changed the pinout of a fitted part |
| C: wiring review, part-centric | 1 agent | every active/polarized part pin by pin against the verified facts, then the required passives |
| D: wiring review, net-centric | 1 agent | every net of both boards: schematic netlist vs. PCB pad nets (scripted, 0 mismatches), each pin against the facts; symbol and footprint definitions read separately |
| Reconcile | main session | C and D merged; every finding reported by only one of them re-checked against the netlist, the PCB and the PDF (column "Source") |

Design data used: `kicad-cli sch export netlist` for both schematics; pad → net, side, rotation and position from
the `.kicad_pcb` via pcbnew; symbols in `hardware/lib/louie.kicad_sym`, `lcsc.kicad_sym` and KiCad stock libraries;
footprints in `hardware/lib/*.pretty` and KiCad stock; `hardware/bom/parts.csv`.

## 2. Result in short

- **No errors.** No part is connected incorrectly. Datasheet pinout, symbol pins, footprint pads and PCB pad nets agree
  for every IC, transistor, diode and connector on both boards. Polarized parts are oriented correctly, and every
  part is within its absolute maximum ratings at VSYS 5.5 V, VBUS 5 V and 3V3.
- **12 warnings** (section 4): deviations from datasheet recommendations or marginal levels. The most important ones
  before ordering are W1 (SENSE overvoltage), W4 (150 µA through the LIS2DH12 SA0 pull-up), W6/W7/W8 (decoupling
  and EN RC far from the pins) and W11 (IO9 without external pull-up). Most can be fixed with one 0402 part or a
  placement change. W4 can alternatively be fixed in firmware.
- **The three known open points** are resolved or assessed (section 5): A18 polarity is answered, the 5.5 V
  tolerance is verified, and the EN RC position is a warning (W6).

## 3. Checked and correct

| Part | Checked | Result |
|---|---|---|
| U1 ESP32-C6-MINI-1 | all 53 pads: symbol ↔ MOD Table 3-1 ↔ footprint ↔ PCB net; IO assignment vs. [main-board-c6.md](main-board-c6.md) 2.3; EPAD 49 and corners to GND; pad 1 at the antenna end; EN 10 k / 1 µF; IO8 10 k pull-up; dividers into ADC pins ≤ 2.75 V | correct (footprint geometry also checked against MOD Fig. 11-1, closes part of A11) |
| U2 DRV8213DSG | pins 1 VM, 2 OUT1, 3 OUT2, 4 GND, 5 IN2, 6 IN1, 7 GAINSEL, 8 IPROPI, EP 9 = GND; VM on VSYS (1.65–11 V); C4 100 nF 1.1 mm from VM; GAINSEL = GND → 205 µA/A; R1 1.24 k → ITRIP ≈ 2.0 A (1.74–2.30 A with tolerances) | correct |
| U3 AP2112K-3.3 | SOT-25 (K package): 1 VIN, 2 GND, 3 EN, 4 NC, 5 VOUT; EN on VIN; CIN/COUT 1 µF within 2 mm | correct |
| U4 LIS2DH12 | pins per LIS Table 2; LGA-12 pin 1 position with rotation 180°; CS = 3V3 (I²C); SA0 = GND (0x18); RES pin 5 and 6–8 to GND; Vdd = Vdd_IO = 3V3; INT1 → IO2, INT2 NC; I²C pull-ups 10 k | correct (see W4, W5, W8) |
| U5, U102 USBLC6-2SC6 | 1/6 D+, 3/4 D−, 2 GND, 5 VBUS on both boards | correct (see W9) |
| U6 TPS22918 (DNP) | 1 VIN = VSYS, 2 GND, 3 ON = IO15, 4 CT open, 5 QOD open, 6 VOUT; ON pull-down R22 | correct (fit R22 together with U6, N3) |
| Q1, Q101 AO3401A | SOT-23 1 G, 2 S, 3 D; D = battery, S = VSYS, G = VBUS with pull-down: on without USB, off with USB; a reversed cell is blocked by the body diode (main board) | correct |
| D2 SS34F, D102 SS34 | cathode (pad 1, silk bar) on VSYS, anode on VBUS; 40 V / 3 A | correct |
| D1, D101 LEDs | cathode pad 1 on GND / STAT; anode through 1 k | correct (see N2, N5) |
| J4, J101 TYPE-C-31-M-12 | A1/A12/B1/B12 GND, A4/A9/B4/B9 VBUS, CC1/CC2 each 5.1 k to GND, both D+/D− rows connected, SBU NC, shell to GND; pad order vs. HRO drawing | correct |
| J102 JST-PH | pad 1 = BAT (+), pad 2 = GND | correct (polarity of the purchased pack still to check) |
| U101 MCP73831-2ACI | 1 STAT, 2 VSS, 3 VBAT, 4 VDD = VBUS, 5 PROG; R103 2 k → 505 mA; C101/C102 4.7 µF | correct (see N7) |
| F1 BSMD0805-050-6V (DNP) | Vmax 6 V ≥ 5.5 V, not polarized | correct |
| Netlist vs. PCB | every pad of every footprint on both boards | 0 mismatches |

## 4. Findings

Severity: **error** = wrong connection or rating violation; **warning** = deviation from a datasheet recommendation
or marginal level; **note** = observation or documentation issue. Source: C, D or C+D. "re-checked" means
the main session confirmed a single-source finding against the design data and the PDF.

### Warnings

| # | Source | Finding | Evidence | Recommended fix |
|---|---|---|---|---|
| W1 | C+D | **SENSE (IO3) sees up to VSYS.** R5 100 k connects OUT_A directly to IO3. R3 sits on OUT_A, so nothing divides the voltage. With the motor driving OUT_A high, IO3 reaches about 4.2–5.5 V and only the internal ESD diode holds it, injecting roughly 10–20 µA into 3V3. | ESP32 VIH max = VDD + 0.3 V (MOD Table 6-3); no injection-current limit is specified. Netlist: R5 /OUT_A–/SENSE, /SENSE only at U1 pad 6. | Raise R5 to 470 k–1 M (≤ 4 µA; the lever level stays about 3 V because the input leakage is ≤ 50 nA), or add a divider resistor from SENSE to GND. Check the lever level on the prototype (A4). |
| W2 | C+D | **VBUS node floats up from Schottky leakage.** Without USB, only R14 + R15 = 200 k (main) or R105 100 k (charger) pull the VBUS node down. D2/D102 reverse leakage from VSYS rises to tens of µA when warm, lifting the Q1 gate and VBUS_DET. Q1 then conducts only partly (body diode, 0.7 V loss) and VBUS_DET may read HIGH. | SS34F IR typ. 1.4 µA at 25 °C, about 75 µA at 75 °C (MDD Fig. 2); netlist /VBUS_J4. | Add a 10–22 k bleed from VBUS_J4 to GND (draws current only with USB), or lower R14/R15 (combine with W3). Same on the charger: R105 → 10–22 k. Measure VBUS_DET and VSYS on battery when warm. |
| W3 | C+D | **VBUS_DET is not a guaranteed digital HIGH.** 100 k/100 k gives 2.50 V at 5.0 V and 2.375 V at 4.75 V; VIH min is 2.475 V. | MOD Table 6-3; already noted under A5. | R14 → 68 k (5.5 V → 3.27 V, 4.75 V → 2.83 V), or use VBUS_DET only through the ADC. |
| W4 | C+D, re-checked | **LIS2DH12 SA0 to GND draws about 150 µA continuously.** SDO/SA0 has an internal pull-up of typ. 20–30 k that can only be switched off in software (CTRL_REG0 = 0x90). The setting is lost on every power-up. That is about 20× the deep-sleep budget. | LIS p.9 Table 3, p.33 Tables 25–26; U4 pad 3 = /GND. | a) Firmware writes CTRL_REG0 = 0x90 at every start (no hardware change), or b) tie SA0 to 3V3 → address 0x19 (update parts.csv, main-board-c6.md 5.2 and the firmware). Recommendation: b), because it cannot be forgotten. |
| W5 | C+D | **J2 INT is shared between LIS2DH12 INT1 (push-pull) and an external switch to GND.** With U4 fitted, INT idles low (default active-high), so a switch to GND has no effect. An internal pull-up on IO2 fights the push-pull output, and with INT_POLARITY = 1 a closed switch shorts the driven-high output. | LIS p.21 Table 13 (push-pull), p.38 Table 43 (INT_POLARITY default 0 = active-high). Netlist /INT: U4-12, U1-5, J2-5. | Keep INT active-high, wake IO2 on HIGH without an internal pull-up. Allow an external INT switch only with U4 not fitted (document it on J2), or add a ≥ 10 k series resistor between U4 INT1 and /INT. |
| W6 | C+D | **EN RC far from EN pad 8** (open point 3). R2 pad is 6.9 mm and C12 pad 7.1 mm from U1 pad 8 in a straight line. J3 pad 1 adds a further EN branch about 10 mm away. EN has no tracks yet, so the routed length is unknown (≥ 15 mm expected, through vias). | HDG §1.3.3 (p.7, PDF 10): RC 10 k / 1 µF and "keep the CHIP_PU trace as short as possible"; MOD Fig. 9-1 shows the RC at the EN pin. There is no millimetre rule. Positions from the PCB dump. | Move at least C12 next to pad 8 (the capacitor at the pin does the filtering; R2 can stay further away). Otherwise route EN on an inner layer next to solid GND, keep the J3 branch short, and test resets with ESD and motor PWM on the prototype. |
| W7 | C+D | **No capacitor near the module 3V3 pad.** The nearest is C11 at about 14 mm (C9 16 mm, C10 19 mm); Espressif shows 22 µF + 0.1 µF at the module. | MOD Fig. 9-1, HDG §1.3.2; mitigated by 10 µF + 1 µF + 10 nF + 4 × 0.1 µF inside the module (MOD Fig. 8-1). | Add 100 nF (ideally plus 10 µF) at pad 3 if there is space, otherwise a wide 3V3 pour. Measure the ripple during Wi-Fi TX on the prototype. |
| W8 | C+D | **LIS2DH12 decoupling about 6 mm away.** C15 100 nF is about 6 mm from Vdd/Vdd_IO (pins 9/10); the datasheet asks for 100 nF + 10 µF as close as possible. | LIS p.20 Fig. 5; PCB positions. | Move C15 next to U4 pins 9/10. A separate 10 µF is optional (C9 is on the rail). |
| W9 | C (warning), D (note) | **USBLC6 VBUS pin 5 without 100 nF.** On the main board VBUS_J4 has no capacitor at all (deliberate per [main-board-c6.md](main-board-c6.md) 2.4). On the charger C101 is about 8 mm from U102 pin 5. | ST USBLC6 p.9 Fig. 18 (100 nF at pin 5; pin 5 is the clamp reference). | Add 100 nF 0402 directly at U5 pin 5 (and at U102). 100 nF is uncritical for the USB inrush limit (10 µF). |
| W10 | C (warning), D (note) | **No footprints for USB D+/D− series resistors.** | HDG §1.3.13: reserve 22–33 Ω in series near the module. | Add 0402 footprints (0 Ω / 22 Ω) near U1 pads 17/18 if there is space; otherwise accept and test enumeration. |
| W11 | C only, re-checked | **IO9 (BOOT) without external pull-up.** /BOOT goes only to U1 pad 23 and J3 pad 3; only the weak internal pull-up holds it. | HDG strapping section: a pull-up on GPIO9 is recommended, and no large capacitance. Netlist /BOOT. | Add 10 k from IO9 to 3V3 (0402 next to R11). |
| W12 | C (warning), D (note) | **Low cell: 3V3 drops below the module minimum of 3.0 V.** AP2112K dropout is up to 250/400 mV at 600 mA. At VSYS 3.0–3.3 V (minus the Q1 drop), 3V3 is about 2.8–3.1 V. There is no supervisor, only the EN RC. | AP p.8 (VDROP); MOD Table 6-2 (VDD33 3.0–3.6 V); HDG §1.3.3 recommends a reset IC for slowly falling supplies (battery). | Firmware: brownout detector on, cut-off ≥ 3.4 V under load (A3). Optional: footprint for a 3.0 V supervisor on EN (DNP). The doc statement "C6 runs from 3.0 V" means 3V3 ≥ 3.0 V, not VSYS. |

### Notes

| # | Source | Finding | Recommendation |
|---|---|---|---|
| N1 | C, re-checked | IN1/IN2 (IO18/IO19) have weak pull-ups during reset (SOC Table 2-2: WPU) → DRV8213 brakes. This confirms F17. | Decide F17 as planned (test-hardware 4.4). |
| N2 | C | D1 green 0402 at 3.3 V through 1 k: with VF typ. 2.8 V (representative datasheet) only about 0.5 mA, possibly dark with a worst-case part. | Pick a specific LCSC LED with a known VF, or R9 → 220–330 Ω. |
| N3 | C+D | U6 must always be fitted together with R22 (ON must not float; IO15 has no pull). JP1 is an R_0603 footprint (0 Ω), not a solder bridge. VLED needs F1. | Assembly note in parts.csv. |
| N4 | C | VBAT_ADC measures VSYS, not the cell (with USB about 4.6 V). | Qualify the reading with VBUS_DET in firmware; document it. |
| N5 | D, re-checked | KT-0603R datasheet: pad ① = anode. KiCad LED_0603 pad 1 = cathode. The netlist is correct (pad 1 = STAT = K), but the JLC placement must follow the cathode mark, not the vendor pad number. | Check D101 (and D1) orientation in the JLC placement preview. |
| N6 | C+D | Charger board: no reverse-polarity protection. A reversed JST pack destroys U101 (VBAT abs min −0.3 V). The main board is protected by Q1. | Already L3: "+" on the silkscreen at J102/TP101, check the cell before plugging in. |
| N7 | C+D | MCP73831 at 500 mA in SOT-23-5: about 0.75 W → thermal regulation (slower charging, not harmful). | Already L2: keep it, or 3.3 k (300 mA); copper area. |
| N8 | C+D | ITRIP ≈ 2.0 A is correct; the R8/C14 filter delays the IPROPI node by about 0.2 ms. OCP (≥ 4 A) covers hard faults. | Acceptable. |
| N9 | D | OUT_B feeds about 0.2 mA back into 3V3 through R4 while the motor drives OUT_B high (documented in main-board-c6.md 2.5). | Firmware invariant: ESP active whenever the motor runs. |
| N10 | D | 2 × 47 µF behind D2 exceed the USB plug-in limit (10 µF) (already noted as unverified in idea-usb-c-main-board.md). | Accept; uncritical in practice. |
| N11 | D, re-checked | USB-C footprint (copy of the KiCad stock footprint): outer pads 6.50/4.90 mm apart instead of 6.40/4.80 mm in the HRO drawing; pads longer. Signal order is correct. | No change needed (widely used footprint). |
| N12 | D | J7: 3.3 V data into 5 V NeoPixels (VIH ≈ 0.7 × VLED) is marginal on USB power. | 3.3 V-compatible LED types or a level shifter (J7 is optional). |
| N13 | C+D | Capacitors: all stated ratings ≥ 10 V on ≤ 5.5 V nets. Missing voltages in parts.csv (C10–C14, C16). X5R DC-bias derating: C1/C2 47 µF at 5 V give about 50 %. C101/C102 4.7 µF 0603 fall below the 4.7 µF that MCP73831 requires. | Add voltages; C101/C102 → 10 µF. |
| N14 | C, re-checked | Module antenna end about 6 mm inboard of the −x board end (board x 76.98, module from about 82.9). HDG wants the antenna at the board edge. | Already F1/T4 (RSSI test). |
| N15 | C | Docs: idea-usb-c-main-board.md:52 "AP2112K max. 6 V (unverified)" → verified 6.5 V abs / 6.0 V recommended; charger-board.md §2 "3 × 47 µF" → 2 × 47 µF; main-board-c6.md has no section 2.7 (supply range is in 3.2 / A3). | Update the docs when they are next touched. |

## 5. Known open points

**A18 – LIS2DH12 INT polarity.** Answered: INT_POLARITY (CTRL_REG6 bit 1) resets to 0 = active-high; INT1/INT2
are always push-pull (LIS p.38 Table 43, p.21 Table 13). Active-high matches the SENSE wake (IO3 HIGH), so both wake
sources wake on HIGH. Remaining point: J2 sharing (W5).

**5.5 V tolerance** (marked unverified in idea-usb-c-main-board.md): verified.

| Part | Pin | Abs max | Recommended | 5.5 V |
|---|---|---|---|---|
| AP2112K | VIN, EN | 6.5 V | 2.5–6.0 V (EN VIH up to 6.0 V) | OK |
| AO3401A | VDS / VGS | −30 V / ±12 V | no table in the datasheet | OK |
| DRV8213 | VM / IN, GAINSEL | 12 V / 5.75 V | 1.65–11 V / 0–5.5 V | OK (IN driven at 3.3 V only) |
| TPS22918 | VIN | 6 V | 1–5.5 V | OK, at the recommended limit |
| USBLC6-2SC6 | VBUS | VBR min 6 V | – | OK, 0.5 V margin |
| BSMD0805-050-6V | – | Vmax 6 V | – | OK, 0.5 V margin |
| MCP73831 | VDD | 7.0 V | 3.75–6.0 V | OK |
| LIS2DH12, ESP32-C6 | supply / IO | 4.8 V / 3.6 V | ≤ 3.6 V | only from 3V3; all 5 V-domain signals into the ESP32 go through dividers, except SENSE (W1) |

**EN RC at the module corner** (since 2026-11-09, `placement.py:52-53`): assessed as warning W6. Espressif gives the
values (10 k / 1 µF, unchanged) and says to keep the CHIP_PU trace as short as possible, but no millimetre limit.
At about 7 mm from the pad plus the J3 branch, the long part of the EN net is unfiltered, high impedance (10 k) and
exposed to motor PWM and ESD. Recommendation: move C12 next to pad 8; R2 may stay where it is.

## 6. Not verified, and why (state `32a3535`)

- **Routed lengths and layer changes** (EN, 3V3 to pad 3, USB pair impedance, thermal vias in the EPADs): the main
  board has no routing for these nets yet (F15, another session is routing). Re-check after routing.
- **ESP32-C6 injection current** (W1): Espressif specifies no limit; the assessment rests on VIH max.
- **Schottky reverse leakage at our operating point** (W2): only typical curves at 10 % / 100 % VR exist, so measure on
  the prototype.
- **AO3401A pin numbers**: the datasheet names leads only (G/S/D, top view with dot). Pin 1 = G, 2 = S, 3 = D follows the
  JEDEC SOT-23 convention and matches the KiCad symbol/footprint and JLC practice.
- **D1 green LED**: no fixed part number, only checked against a representative datasheet (polarity convention and VF).
- **Per-pin wake levels on the C6 in deep sleep** (IO2 and IO3 both HIGH): an ESP-IDF/TRM question, not in the
  datasheets. Since both are active-high, ext1 ANY_HIGH is enough.
- **USB inrush and NeoPixel VIH**: from the USB specification and typical WS2812 data, not from the project datasheets.
- **Battery pack polarity at J102**: JST defines none; depends on the purchased pack.
- **Official ST documents** for LIS2DH12 and USBLC6: st.com blocked the automatic download; the LCSC copies are
  unmodified ST documents (LIS2DH12 Rev 6, USBLC6-2 Rev 5 from 2011). A newer USBLC6 revision exists but was not
  compared.
- **Mechanical details** of the USB-C shell slots and the JST mounting pads: only the electrical pad mapping and the pad
  spacing were compared (N11).

## 7. Delta review: power path for VSYS up to 6.6 V (2026-11-09)

Same method on a smaller scale: Agent A (SPX3819 datasheet, every VSYS part at 6.6 V, F1 candidates), Agent B
(independent verification: about 60 verified, 8 corrected, 9 unverifiable – all of them LCSC stock/price), then
Agent C (part-centric) and Agent D (net-centric, old vs. new netlist) on the netlist and PCB exported from the main
checkout. Facts: [datasheet-facts.md](datasheet-facts.md) G4. C and D agree on every warning. The main session
re-checked the U6 output net, the U3/U6 pad nets and the SPX3819 capacitor statement.

### 7.1 Checked and correct

- **U3 SPX3819M5-L-3-3** (C9055): 1 VIN = VSYS, 2 GND, 3 EN = VSYS, 4 BP open, 5 VOUT = 3V3. Pinout is identical to the
  AP2112K. VIN/EN abs max ±20 V, operating 2.5–16 V, EN may be tied to VIN (SPX p.2, Fig. 1). BP open is allowed (only more noise).
- **U6 SPX3819M5-L-5-0** (DNP, LCSC **C13417**): 1 VIN = VSYS, 2 GND, 3 EN = IO15, 4 BP open, 5 VOUT = VLED_SW.
  EN VIH min 2.0 V / VIL max 0.4 V, EN current ≤ 20 µA (SPX p.3): 3.3 V from IO15 is a valid HIGH, R22 100 k gives a
  valid LOW, open EN = off. EN stays ≤ VIN because 3V3 is derived from VSYS.
- **R6/R7 680 k / 470 k**: 6.6 V → 2.70 V at IO0, matching the firmware constant 2.447 (`louie_v1.rs`).
- **6.6 V ratings:** DRV8213 VM (12 V abs / 11 V rec), AO3401A (−30 V, ±12 V), SS34F (40 V), C1/C2/C8 16 V, SPX3819 – OK.
  The removed TPS22918 (6 V abs) and BSMD0805-050-6V (6 V) would have violated 6.6 V, so the change was necessary.
- **Netlist vs. PCB** in the new state: no mismatch; all net differences from the old netlist are explained by the
  stated changes (D).

### 7.2 New and changed findings

| # | Source | Severity | Finding | Recommended fix |
|---|---|---|---|---|
| W13 | C+D, re-checked | warning | **U6 has no capacitor at its output pin.** /VLED_SW = U6 pin 5 + F1 only; the only capacitor (C17) sits about 15 mm away behind the PTC (up to 0.85 Ω). Without F1, U6 runs with no output capacitor at all. SPX p.7: an output capacitor is required for stability. | Add a 1–2.2 µF footprint (DNP, fitted together with U6) directly at U6 pin 5. Assembly rule: U6 ⇒ R22 + F1 + Cout. |
| W14 | C+D, re-checked | warning | **SPX3819 stability with all-ceramic outputs not confirmed.** The datasheet gives no minimum COUT, no ESR range and no word on MLCC. It mentions 2.2 µF aluminium or 1 µF tantalum and recommends bench testing (SPX p.7). U3: C11 1 µF and C9 10 µF within about 2 mm, C10 100 nF (all MLCC). The capacitance is ample; the open risk is very low ESR. | Bench test on the dev board or prototype: load step 0 → 300 mA at VSYS 3.6 V and 6.6 V, look for ringing on 3V3. Insurance: an option for C9 as tantalum/polymer, or 0.5–1 Ω in series with C9. The BOM alternative MIC5219 needs the same test. |
| W15 | C+D | warning | **Q1 does not separate the battery from USB above about 5.2 V.** With USB (VSYS ≈ 4.6 V through D2) and fresh 4 × AA (6.4 V) or 4 × NiMH (5.6 V), the body diode conducts and VGS ≈ −0.6…−1 V leaves the channel partly on. The board runs from the cells; Q1 dissipates about 0.3 W at 0.5 A and up to about 1.6 W at a 2 A stall (PD 1.4 W ≤ 10 s, about 1 W steady). No abs max exceeded; the "blocks with USB" statement no longer holds. | a) document "remove AA cells on USB", firmware detects VBUS_DET = 1 with VSYS > 5 V and limits the motor current · b) back-to-back P-FET or ideal-diode controller · c) accept for alkaline, measure Q1 temperature at stall with NiMH + USB. Correct the Q1 description in parts.csv. |
| W16 | C+D | warning | **J7 data level** (was N12): VLED is now regulated to 5.0 V, so VIH (0.63 × 5 V = 3.15 V for V5 types, 3.5 V for 0.7 × VDD types) is above the guaranteed ESP32 VOH min of 2.64 V. | Level shifter (e.g. 74AHCT1G125, DNP) on IO23, or the adjustable SPX3819 set to about 4.3–4.5 V, or a first pixel at VLED − diode. |
| W17 | C (D partly) | warning | **U6 short circuit and heat.** U6 limits at 800–950 mA, below the undefined trip zone of a 0.5 A / 1 A PTC, so F1 will usually not trip. A J7 short ends in thermal-shutdown cycling (about 5 W). θJA 191 °C/W allows only about 0.45 W (≈ 280 mA at 6.6 → 5 V). U6 (bottom) is 3.3 mm from U3 (top). | Choose F1 to match U6 (e.g. about 0.2 A hold, ≥ 8 V), or treat U6 as the protection and document it; keep the brightness cap and lower it above 6 V. |
| W1 | C+D | warning (worse) | SENSE clamp current rises to about 30 µA at 6.6 V. | Unchanged: R5 → 470 k–1 M. |
| W2 | C+D | warning (worse) | D2 now sees up to 6.6 V reverse without USB; the floating VBUS_J4 node can approach the USBLC6 VBR (6 V) when warm (µA, harmless). | Unchanged: 10–22 k bleed on VBUS_J4. |
| W6 | C+D | warning (worse) | **EN RC now about 12 mm** (C12 12.0 mm, R2 12.6 mm straight line) from EN pad 8, on the opposite module edge; routed at least 12–16 mm. The docs' "about 10 mm" understates it; the J3 branch got shorter. | C12 (or an extra 10–100 nF) as close to pad 8 as possible, e.g. one bottom part under pad 8; otherwise route EN through a via on an inner layer between GND and test reset immunity. |
| W12 | C+D | warning (worse) | **More dropout:** SPX3819 180/350/450 mV (typ / max 25 °C / max) at 150 mA, about 290/610 mV at a 380 mA TX peak, against about 160/255 mV for the AP2112K. VSYS needs about 3.5–3.6 V for 3V3 ≥ 3.0 V; firmware `VSYS_MIN_MV = 3300` is too low. | Cut-off ≥ 3500–3600 mV under load, brownout detector on; the optional supervisor gains weight. |
| N16 | C+D | note | R4 back-feed into 3V3 rises to about 0.33 mA at 6.6 V; SPX3819 sink capability is unspecified. | Keep the firmware invariant (ESP active while the motor runs). |
| N17 | C | note | U3 quiescent current 90 typ / 150 max µA (190 µA over temperature): worst-case deep-sleep budget about 2× the docs. U3 at 6.6 V reaches θJA limits at about 135 mA average. | Measure deep-sleep current and U3 temperature on 4 × AA. |
| N18 | C+D | note | F1 footprint (0.97 × 1.40 mm pads, 0.9 mm gap) vs. candidate land patterns (1.0 × 1.5 mm, 1.1–1.2 mm gap): acceptable. Candidates ≥ 8 V (proposals, stock not confirmed): TECHFUSE SMD0805-050-16V **C2833485** (0.6 mm high), BNstar SMD0805-050C-16V C2760262, R+O SMD0805-050-16 C46640986. | Select F1 together with W17. |
| N19 | C+D | note | Stale fields and texts: U6 without LCSC number (C13417); F1 value "0.5A 16V" vs. parts.csv "≥ 8 V, to select"; C8/C4 voltage only in parts.csv; `board/mod.rs` comment still says 470 k / 470 k; placement.py comment "AP2112K"; main-board-c6.md 2.5 (0.2 mA at 5.5 V) and 11.9 ("about 10 mm"). | Update when the files are next touched. |

### 7.3 Not verified (delta)

- SPX3819 with MLCC-only outputs, its behaviour with VOUT > VIN, its sink capability and its thermal-shutdown
  threshold: not specified in Rev 2.0.5, so bench tests are needed.
- Q1 operating point with USB + 4 × AA: estimated from VGS(th) and VSD only.
- WS2812 VIH (0.63 vs. 0.7 × VDD): no LED datasheet in `datasheets/`.
- Routed lengths (EN, 3V3, VLED_SW, IO15): the stored PCB is unrouted (126 unconnected).
- LCSC stock and price for C9055, C13417 and the F1 candidates: the LCSC API was not reachable.
- Real θJA of U3/U6 on the 14.1 mm 4-layer board inside the sleeve.

### 7.4 Status of fixes (2026-11-09, late evening)

Changed in the main checkout after the delta review and confirmed in the schematic netlist (not yet on the PCB):

| Finding | Change | Status |
|---|---|---|
| W1 | R5 = 470 k (clamp current about 6 µA at 6.6 V) | fixed in schematic |
| W4 | U4 pin 3 (SA0) on +3V3 → I²C address 0x19; GND ties pins 5–8 | fixed in schematic; check that docs and firmware use 0x19 |
| W12 | firmware `VSYS_MIN_MV = 3600` | fixed |
| N19 | U6 LCSC C13417; stale comments in board/mod.rs, placement.py, gen_main_pcb.py | fixed |

| W13 | C18 2.2 µF at the U6 output (commit `8ce96f0`) | addressed |
| W16, W17 | U6 now adjustable SPX3819 at 3.95 V (R23/R24); F1 and JP1 dropped, U6 limits the current | addressed; the adjustable circuit was **not** reviewed against the datasheet yet |
| W15 | documented, firmware lowers the stall limit to 0.8 A on USB (F28) | accepted for this revision |

Still open: W6 (EN RC, F22) and the SPX3819 load-step test (W14, F27, test-hardware.md 4.7).
