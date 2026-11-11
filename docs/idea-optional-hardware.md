# Optional extra hardware on the bottom side

Status: 2026-11-11 · **Pads and DNP footprints from section 0/0b are implemented in schematic and placement, and
the board is routed completely** (0 unconnected, DRC 0; positions: [main-board-c6.md](main-board-c6.md) 11.7, routing result 11.4).
Complements [hardware-concept.md](hardware-concept.md), [main-board-c6.md](main-board-c6.md) and [ideas.md](ideas.md).

Applies to the main board with **ESP32-C6-MINI-1, DRV8213, 4 layers**. Rejected candidates and earlier
decisions (C3 research, hardware load pulse, RC footprints on S2–S4): see
[decision-history.md](decision-history.md).

Contents:
- **0** Principle, free pins, space and height; 0.4 what is implemented on the bottom
- **0b** What the pads can be used for: LED chain on J7, four wired buttons on J6, paddle detection,
  overall assignment, assembly variants, datasheet check
- **1** Further ideas, not implemented yet

Markers: **(verified)** = backed by a source · **(unverified)** = from a secondary source or calculated; check before
use or measure on a sample.

---

## 0. Principle and inventory

**Principle of the project owner:** Everything essential is on the **top** and is fully machine-assembled (single-sided
Economic PCBA at JLC). The board works **without any manual work** (power via USB-C; battery cables on J1/J5 are
installation, not assembly). The **bottom is strictly optional:** pads, footprints for hand soldering,
test points. Components on the bottom are **never** assembled (DNP), otherwise the PCBA becomes double-sided and more expensive.

Coordinates: board center = (0; 0), antenna at −x, USB-C at +x, +y = side of the USB-C opening.

### Summary

- **There is no space left on top** (99 mm² free, fragmented, no 3 × 3 mm piece). New components on top: none.
  U4 LIS2DH12 + C15 (acceleration, INT on IO2) and D1/R9 (status LED) are on top and stay.
- **On the bottom** about 380 mm² are free. GND runs solid on In1, stubs run on In2. A pad costs
  one via and a short trace. The bottleneck is the via positions under the module, not the area.
- **Implemented (0.4, 0b.4):** J6 "players" (four inputs S1–S4), J7 "LED" (chain, LED or button) with
  DNP load switch U6, J3 as a complete service connector (with RXD), DNP pre-circuit on IO5, four
  test points. Except **IO22 (reserve)** all GPIOs are assigned.
- None of this is needed for basic operation. The board works with the bottom unassembled.

### 0.1 Inventory

#### Free C6 GPIOs and their properties

Fixed (main-board-c6.md 2.3): IO0/1/3/4 (VBAT_ADC, ISEN_ADC, SENSE, VBUS_DET, without pads), **IO2** INT
(J2-5, LP GPIO, deep sleep wake), **IO6/IO7** SDA/SCL (J2-3/4), **IO9** BOOT (J3-3), **IO16** TXD (J3-2), **EN**
(J3-1), IO12/13 USB, IO14 LED, IO18/19 motor. Eight pins were free for optional hardware:

| GPIO (module pad, position) | ADC | Deep sleep wake | Strapping / boot | today |
|---|---|---|---|---|
| **IO5** (10, edge +y, x = −5.6) | ADC1_CH5 | **yes** (LP_GPIO5) | only SDIO edge, level irrelevant | S1 (J6-2), DNP pre-circuit N4 |
| IO8 (22, right, y = −3.2) | – | no | **yes**: only in download mode (IO9 = 0) IO8 must be 1 | S4 (J6-5), R11 10 k pull-up on top |
| IO15 (20, right, y = −1.6) | – | no | JTAG source, effective only with burned eFuse | enable U6 (LED supply) |
| IO17 = RXD (30, edge −y, x = −8.8) | – | no | UART0 RX of the ROM (input) | RXD on J3-5 |
| IO20 (26, edge −y, x = −5.6) | – | no | – | S2 (J6-3) |
| IO21 (27, edge −y, x = −6.4) | – | no | – | S3 (J6-4) |
| **IO22** (28, edge −y, x = −7.2) | – | no | – | **free (reserve)** |
| IO23 (29, edge −y, x = −8.0) | – | no | – | LED data (J7-2) |

(Module pads read from the 4-layer board, verified; ADC/LP/strapping from analysis-wireless-controllers.md 3b.1, verified.)

- **Wake:** Only LP GPIO0–7 wake from deep sleep. Of the optional pins that is only IO5 (S1). All others
  wake only from light sleep. That is enough for game buttons, because the game is running anyway at that point; deep sleep is ended
  by the lever (SENSE).
- **TXD (IO16)** outputs the ROM log at boot and stays the console.

#### Free area (measured, pcbnew grid 0.05 mm, before the pads were added)

Usable = board without antenna area (x < −14.6), without 0.32 mm edge strip and without the area under the
end caps (|x| > 22.2): **475 mm²**.

| | Value |
|---|---|
| **Top** free of courtyards | 99 mm², of which 20 mm² fit 2 × 2 mm, **0** fit 3 × 3 mm |
| top free also of traces and pads (+0.2 mm) | 29 mm² |
| **Bottom** free of courtyards | **382 mm²** (in the pocket \|y\| ≤ 5.2: 312 mm²) |
| bottom free also of traces and pads (+0.2 mm) | 185 mm², of which 9 mm² as 3 × 3 mm in one piece |

Largest copper-free pieces on the bottom: x +12.8 … +19.2, y −4.2 … −0.5 (under USB-C, next to J5, about 19 mm²) and
x +3.2 … +6.3, y −5.8 … −2.0 (under C1/C2, about 11 mm²).

#### Height on the bottom

- The board bottom is 0.3 mm below the cell axis. The AA shell (`sleeve.scad`) has a
  **pocket 10.4 mm wide (|y| ≤ 5.2) and 2.0 mm deep** under the board; outside of it the board rests on the shell.
- Components on the bottom up to about **1.5 mm** high (0.5 mm clearance for solder and tolerance), only in |y| ≤ 4.5. Wires on the
  pads likewise only in the pocket or in the cable window (x = 10 … 19, +y). Check: `just hull`.
