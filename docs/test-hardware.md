# Test setup (breadboard) and prototype boards

Status: 2026-11-06 · Prices retrieved on 2026-11-06, gross incl. 19 % VAT unless stated otherwise.

Markers: **(verified)** = source read or recalculated from the project files · **(unverified)** = estimate,
secondary source, or not checked in the datasheet.

References: pinout, strapping, wake [hauptplatine-c6.md](hauptplatine-c6.md) 2.3–2.5, DRV8213
[hauptplatine-c6.md](hauptplatine-c6.md) 3, motor stage and lever detection [hardware-konzept.md](hardware-konzept.md)
5.1/5.2, part values [teile.csv](../hardware/bom/teile.csv), firmware [firmware-architecture.md](firmware-architecture.md)
(3.1 board `board-devkitc-c6`, 11 step 0), tests T1–T9 and assumptions in [offene-punkte.md](offene-punkte.md),
manufacturing costs [kostenabschaetzung.md](kostenabschaetzung.md).

## Summary

- **Decision (2026-11-06):** **No motor driver on the breadboard** (no MP6550, DRV8833, INA219, MOSFET). The test
  setup has two purposes: **pre-order checks** that reduce the risk of the PCB design (section 4) and
  **software development** in LED mode (section 5). Motor control, stall detection and current calibration are done
  on the 5 prototype boards (section 6, 7).
- **Buy only the dev board:** **Waveshare ESP32-C6-DEV-KIT-N8**, 13.90 € incl. shipping on Amazon.de (verified),
  same module ESP32-C6-WROOM-1-N8, pinout DevKitC-1-N8-compatible per seller. Alternative: Espressif
  **ESP32-C6-DevKitC-1-N8** (approx. 21 € incl. shipping at Reichelt, unverified).
- **Everything else exists:** parts drawer (R, C, buttons, switches, LEDs, pots), the real Looping Louie (old and new
  model), lab power supply (adjustable, current limit, display), multimeter with scope function, classic ESP32
  (BTHome simulator), ESP8266 (extra Wi-Fi clients), Shelly BLU Button.
- **Answered before ordering (section 4):**

| Check | Design value it can change |
|---|---|
| 4.1 Motor current, start-up, stall, winding (lab supply only) | R1 / ITRIP 2 A, C1/C2, trace widths (A16), LDO/brownout budget (A3), A2 |
| 4.2 Lever network R3/R4/R5 on the real Louie | R3/R4/R5 values, board orientation (diode in the new model), A4 |
| 4.3 Boot, strapping, deep-sleep wake with the real external parts | IO8/S4, R22, VBUS divider R14/R15, wake pin assignment |
| 4.4 IO18/IO19 level in reset, boot and deep sleep (F17) | 3.3 k pull-downs on IN1/IN2 yes/no |
| 4.5 ADC accuracy VSYS 470 k/470 k + 100 nF and VBUS 100 k/100 k | R6/R7/C13, R14/R15, resistor tolerance (A5) |

- **Only the prototype answers:** footprints and assembly, antenna in the compartment, DRV8213 (ITRIP, IPROPI
  accuracy, autosleep, heating), LDO under real load, quiescent current, mechanics (section 6).

---

## 1. Purpose and scope

| PCB risk | Testable before ordering? | How | Design value it can change |
|---|:---:|---|---|
| Motor current: running, start-up peak, stall | **yes** | 4.1: lab supply directly on the battery contacts, shunt + scope | R1 (ITRIP 2 A), C1/C2 bulk caps, trace widths and vias (A16), A2 |
| VSYS droop at motor start, LDO/brownout budget | **partly** | 4.1: stall current × estimated LiPo internal resistance (calculation) | A3: LDO choice, firmware ramp; real check only on the board |
| Lever detection network on the real Louie | **yes** | 4.2: R3/R4/R5 at the battery contacts, no driver | R3/R4/R5, orientation of the board (diode in the new model), A4 |
| Deep-sleep wake on IO3 / IO2 / IO4 (and S1 on IO5) | **yes** | 4.3 with the real external parts | wake pin assignment, VBUS divider ratio |
| Boot/strapping with the real external parts (IO8 incl. pressed S4, IO9, IO15, IO4, IO5) | **yes** | 4.3 | S4 on IO8 or another pin, R22 |
| Reset and deep-sleep level of IO18/IO19 (F17) | **yes** | 4.4: 200 k pull-down emulates the DRV8213 input | 3.3 k pull-downs on IN1/IN2 |
| VSYS divider 470 k/470 k + 100 nF with the C6 ADC; VBUS divider 100 k/100 k | **yes** | 4.5: lab supply sweep vs. multimeter | R6/R7/C13, R14/R15 (A5) |
| Footprints, rotation, polarity, assembly | no | datasheet check, JLC preview (section 6) | – |
| Antenna in the compartment, RSSI (T4, A7) | no | prototype | – |
| DRV8213: IPROPI accuracy (A6), autosleep leakage, heating, ITRIP behavior | no | prototype; R1, R8, C14 are swappable 0402 parts | – |
| LDO AP2112K under real load, power path, USB-C | no | prototype | – |
| Deep-sleep quiescent current of the board | no | prototype; the dev board has its own LDO, USB bridge and LEDs | – |

**Not an order gate:** whether the C6 handles 8 phones + BLE scan and how large the firmware gets are **software
questions**. No other module fits the AA format; the order uses the **H8** (F14). Both are measured in section 5.

**Recoverability:** if USB on J4 fails on the prototype, flashing still works via the service pads **J3** (EN, TXD,
BOOT, GND, RXD) with a USB-UART adapter (hauptplatine-c6.md 2.4, A14).

---

## 2. Shopping list and parts drawer

