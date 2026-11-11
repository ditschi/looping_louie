# Test setup (breadboard) and prototype boards

Status: 2026-11-11 (buck converter tests 4.7 for rev B) · Prices retrieved on 2026-11-06, gross incl. 19 % VAT unless stated otherwise.

Markers: **(verified)** = source read or recalculated from the project files · **(unverified)** = estimate,
secondary source, or not checked in the datasheet.

References: pinout, strapping, wake [main-board-c6.md](main-board-c6.md) 2.3–2.5, DRV8213
[main-board-c6.md](main-board-c6.md) 3, motor stage and lever detection [hardware-concept.md](hardware-concept.md)
5.1/5.2, part values [parts.csv](../hardware/bom/parts.csv), firmware [firmware-architecture.md](firmware-architecture.md)
(3.1 board `board-devkitc-c6`, 11 step 0), tests T1–T15 and assumptions in [open-items.md](open-items.md),
manufacturing costs [cost-estimate.md](cost-estimate.md).

## Summary

- **Decision (2026-11-06):** **No motor driver on the breadboard** (no MP6550, DRV8833, INA219, MOSFET). The test
  setup has two purposes: **pre-order checks** that reduce the risk of the PCB design (section 4) and
  **software development** in LED mode (section 5). Motor control, stall detection and current calibration are done
  on the 5 prototype boards (section 6, 7).
- **Buy only the dev board:** **Waveshare ESP32-C6-DEV-KIT-N8**, 13.90 € incl. shipping on Amazon.de (verified),
  module ESP32-C6-WROOM-1-N8. **Pin header identical to the Espressif DevKitC-1** (verified, Waveshare schematic vs.
  Espressif user guide); one USB-C port with hub, two serial ports (section 3.1). Alternative: Espressif
  **ESP32-C6-DevKitC-1-N8** (approx. 21 € incl. shipping at Reichelt, unverified).
- **Test firmware ready (not built yet):** [firmware/louie-fw](../firmware/louie-fw/README.md) with the bring-up in LED
  mode and one probe per check (`lever_probe`, `boot_probe`, `pin_probe`, `adc_probe`), started with
  `just fw-run <name> <port>` (section 8).
- **Everything else exists:** parts drawer (R, C, buttons, switches, LEDs, pots), the real Looping Louie (old and new
  model), lab power supply (adjustable, current limit, display), multimeter with scope function, classic ESP32
  (BTHome simulator), ESP8266 (extra Wi-Fi clients), Shelly BLU Button.
- **Answered before ordering (section 4):**

| Check | Design value it can change |
|---|---|
| 4.1 Motor current, start-up, stall, winding (lab supply only) | R1 / ITRIP 2 A, C1/C2, trace widths (A16), brownout budget and cut-off (A3, F24), A2 |
| 4.2 Lever network R3/R4/R5 on the real Louie | R3/R4/R5 values, board orientation (diode in the new model), A4 |
| 4.3 Boot, strapping, deep-sleep wake with the real external parts | IO8/S4, R22, VBUS divider R14/R15, wake pin assignment |
| 4.4 IO18/IO19 level in reset, boot and deep sleep (F17) | 3.3 k pull-downs on IN1/IN2 yes/no |
| 4.5 ADC accuracy VSYS 680 k/470 k + 100 nF and VBUS 100 k/100 k | R6/R7/C13, R14/R15, resistor tolerance (A5) |

- **Only the prototype answers:** footprints and assembly, antenna in the compartment, DRV8213 (ITRIP, IPROPI
  accuracy, autosleep, heating), the buck converter U3 (ripple, load step, 100 % mode, standby, temperature, ADC noise:
  4.7, T10–T15), mechanics (section 6).

---

## 1. Purpose and scope