- **With a deeper pocket:** Calculated with 0.8 mm remaining wall (radius 6.45 mm), heights up to about 5.4 mm at |y| ≤ 3 and
  up to about 4.3 mm at |y| ≤ 4.5 would be possible (envelope calculation, unverified, test print).

### 0.2 Usefulness assessment: which pads are worth it?

| Criterion | Finding |
|---|---|
| **Benefit** | Wired game buttons or paddle contacts (test and stopgap for the button players from idea-wireless-buttons.md 4.2, without port expander), external LED chain, UART RX for debugging, an ADC input with deep sleep wake (IO5). |
| **Testability** | Measurable at pads: 3V3, I²C, INT, EN, TXD, RXD, BOOT, BAT_IN, OUT_A/OUT_B. Plus test points for **VSYS, VBUS, ISEN (IPROPI) and SENSE**, the quantities for bringing up motor, current limit and lever. With TXD and RXD, J3 is a complete console, the fallback path when USB-CDC hangs or USB-C is plugged into the power bank for measuring. |
| **Antenna risk** | All pads are at x ≥ −13.6 (like J3). The keep-out areas at x < −14.6 stay untouched on all layers. |
| **Strapping risk** | IO8 only as input (S4); a pressed button does not disturb normal boot (0b.6). RXD (IO17) is input only in the ROM. |
| **ESD risk** | The pads are inside the closed battery compartment. For wires going outside (buttons, LED chain): **series resistor in the cable** (1 kΩ on inputs, 330 Ω on LED data), wire twisted with GND. No TVS diodes on the board (unverified whether the pin ESD of the C6 is enough for long lines). |
| **Short circuit risk in the compartment** | VSYS is unfused (LiPo only via its protection IC, USB via D2). VSYS reaches J7 **only via the LED LDO U6 (3.95 V, current limit approx. 0.8–0.95 A, thermal shutdown)**, never directly to a pad and not next to GND. |
| **Effort** | One via and a short trace on In2 per pad. The footprints under the module compete with the vias the router uses to escape the module pads (main-board-c6.md 11.7). Hence as few footprints as possible. |

**No universal pad block:** The blocks are distributed by location. I²C stays on J2 (edge +y, where SDA/SCL/INT
exit), the inputs go to J6 under the module (edge −y, where IO20/21 exit), the LED chain to J7 near
the VSYS strip. Pads 1.4 mm, suitable for wire and pogo pins (e.g. P75/P100); test points as round pads Ø 1.0 mm.

### 0.3 Candidates (C6, 4 layers)

"Top" = machine-assembled. "Bottom" = optional, hand soldering or pads only.

| # | Component | Benefit for the game | Pins | Result |
|---|---|---|---|---|
| K1 | LIS2DH12 | knock, lift, shake; INT on IO2 → deep sleep wake | I²C + IO2 | **top** (U4 + C15), assembly optional; basic operation works without it |
| K2 | LIS2DW12 | like K1, flatter, more economical | like K1 | only as BOM alternative for U4 (pin compatibility unverified, section 1) |
| K4 | SC7A20 | like K1 | like K1 | at most a second source for U4 (register compatibility unverified, section 1) |
| K6 | I²C pads | any breakout | 5 | **J2** (3V3, GND, SDA, SCL, INT) |
| K7 | TMAG5273 | magnet gimmicks; speed is already available via ISEN | I²C | no footprint; as breakout on J2 (section 1) |
| K8 | DRV5032 | Hall switch | 1 GPIO | no footprint; external on J6 (3V3/GND/input) |
| K15 | buttons | wired game buttons, second button | 4 | **J6** S1–S4 (S1 with deep sleep wake) |
| K16 | piezo disc | knock per arm | 1 per arm | on J6 digital or on IO5 analog (0b.3) |
| N2 | external LED chain (WS2812/SK6812) | status/effects on the outside of the game | IO23 + VLED | **J7** with U6/C18/R23/R24/C17 (0b.1) |
| N3 | UART RX | debugging without USB | IO17 | **J3-5** |
| N4 | DNP pre-circuit IO5 (R to 3V3, R and C to GND, 0402) | NTC, resistor ladder, potentiometer, piezo bleeder resistor | IO5 | **R19/R20/C16 DNP** |
| N5 | test points VSYS, VBUS_J4, ISEN, SENSE | bring-up, test fixture | – | **TP1–TP4** |
| N6 | Hall sensor for lever/tower | the board already detects lever and rotation via SENSE and ISEN | – | no: the board is far from lever and tower |
| N7 | cell voltage/temperature | VBAT is measured; the cell IC handles protection | IO5 | no footprint; NTC possible via N4 |
| N8 | second motor/vibration | – | – | no (DRV8213 has one channel) |

### 0.4 Implemented: pads and footprints on the bottom

**Top:** no new components.

**Bottom (all optional, nothing assembled).** Exact position, grid and coordinates: main-board-c6.md 11.7.
GPIO assignment: 0b.4.

| Ref | Type | Assignment |
|---|---|---|
| **J3** "Service" | pads 1 × 5 | 1 EN · 2 TXD · 3 BOOT · 4 GND · 5 RXD (IO17) |
| **J6** "Players" | pads 1 × 6, **2.0 mm** (room for the vias next to the module) | 1 3V3 · 2 S1 IO5 · 3 S2 IO20 · 4 S3 IO21 · 5 S4 IO8 · 6 GND |
| **R19, R20, C16** (N4) | 0402 DNP | IO5 → 3V3 (10 k) / → GND (1 MΩ, piezo bleeder, value depends on use) / → GND (10 nF) |
| **J7** "LED" | pads 1 × 3, 2.54 mm | 1 VLED · 2 IO23 · 3 GND |
| **U6** | LDO SPX3819M5-L (adjustable), SOT-23-5, DNP (since 2026-11-09, main-board-c6.md 2.7) | IN = VSYS, OUT = VLED (3.95 V via R23/R24 220 k / 100 k), EN = IO15; C18 2.2 µF at the output |
| **C17, R22** | 10 µF 0805 / 100 k 0402, DNP | VLED → GND / IO15 → GND |
| **TP1, TP2** | test points Ø 1.0 mm (`louie:TestPad_D1.0mm`) | VSYS, VBUS_J4; measure ISEN at R1 and SENSE at R5 on top (TP3/TP4 dropped, routing) |
| **J2** | pads 1 × 5 | 3V3, GND, SDA, SCL, INT; center y = +4.3 so the pads lie in the pocket |