### 2.1 Buy

| Part | Purpose | Qty | Price | Source |
|---|---|---:|---:|---|
| **Waveshare ESP32-C6-DEV-KIT-N8** | device under test (WROOM-1-N8, 8 MB) | 1 | 13.90 € incl. shipping (verified, 2026-11-06) | Amazon.de, seller Bolin Electronic (Waveshare store) |
| *Alternative:* ESP32-C6-DevKitC-1-N8 | same, Espressif original | 1 | approx. 14.70 € + approx. 5.95 € shipping (unverified) | [Reichelt](https://www.reichelt.de/de/de/shop/produkt/entwicklungsboard_esp32-c6-wroom-1_u-380385) |

- **Why 8 MB:** the board target is the H8. Whether the firmware also fits an N4 is shown by a build with the 4 MB
  partition table (firmware-architecture.md 6.1); it runs the same on the 8 MB board.
- **Waveshare:** one USB-C port with a CH334 USB hub + CH343 UART, so native USB and UART work over one cable
  (verified, seller page). RGB LED pin and GPIO14 availability are **unverified**; assume the same as the DevKitC-1.
- **Do not buy:** motor driver boards, INA219, LiPo/charger, logic analyzer, USB tester, SMD adapters.

### 2.2 Existing devices

| Device | Use |
|---|---|
| Real Looping Louie, old model (1 × C, 1.5 V) and new model (2 × AA, 3 V) | 4.1, 4.2 |
| Lab power supply (adjustable, current limit, current display) | 4.1, 4.2, 4.5 |
| Multimeter with scope function | all checks |
| Classic ESP32 (BLE) | device B: BTHome button simulator with time reference (5.3) |
| ESP8266 (1–n) | extra Wi-Fi stations with WebSocket client (5.3) |
| Shelly BLU Button | T7 (5.3) |

### 2.3 Parts drawer

Values as on the board where a board part is emulated (teile.csv).

| Part | Value | Qty | Used for |
|---|---|---:|---|
| Resistor | **100 k** | 6 | R3 (OUT_A → GND), R5 (SENSE → IO3), R22 (IO15 → GND), R14/R15 (VBUS divider), IO2 pull-down |
| Resistor | **10 k** | 1 | R4 (OUT_B → 3V3) |
| Resistor | **470 k** | 2 | R6/R7 (VSYS divider) |
| Resistor | **200 k** (or 2 × 100 k in series) | 2 | DRV8213 input pull-down emulation (4.4) |
| Resistor | **1 M** | 2 | leakage emulation (4.2) |
| Resistor | **1 k** | 4 | LED series resistors, ISEN filter (R8) |
| Capacitor | **100 nF** | 2 | C13 (VSYS divider), ISEN filter (C14) |
| Shunt resistor | **0.1–0.5 Ω, ≥ 1 W** (e.g. 0.22 Ω or 2 × 0.47 Ω in parallel) | 1 | motor current on the scope (4.1) |
| LEDs | any color | 3 | IO18, IO19 (motor), IO10 (status) |
| Pots | 10 k | 2 | IO0 (VSYS), IO1 (ISEN) in LED mode |
| Switches (or jumpers) | – | 2 | IO3 lever, IO4 USB in LED mode |
| Buttons | – | 5 | S1–S4 (IO5, IO20, IO21, IO8), IO2 INT |
| Silicon diode (1N4148) and Schottky (1N5819) | – | 1 each | diode-in-series emulation (4.2) |
| Breadboard, jumpers, alligator clips | – | – | connection at the battery compartment |

---

## 3. Pinout of the dev board

Goal: **the same GPIO numbers as on the board** ([hauptplatine-c6.md](hauptplatine-c6.md) 2.3). The DevKitC-1 breaks
out all required GPIOs **except IO14** (verified, Espressif user guide: J1 0–8, 10, 11; J3 9, 12, 13, 15–23); for
the Waveshare board this is **unverified**. Board feature: **`board-devkitc-c6`** (firmware-architecture.md 3.1).

| GPIO | PCB net / part | Pre-order checks (section 4) | Software, LED mode (section 5) |
|---|---|---|---|
| IO0 | VBAT_ADC, R6/R7 470 k/470 k + C13 | divider from the lab supply (4.5) | pot wiper (= VSYS / 2) |
| IO1 | ISEN_ADC, R8/C14 | free | pot wiper via 1 k / 100 nF (simulated current, 255 mV/A) |
| IO2 | INT (LIS2DH12 INT1, J2) | button to 3V3 + 100 k to GND (wake, 4.3) | free |
| IO3 | SENSE, R5 100 k | R3/R4/R5 network at the Louie (4.2) | switch to 3V3, 100 k to GND (lever) |
| IO4 | VBUS_DET, R14/R15 100 k/100 k | divider from the lab supply 5 V (4.3, 4.5) | switch to 3V3, 100 k to GND (USB) |
| IO5 | S1 (J6) | button to GND, internal pull-up (4.3) | same |
| IO6 / IO7 | SDA / SCL | free | free (sensor probe reports "no sensor") |
| IO8 | S4 (J6), strapping, R11 10 k | button to GND (4.3) | button to GND (collides with RGB LED, see below) |
| IO9 | BOOT (J3) | BOOT button of the dev board | same |
| IO10 | – (PCB: status LED on **IO14**) | free | status LED + 1 k |
| IO12 / IO13 | USB D− / D+ | USB-C of the dev board | same |
| IO15 | U6 enable, R22 100 k | 100 k to GND (4.3) | free |
| IO16 / IO17 | TXD / RXD (J3) | UART bridge of the dev board | same |
| IO18 / IO19 | MOT_IN1 / MOT_IN2 | 200 k to GND each, scope (4.4) | LED + 1 k from 3V3 to the pin each |
| IO20 / IO21 | S2 / S3 (J6) | free | button to GND |
| IO22 | spare | free | free |
| IO23 | LED data J7 | free | input for the latency reference from device B (5.3) |

**Differences from the board:**

- **IO14 → IO10:** status LED on IO10 (board definition).
- **IO8:** the dev board has its own **10 k pull-up and the RGB LED (WS2812)** on IO8 (verified for the Espressif
  DevKit schematic, unverified for Waveshare). So the IO8 check in 4.3 only tests the case "S4 pressed during reset";
  R11 itself is not new. During play the button sends garbage to the RGB LED; this is harmless. The firmware
  reports only S1–S3 on the dev board.
- **IO4:** in LED mode only a switch (`vbus_divider = None`); in 4.3/4.5 the real 100 k/100 k divider.
- **Supply:** always power the dev board via USB. Do not feed the 5V or 3V3 pin at the same time (verified, Espressif
  user guide). Common ground with the lab supply whenever both are connected.
- **ADC inputs max. 3.3 V.** No lab-supply voltage directly on a GPIO.

---

## 4. Pre-order checks

General rules:

- **Lab supply current limit** 1 A at first power-up, then as stated per check.
- **Stall:** hold the arm for at most **2–3 s**. Old model (1.5 V nominal): voltages above 3 V only briefly (< 2 s,
  no stall).
- **Scope ground** only at the lab supply's negative terminal (shunt low side). If the scope is earthed, the lab
  supply output must be floating (unverified for your devices, check before connecting).
- Enter the results in [offene-punkte.md](offene-punkte.md) (A2–A5, F17, T1, T5).

**Firmware:** small Rust test binaries from step 0 of firmware-architecture.md 11 (proposal:
`louie-fw/examples/{lever_probe,boot_probe,pin_probe,adc_probe}.rs`, feature `board-devkitc-c6`). Fallback: the
ESP-IDF examples `system/deep_sleep` and `peripherals/adc/oneshot_read` with changed pin numbers.

### 4.1 Motor characterization (lab supply, no ESP)

**Goal:** running current, start-up peak, stall current and winding resistance of both models. This sets R1 (ITRIP),
C1/C2, trace widths and the brownout budget.

**Circuit:**

```
Lab +  ── contact 1 (battery compartment) ── lever (closed) ── motor ── contact 2 ──┐
Lab −  ──────────────────────────── shunt 0.22 Ω (≥ 1 W) ───────────────────────────┘
Scope: probe at contact 2 / shunt top, ground at Lab −     I = U_shunt / R_shunt
Multimeter (V): across contacts 1–2 (real motor voltage, without shunt drop)
```

**Procedure:**

1. **Winding resistance:** supply off, multimeter Ω across the contacts, lever closed, arm in 6–8 positions, note
   the **smallest** value (commutator). Null the test leads first. Cross-check: lab supply with 0.3 A limit, arm
   held, R = U_contacts / I (4-wire, more accurate at low Ω).
2. **Running current:** set voltage, output on, let it run 10 s, read the current from the display.
3. **Start-up peak:** arm at rest, scope in single-shot trigger on rising shunt voltage, switch the output on.
   Note peak and time until the running current is reached. Supply limit 3 A for this step.
4. **Stall:** hold the arm 2–3 s, read the current (display and scope). Supply limit 3 A.
5. Note heat and noise.

| Model | Voltage | Running (A) | Start-up peak (A / ms) | Stall (A) | U/R calc (A) | Note |
|---|---|---:|---:|---:|---:|---|
| old | 1.5 V | | | | | |
| old | 3.0 V (briefly, no stall) | | | – | | |
| new | 3.0 V | | | | | |
| new | 3.7 V | | | | | |
| new | 4.2 V | | | | | |
| new | 5.0 V (briefly) | | | – | | |

| Parameter | Old model | New model |
|---|---:|---:|
| Winding resistance cold, minimum (Ω) | | |
| Resistance with lever open | | |

**Why the lab supply is enough:** with 20 kHz PWM the winding smooths the current; the motor sees roughly the
effective voltage d × VSYS (hardware-konzept.md 5.1). The current at a lab voltage U therefore approximates the
board at effective voltage U (unverified; the DRV8213 adds 0.24 Ω Rds(on), hauptplatine-c6.md 3.1). The battery
then delivers roughly d × I_motor on average.

**Consequences (pass criteria and design values):**

- **A2 holds** if the running current at nominal voltage is < 1 A. Otherwise re-evaluate battery size and turbo limit.
- **R1 / ITRIP:** ITRIP = 0.51 V / (R1 × 205 µA/A) (verified, hauptplatine-c6.md 3.1). Stay well below the OCP of
  approx. 4 A.

| R1 (E96) | ITRIP | ISEN scale at the ADC | Use if |
|---|---:|---:|---|
| 1.65 k | 1.51 A | 338 mV/A | stall at the highest used effective voltage < 1.2 A (more resolution, A6) |
| **1.24 k (current)** | **2.01 A** | **254 mV/A** | stall approx. 1.2–2.5 A |
| 1.00 k | 2.49 A | 205 mV/A | stall > 2.5 A and the start-up is too slow at 2 A |
| 825 Ω | 3.02 A | 169 mV/A | only if 2.5 A is clearly not enough; check heat (2 A stall ≈ +63 K already) |

  If the stall current is below ITRIP, the limit is only short-circuit protection and the firmware stall detection
  (≤ 0.5 s) must work on its own. If the start-up peak is above ITRIP, the motor still starts, only more slowly.
- **Trace widths (A16):** the battery-motor path is designed for 2 A. If ITRIP goes above 2 A, re-run the routing gate
  (IPC-2221) and add vias (one 0.3 mm via ≈ 1 A).
- **C1/C2 (2 × 47 µF):** they cover the 20 kHz PWM ripple, not the start-up (that lasts ms; 2 A for 1 ms from 50 µF
  would be 40 V droop). Ripple estimate without help from the battery: ΔV ≈ I × d(1−d) / (f × C), worst case d = 0.5,
  2 A, 50 µF effective (X5R under DC bias, unverified) → approx. 0.5 V p-p. If the measured stall current is
  > 2 A, plan a third 47 µF footprint.
- **VSYS droop / A3:** ΔV ≈ I × (R_i + R_path). LiPo R_i estimate 0.1–0.3 Ω (unverified, higher when cold or empty),
  Q1 + contacts approx. 0.1 Ω. Example 2 A × 0.4 Ω = 0.8 V: a 3.7 V cell drops to 2.9 V, the AP2112K (dropout
  approx. 250 mV) then gives less than 3.0 V → brownout risk. If the calculation is critical: stronger firmware
  ramp (software) or a buck-boost (hardware, A3). Final check only on the board.

### 4.2 Lever detection network on the real Louie

**Goal:** check R3/R4/R5 with the real motor and lever, both models; detect a diode in series; check deep-sleep wake
with ANY_HIGH on IO3 (T1, A4).

**Circuit** (no driver; this is the state with the DRV8213 in coast/autosleep):

```
Dev board GND ──[100 k R3]──┬── contact 1 (OUT_A) ── lever ── motor ── contact 2 (OUT_B) ──[10 k R4]── dev board 3V3
                            └──[100 k R5]── IO3 (SENSE)
optional leakage emulation: 1 M from OUT_A to GND, then 1 M from OUT_B to GND
```

- The DRV8213 outputs are **Hi-Z in coast (0/0)** (verified, hauptplatine-c6.md 3.1). That no output pull-down or
  leakage acts in autosleep is **unverified** (hauptplatine-c6.md 3.2). The 1 M resistors emulate a few µA of
  leakage to show the margin; the final check is on the prototype.
- Expected: lever closed SENSE = 3.3 V × 100 k / (110 k + R_motor) ≈ **3.0 V**; lever open ≈ 0 V (verified, calculation).
- C6 input thresholds: HIGH > 0.75 × VDD = 2.48 V, LOW < 0.25 × VDD = 0.83 V (C6 datasheet DC characteristics,
  unverified, not re-read).

**Procedure:**

1. Multimeter only: resistance and diode test contact 1 ↔ 2 in both directions, lever closed and open.
2. Wire the network. Measure SENSE (at IO3) and OUT_A, lever closed/open, both models.
3. Repeat with the 1 M leakage emulation.
4. Firmware `lever_probe`: IO3 **without internal pull-up/pull-down** (a 45 k internal pull-up would read HIGH with the
   lever open). Log edges every 10 ms; toggle the lever 20 ×. Then deep sleep with ext1 ANY_HIGH on IO3; toggle 20 ×
   and count wake-ups (wake cause in the log after boot).
5. Special case "lever closed when going to sleep" (hauptplatine-c6.md 2.5): test the firmware fallback (wake on
   LOW or timer every 5 s).

| Measurement | Old: closed | Old: open | New: closed | New: open | Expected |
|---|---:|---:|---:|---:|---|
| Resistance contact 1 → 2 / 2 → 1 (Ω) | | | | | closed: winding; open: ∞ |
| Diode test 1 → 2 / 2 → 1 | | | | | same both ways (no diode) |
| SENSE at IO3 (V) | | | | | ≈ 3.0 / ≈ 0 |
| SENSE with 1 M leakage (V) | | | | | ≥ 2.7 / ≤ 0.3 |
| Firmware reads lever (of 20) | | | | | 20 / 20 |
| Wake from deep sleep ANY_HIGH (of 20) | | – | | – | 20 / 20 |

**Pass criterion:** closed ≥ **2.7 V** (margin over 2.48 V), open ≤ **0.5 V** (margin under 0.83 V), also with
leakage emulation; 20/20 reads and wake-ups.

**On failure:**

- **Diode in series (new model):** forward direction at approx. 30 µA costs approx. 0.5 V (silicon) or 0.15 V
  (Schottky) (unverified). With 0.5 V: SENSE = 2.8 V × 100/110 ≈ **2.55 V**, only 70 mV above VIH (verified,
  calculation). Then: R4 10 k → **4.7 k** (2.67 V) or R3 100 k → **220 k** (2.68 V; more sensitive to leakage).
  Emulate with the 1N4148 in series before deciding. In reverse direction SENSE stays 0 V → fix the board
  orientation in the compartment or swap R3/R4 between the contacts.
- **Leakage moves the levels:** lower R3/R4 (more current: R3 47 k / R4 4.7 k ≈ 65 µA) or switch to a comparator (A4
  alternatives).

### 4.3 Boot, strapping and deep-sleep wake with the real external parts

**Goal:** the board's external parts on strapping and wake pins do not disturb boot or download, and every wake
source works (T1, T5, A20).

**Circuit:**

```
IO15 ──[100 k R22]── GND
IO4  ── midpoint of 100 k (from lab +5 V) / 100 k (to GND)     lab − to dev board GND
IO5  ── button S1 ── GND            IO8 ── button S4 ── GND     (internal pull-ups)
IO2  ── button ── 3V3, 100 k to GND (emulates LIS2DH12 INT1, push-pull, active high)
IO3  ── network from 4.2 or switch to 3V3 + 100 k to GND
IO9  ── BOOT button of the dev board
```

**Procedure (firmware `boot_probe`: logs reset reason, wake cause and pin levels at start):**

| # | Case | Repeat | Expected | Result |
|---|---|---:|---|---|
| 1 | Reset (EN) with all parts, nothing pressed | 10 | normal boot | __ / 10 |
| 2 | Reset with **S4 (IO8) pressed** | 10 | normal boot (IO8 matters only for download) | __ / 10 |
| 3 | Reset with S1 (IO5) pressed, with VBUS divider at 5 V and at 0 V | 10 each | normal boot | __ / 10 |
| 4 | Reset with BOOT pressed | 3 | ROM download mode | __ / 3 |
| 5 | Reset with BOOT **and** S4 pressed | 3 | no normal boot (invalid combination, unverified); release → normal boot | __ / 3 |
| 6 | Flash via USB (`espflash`) while S4 is held | 3 | flashing works (USB-Serial-JTAG, unverified) | __ / 3 |
| 7 | Deep sleep, wake via IO3 ANY_HIGH | 10 | wake, cause = ext1 IO3 | __ / 10 |
| 8 | Deep sleep, wake via IO2 (button) | 10 | wake, cause = ext1 IO2 | __ / 10 |
| 9 | Deep sleep, wake via IO4 (lab 0 → 5 V) | 10 | wake, cause = ext1 IO4 | __ / 10 |
| 10 | Deep sleep, wake via S1 (IO5 LOW) together with 7–9 HIGH | 10 | wake (per-pin ext1 level on the C6, unverified) | __ / 10 |
| 11 | IO4 digital level at VBUS 4.75 / 5.0 / 5.25 V | 1 each | HIGH | |

**Pass criterion:** all cases as expected.

**On failure:**

- **Case 2 or 6 fails:** move S4 off IO8 (e.g. to IO22) (A20).
- **Case 10 fails** (no mixed levels in ext1): S1 is not a wake source, or wake S1 via the LP core / a different
  pin (software), no PCB change needed if S1 wake is optional.
- **Case 9 or 11 fails:** VBUS 5 V × 100/200 = **2.5 V**, only 25 mV above VIH 2.48 V; at 4.75 V (USB minimum)
  2.38 V is **below** VIH (verified, calculation; VIH unverified). Change R14/R15 to e.g. **68 k / 100 k** (5 V →
  2.98 V, 4.75 V → 2.83 V, 5.25 V → 3.13 V). R14/R15 also pull down the gate of Q1; check that Q1 still blocks
  (V_GS at VBUS 5 V, D2 drop ≈ 0.4 V, unverified).
- **IO15 with R22 disturbs boot:** unexpected (strapping without eFuse has no effect); report and remove R22.

### 4.4 Reset and deep-sleep level of IO18/IO19 (F17)

**Goal:** know the level of IN1/IN2 during reset, boot and deep sleep. During reset the C6's internal ~45 k pull-ups
pull IO18/IO19 HIGH (verified, hauptplatine-c6.md 3.2); against the DRV8213's internal 200 k pull-down this gives
3.3 V × 200 / 245 ≈ **2.7 V = HIGH → brake** (verified, calculation). IO18/IO19 are **not LP GPIOs**; their pad
state in deep sleep is unverified.

**Why deep sleep matters:** if both inputs are HIGH in deep sleep, the DRV8213 stays awake in **brake**: both outputs
are pulled to GND, so SENSE stays at 0 V → **lever detection and lever wake-up fail**, plus extra quiescent current.

**Circuit:** remove the LEDs from IO18/IO19. **200 k from IO18 to GND and from IO19 to GND** (DRV8213 input
emulation). Scope on IO18 (and IO19 on a second channel if available; otherwise one after the other), trigger on EN
rising. If the 4.2 network is wired, also measure SENSE at IO3 with the lever closed.

**Procedure (firmware `pin_probe`: drives IO18/IO19 LOW as early as possible in `main`, then optional deep sleep):**

| Case | Measure | IO18 | IO19 | SENSE (lever closed) |
|---|---|---|---|---|
| a) Power-up (USB plug) and EN reset | level and duration of the HIGH window from EN release until the firmware drives LOW; both pins rise/fall together? | ___ V, ___ ms | ___ V, ___ ms | – |
| a) Software reset, panic, watchdog reset | same | | | – |
| b) Deep sleep **without** hold | level | ___ V | ___ V | ___ V |
| c) Deep sleep **with** `gpio_hold_en` on LOW before sleeping (+ `gpio_deep_sleep_hold_en` if applicable on the C6) | level | ___ V | ___ V | ___ V |
| Wake-up from c) | glitch at wake? | | | – |