| PCB risk | Testable before ordering? | How | Design value it can change |
|---|:---:|---|---|
| Motor current: running, start-up peak, stall | **yes** | 4.1: lab supply directly on the battery contacts, shunt + scope | R1 (ITRIP 2 A), C1/C2 bulk caps, trace widths and vias (A16), A2 |
| VSYS droop at motor start, brownout budget | **partly** | 4.1: stall current × estimated LiPo internal resistance (calculation) | A3: cut-off threshold, firmware ramp; real check only on the board (T12) |
| Lever detection network on the real Louie | **yes** | 4.2: R3/R4/R5 at the battery contacts, no driver | R3/R4/R5, orientation of the board (diode in the new model), A4 |
| Deep-sleep wake on IO3 / IO2 / IO4 (and S1 on IO5) | **yes** | 4.3 with the real external parts | wake pin assignment, VBUS divider ratio |
| Boot/strapping with the real external parts (IO8 incl. pressed S4, IO9, IO15, IO4, IO5) | **yes** | 4.3 | S4 on IO8 or another pin, R22 |
| Reset and deep-sleep level of IO18/IO19 (F17) | **yes** | 4.4: 200 k pull-down emulates the DRV8213 input | 3.3 k pull-downs on IN1/IN2 |
| VSYS divider 680 k/470 k + 100 nF with the C6 ADC; VBUS divider 100 k/100 k | **yes** | 4.5: lab supply sweep vs. multimeter | R6/R7/C13, R14/R15 (A5) |
| Footprints, rotation, polarity, assembly | no | datasheet check, JLC preview (section 6) | – |
| Antenna in the compartment, RSSI (T4, A7) | no | prototype | – |
| DRV8213: IPROPI accuracy (A6), autosleep leakage, heating, ITRIP behavior | no | prototype; R1, R8, C14 are swappable 0402 parts | – |
| Buck converter U3 under real load (T10–T15), power path, USB-C | no | prototype, 4.7 | – |
| Deep-sleep quiescent current of the board | no | prototype; the dev board has its own LDO, USB bridge and LEDs | – |

**Not an order gate:** whether the C6 handles 8 phones + BLE scan and how large the firmware gets are **software
questions**. No other module fits the AA format; the order uses the **H8** (F14). Both are measured in section 5.

**Recoverability:** if USB on J4 fails on the prototype, flashing still works via the service pads **J3** (EN, TXD,
BOOT, GND, RXD) with a USB-UART adapter (main-board-c6.md 2.4, A14).

---

## 2. Shopping list and parts drawer

### 2.1 Buy