All parts within |y| ≤ 4.8; tallest part U6 (then the TPS22918-DBV, max. 1.45 mm according to TI; the generic KiCad model is
1.64 mm, so `just hull` reported an overrun; U6 is now the SPX3819 in SOT-23-5, main-board-c6.md 2.7). `just fab` omits all DNP parts from the placement file and
BOM (`--exclude-dnp`).

**Deliberately not planned:**

| What | Why |
|---|---|
| Components on the top | no 3 × 3 mm piece free; none of it is essential |
| Assembled parts on the bottom | double-sided PCBA, extra cost, contradicts the principle |
| RC footprints on S2–S4 | internal pull-ups (45 k) and 1 kΩ in the cable are enough; footprints would block via positions (decision 2026-11-05) |
| Hardware load pulse for power banks | firmware keeps the power bank awake (idea-power-bank.md, decision 2026-11-05); IO22 stays free |
| Connectors on the bottom (JST-SH, Qwiic) | about 2.9 mm high (unverified); solder wires on |
| Level shifter or series resistor in the LED data path | V5 LEDs do not need one; the resistor belongs at the cable end (0b.1) |
| VSYS directly on a pad | unfused; only via U6 (LDO with current limit) |

---

## 0b. Extensions using the pads

Questions of the project owner: (1) Is J7 suitable for a NeoPixel chain, and flexibly also for a single LED or a
button? (2) How do you connect four wired buttons (one per arm)? (3) Piezo knock sensor instead of LIS2DH12 to detect
paddle presses? (4) Overall assignment of the free GPIOs and pads on the bottom.

Datasheet values read directly (verified): ESP32-C6 datasheet v1.5 (table 2-2 pin states, table 5-4
DC characteristics, table 5-5 ADC), WS2812B (Worldsemi, Adafruit copy). From search results or
datasheet excerpts (verified, characteristic value only): WS2812B-V5, WS2812B-Mini, SK6812, 74AHCT1G125, SN74LV1T34, TPS22918.

### Summary

1. **J7 is suitable for an LED chain**, with V5-generation LED types (V_IH = 0.63 · VDD: WS2812B-V5,
   WS2812B-Mini-V3, WS2812B-2020) and a **switch in the supply** (U6, enable IO15), because addressable
   LEDs draw quiescent current even when dark. No level shifter on the board. J7 is flexible without extra parts on the
   board: chain, single LED (series resistor in the cable, LEDC PWM) or button (internal pull-up).
2. **Four wired buttons: one dedicated GPIO with pull-up each** on J6 (S1 = IO5, S2 = IO20, S3 = IO21, S4 = IO8).
   Simultaneous presses, interrupt, two wires per arm. A resistor ladder is reliable only for single presses;
   a port expander only for more than four inputs.
3. **Detecting the paddle:** The LIS2DH12 stays on top but only detects "someone hit somewhere". Per arm the best option is a
   **contact under the paddle** (reed switch + magnet or microswitch) on J6; a piezo per arm works on the same
   pads (second choice). Medium benefit (statistics, hit attribution, new modes), not for basic operation.
4. **Pins:** IO5/IO20/IO21/IO8 player inputs, IO15 LED supply on, IO17 RXD, IO23 LED data, IO22 free.

### 0b.1 NeoPixel on J7

#### Levels and supply

| Quantity | Value | Source |
|---|---|---|
| C6 V_OH | ≥ 0.8 · VDD = **2.64 V** (at high-impedance load, typ. close to 3.3 V) | C6 DS tab. 5-4 (verified) |
| C6 V_IH / V_IL (input) | 0.75 · VDD = 2.48 V / 0.25 · VDD = 0.83 V | C6 DS tab. 5-4 (verified) |
| C6 internal pull-up/-down | 45 kΩ typ. | C6 DS tab. 5-4 (verified) |
| C6 drive current | 20 mA default, up to 40 mA (PAD_DRIVER = 3) | C6 DS tab. 2-2/5-4 (verified) |
| WS2812B (5050, old) | VDD 3.5–5.3 V (abs.), characteristics at 4.5–5.5 V; **V_IH 0.7 · VDD**; T0H 0.4 µs, T1H 0.8 µs, T0L 0.85 µs, T1L 0.45 µs each ±150 ns; reset > 50 µs | WS2812B DS (verified) |
| WS2812B-V5 | VDD 3.7–5.3 V; **V_IH 0.63 · VDD**; reset > 280 µs | Worldsemi V5 (verified, excerpt) |
| WS2812B-Mini (3535) | VDD 3.7–5.3 V; V_IH 0.63 · VDD | WS2812B-Mini DS (verified, excerpt) |
| WS2812B-2020 V6 | 2.0 × 2.0 × 0.84 mm; VDD 3.7–5.3 V; quiescent current ≤ 1 µA | WS2812B-2020-V6 DS (verified) |
| SK6812 / SK6805 | VDD 3.7–5.5 V; **V_IH 0.7 · VDD** | SK6812 DS (verified, excerpt) |

What arrives at DIN (3.3 V from the C6) versus the threshold:

| LED supply | VDD | V_IH at 0.7 · VDD | V_IH at 0.63 · VDD | Rating |
|---|---|---|---|---|
| VSYS on battery (via Q1) | 3.0–4.2 V | 2.1–2.94 V | 1.9–2.65 V | level **ok**; **below 3.7 V VDD out of spec** (blue/green get weaker, color shifts) |
| VSYS via USB (J4 → D2 SS34) or charger board | about 4.6 V | **3.22 V** (tight, only 80 mV margin) | 2.90 V (ok) | 0.63 types ok, 0.7 types a matter of luck |
| VBUS 5 V directly | 5.0 V | **3.5 V** (out of range) | 3.15 V (tight) | not planned; also only with USB |
| 3V3 from the LDO | 3.3 V | – | – | no: VDD below spec, and Wi-Fi peaks (382 mA) plus LEDs would load the 3.3 V regulator (TPS62162, 1 A) without need |