**Decision rule (F17):**

- **Keep without external parts** (option a) if (b) or (c) gives a reliable **LOW** in deep sleep (< 0.5 V, also
  after 10 sleep cycles) **and** the boot HIGH window is short (**< approx. 0.5 s**) with both pins HIGH together
  (brake, no drive). The firmware then uses the variant that works (hold or none).
- **Add 3.3 k pull-downs on IN1/IN2** (option b) if deep-sleep LOW cannot be guaranteed, or if one pin is HIGH alone
  for more than a few µs (drive pulse). 3.3 k against 45 k gives 3.3 V × 3.3 / 48.3 ≈ 0.23 V in reset (verified,
  calculation); cost approx. 1 mA per pin while HIGH.
- With (c) working, SENSE in deep sleep must be ≈ 3.0 V with the lever closed (as in 4.2).

### 4.5 ADC accuracy of the VSYS and VBUS dividers

**Goal:** the 470 k/470 k divider with 100 nF (source impedance 235 k) is accurate enough for the battery cut-off at
3.3–3.4 V (A5); the VBUS divider gives a usable value.

**Circuit:**

```
Lab + ──[470 k R7]──┬──[470 k R6]── GND        Lab + ──[100 k R14]──┬──[100 k R15]── GND
                    ├── 100 nF C13 ── GND                          └── IO4
                    └── IO0
Lab − ── dev board GND; multimeter on Lab + (reference)
```