| Part | Purpose | Qty | Price | Source |
|---|---|---:|---:|---|
| **Waveshare ESP32-C6-DEV-KIT-N8** | device under test (WROOM-1-N8, 8 MB) | 1 | 13.90 € incl. shipping (verified, 2026-11-06) | Amazon.de, seller Bolin Electronic (Waveshare store) |
| *Alternative:* ESP32-C6-DevKitC-1-N8 | same, Espressif original | 1 | approx. 14.70 € + approx. 5.95 € shipping (unverified) | [Reichelt](https://www.reichelt.de/de/de/shop/produkt/entwicklungsboard_esp32-c6-wroom-1_u-380385) |

- **Why 8 MB:** the board target is the H8. Whether the firmware also fits an N4 is shown by a build with the 4 MB
  partition table (firmware-architecture.md 6.1); it runs the same on the 8 MB board.
- **Waveshare:** details in section 3.1 (verified, schematic).
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

Values as on the board where a board part is emulated (parts.csv).

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

## 3. The dev board

### 3.1 Waveshare ESP32-C6-DEV-KIT-N8: facts from the schematic

All points verified in the Waveshare schematic (`ESP32-C6-DEV-KIT-N8-Schematic.pdf`, wiki, 2026-11-07) unless marked.

| Item | Waveshare DEV-KIT-N8 | Consequence for the tests |
|---|---|---|
| Module | ESP32-C6-**WROOM-1**-N8 (8 MB flash, PCB antenna); the board uses the **MINI-1** | same chip and GPIO numbers; WROOM-1 has **no GPIO14** (pin 22 NC) → status LED on IO10 |
| Pin headers | 2 × 16, 2.54 mm, **same order as DevKitC-1 J1/J3** (3.2) | Espressif pinout drawings apply |
| USB | **one USB-C**, CH334F hub: port 1 → C6 USB-Serial-JTAG (IO12/IO13), port 2 → **CH343P** USB-UART on UART0 (IO16/IO17) | two serial ports over one cable (8.2); the UART port stays connected in deep sleep |
| Auto download | CH343 DTR/RTS → 2 × SS8050 → EN and IO9 (classic circuit) | `espflash` works on both ports |
| EN / RESET | 10 k pull-up, 1 µF; RESET button via Schottky D2 to EN **and via D3 to the hub's RESET#** | pressing RESET also re-enumerates both serial ports (monitor drops, 8.2) |
| BOOT | button IO9 → GND, no external pull-up (C9 not fitted) | as on the board (J3) |
| IO8 | **10 k pull-up (R8)** + WS2812B-0807 DI via 0 Ω (R10) | see "Differences" below; S4 not usable |
| 3V3 | SGM2212-3.3 LDO from VCC_5V; red power LED with 2 k on 3V3 (≈ 0.7 mA, calculated) | dev board quiescent current not meaningful (LED, LDO, WS2812 idle current) |
| 5V pin | VCC_5V, fed from USB VBUS via Schottky **D1** (B5819WS) | USB and 5V pin do not short each other; still power only via USB (below) |
| Hub/UART supply | CH334 and CH343 get 3V3 only when USB VBUS is present (Q1 SI2301 + Q2 MMBT3904) | fed via the 5V pin the USB side is off |
| Other GPIOs | no onboard parts on IO0–IO7, IO10, IO11, IO15, IO18–IO23 | all check pins free |

Wiki notes (Waveshare, unverified): supply ≥ 5 V, below 4.9 V the USB connection may drop; ESP-IDF ≥ 5.1.

### 3.2 Pinout and use per check

Goal: **the same GPIO numbers as on the board** ([main-board-c6.md](main-board-c6.md) 2.3). Board feature:
**`board-devkitc-c6`** (firmware-architecture.md 3.1, [devkitc_c6.rs](../firmware/louie-fw/src/board/devkitc_c6.rs)).

- **Header P1** (with 3V3/5V): 1 3V3 · 2 EN · 3 IO4 · 4 IO5 · 5 IO6 · 6 IO7 · 7 IO0 · 8 IO1 · 9 IO8 · 10 IO10 ·
  11 IO11 · 12 IO2 · 13 IO3 · 14 5V · 15 GND · 16 NC
- **Header P2** (with TX/RX): 1 GND · 2 TX (IO16) · 3 RX (IO17) · 4 IO15 · 5 IO23 · 6 IO22 · 7 IO21 · 8 IO20 ·
  9 IO19 · 10 IO18 · 11 IO9 · 12 GND · 13 IO13 (USB D+) · 14 IO12 (USB D−) · 15 GND · 16 NC

(Verified, schematic; which header is left or right: check the silkscreen.)

| GPIO (header pin) | PCB net / part | Pre-order checks (section 4) | Software, LED mode (section 5) |
|---|---|---|---|
| IO0 (P1-7) | VBAT_ADC, R6/R7 680 k/470 k + C13 | divider from the lab supply (4.5) | pot wiper (= VSYS / 2) |
| IO1 (P1-8) | ISEN_ADC, R8/C14 | free | pot wiper via 1 k / 100 nF (simulated current, 255 mV/A) |
| IO2 (P1-12) | INT (LIS2DH12 INT1, J2) | button to 3V3 + 100 k to GND (wake, 4.3) | free |
| IO3 (P1-13) | SENSE, R5 100 k | R3/R4/R5 network at the Louie (4.2) | switch to 3V3, 100 k to GND (lever) |
| IO4 (P1-3) | VBUS_DET, R14/R15 100 k/100 k | divider from the lab supply 5 V (4.3, 4.5) | switch to 3V3, 100 k to GND (USB) |
| IO5 (P1-4) | S1 (J6) | button to GND, internal pull-up (4.3) | same |
| IO6 / IO7 (P1-5/6) | SDA / SCL | free | free (sensor probe reports "no sensor") |
| IO8 (P1-9) | S4 (J6), strapping, R11 10 k | button to GND (4.3) | button to GND (collides with RGB LED, see below) |
| IO9 (P2-11) | BOOT (J3) | BOOT button of the dev board | same |
| IO10 (P1-10) | – (PCB: status LED on **IO14**) | free | status LED + 1 k |
| IO12 / IO13 (P2-14/13) | USB D− / D+ | USB-C of the dev board | same |
| IO15 (P2-4) | U6 enable, R22 100 k | 100 k to GND (4.3) | free |
| IO16 / IO17 (P2-2/3) | TXD / RXD (J3) | UART bridge of the dev board | same |
| IO18 / IO19 (P2-10/9) | MOT_IN1 / MOT_IN2 | 200 k to GND each, scope (4.4) | LED + 1 k from 3V3 to the pin each |
| IO20 / IO21 (P2-8/7) | S2 / S3 (J6) | free | button to GND |
| IO22 (P2-6) | spare | free | free |
| IO23 (P2-5) | LED data J7 | free | input for the latency reference from device B (5.3) |

**Differences from the board:**

- **IO14 → IO10:** status LED on IO10 (board definition).
- **IO8:** the dev board has its own **10 k pull-up and the RGB LED (WS2812)** on IO8 (verified, Waveshare schematic
  R8/R10). So the IO8 check in 4.3 only tests the case "S4 pressed during reset";
  R11 itself is not new. During play the button sends garbage to the RGB LED; this is harmless. The firmware
  reports only S1–S3 on the dev board.
- **IO4:** in LED mode only a switch (`vbus_divider = None`); in 4.3/4.5 the real 100 k/100 k divider.
- **Supply:** always power the dev board via USB. Do not feed the 5V or 3V3 pin at the same time (verified, Espressif
  user guide; on the Waveshare board D1 protects USB from the 5V pin, the 3V3 pin has no protection). Common ground
  with the lab supply whenever both are connected.
- **ADC inputs max. 3.3 V.** No lab-supply voltage directly on a GPIO.

---

## 4. Pre-order checks

General rules:

- **Lab supply current limit** 1 A at first power-up, then as stated per check.
- **Stall:** hold the arm for at most **2–3 s**. Old model (1.5 V nominal): voltages above 3 V only briefly (< 2 s,
  no stall).
- **Scope ground** only at the lab supply's negative terminal (shunt low side). If the scope is earthed, the lab
  supply output must be floating (unverified for your devices, check before connecting).
- Enter the results in [open-items.md](open-items.md) (A2–A5, F17, T1, T5).

**Firmware:** one probe per check in [firmware/louie-fw/examples](../firmware/louie-fw/examples) (4.2 `lever_probe`,
4.3 `boot_probe`, 4.4 `pin_probe`, 4.5 `adc_probe`), usage in section 8. Fallback if the Rust build is not ready yet:
the ESP-IDF examples `system/deep_sleep` and `peripherals/adc/oneshot_read` with changed pin numbers.

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
effective voltage d × VSYS (hardware-concept.md 5.1). The current at a lab voltage U therefore approximates the
board at effective voltage U (unverified; the DRV8213 adds 0.24 Ω Rds(on), main-board-c6.md 3.1). The battery
then delivers roughly d × I_motor on average.

**Consequences (pass criteria and design values):**

- **A2 holds** if the running current at nominal voltage is < 1 A. Otherwise re-evaluate battery size and turbo limit.
- **R1 / ITRIP:** ITRIP = 0.51 V / (R1 × 205 µA/A) (verified, main-board-c6.md 3.1). Stay well below the OCP of
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
  Q1 + contacts approx. 0.1 Ω. Example 2 A × 0.4 Ω = 0.8 V: a 3.7 V cell drops to 2.9 V, the buck in 100 % mode
  (approx. 0.2 V at 380 mA) then gives less than 3.0 V → brownout risk. If the calculation is critical: stronger
  firmware ramp and a cut-off on the filtered VSYS (main-board-c6.md 2.7). Final check only on the board (T12).

### 4.2 Lever detection network on the real Louie

**Goal:** check R3/R4/R5 with the real motor and lever, both models; detect a diode in series; check deep-sleep wake
with ANY_HIGH on IO3 (T1, A4).

**Circuit** (no driver; this is the state with the DRV8213 in coast/autosleep):

```
Dev board GND ──[100 k R3]──┬── contact 1 (OUT_A) ── lever ── motor ── contact 2 (OUT_B) ──[10 k R4]── dev board 3V3
                            └──[100 k R5]── IO3 (SENSE)
optional leakage emulation: 1 M from OUT_A to GND, then 1 M from OUT_B to GND
```

- The DRV8213 outputs are **Hi-Z in coast (0/0)** (verified, main-board-c6.md 3.1). That no output pull-down or
  leakage acts in autosleep is **unverified** (main-board-c6.md 3.2). The 1 M resistors emulate a few µA of
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
5. Special case "lever closed when going to sleep" (main-board-c6.md 2.5): test the firmware fallback (wake on
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
pull IO18/IO19 HIGH (verified, main-board-c6.md 3.2); against the DRV8213's internal 200 k pull-down this gives
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

**Goal:** the 680 k/470 k divider with 100 nF (source impedance 278 k, VSYS up to 6.6 V, main-board-c6.md 2.7) is
accurate enough for the battery cut-off at approx. 3.4–3.5 V filtered (A5, main-board-c6.md 2.7); the VBUS divider gives a usable value.

**Circuit:**

```
Lab + ──[680 k R6]──┬──[470 k R7]── GND        Lab + ──[100 k R14]──┬──[100 k R15]── GND
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
specify **1 %** resistors for R6/R7 in parts.csv (tolerance not stated there today; 2 × 1 % → up to approx. 2 % ratio
error, 84 mV at 4.2 V) or a one-point calibration in the firmware.

### 4.6 Results → design

| Result | Changes | Where |
|---|---|---|
| 4.1 stall current, running current | R1, C1/C2 count, trace widths; A2, A3 | parts.csv, routing gate |
| 4.2 SENSE levels, diode | R3/R4/R5, board orientation; A4 | parts.csv, hardware-concept.md 5.2 |
| 4.3 strapping, wake, IO4 threshold | S4 pin, R14/R15 ratio | main-board-c6.md 2.3/2.4 |
| 4.4 IO18/IO19 levels | 3.3 k pull-downs (F17) | main-board-c6.md 3.2 |
| 4.5 ADC error | R6/R7/C13, tolerance; A5 | parts.csv |

---

### 4.7 Buck converter U3 (prototype board)

**Goal:** the TPS62162 buck converter (U3 with L1 2.2 µH, C8 10 µF, C9 22 µF; main-board-c6.md 2.7) is stable, quiet
enough for the ADC and the radio, stays cool, and its 100 % mode sets the real cut-off numbers (A3, A21, F24).
The block exists only as a WSON on the board, so these tests run **on the prototype board** and do not gate the order.
They replace the former load-step test of the SPX3819 LDO on an adapter (decision-history.md).

**Setup:** lab supply on BAT_IN/GND (J5) instead of a cell, current limit 1 A; scope with AC coupling, 20 MHz bandwidth
limit and a short ground spring directly at C9; electronic load or switched resistor on 3V3 as in the sketch:

```
3V3 (C9) ──┬── 11 Ω (1 W) ── drain AO3400 source ── GND        11 Ω ≈ 300 mA at 3.3 V
           └── scope probe (ground spring at C9)    gate ── 100 Ω ── function generator / GPIO of the dev board
```

| Test | Procedure | Pass |
|---|---|---|
| **T10** ripple and spikes | VSYS 3.0 / 3.7 / 5.0 / 6.6 V, each with no load and with 300 mA; scope at C9 | ≤ 30 mV p-p, no sustained ringing |
| **T11** load step | 0 → 300 mA with the switched 11 Ω (100 Hz–1 kHz, 10–50 % duty), trigger on the gate, at VSYS 3.7 V and 6.6 V | dip ≤ 150 mV, recovery ≤ 100 µs |
| **T12** 100 % mode entry | sweep VSYS down from 4.0 to 3.0 V at 150 mA and at 380 mA load, read 3V3 with the multimeter | 3V3 ≥ 3.0 V down to VSYS ≈ 3.3 V at 150 mA and ≈ 3.5 V at 380 mA; the measured values set the cut-off thresholds in main-board-c6.md 2.7 |
| **T13** standby | board in deep sleep, current at BAT_IN at VSYS 3.5 / 3.7 / 4.0 / 6.0 V (multimeter µA range, short it during boot) | ≤ 40 µA above 3.8 V; below 3.8 V the converter stays in PWM (wiring review W21): record the value, it decides F29 |
| **T14** temperature | Wi-Fi TX continuously at VSYS 6.6 V for 10 min, temperature of U3 and L1 (thermocouple or IR) | < 60 °C in free air |
| **T15** ADC noise | VBAT_ADC and ISEN_ADC at 10 Hz with the buck in power-save mode vs. 3V3 from a bench LDO | no visible difference |
| **T4** addition | RSSI test with the buck running and with 3V3 from the bench supply | no RSSI difference > 2 dB |

T15 and the T4 addition need 3V3 from a bench supply while U3 is not switching. EN is tied to VIN on the board, so U3
cannot be switched off separately; how to feed 3V3 without back-feeding through U3 (e.g. L1 not fitted on one board)
is still open.

**On failure:** ringing or ripple too high → second output capacitor or 22 µF in a larger package, check the SW loop
in the layout; dropout too high → accept a higher cut-off or look at the DCR of L1 (DFE201610E, Sunlord WPN201610U);
ADC noise → sample in a quiet window or average; hot → check the soldering of the exposed pad. Alternatives and their
trade-offs: [proposal-supply-buck.md](proposal-supply-buck.md) 3 and 8.
**Buy:** AO3400, 11 Ω 1 W (or 2 × 22 Ω 0.5 W in parallel); the rest exists (lab supply, scope, multimeter).

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
stand in for driver and motor. The bring-up binary already does this with keys or a sweep as setpoint (8.3).

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
| F4 | SoftAP + STA (Wi-Fi test, software-concept.md 3.3) | passive scan | 4 WS | 1 h |
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
- **Buck converter U3:** tests T10–T15 in 4.7 (ripple, load step, 100 % mode and cut-off, standby, temperature, ADC
  noise); brownout at Wi-Fi peak + motor start with a low cell (A3).
- **3V3 at the module during Wi-Fi TX:** scope directly at module pad 3 (3V3) and pad 1/2 (GND), AC coupling, while the
  firmware sends continuously (e.g. iperf or a Wi-Fi TX test). Pass: dips below approx. 150 mV, no brownout reset. If not:
  the next revision needs a capacitor closer to the module (no room in this one, main-board-c6.md 11.10).
- **Reset and boot with the EN RC approx. 12 mm from the EN pin and without an external IO9 pull-up:** 50 power cycles
  each from the cell and from USB, plus a few with the motor running; every one must boot normally (no download mode,
  no reset loop). Plus ESD/noise check: touch the board ends and J3 during operation.
- Power path Q1/D2, USB-C J4, ESD U5, CC resistors; USB + 4 × AA (F28): VSYS, temperature of Q1 at stall.
- LIS2DH12 vs. motor vibration (T6, A19), INT on IO2 (A18).
- Antenna in the compartment with metal contact, RSSI in both orientations, with and without the buck running (T4, A7, F1).
- Deep-sleep quiescent current of the whole board (T13, target ≤ 40 µA).
- Mechanics: sleeve, contacts, USB-C opening (F3, F4, A1).

The 5 assembled boards allow losing one (e.g. in a stall or thermal test).

**Before ordering, without hardware:**

- Footprint check against the datasheets, especially ESP32-C6-MINI-1 (A11), DRV8213 WSON-8, LIS2DH12 LGA-12, USB-C.
- JLC assembly preview: rotation and polarity of every part (pin 1 of U1–U6, D1, D2, Q1, C orientation).
- 3D check and envelope (`just hull`, A1, A13).
- ERC/DRC with 0 errors and 0 unrouted (main-board-c6.md 7).

---

## 7. Prototype boards

### 7.1 Key data

- **Outline:** 46.0 × 14.1 mm; the ends (0.8 mm into the end caps) are 12.5 mm wide, inner corners R 0.5 mm (mill),
  outer corners R 0.3 mm, 0.3 × 9 mm recess in front of USB-C (`hardware/scripts/board_outline.py`, since 2026-11-06).
  About 6.5 cm². 4 layers,
  0.8 mm, single-sided assembly.
- **Extended parts at JLC:** ESP32-C6-MINI-1, DRV8213DSGR, AP2112K-3.3, TYPE-C-31-M-12, USBLC6-2SC6, SS34F,
  LIS2DH12TR = 7 (verified, JLC parts API, state 2026-11-06 with the AP2112K); AO3401A is Basic. With special values
  (1.24 k 1 %, 47 µF 1206) **calculated as 8** (unverified). **Rev B:** U3 becomes the TPS62162DSGR (C40256, Extended,
  4,992 in stock, 0.97 USD at 10+ on 2026-11-10) and the inductor L1 (C79317, 0.09 USD) adds one Extended type → **9**
  (cost-estimate.md 2.2).
- **JLC stock (2026-11-06, verified):**

| Part | LCSC | JLC stock | Price 1+ / 10+ / 30+ USD |
|---|---|---:|---|
| ESP32-C6-MINI-1-N4 | C5736265 | 2,246 | 4.09 / 3.59 / 3.33 |
| **ESP32-C6-MINI-1-H8** | C42403058 | **620** | 5.39 / 4.62 / 4.16 |
| DRV8213DSGR | C22407186 | 3,704 | 1.04 / 0.93 / 0.81 |
| LIS2DH12TR | C110926 | 34,172 | 0.93 / 0.77 / 0.66 |
| AP2112K-3.3TRG1 (state 2026-11-06) | C51118 | 16,038 | 0.18 / 0.15 / 0.13 |
| TPS62162DSGR (rev B, 2026-11-10) | C40256 | 4,992 | – / 0.97 / – |

  The H8 is **available**. Check the stock again before ordering.

### 7.2 JLCPCB fees (Economic PCBA)

| Item | Value | Status |
|---|---|---|
| Setup / stencil | 8.18 / 1.53 USD per order | verified |
| Extended part | 3.07 USD per type and order | verified |
| Solder joint | 0.0016 USD; minimum 0.48 USD per board | fee verified, joint count unverified |
| X-ray (module/LGA) | 1.64 USD per board for 1–10, 0.82 for 11–50 | tiers verified, counting method unverified |
| Minimum quantity | 5 boards, at least 2 of them assembled | verified (secondary source) |
| PCB 4 layers | 5 pcs approx. 5 USD, 10 pcs approx. 10, 30 pcs approx. 20 USD | unverified (cost-estimate.md 5.2) |
| Shipping DE | 8 / 8 / 10 / 15 € | unverified |
| VAT / customs | 19 % on goods + shipping; below 150 € goods value flat 3 € customs, above approx. 2 % | verified (cost-estimate.md 2.4) |
| Exchange rate | 1 USD = 0.885 € | as in cost-estimate.md |

### 7.3 Scenarios (with -N4; H8 approx. +1.2 € per assembled board; all unverified)

| Scenario | Boards / assembled | Fixed net USD | Variable net USD | **Total gross** | per assembled board | Fixed-cost share |
|---|---|---:|---:|---:|---:|---:|
| 1 | 5 / 2 | 43 | 18 | **≈ 76 €** | 38 € | 75 % |
| 2 | 5 / 5 | 43 | 45 | **≈ 105 €** | 21 € | 55 % |
| 3 | 10 / 10 | 48 | 81 | **≈ 150 €** | 15 € | 43 % |
| 4 | 30 / 30 | 59 | 201 | **≈ 296 €** | 9.90 € | 27 % |

- Parts per board approx. 6.90 USD (1–9 pcs), 5.95 (10+), 5.40 (30+); the module is a good 55 % of that. Rev B adds
  approx. 1.1 USD per board (U3, L1, capacitors) and 3.07 USD per order for one more Extended type, i.e. approx.
  +9 € for scenario 2 (cost-estimate.md 1).
- Other vendors for 5 assembled (unverified): PCBWay approx. 130–200 €, Aisler approx. 200–260 € (cost-estimate.md).

### 7.4 Recommendation

1. **Run the pre-order checks 4.1–4.5** and enter the results in open-items.md (A2–A5, F17, T1, T5). Change design
   values per 4.6 before ordering.
2. **Scenario 2: 5 boards, 5 assembled (≈ 105 €)**, directly with H8 if the H8 stock is sufficient (≈ +6 €).
   Compared with 5/2, 3 more boards cost only approx. 29 €. Motor, DRV8213, brownout, RSSI, sensor, quiescent current
   and mechanics become testable on several units; losing one is acceptable.
3. Software development in LED mode (section 5) runs in parallel and does not gate the order.
4. Only after a successful prototype 10–30 pcs (scenario 3/4).
5. Before ordering, load Gerber/BOM/CPL into the JLC calculator and read the real prices (F13).

### 7.5 Reorders and revisions

- **Fixed costs apply per order:** setup approx. 8 USD, extended fee approx. 3 USD per type (approx. 28 USD for 9 types with rev B),
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

## 8. Test firmware: setup and usage

Code and details: [firmware/louie-fw/README.md](../firmware/louie-fw/README.md). Status 2026-11-07: **written, not
built and not run yet**; the first build is the first task when the board arrives.

### 8.1 Setup (once)

1. `./setup.sh` (section "Firmware"): rustup with the pinned nightly + `rust-src`, `ldproxy`, `espflash`. Also
   `python3-venv`, user in group `dialout`.
2. `just fw-build`: the first build downloads ESP-IDF v5.5.5 into `~/.espressif` and takes 10–20 min (unverified).
   The repo path contains spaces, which ESP-IDF does not support; the Cargo target directory therefore lives in
   `~/.cache/louie-fw/target`. If the build still fails on paths: work from a clone without spaces (README).

### 8.2 Connecting

- One USB-C cable; `just fw-ports` shows two devices: **CH343** (`usb-1a86_…`, UART0) and **USB-Serial-JTAG**
  (`usb-Espressif_…`).
- **Use the CH343 port** for flashing and monitoring: keys go only to UART0, and it stays connected while the C6
  is in deep sleep (the USB-Serial-JTAG port disappears). Example: `just fw-run boot_probe /dev/serial/by-id/usb-1a86_…`.
- The **RESET button also resets the USB hub**: both ports drop for a moment. For reset series use a terminal that
  reconnects on its own (e.g. `tio <port>`) instead of `espflash monitor` (unverified how espflash reacts).

### 8.3 Smoke test and bring-up (LED mode)

| Step | Action | Expected |
|---|---|---|
| 1 | Plug in the bare board | power LED on, `just fw-ports` lists both ports |
| 2 | `just fw-run boot_probe <CH343 port>` without any wiring | banner: reset reason, wake cause, `levels:` line; ROM log shows `boot:0x..` |
| 3 | Wire LED mode (5.1), `just fw-run` | status LED IO10 blinks 1 Hz, log line every 0.5 s |
| 4 | VSYS pot to ≥ 1.65 V wiper (VSYS ≥ 3.3 V), lever switch closed | state `Run` |
| 5 | Keys `+` / `-` (250 mV steps), `s` sweep | one motor LED dims with the setpoint, direction changes the LED; ramp 4 V/s |
| 6 | Open the lever switch / VSYS pot below 3.3 V | `LeverOpen` / `LowBattery`, both LEDs on (coast) |
| 7 | ISEN pot above ≈ 383 mV (1.5 A) while running | after 0.3 s `Stall`, both LEDs off (brake); `r` clears |
| 8 | Key `p` (panic) | restart, state `Locked` (double blink) until the lever goes open → closed (E15) |
| 9 | Buttons S1–S3 | `button Sn pressed` in the log |

Placeholders in `src/main.rs` (ramp, VSYS cut-off, stall threshold) are LED-mode values, not motor values.

### 8.4 Probes for the pre-order checks

| Check | Command | Keys | Note in the tables of section 4 |
|---|---|---|---|
| 4.2 lever | `just fw-run lever_probe <port>` | `c` auto cycle (closed at sleep → wake on LOW), `t` the same with timer 5 s fallback, `s` one sleep, `z` reset counters; after each wake `x` within 2 s stops | edges and closings in the log ("reads of 20"), `wake #n` ("wake-ups of 20") |
| 4.3 boot / wake | `just fw-run boot_probe <port>` | `7` / `8` / `9` / `a` = cases 7 / 8 / 9 / 10 (repeat automatically, `x` stops), `l` live levels (case 11), `r` software restart | cases 1–5: banner + ROM `boot:` line after each reset; case 6: flash over the **USB-Serial-JTAG** port (as on the board) while S4 is held |
| 4.4 IO18/IO19 | `just fw-run pin_probe <port>` | `w` sleep without hold (b), `h` with hold (c), `n` 10 × (c), `r` / `p` / `d` software / panic / watchdog reset (a) | levels and HIGH window from the scope; the logged µs are only the app part |
| 4.5 ADC | `just fw-run adc_probe <port>` | `f` burst mode (64 conversions) | per second: pin mV mean/min/max and input mV with the nominal ratio; convert with the measured ratio |

Recommended order: 8.3 steps 1–2 → 4.5 (lab supply only on dividers) → 4.3 → 4.4 → 4.2 at the Louie; 4.1 needs no ESP.

---

## Sources

Retrieved on 2026-11-06; Waveshare and ESP-IDF headers on 2026-11-07.

- Waveshare ESP32-C6-DEV-KIT-N8 wiki: https://www.waveshare.com/wiki/ESP32-C6-DEV-KIT-N8 ; schematic (module, CH334F hub,
  CH343P, auto download, RESET to hub, IO8 with R8 10 k + WS2812B, SGM2212, D1, VCC_Open switch, headers P1/P2):
  https://files.waveshare.com/wiki/ESP32-C6-DEV-KIT-N8/ESP32-C6-DEV-KIT-N8-Schematic.pdf (verified)
- ESP-IDF v5.5 headers (`esp_sleep.h`: `esp_sleep_enable_ext1_wakeup_with_level_mask`; `soc_caps.h` C6: ext1 per pin,
  wake GPIOs 0–7, `SOC_GPIO_SUPPORT_HOLD_SINGLE_IO_IN_DSLP`; `adc_oneshot.h`, `adc_cali_scheme.h`; LEDC clock sources):
  https://github.com/espressif/esp-idf/tree/v5.5.1/components (verified)

- ESP32-C6-DevKitC-1 user guide (headers J1/J3, GPIO14 not broken out, power supply options):
  https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32c6/esp32-c6-devkitc-1/user_guide.html (verified in the previous version of this document)
- ESP32-C6-DevKitM-1 user guide and schematic (RGB LED on IO8 with 10 k, SGM2212-3.3, CP2102N):
  https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32c6/esp32-c6-devkitm-1/user_guide.html,
  https://dl.espressif.com/dl/schematics/esp32-c6-devkitm-1-schematics.pdf (verified, text extract)
- Reichelt ESP32-C6-DevKitC-1-N8: https://www.reichelt.de/de/de/shop/produkt/entwicklungsboard_esp32-c6-wroom-1_u-380385 (price unverified)
- Waveshare ESP32-C6-DEV-KIT-N8 on Amazon.de (13.90 € incl. shipping, seller Bolin Electronic / Waveshare store; module,
  USB hub CH334 + UART CH343, pinout per seller) (verified, 2026-11-06)
- TI DRV8213 (ITRIP, IPROPI, coast Hi-Z, autosleep): https://www.ti.com/product/DRV8213, values in
  [main-board-c6.md](main-board-c6.md) 3.1 (verified)
- ESP32-C6 datasheet (strapping, internal pull-ups during reset, DC characteristics): values in
  [main-board-c6.md](main-board-c6.md) 2.4/3.2 (pull-ups verified; VIH/VIL not re-read)
- JLCPCB PCBA prices: https://jlcpcb.com/help/article/pcb-assembly-price (verified)
- JLCPCB parts API (stock, Extended/Basic) for C5736265, C42403058, C22407186, C110926, C51118 (verified, 2026-11-06)
- JLCPCB minimum quantity PCBA: https://jlcpcb.com/solutions/pcb-prototype-assembly (secondary source)
- PCB, shipping and vendor assumptions: [cost-estimate.md](cost-estimate.md) 2.4, 5.2