**Conclusion:** On VSYS with **V5 types (0.63 · VDD)** the 3.3 V level is sufficient over the whole range, without a
level shifter. In practice SK6812 and old WS2812B mostly work too (unverified). Below about 3.6 V battery voltage
the firmware dims the LEDs or switches them off (VBAT_ADC is measured anyway).

**Level shifter / sacrificial LED, assessed:**

| Solution | Rating |
|---|---|
| 74AHCT1G125 | **unsuitable**: VCC 4.5–5.5 V (V_IH 2.0 V). On battery VSYS is 3.0–4.2 V, i.e. out of range (verified, Nexperia DS) |
| SN74LV1T34 (TI, SOT-23-5) | **suitable if needed**: single supply 1.65–5.5 V, lowered input thresholds, 3.3 V input at 5 V VCC permitted (verified, TI product page). Not on the board; if needed as a tiny part at the start of the chain in the cable |
| "Sacrificial LED" (first LED powered via a diode at VDD − 0.7 V, it regenerates the level) | works on USB (4.6 V → 3.9 V); on battery the first LED is then at 2.3–3.5 V, clearly out of range. Not recommended |
| V5 LEDs directly | **recommended**, zero components |

#### Quiescent current, switch in the supply

Addressable LEDs draw current even when dark, depending on type a few 100 µA to about 1 mA per LED (old types) or
≤ 1 µA (WS2812B-2020 V6) (unverified, type-dependent). Eight LEDs at 0.6 mA = 5 mA; that is about two hundred times the
deep sleep budget (board approx. 25 µA above 3.8 V, main-board-c6.md 2.7). A 1000 mAh battery would be empty in just over a week.

**U6 (DNP): LDO SPX3819M5-L, adjustable (SOT-23-5)** between VSYS and VLED (since 2026-11-09, previously load switch
TPS22918, which allowed only 5.5 V): VIN up to 16 V, 500 mA, internal current limit (approx. 0.8–0.95 A) and thermal
shutdown. VOUT = 1.235 V × (1 + R23/R24) = **3.95 V** (R23 220 k, R24 100 k), C18 2.2 µF directly at the output. It
switches the LED supply (EN on **IO15**, V_IH 2.0 V, with **R22 100 kΩ to GND**; IO15 has no pull at and after reset and
is not an LP pin, so R22 keeps U6 off during reset and in deep sleep) and limits VLED when VSYS is up to 6.6 V (4 × AA).
Why 3.95 V and not a fixed 5.0 V type: V5 LED types need V_IH = 0.63 · VDD; at 3.95 V that is 2.49 V, below the
guaranteed ESP32 V_OH of 2.64 V, at 5.0 V it would be 3.15 V and need a level shifter, for which there is no room on
the bottom. V5 types run from 3.7 V. With a Li-ion cell U6 runs in dropout (VLED ≈ VSYS − 0.3 V). The brightness cap
keeps its dissipation low. No PTC any more: U6 limits the current itself (a 0.5 A PTC would hardly trip below its
current limit); a short circuit on J7 makes U6 cycle in thermal shutdown. The former bypass jumper JP1 is dropped.

#### Current, voltage drop, decoupling, series resistor

- **Current:** up to about 12 mA per color, i.e. about 36 mA per LED at full white (2020/3535); large 5050 up to about 50–60 mA
  (unverified). Sensible for Louie: 4 LEDs (one per player color at the arm roots) up to 8 LEDs. **Firmware cap
  about 30 % brightness** → 4 LEDs ≈ 40 mA, 8 LEDs ≈ 90 mA (unverified). The motor draws 1–2 A from VSYS anyway.
- **Voltage drop:** 2 × 40 cm wire 0.08 mm² (AWG 28, about 0.21 Ω/m) ≈ 0.17 Ω; at 0.1 A 17 mV, at 0.5 A 85 mV
  (calculated). Not critical. The problem is VSYS dips at motor start-up: buffer at the chain.
- **Decoupling:** 100 nF per LED (usually present on strips), **10–47 µF** at the start of the chain. Adafruit recommends
  500–1000 µF for large strips on large power supplies; for 4–8 LEDs less is enough (unverified). On the board
  **C17 10 µF 0805 on VLED (DNP)**.
- **Series resistor 330 Ω (300–500 Ω) at the start of the chain, i.e. at the LED end of the cable**, not on the board
  (Adafruit Best Practices, verified). It damps overshoot and limits the current if DIN carries voltage
  before VDD is present. On the board IO23 → J7-2 is a direct trace.
- **Cable:** DIN twisted with GND, up to about 1 m without problems (Adafruit: "one to two meters"). ESD: the LEDs sit
  in the housing under plastic; series resistor plus C6 ESD (HBM ± 2 kV, C6 DS) is enough (unverified).
- **Power-on behavior:** IO23 has the internal pull-up during reset (C6 DS tab. 2-2: IO18–IO23 = WPU during reset),
  afterwards it is open. Until the firmware initializes the chain, DIN can float → random colors. With U6 off
  (R22) nothing happens.

#### Timing

- The 800 kHz protocol (T0H/T1H ±150 ns) is generated in hardware by the C6 **RMT** (C6 DS 4.2.1.11, 4 channels;
  at 40 MHz clock 25 ns resolution). Wi-Fi interrupts then do not shift any bits. The firmware uses the ESP-IDF RMT driver
  (via esp-idf-hal or the IDF component `led_strip`; choice in
  [firmware-architecture.md](firmware-architecture.md)). Bit-banging would be disturbed by Wi-Fi.
- For long chains the RMT memory has to be refilled by interrupt; whether this causes glitches with active Wi-Fi
  is open (unverified). Irrelevant for 4–16 LEDs. The motor uses LEDC, so no conflict.
- 8 LEDs × 24 bit × 1.25 µs = 0.24 ms per frame, plus reset ≥ 280 µs (V5).

#### J7 flexible: chain, single LED or button

**No component in the data path.** J7-2 is IO23 directly; everything else sits in the cable. The firmware learns from a
setting ("J7: LED chain n / LED / button / off") what is connected.