**Before:** measure the drawer resistors with the multimeter and calculate the real ratio. Drawer parts are often 5 %;
the test checks the ADC and loading error, not the resistor tolerance.

**Procedure (firmware `adc_probe`):** ADC1 oneshot, 12 dB attenuation, **calibrated** (`adc_cali` curve fitting,
formerly `esp_adc_cal`), 16 samples averaged. Log at **10 Hz** (operating rate) and once as a 1 kHz burst (loading
of C13).

| Lab + (multimeter) | VSYS from IO0 at 10 Hz | Error | VSYS at 1 kHz burst | VBUS from IO4 | Error |
|---:|---:|---:|---:|---:|---:|
| 3.00 V | | | | – | |
| 3.30 V | | | | – | |
| 3.60 V | | | | – | |
| 3.90 V | | | | – | |
| 4.20 V | | | | – | |
| 4.75 V | | | | | |
| 5.00 V | | | | | |
| 5.25 V | | | | | |

**Pass criterion:** error **< 2 % or < 50 mV** (whichever is larger) over 3.0–4.2 V with the measured ratio; no
drift at 10 Hz; VBUS readable to ± 0.1 V.

**Background (unverified estimates):** the sampling capacitor of a few pF takes about 40 µV from 100 nF per sample;
τ = 235 k × 100 nF = 23.5 ms, so 10 Hz recharges fully. Pin leakage of some 10 nA × 235 k gives about 10 mV.