| Use | Connection | Firmware | U6 group |
|---|---|---|---|
| NeoPixel chain (also 1 LED = "RGB LED") | J7-1 VLED, J7-2 via 330 Ω to DIN, J7-3 GND, 10–47 µF at the start | RMT, IO15 = 1 to switch on | U6, R23, R24, C18 assembled |
| single one-color LED | J7-2 → series resistor → LED → J7-3; e.g. 470 Ω–1 kΩ for 2–3 mA | LEDC PWM (6 channels, motor uses 2) | **leave open** |
| button | J7-2 → button → J7-3, optionally 1 kΩ in series | input with internal pull-up, edge interrupt; wake only from light sleep | leave open |
| analog RGB LED (4 legs) | does **not** work on J7 (needs 3 PWM pins); use a single WS2812/SK6812 instead | – | – |

### 0b.2 Four wired buttons (one button or contact per arm)

#### Pin budget

Optional GPIOs: IO5, IO8, IO15, IO17, IO20, IO21, IO22, IO23. Assigned: IO23 LED data, IO15 LED supply,
IO17 RXD. **For the player inputs: IO5, IO8, IO20, IO21.** IO22 stays reserve.

| GPIO | Pull in operation | Reset state (C6 DS tab. 2-2) | Deep sleep wake | Special feature |
|---|---|---|---|---|
| IO5 | internal 45 k | IE (open) | **yes** (LP GPIO5) | only free ADC pin; N4 pre-circuit |
| IO20 | internal 45 k | WPU | no (light sleep yes) | – |
| IO21 | internal 45 k | WPU | no | – |
| IO8 | **R11 10 k external** (present) | IE + R11 | no | strapping: only in download mode (IO9 = 0) IO8 must be 1; a pressed button only interferes if BOOT is pressed at the same time (0b.6) |
| IO22 (reserve) | internal | WPU | no | replacement for one input, but not brought out to a pad |

#### Comparison

| Criterion | (a) 4 GPIOs with pull-up | (b) resistor ladder on IO5 (ADC) | (c) I²C port expander on J2 |
|---|---|---|---|
| Simultaneous presses | **yes, all 16 combinations** | single presses reliable; 16 combinations only marginally (see below) | yes (8 inputs) |
| Latency | edge interrupt, hardware µs, in firmware < 1 ms (unverified under Wi-Fi load) | ADC polling at intervals (1–5 ms); continuous ADC with DMA possible (0b.3) | INT → interrupt → I²C read (≈ 0.3 ms at 100 kHz) ≈ 1–2 ms |
| Debouncing | software 5–20 ms | averaging over several measurements | software |
| Noise immunity / ESD, 40 cm cable | 45 k internal is high-impedance next to 1–2 A motor PWM → 1 kΩ in series in the cable, wire twisted with GND | contact and connector resistances shift the levels; ADC ±40 mV (C6 DS) | I²C only short (expander next to the board), button lines as (a) |
| Deep sleep wake | only S1 on IO5. Not needed: the lever wakes | practically no: the "lightest" button pulls IO5 only to 2.9 V, nothing gets below V_IL 0.83 V | yes, if INT is on an LP pin (see below) |
| Pads | 4 signals + GND (+ 3V3) | 1 signal + GND + 3V3 | no new ones (J2), INT see below |
| Wiring | 2 wires per arm, star topology | **one 2-wire line through all arms** possible | as (a) from the expander |
| Cost | €0 on the board | 5 resistors | expander breakout about €1–3 |

**On the resistor ladder (b), calculated:** pull-up R0 = 10 k (R19 from N4) to 3V3, button k with its own
resistor to GND, in parallel. Best E24 values (search over all combinations, 1 % tolerance):
**11 k, 18 k, 36 k, 68 k**. Single presses: 2.88 / 2.57 / 2.11 / 1.71 V (gaps > 300 mV, reliable). All
16 combinations lie between 1.13 and 3.3 V; the **smallest gap in the worst case is only 28 mV**,
less than the absolute ADC inaccuracy (±40 mV). With per-device calibration it could work; with motor noise and
contact resistance not reliably. Simultaneous presses are the normal case in the game, though.

**On the expander (c):** PCF8574/TCA9534/MCP23008 (type open). **Caution INT:** J2-5 /INT is connected on the board to
LIS2DH12 INT1 (U4 pad 12), and the LIS2DH12 drives push-pull (only polarity switchable, unverified). An
open-drain INT of the expander must not be added there. So connect the expander INT to **IO5** (S1 pad), not to J2-5, or leave out
U4. (c) is only worth it if more than four inputs are needed (e.g. joker button **and**
paddle contact per arm = 8).

**Recommendation: (a)**, implemented this way (J6, 0b.4).

#### Connectors and cables

- **No connector on the board:** only about 1.5 mm height is free on the bottom; JST-SH (about 2.9 mm, unverified) and PH
  do not fit. Solder wires to J6.
- From J6 a **6-wire cable** (e.g. ribbon 1.27 mm or thin stranded wire) through the cable window into the base
  to a small **distributor** (perfboard or terminal strip). There a **pluggable 2-pin connection** per arm
  (JST-PH 2.0 mm or XH 2.5 mm with crimp contacts), because the arms are removed for the box. 40 cm per
  arm, signal and GND twisted.
- **1 kΩ in series** per signal wire at the board end (heat shrink), against interference and ESD spikes. Pressed level
  with 1 k: 0.07 V (45 k internal) or 0.30 V (IO8, R11 10 k), both < V_IL 0.83 V.

### 0b.3 Detecting the paddle: LIS2DH12, piezo or contact

#### What is "paddle pressed" good for?

| Use | Value | Remark |
|---|---|---|
| **Statistics** (hits per player, reaction time after 🎭 fake brake or ⏪) | medium | only visible with "📊 Statistics & elimination" (PoC: „📊 Statistik & Ausscheiden“) |
| **Hit attribution** | medium to high, experimental | current spike on a hit (ideas.md "hit hunch") + which paddle was pressed in the last ~300 ms → "Lena hit Louie". Without a paddle sensor there is only the current spike without a name |
| **New modes** ("ammo": n hits per round; paddle lock as a penalty, shown rather than enforced) | medium | the mode builder would need a new event |
| False start during the countdown ("Hands on the paddles!") | low | more of a fun display |
| **Trigger a joker** via the paddle (e.g. double hit) | **no** | hitting is the game action; false triggers are certain. Jokers belong on the phone, wireless button or wired button |
| Detect elimination | no | chickens fall independently of the paddle |