**On failure:** smaller divider (e.g. **220 k / 220 k**, 9.5 µA quiescent at 4.2 V instead of 4.5 µA) or larger C13;
specify **1 %** resistors for R6/R7 in teile.csv (tolerance not stated there today; 2 × 1 % → up to approx. 2 % ratio
error, 84 mV at 4.2 V) or a one-point calibration in the firmware.

### 4.6 Results → design

| Result | Changes | Where |
|---|---|---|
| 4.1 stall current, running current | R1, C1/C2 count, trace widths; A2, A3 | teile.csv, routing gate |
| 4.2 SENSE levels, diode | R3/R4/R5, board orientation; A4 | teile.csv, hardware-konzept.md 5.2 |
| 4.3 strapping, wake, IO4 threshold | S4 pin, R14/R15 ratio | hauptplatine-c6.md 2.3/2.4 |
| 4.4 IO18/IO19 levels | 3.3 k pull-downs (F17) | hauptplatine-c6.md 3.2 |
| 4.5 ADC error | R6/R7/C13, tolerance; A5 | teile.csv |

---

## 5. Software development setup (LED mode)

### 5.1 Wiring

| Function | Wiring | Behavior |
|---|---|---|
| Motor IN1 / IN2 (IO18 / IO19) | each: 3V3 → 1 k → LED → pin (LED on when the pin is LOW) | drive/brake scheme as on the board (forward IN1 = 1, IN2 = PWM (1 − d)): **which LED lights = direction, brightness = speed**; brake (1/1) both off, coast (0/0) both on |
| ISEN (IO1) | pot 10 k between 3V3 and GND, wiper via 1 k / 100 nF | simulated motor current at 255 mV/A; turning past the threshold = stall |
| VSYS (IO0) | pot 10 k, wiper direct | wiper voltage = VSYS / 2 (1.5–2.1 V ≙ 3.0–4.2 V) |
| Lever (IO3) | switch to 3V3, 100 k to GND | closed = HIGH, wake ANY_HIGH |
| USB (IO4) | switch to 3V3, 100 k to GND | `vbus_present()` |
| S1–S4 (IO5, IO20, IO21, IO8) | button to GND, internal pull-ups | S4 collides with the RGB LED (section 3) |
| Status LED (IO10) | LED + 1 k to GND | board: IO14 |
| Latency reference (IO23) | wire from device B, common GND | 5.3 |

The firmware is the same as for the board (`board-devkitc-c6`): it drives the DRV8213 scheme; only the LEDs and pots
stand in for driver and motor.

### 5.2 What can be developed and tested

- Rust toolchain, build, flashing, logs (same chip, same GPIO numbers).
- Game logic, modes, dead-man timer, emergency stop, stall reaction (pot), lever logic, sleep/wake, watchdog.
- Web UI, protocol, Wi-Fi STA/hotspot with captive portal and mDNS (T8), with phones and ESP8266 clients.
- BLE: Shelly BLU Button (T7) and the classic ESP32 as BTHome simulator; joker latency.
- OTA with rollback, flash size (N4 vs. H8), heap and stack measurements.

### 5.3 Radio and load tests

**Setup:**

- **Device A (dev board):** Rust test firmware with SoftAP (8 stations), captive DNS, mDNS, HTTP server with
  WebSocket, a state (approx. 250 bytes JSON) to all clients 10 × per second, passive BLE scan (BTHome), 50 ms game
  tick with LEDC 20 kHz (LED mode), task watchdog. The game logic computes the preview of a mode with bots every 30 s.
- **Device B (button simulator):** classic ESP32 (BLE). Sends a BTHome "press" advertisement with a running packet ID
  every 2 s and sets a GPIO at the same time; wire to **IO23 of device A** (GND connected). Arduino with NimBLE or
  ESPHome is enough.
- **Joker latency:** device A timestamps the edge on IO23 and the BLE reception with the same clock (`esp_timer`).
- **Shelly BLU Button (T7):** advertising interval, fixed MAC, legacy advertising, "long" when the hold time is
  reached or on release; hit rate over 100 presses.