Conclusion: nice extra knowledge, not basic operation. So only via the optional inputs.

#### (a) LIS2DH12 on the board (battery compartment)

- A hit on a paddle travels through the arm into the base and arrives as a shock at the sensor. **"Someone hit"
  is plausible** (tap detection with high-pass, threshold above the motor noise). Up to 1.344 kHz ODR
  in low-power mode (ST, unverified) is enough for shocks.
- **Which arm?** The arms are 90° apart; the direction of the shock in X/Y in principle contains a direction.
  With a sensor off-center, plastic joints, play in the plug connections and the motor on top,
  a **reliable attribution is not to be expected** (unverified, measure). Four players often hit almost simultaneously.
- **Motor vibration** is always present (rotation frequency plus gearbox); it masks especially weak hits.
- Further uses: lift/tip-over → motor off (safety), shaking, deep sleep wake via IO2.
- **Rating: keep on top** (about $0.40, assembly option). It does not replace a sensor per arm.

#### (b) Piezo on the board

No. The board sits in the AA sleeve in the battery compartment, poorly coupled mechanically; it would measure the same
as the LIS2DH12, only worse. There is no space on top, and the height on the bottom is too small (piezo buzzer
≥ 1.9 mm).

#### (c) Piezo disc per arm via cable

- **ADC pins:** The C6 has ADC1 on IO0–IO6 (C6 DS, 7 channels). Used: IO0 VBAT, IO1 ISEN, IO3 SENSE, IO4
  VBUS_DET, IO6 SDA, IO2 INT. **Only IO5 is free.** So four analog piezos do not work.
- **Digital works:** A strong hit produces several volts up to a few
  10 V on a piezo disc with a 1 MΩ load (unverified, measure on a sample; the load resistor sets lower cutoff frequency and amplitude, MSI app note
  "Interfacing Piezo Film to Electronics"). The C6 input switches at 2.48 V (V_IH). So the input becomes a
  comparator with a fixed threshold, and light motor hum stays below it.
- **Circuit per arm (all in the cable or at the piezo):** 1 MΩ in parallel to the disc (bleeder resistor, Arduino
  Knock example), **100 kΩ in series** to the pin. The internal clamp diodes of the C6 then limit to 3.3 V + 0.5 V
  with < 0.3 mA at 30 V peak (calculated). For more margin: BAT54S (SOT-23) at the cable end. No RC needed:
  disc (20–27 mm, about 10–20 nF, unverified) and 1 MΩ give τ ≈ 10–20 ms; the pulse is stretched anyway.
  Firmware: input without pull, rising edge, 50–100 ms dead time.
- **Not on IO8** (R11 10 k pulls the level up, the pulse collapses across 100 k/10 k). Piezo channels: IO5,
  IO20, IO21.
- **Analog on IO5:** Only one channel, e.g. "sum of all arms" with adjustable threshold; R20 (1 MΩ) is intended as the
  bleeder resistor for this. The ADC can do 100 kSPS with DMA and threshold interrupt (C6 DS 4.2.2.1); under
  ESP-IDF this is the continuous ADC driver (`adc_continuous`), reachable from Rust via esp-idf-hal or esp-idf-sys
  (unverified, check before implementation).
- **Crosstalk:** A hit on arm 1 also shakes arm 2. With a fixed digital threshold neighboring arms
  may trigger too; countermeasure "first edge wins, lock for 20 ms" (unverified, measure).
- **Cost:** disc €0.10–0.30, 2 resistors, cable (unverified).

#### (d) Contact under the paddle = wired button from 0b.2

| Type | Mounting | Advantages | Disadvantages |
|---|---|---|---|
| **Reed switch + magnet** (about €0.20–0.50 + €0.10, unverified) | reed in the arm under the player end of the paddle, small magnet under the paddle | contactless, no force, does not change the feel of the game, 2 wires, no crosstalk | glass tube fragile (glue it in), adjust switching distance |
| **Microswitch** (€0.20–1) | at the stop of the paddle | unambiguous, robust | actuation force can change the feel of hitting; mounting per model |
| Copper foil contact | two foil strips on paddle and stop | almost free | wear, intermittent contact |
| Hall switch DRV5032 | like reed | bounce-free | needs 3V3 = 3 wires (J6-1) |
| Piezo (c) | glue on | no mechanics | crosstalk, fixed threshold |

A contact delivers exactly the desired information ("player 3 hit"), without signal processing, without
crosstalk, using the circuit from 0b.2. **This is the simplest solution.** Whether a joker button or a
paddle contact is connected to an input is purely a firmware setting (in device-pairing.md another
"input": device = cable, key = S1–S4). Both at the same time per arm needs 8 inputs → joker via phone
or wireless button, paddle via J6; or expander (0b.2 c).

**Recommendation 0b.3:** **Keep the LIS2DH12 on top**. **No piezo** on the board. Paddle detection per arm
optionally via **reed switch (or microswitch) on J6**, piezo per arm only as plan B on the same pads.
First try on a sample whether a reed fits under the paddle (mechanics per model, unverified).

### 0b.4 Overall assignment of the free GPIOs (implemented)

| GPIO (module pad) | Function | Pad | Circuit on the bottom (DNP) | Wake |
|---|---|---|---|---|
| **IO5** (10) | **S1** player 1 (button/reed/piezo); alternatively ADC (ladder, NTC, piezo sum) | **J6-2** | internal 45 k; R19/R20/C16 (N4) | **deep sleep** (LP) |
| **IO20** (26) | **S2** | J6-3 | internal 45 k | light sleep |
| **IO21** (27) | **S3** | J6-4 | internal 45 k | light sleep |
| **IO8** (22) | **S4** (button/reed only, no piezo) | J6-5 | **R11 10 k on top (present)** | light sleep |
| **IO15** (20) | LED supply on (U6 ON) | – | **R22 100 k → GND** | – |
| **IO17** RXD (30) | UART0 RX (console) | **J3-5** | – | – |
| **IO22** (28) | **free (reserve)**, no pad | – | – | – |
| **IO23** (29) | LED data / LED / button | **J7-2** | – | light sleep |