- **Clients:** ideally 8 phones/tablets plus a PC load script; missing phones are replaced by **ESP8266** stations
  holding a WebSocket each. One can emulate a hanging phone ("stops reading", firmware-architecture.md 5.4).

| No. | Network | BLE | Load | Duration |
|---|---|---|---|---|
| F1 | STA in home network | off | 8 WS, 10/s | 2 h |
| F2 | STA in home network | passive scan | 8 WS, 10/s, button every 2 s | 2 h |
| F3 | SoftAP, 8 stations | passive scan | as F2, LEDs in game tick | 2 h |
| F4 | SoftAP + STA (Wi-Fi test, software-konzept.md 3.3) | passive scan | 4 WS | 1 h |
| F5 | as F3, reload on 2 phones every 10 s | passive scan | socket peaks | 1 h |

| Metric | How (Rust / ESP-IDF) | Abort if | Result F1–F5 |
|---|---|---|---|
| Min. free heap / largest block | `esp_get_minimum_free_heap_size()`, `heap_caps_get_largest_free_block(MALLOC_CAP_8BIT)` every second | < 30 KB free or largest block < 8 KB (target: ≥ 60 KB / ≥ 16 KB, firmware-architecture.md 6.3) | |
| Errors / restarts | log, `esp_reset_reason()`, counter in NVS | one restart or allocation failure in 2 h | |
| WebSocket delivery | PC script: share of received states, gaps | < 98 % or gap > 1 s | |
| Joker detection STA (F2) | device B → IO23 vs. BLE reception | < 98 % within 300 ms | |
| Joker detection SoftAP (F3) | as above | < 90 % within 300 ms → BLE buttons only in STA mode or state rate 5/s | |
| Game tick jitter | timestamp in the 50 ms tick | outliers > 100 ms | |
| Preview | computation time, heap peak | > 1.5 s or > 30 KB | |
| Firmware size | build output vs. OTA slot (4 MB: 2 slots of approx. 1.9 MB each) | no abort; informs N4/H8 (F14) | ______ MiB |
| Captive portal (T8) | iOS + Android | does not appear → separate topic | |

Heap too tight: limit clients to 6, send state as a binary/delta message, test again.

### 5.4 What LED mode cannot show

- Real motor behavior: start-up, stall threshold, current calibration, jerks and kickback (T9).
- DRV8213 behavior, lever detection while running (current ≈ 0), brownout at motor start.
- RSSI in the compartment, quiescent current. All on the prototype (section 6).

---

## 6. What only the prototype board shows

- **Motor on the DRV8213:** ITRIP with R1, IPROPI accuracy at low currents (A6), heating during stall, autosleep and
  leakage on OUT_A/OUT_B (A4 final, T2), stall detection and its thresholds, jerks and kickback (T9).
- AP2112K with an empty battery, brownout at Wi-Fi peak + motor start (A3).
- Power path Q1/D2, USB-C J4, ESD U5, CC resistors.
- LIS2DH12 vs. motor vibration (T6, A19), INT on IO2 (A18).
- Antenna in the compartment with metal contact, RSSI in both orientations (T4, A7, F1).
- Deep-sleep quiescent current of the whole board.
- Mechanics: sleeve, contacts, USB-C opening (F3, F4, A1).

The 5 assembled boards allow losing one (e.g. in a stall or thermal test).

**Before ordering, without hardware:**

- Footprint check against the datasheets, especially ESP32-C6-MINI-1 (A11), DRV8213 WSON-8, LIS2DH12 LGA-12, USB-C.
- JLC assembly preview: rotation and polarity of every part (pin 1 of U1–U6, D1, D2, Q1, C orientation).
- 3D check and envelope (`just hull`, A1, A13).
- ERC/DRC with 0 errors and 0 unrouted (hauptplatine-c6.md 7).

---

## 7. Prototype boards

### 7.1 Key data

- **Outline:** 46.0 × 14.1 mm; the ends (0.8 mm into the end caps) are 12.5 mm wide, inner corners R 0.5 mm (mill),
  outer corners R 0.3 mm, 0.3 × 9 mm recess in front of USB-C (`hardware/scripts/board_outline.py`, since 2026-11-06).
  About 6.5 cm². 4 layers,
  0.8 mm, single-sided assembly.
- **Extended parts at JLC:** ESP32-C6-MINI-1, DRV8213DSGR, AP2112K-3.3, TYPE-C-31-M-12, USBLC6-2SC6, SS34F,
  LIS2DH12TR = 7 (verified, JLC parts API); AO3401A is Basic. With special values (1.24 k 1 %, 47 µF 1206)
  **calculated as 8** (unverified).
- **JLC stock (2026-11-06, verified):**

| Part | LCSC | JLC stock | Price 1+ / 10+ / 30+ USD |
|---|---|---:|---|
| ESP32-C6-MINI-1-N4 | C5736265 | 2,246 | 4.09 / 3.59 / 3.33 |
| **ESP32-C6-MINI-1-H8** | C42403058 | **620** | 5.39 / 4.62 / 4.16 |
| DRV8213DSGR | C22407186 | 3,704 | 1.04 / 0.93 / 0.81 |
| LIS2DH12TR | C110926 | 34,172 | 0.93 / 0.77 / 0.66 |
| AP2112K-3.3TRG1 | C51118 | 16,038 | 0.18 / 0.15 / 0.13 |

  The H8 is **available**. Check the stock again before ordering.

### 7.2 JLCPCB fees (Economic PCBA)