IO2 (INT) and IO6/IO7 (I²C) stay on J2. Pads and footprints: 0.4; position: main-board-c6.md 11.7.

### 0b.5 Assembly variants and firmware notes

| Application | Assemble / connect | Firmware |
|---|---|---|
| Four wired buttons or paddle contacts | nothing on the board; wires on J6, 1 kΩ per signal in the cable | inputs with internal pull-up (S4: R11), edge interrupt, debouncing 5–20 ms; S1 optionally as deep sleep wake source (LP GPIO5) |
| Piezo per arm (digital) | 1 MΩ in parallel + 100 kΩ in series in the cable; only S1–S3 | input without pull, rising edge, 50–100 ms dead time |
| Piezo sum / NTC / potentiometer on IO5 (analog) | R19 and/or R20, C16 depending on use (piezo: R20 1 MΩ; NTC: R19 as divider) | ADC1_CH5, single measurement or continuous |
| Resistor ladder on IO5 | R19 10 k; buttons with 11/18/36/68 k to GND in the cable | ADC, only single presses reliable |
| NeoPixel chain on J7 | U6, R22, R23, R24, C18, C17; 330 Ω and 10–47 µF at the start of the chain | RMT; IO15 = 1 before the first frame; brightness cap about 30 %; dim below about 3.6 V VBAT |
| single LED on J7 | nothing; series resistor in the cable | LEDC PWM on IO23 |
| button on J7 | nothing | input with pull-up on IO23 (light sleep) |
| Console | wires or pogo adapter on J3 (EN, TXD, BOOT, GND, RXD) | UART0, 115200 baud ROM log |
| I²C breakout | wires on J2 (3V3, GND, SDA, SCL, INT) | INT shares IO2 with U4 (push-pull, see 0b.2) |
| Bring-up | probe/pogo on TP1/TP2 (VSYS, VBUS), ISEN at R1, SENSE at R5 | – |

The setting of what is connected to J6/J7 belongs to the device configuration ([device-pairing.md](device-pairing.md)).
Driver choice and firmware structure: [firmware-architecture.md](firmware-architecture.md). First experiments with
buttons on the player inputs on the breadboard: [test-hardware.md](test-hardware.md).

### 0b.6 Implementation and datasheet check

Implemented in `gen_main_schematic.py`, `placement.py`, `gen_main_pcb.py` (all generated, nothing in the GUI), BOM
`parts.csv` (status "DNP/optional"). Assignment as in 0b.4. Position, routing status and envelope: main-board-c6.md 11.7.

**Datasheet check ESP32-C6 (Series Datasheet v1.5, tab. 2-1/2-2 and chap. 3, read 2026-11-04, verified):**

| GPIO | Net | at reset / after reset | Consequence |
|---|---|---|---|
| IO0, IO1 | VBAT_ADC, ISEN_ADC | – / – (no pull) | dividers undistorted |
| IO2, IO3, IO4, IO5 | INT, SENSE, VBUS_DET, IO5 (S1) | IE / IE | no pull; IO4/IO5 (MTMS/MTDI) only for SDIO slave edges, irrelevant here |
| IO6 | SDA | – / IE + WPU (JTAG pad, eFuse default) | R16 10 k external anyway |
| IO7 | SCL | – / IE | R10 |
| IO8 | S4 | IE / IE, strapping | **SPI boot (IO9 = 1): IO8 any level** (tab. 3-3); only download mode (IO9 = 0) needs IO8 = 1. An S4 button pressed at power-on therefore does not disturb normal boot; only S4 + BOOT together gives no valid download mode. ROM log control via IO8 only with eFuse UART_PRINT_CONTROL ≠ 0 (default 0) |
| IO9 | BOOT | IE + WPU / IE + WPU | button on J3 |
| IO12/IO13 | USB | USB pull-up | – |
| IO14 | LED | – / IE | LED off at boot |
| IO15 | IO15 (U6 ON) | IE / IE, **no internal pull** | **R22 required**, otherwise ON floats (TI: "do not leave floating"); EN threshold of the SPX3819: to check in the datasheet review. Strapping (JTAG source) only with eFuse JTAG_SEL_ENABLE |
| IO16 | TXD | – / WPU + OE | ROM log |
| IO17 | RXD | – / IE + WPU | console |
| IO18, IO19 | MOT_IN1, MOT_IN2 | **WPU** / IE | During reset 45 k pull both DRV8213 inputs high (against its internal pull-down): IN1 = IN2 = 1 is "brake", no drive (DRV8213 truth table not re-read, unverified); afterwards the firmware takes control |
| IO20, IO21 | S2, S3 | WPU / IE | inputs, not critical |
| IO22 | – (reserve) | WPU / IE | free. For a later load on the pin (e.g. MOSFET gate): 45 k pull-up during reset, so gate pull-down ≤ 4.7 k |
| IO23 | LED data | WPU / IE | DIN briefly high; no effect with U6 off (R22) |

- **Glitches at power-on:** v1.5 has no glitch table (searched, verified). A forum report mentions a
  pulse < 10 µs on IO21 at start-up (unverified, not read); consistent with "WPU only during reset" on IO18–IO23. Not critical for the
  inputs S2/S3.
- **Open (on a sample):** try IO8 with a pressed button at power-on (test setup:
  [test-hardware.md](test-hardware.md)); LIS2DH12 INT (push-pull, CTRL_REG6) not checked; height of U6 versus
  pocket (1.45 mm according to TI, 1.64 mm in the generic 3D model).

### Sources for 0/0b

- ESP32-C6 Series Datasheet v1.5 (tab. 2-1/2-2 pin states, chap. 3 strapping, 4.2.1.11 RMT, 4.2.2.1 SAR ADC, tab. 5-4/5-5):
  https://www.espressif.com/sites/default/files/documentation/esp32-c6_datasheet_en.pdf
- WS2812B datasheet (Worldsemi, Adafruit copy): https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf
- WS2812B-V5 (Worldsemi): https://learn.watterott.com/kb/ws281x/WS2812B-v5.pdf
- WS2812B-Mini-V3: https://learn.watterott.com/kb/ws281x/WS2812B-Mini-v3.pdf
- WS2812B-2020 V6 (TME): https://www.tme.com/Document/f57342b0dc3e7d573aa1f8b6b5942fcf/WS2812B-2020-V6_V1.2_EN.pdf
- SK6812 (OPSCO, LCSC C5378720): https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2303300930_OPSCO-Optoelectronics-SK6812_C5378720.pdf
- 74AHC1G125/74AHCT1G125 (Nexperia): https://pdf.elecfans.com/p/5172803.html
- TI SN74LV1T34: https://www.ti.com/product/SN74LV1T34
- TI TPS22918 (datasheet SLVSD76C: ON V_IH 1 V / V_IL 0.5 V, DBV 1.45 mm, CT/QOD circuit): https://www.ti.com/lit/ds/symlink/tps22918.pdf;
  LCSC C131941 (TPS22918DBVR), C2680345 is the small reel DBVT
- PTC BHFUSE BSMD0805-050-6V (0.5 A, 6 V, 1.1 mm): https://www.lcsc.com/product-detail/C883108.html
- Adafruit NeoPixel Überguide, Best Practices: https://learn.adafruit.com/adafruit-neopixel-uberguide/best-practices
- Arduino "Detect a Knock" (piezo with 1 MΩ): https://docs.arduino.cc/built-in-examples/sensors/Knock
- Measurement Specialties (now TE), app note 01800004-000 "Interfacing Piezo Film to Electronics", Rev B 2006
  (load resistor, buffer): https://pages.hmc.edu/spjut/NewE80/PDFs/PiezoElectronics.pdf

---

## 1. Further ideas, not implemented yet

Everything here works without changing the board via the existing pads (J2 = I²C + INT, J6, J7) or as a
BOM alternative. Values come from the earlier research and must be checked before use.

| Idea | Connection | Benefit | Characteristics | Note |
|---|---|---|---|---|
| **LIS2DW12** instead of LIS2DH12 (U4) | footprint U4 | flatter, more economical | LGA-12 2 × 2 × 0.7 mm; from about 1 µA; INT switchable to open-drain via register (verified) [ST][st-lis2dw12], [ST Community][st-lis2dw12-int]; LCSC C189624 | check pin and register compatibility with U4 (unverified) |
| **SC7A20** as second source for U4 | footprint U4 | LIS2DH12 supply shortage | LGA-12 2 × 2 mm, register-compatible according to distributors; LCSC C5126709 [LCSC][lcsc-sc7a20] | compatibility unverified, documentation mostly Chinese |
| **TMAG5273** 3D Hall (breakout) | J2 (I²C + INT) | magnet "game pieces", lid/lever position, joystick with magnet | SOT-23-6; 2.3 mA active, 1 µA wake-up-and-sleep, 5 nA sleep (verified) [TI][ti-tmag5273] | whether a magnet gets close enough to moving parts depends on the toy; speed is already available via ISEN |
| **DRV5032** Hall switch | J6 (3V3, GND, input) | bounce-free paddle contact, magnet detection | SOT-23; 0.54 µA (5 Hz variant) (verified) [TI][ti-drv5032] | 3 wires per sensor |
| **MAX17048** state of charge (breakout) | J2 (I²C, address 0x36) | battery % (ModelGauge) | TDFN-8 2 × 2 mm; 23 µA active, 3 µA hibernate (verified) [Flux/LCSC][flux-max17048]; LCSC C2682616 | low priority: VBAT_ADC already measures the cell |
| **Light sensor** (e.g. LTR-303ALS, breakout) | J2 | "lights off → night mode" | I²C, about 2 × 2 mm (unverified) | only useful outside the battery compartment |
| **External piezo buzzer** | J7-2 or a free input on J6, with GND | tones, start signal | flat SMD buzzers from 1.9 mm (Murata PKMCS0909E4000-R1, verified) [RS][rs-pkmcs] | alternative without hardware: tones via the motor (audio-frequency PWM on the DRV8213, sound unverified, test) |
| **I²C port expander** (PCF8574/TCA9534/MCP23008) | J2, INT on IO5 | more than four inputs (joker **and** paddle per arm) | breakout about €1–3 | INT not on J2-5 (push-pull of the LIS2DH12), 0b.2 |

**Hand soldering**, in case someone solders a component directly onto a breakout or an add-on board:

| Package | Soldering iron | Hot air/hot plate | Rating |
|---|---|---|---|
| SOT-23 / SOT-23-6, 0402/0603 | good | – | ★★★ easy |
| DFN/TDFN/QFN with pads to the edge | feasible with flux and tinned pads | good | ★★ medium |
| LGA (accelerometers, MEMS microphone) | gamble, pads completely under the package | yes, with flux | ★ hard |

LGA with a soldering iron only works with pads extended outward (hand-soldering footprint); inspection only electrically
(I²C scan, WHO_AM_I) ([hackaday.io LIS3DH breakout][hd-lis3dh], [FEDEVEL forum][fedevel]). For anyone without
hot air, a ready-made breakout on J2 is the easier way.

[st-lis2dw12]: https://www.st.com/en/mems-and-sensors/lis2dw12.html
[st-lis2dw12-int]: https://community.st.com/mems-sensors-48/lis2dw12-how-are-the-interrupt-pins-internally-connected-74391
[lcsc-sc7a20]: https://www.lcsc.com/product-detail/Attitude-Sensor-Gyroscope_Hangzhou-Silan-Microelectronics-SC7A20TR_C5126709.html
[ti-tmag5273]: https://www.ti.com/product/TMAG5273
[ti-drv5032]: https://www.ti.com/product/DRV5032
[flux-max17048]: https://www.flux.ai/lcsc/max17048gplust10~jvyd.md
[rs-pkmcs]: https://uk.rs-online.com/web/p/piezo-buzzers/9010898P
[hd-lis3dh]: https://hackaday.io/project/8369-lis3dh-breakout-board
[fedevel]: https://fedevel.com/forum/beginners/17960-how-to-solder-packages-lga-and-others-by-hand