| Item | Value | Status |
|---|---|---|
| Setup / stencil | 8.18 / 1.53 USD per order | verified |
| Extended part | 3.07 USD per type and order | verified |
| Solder joint | 0.0016 USD; minimum 0.48 USD per board | fee verified, joint count unverified |
| X-ray (module/LGA) | 1.64 USD per board for 1–10, 0.82 for 11–50 | tiers verified, counting method unverified |
| Minimum quantity | 5 boards, at least 2 of them assembled | verified (secondary source) |
| PCB 4 layers | 5 pcs approx. 5 USD, 10 pcs approx. 10, 30 pcs approx. 20 USD | unverified (kostenabschaetzung.md 5.2) |
| Shipping DE | 8 / 8 / 10 / 15 € | unverified |
| VAT / customs | 19 % on goods + shipping; below 150 € goods value flat 3 € customs, above approx. 2 % | verified (kostenabschaetzung.md 2.4) |
| Exchange rate | 1 USD = 0.885 € | as in kostenabschaetzung.md |

### 7.3 Scenarios (with -N4; H8 approx. +1.2 € per assembled board; all unverified)

| Scenario | Boards / assembled | Fixed net USD | Variable net USD | **Total gross** | per assembled board | Fixed-cost share |
|---|---|---:|---:|---:|---:|---:|
| 1 | 5 / 2 | 43 | 18 | **≈ 76 €** | 38 € | 75 % |
| 2 | 5 / 5 | 43 | 45 | **≈ 105 €** | 21 € | 55 % |
| 3 | 10 / 10 | 48 | 81 | **≈ 150 €** | 15 € | 43 % |
| 4 | 30 / 30 | 59 | 201 | **≈ 296 €** | 9.90 € | 27 % |

- Parts per board approx. 6.90 USD (1–9 pcs), 5.95 (10+), 5.40 (30+); the module is a good 55 % of that.
- Other vendors for 5 assembled (unverified): PCBWay approx. 130–200 €, Aisler approx. 200–260 € (kostenabschaetzung.md).

### 7.4 Recommendation

1. **Run the pre-order checks 4.1–4.5** and enter the results in offene-punkte.md (A2–A5, F17, T1, T5). Change design
   values per 4.6 before ordering.
2. **Scenario 2: 5 boards, 5 assembled (≈ 105 €)**, directly with H8 if the H8 stock is sufficient (≈ +6 €).
   Compared with 5/2, 3 more boards cost only approx. 29 €. Motor, DRV8213, brownout, RSSI, sensor, quiescent current
   and mechanics become testable on several units; losing one is acceptable.
3. Software development in LED mode (section 5) runs in parallel and does not gate the order.
4. Only after a successful prototype 10–30 pcs (scenario 3/4).
5. Before ordering, load Gerber/BOM/CPL into the JLC calculator and read the real prices (F13).

### 7.5 Reorders and revisions

- **Fixed costs apply per order:** setup approx. 8 USD, extended fee approx. 3 USD per type (approx. 25 USD for 8 types),
  plus shipping, VAT and customs. Together approx. **57 € gross** per order (unverified).
- **Reordering saves nothing:** the stencil costs only approx. 1.5 USD. A repeat order therefore carries almost the
  full fixed costs. 2 × 5 boards cost much more than 1 × 10 (≈ 210 € vs. ≈ 150 €, unverified).
- **A revision costs as much as a new order:** approx. 75 € (2 boards) to 105 € (5 boards) and 2–3 weeks. This is why
  the pre-order checks (section 4) are worth doing.
- **Cheaper only through quantity per order.** From 30 pcs the fixed-cost share drops to approx. a quarter.
- **Parts in the JLC warehouse in advance:** JLC offers to buy parts in advance for your own account (Parts Pre-order /
  own parts library). This can reserve e.g. the H8 for the batch if the stock (620) drops.
  Conditions, storage time and whether the extended fee then no longer applies: **unverified**, check before ordering.

---

## Sources

Retrieved on 2026-11-06.

- ESP32-C6-DevKitC-1 user guide (headers J1/J3, GPIO14 not broken out, power supply options):
  https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32c6/esp32-c6-devkitc-1/user_guide.html (verified in the previous version of this document)
- ESP32-C6-DevKitM-1 user guide and schematic (RGB LED on IO8 with 10 k, SGM2212-3.3, CP2102N):
  https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32c6/esp32-c6-devkitm-1/user_guide.html,
  https://dl.espressif.com/dl/schematics/esp32-c6-devkitm-1-schematics.pdf (verified, text extract)
- Reichelt ESP32-C6-DevKitC-1-N8: https://www.reichelt.de/de/de/shop/produkt/entwicklungsboard_esp32-c6-wroom-1_u-380385 (price unverified)
- Waveshare ESP32-C6-DEV-KIT-N8 on Amazon.de (13.90 € incl. shipping, seller Bolin Electronic / Waveshare store; module,
  USB hub CH334 + UART CH343, pinout per seller) (verified, 2026-11-06)
- TI DRV8213 (ITRIP, IPROPI, coast Hi-Z, autosleep): https://www.ti.com/product/DRV8213, values in
  [hauptplatine-c6.md](hauptplatine-c6.md) 3.1 (verified)
- ESP32-C6 datasheet (strapping, internal pull-ups during reset, DC characteristics): values in
  [hauptplatine-c6.md](hauptplatine-c6.md) 2.4/3.2 (pull-ups verified; VIH/VIL not re-read)
- JLCPCB PCBA prices: https://jlcpcb.com/help/article/pcb-assembly-price (verified)
- JLCPCB parts API (stock, Extended/Basic) for C5736265, C42403058, C22407186, C110926, C51118 (verified, 2026-11-06)
- JLCPCB minimum quantity PCBA: https://jlcpcb.com/solutions/pcb-prototype-assembly (secondary source)
- PCB, shipping and vendor assumptions: [kostenabschaetzung.md](kostenabschaetzung.md) 2.4, 5.2
