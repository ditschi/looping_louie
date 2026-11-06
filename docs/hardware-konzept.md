# Hardware concept: Looping Louie Wi-Fi upgrade

Status: 2026-11-06 · Part selection and main board (4 layers) are fixed, routing with the optional pads is in
progress. Main board details: [hauptplatine-c6.md](hauptplatine-c6.md). Rejected variants:
[decision-history.md](decision-history.md).

## 1. Goal

A retrofit kit that goes into the battery compartment of Looping Louie (and Loopin' Chewie) **without soldering**
and makes the game controllable through a **web UI on a phone**.

Requirements:

- **The original lever stays** and is the only control on the game: start/stop of the round
  (and wake-up of the electronics, see 5.3).
- After wake-up the electronics stay **permanently active** and serve a web server,
  whether a game is running or not.
- The game mode **cannot be changed during a running round**.
- Several clients at once: game master + players (boosts from eliminated players etc.).
- Create custom game modes and save them under a name.
- Power from a **1S LiPo with USB-C charging** instead of a 9 V block.
- **One main board in AA format for all models**; only the mechanical adapter differs.
- Open (KiCad), reproducible, orderable assembled from JLCPCB or similar → can be given away.

## 2. Supported models

| Model | Battery compartment | Motor rated voltage | Players |
|---|---|---|---|
| Looping Louie old (Milton Bradley) | 1× C (baby), open compartment without lid, metal plate on one side, spring on the other | 1.5 V | 4 |
| Looping Louie new (Hasbro, smaller) | 2× AA, two separate chambers | 3 V | 4 |
| Loopin' Chewie | 2× AA (assumption; if not, Chewie is not supported) | 3 V | 3 |

Original circuit: battery compartment → lever → motor. In the old model it is verifiably **only wires**,
no capacitor, no diode. No regulator, no reverse operation.

## 3. System overview

```
        ┌──────────────────── Looping Louie (unchanged) ──────────────────────┐
        │   Contact 1 ──── lever ──── motor ──── Contact 2                    │
        └──────┬───────────────────────────────────────┬──────────────────────┘
               │                                       │
   ┌───────────┴───────────────┐            (2× AA: via compartment bridge
   │ Board A  (AA format)      │             and board B = bridge)
   │  ESP32-C6 + antenna       │                       │
   │  H-bridge DRV8213         │───────────────────────┘
   │  USB-C J4 + power path    │
   │  3.3 V regulator          │
   │  lever detection          │
   │  buffer capacitors        │
   └───────────┬───────────────┘
               │ cable: BAT_IN, GND (2 wires to J1, see ladeplatine.md)
   ┌───────────┴───────────────┐
   │ Charger board (AA / base) │
   │  USB-C, charge controller,│
   │  power path, cell protect.│──── JST ──── 1S LiPo
   └───────────────────────────┘
```

## 4. Assemblies

### 4.1 Board A: main board in AA format

**The only constraint is the size of an AA cell** (Ø 14.5 × 50.5 mm). It is known that this fits into the
compartment; the *Salto Sammy* shows that electronics fit into this form.

- Board **46 × 13.5 mm, 0.8 mm thick, 4 layers** (decision 2026-11-03): JLC standard stackup
  **JLC04081H-3313** (0.8 mm, outer 1 oz, inner 0.5 oz); L1 components/signals, L2 (In1) solid GND layer,
  L3 (In2) signals, L4 solder pads/signals; rules 0.15/0.15 mm, via 0.3/0.5 mm (details:
  [hauptplatine-c6.md](hauptplatine-c6.md) chapter 11). Dimensions in `hardware/scripts/board_outline.py`.
  The width is set by the ESP32-C6-MINI-1 (13.2 mm). About 2 mm remain at each end for the
  contacts (mechanics open).
- **Height with single-sided assembly**: The board sits slightly below the center of the AA sleeve
  (top side about 0.5 mm above the center). Then the module (13.2 × 2.4 mm) fits with about 0.1 mm clearance
  at the corners. Narrow parts (≤ 4 mm wide) may be up to about 6 mm high. So height is
  not a problem; **area is the tight constraint**.

#### Assembly

**Single-sided machine assembly with 0402 passives** (top); the bottom has only solder pads, test points and
unassembled footprints (DNP), no connectors. Board B stays a pure bridge. Common parts from several
manufacturers (see `hardware/bom/teile.csv`).

- **The two ends are the H-bridge outputs directly** (OUT1 / OUT2). Therefore the
  mounting direction does not matter; "forward" is calibrated once in software.
- Contents (part list in 5.5): ESP32-C6-MINI-1, DRV8213, 3.3 V LDO, USB-C with ESD and
  power path, 2 × 47 µF buffer, lever detection, voltage divider, status LED, LIS2DH12 (optional),
  solder pads for cable, cell, I²C, service, player inputs and LED connection.
- Layout: H-bridge and buffer at one end, ESP module with antenna at the other, no copper under the antenna
  on any of the four layers.

### 4.2 Board B: bridge (2× AA only)

- Pure copper bridge top ↔ bottom end in AA format, no components, very cheap.
- **Not needed if the charger board stands upright in compartment 2** – it has the same bridge built in.
- Motor current flows `Contact 1 → A → compartment bridge → B → Contact 2`.
- A later board B with electronics (e.g. "charger + sensor") is possible
  ([hauptplatine-c6.md](hauptplatine-c6.md) 5.3); in the old model **both boards then go into the
  C-cell adapter** (see 6).

### 4.3 Charger board

Worked out in [ladeplatine.md](ladeplatine.md) (circuit, layout, holder, **wiring diagram**).

- **AA format** (46 × 12.5 × 1.6 mm). Stands **upright** in the second AA compartment and takes over the
  bridge there; the horizontal USB-C socket on the long edge then points up out of the compartment.
  Alternatively flat in a holder in the base, socket through a hole in the wall.
- MCP73831 (500 mA) with **load sharing** (Schottky + P-MOSFET, Microchip AN1149): play while charging.
- ESD protection USBLC6-2SC6, charge indicator LED, JST-PH and solder pads for the battery.
- Flashing only via J4 on A; the USB socket of the charger board is for charging only (hauptplatine-c6.md 2.4).
- Cable to A: 2 wires (VSYS → J1-1 BAT_IN, GND → J1-4); J1-2/3 have no net.
- The battery sits in the base.

## 5. Circuit details

### 5.1 Motor stage

- **DRV8213DSG** (1.65–11 V, 4 A peak), details in [hauptplatine-c6.md](hauptplatine-c6.md) chapter 3.
- **Current sensing and limiting via IPROPI:** R1 1.24 k limits to about 2 A and protects motor, battery
  and board. The IPROPI voltage goes through an RC filter (1 k / 100 n) to the ADC (255 mV/A):
  motor current for start-up, stall and lever detection while running.
- **Autosleep** at IN1 = IN2 = 0 (< 60 nA), outputs then high-impedance; no nSLEEP pin.
- Supply VM directly from VSYS (3.0–5.5 V: battery or USB).
- **PWM about 20 kHz** (LEDC) so nothing whines. The old code used 1 kHz, which is audible.
- Reverse operation and active braking possible.
- Ramps in the firmware against voltage dips (lesson from *MADXhh/LoopingLouieAdvanced*:
  otherwise brownout and reboot on direction change).
- **Currents do not need to be measured for the layout:** At 20 kHz the motor winding smooths
  the current; the mean follows the effective voltage. With duty cycle limiting and ramps
  the motor sees roughly the currents it sees at its rated voltage. Design with margin
  (2 A limit, wide traces on bridge and contacts). A measurement later only serves
  to set the turbo limit and battery size.

### 5.2 Lever detection via the motor circuit

The original lever is in series with the motor. When the H-bridge is in autosleep (outputs high-impedance):

```
GND ──[100k R3]──┬── OUT_A ── Contact 1 ── lever ── motor (few Ω) ── Contact 2 ── OUT_B ──[10k R4]── 3.3 V
                 │
            SENSE (IO3, via protection resistor R5 100k)
```

- Lever **open**: SENSE ≈ 0 V → "stop"
- Lever **closed**: SENSE ≈ 3.0 V (divider 10k/100k across the motor winding) → "start", wakes from deep sleep
- Also tells: "motor connected?"
- While the motor runs, SENSE is not meaningful. Then the lever is detected by **current**:
  with the lever open, no current flows despite PWM (IPROPI, see 5.1).
- SENSE goes to the GPIO through a protection resistor (100k) because OUT_A rises up to the
  supply voltage (up to 5.5 V) while driving.
- R4 on OUT_B costs about 0.3 mA while driving, or feeds about 0.2 mA back into 3V3 at 5.5 V; not critical
  (hauptplatine-c6.md 2.5).
- The old model has no suppression components and no diode → principle usable without restriction.
  Possible suppression components in the new model do not disturb the DC measurement; a diode in series
  would be a problem (check on the first new model).

The *Salto Sammy Pro* shows that this principle works: there the mode is selected by
flipping the original lever several times.

### 5.3 Power saving and wake-up (no extra main switch)

- After a configurable idle time (e.g. 15 min without game and without client): **deep sleep**.
  DRV8213 in autosleep, LDO with low quiescent current → a few µA to a few tens of µA.
- **Wake-up by flipping the Louie lever**: SENSE is on IO3 (LP GPIO) and wakes the ESP32-C6
  from deep sleep with ANY_HIGH. Further wake sources: INT (IO2), VBUS_DET (IO4), S1 (IO5).
- After wake-up Wi-Fi starts first; the round starts only on the next lever flip or on
  release from the web UI. The details are decided in the software concept.

### 5.4 Power supply

- **1S LiPo** 3.0–4.2 V with protection circuit, size depending on space (e.g. 1000–2000 mAh).
- **Inputs on A (3.0–5.5 V):** USB-C J4 via Schottky D2 to VSYS; battery or charger board (BAT_IN, J1/J5) via
  P-FET Q1 (blocks when USB is present, reverse polarity protection). IO4 (VBUS_DET) detects USB plugged in.
- **Measure supply voltage** (divider 470k/470k on IO0). This keeps the motor voltage constant
  regardless of the state of charge: `duty = U_soll / U_akku`.
- Undervoltage: stop the game and warn in the web UI before the cell protection cuts off.

### 5.5 Microcontroller: ESP32-C6

The **ESP32-C6-MINI-1** (13.2 × 16.6 mm, integrated antenna) offers enough free RAM for Wi-Fi + BLE
(BTHome buttons), 22 GPIOs, ADC up to 3.3 V, wake from LP GPIOs and 802.15.4 (Zigbee/Thread) as an option. Analysis:
[analyse-funk-controller.md](analyse-funk-controller.md) 3b; board: [hauptplatine-c6.md](hauptplatine-c6.md).

- **ESP32-C6-MINI-1-H8** (8 MB flash, C42403058), fallback **-N4** (4 MB, C5736265) without layout change.
  Footprint `lcsc:WIFIM-SMD_ESP32-C6-MINI-1` (the KiCad footprint `RF_Module:ESP32-C6-MINI-1` is not used because of its
  antenna keep-out zone).
- **Native USB** (IO12/IO13) via the **USB-C socket J4 on the board**: flashing, debug and 5 V operation incl.
  motor. Power path see 5.4.
- Updates later via Wi-Fi (OTA, with 8 MB flash).
- **Pin assignment:** [hauptplatine-c6.md](hauptplatine-c6.md) 2.3 is authoritative. In short:

| Group | GPIOs |
|---|---|
| ADC | IO0 VBAT_ADC (divider 470k/470k), IO1 ISEN_ADC (IPROPI, 255 mV/A), IO4 VBUS_DET |
| Wake (LP GPIO) | IO3 SENSE (lever, ANY_HIGH), IO2 INT (LIS2DH12/J2), IO4 VBUS_DET, IO5 S1 |
| Motor | IO18 MOT_IN1, IO19 MOT_IN2 (LEDC PWM) |
| I²C | IO6 SDA, IO7 SCL (LIS2DH12, pads J2, pull-ups R16/R10) |
| USB, service | IO12/IO13 USB (J4), IO9 BOOT, IO16 TXD, IO17 RXD (pads J3) |
| Player inputs J6 | S1 IO5, S2 IO20, S3 IO21, S4 IO8 (strapping, 10k pull-up R11) |
| LED | IO14 status LED, IO23 data J7, IO15 enable load switch U6 (VLED on J7) |
| free | IO22 (reserve) |

**All GPIOs except IO22 (reserve) are in use**; IO5, IO8, IO15, IO20, IO21 and IO23 go to optional pads and
unassembled footprints on the bottom (hauptplatine-c6.md 11.7, [idee-optionale-hardware.md](idee-optionale-hardware.md) 0b.4).

Components of board A (source of truth: `hardware/bom/teile.csv`):

| Ref | Part | Function |
|---|---|---|
| U1 | ESP32-C6-MINI-1-H8 (fallback -N4) | MCU, Wi-Fi/BLE/802.15.4 |
| U2 | DRV8213DSGR (WSON-8 2 × 2) | H-bridge with IPROPI current sensing, current limit 2 A (R1 1.24 k), autosleep |
| U3 | AP2112K-3.3 | LDO 3.3 V |
| U4 + C15 | LIS2DH12 + 100 n | accelerometer, **assembly optional** (DNP possible) |
| U5 | USBLC6-2SC6 | ESD USB |
| J4 | HRO TYPE-C-31-M-12 | USB-C on the long edge +y, opening set back 0.7 mm |
| D2, Q1 | SS34F (SMAF), AO3401A | power path VBUS → VSYS or BAT_IN → VSYS (reverse polarity protection) |
| R12/R13, R14/R15 | 5.1 k, 100 k/100 k | CC sink, VBUS_DET divider (also gate pull-down Q1) |
| C1, C2 | 47 µF 1206 | buffer VSYS |
| C4, C8–C14 | 0402/0603 | decoupling, EN RC, ADC filter |
| R1–R11, R16 | 0402 | IPROPI, EN, lever detection (R3 OUT_A → GND, R4 OUT_B → 3V3, R5), dividers, LED, pull-ups |
| D1 | LED green 0402 | status |
| J1, J2, J3, J5 | solder pads bottom | cable to charger board (BAT_IN, –, –, GND), I²C/INT, service (EN, TXD, BOOT, GND, RXD), cell |
| J6, J7 | solder pads bottom | player inputs (3V3, S1 IO5, S2 IO20, S3 IO21, S4 IO8, GND), LED (VLED, IO23, GND) |
| U6, F1, C17, R22, JP1 | bottom, **DNP** | load switch TPS22918 (IO15), PTC 0.5 A, 10 µF, pull-down; solder jumper VSYS → VLED (open) |
| R19, R20, C16 | bottom, **DNP** | circuit for IO5 (S1): 10 k to 3V3, 1 M and 10 n to GND |
| TP1, TP2 | test points bottom | VSYS, VBUS (measure ISEN at R1, SENSE at R5 on top) |
| BT1, BT2 | pads bottom | end contacts OUT_A / OUT_B |

## 6. Mechanics and adapters

| Model | Board A | Board B | Adapter |
|---|---|---|---|
| 2× AA (new, Chewie) | directly in chamber 1 | chamber 2: **charger board upright** (takes over the bridge); board B only if the charger board sits in the base | AA insert of the charger board; cable past the lid |
| 1× C (old) | in 3D-printed C-cell adapter | not needed (in the fallback case also in the adapter, bridge unused) | adapter Ø 26 × 50 mm |

- Fallback case A + B in the C-cell adapter: both boards stacked about 10 mm apart
  (each ±5 mm from the center). There the adapter is still about 24 mm wide, 4–5 mm
  height per board → fits with margin. Same boards and same cable as with 2× AA.

- C-cell adapter: board A sits in the center, flat contact surfaces at the ends. Opposite them in the compartment
  are a flat metal plate and a spring; the positive terminal nub does not need to be replicated as long as the
  plate lies flat. C cell and AA cell are almost the same length (50 vs. 50.5 mm), so
  no length extension is needed.
- The old model has no lid → the cable simply comes out of the top of the compartment.

### 6.1 Printed parts (`hardware/mechanik/huelle.scad`, export: `just stl`)

All parts print **without support material**; assembly only by plugging together, no tools.

| Part | Count | Print orientation | Function |
|---|---|---|---|
| AA shell | 1 | upright (same cross-section along the length) | carries the board from below, pocket for solder pads and cable, cable window on the side at J1 |
| Cap plus / minus | 1 each | inner side on the bed | hold the board ends in a slot (0.8 mm overlap), positive terminal nub optional |
| C-cell adapter | 1 (old model only) | upright | AA→C adapter, longitudinal slot for the cable |

- **Top side open in AA format:** The board (13.5 mm) is almost as wide as the AA sleeve
  (14.5 mm); above the module no wall thickness remains at the edge. The compartment itself encloses the
  insert; with the C-cell adapter it is fully enclosed.
- **End contacts:** Solder nickel strip 4 × 0.15 mm onto BT1/BT2, route it under the board through the
  slot of the cap and bend it over the center on the outside (answers F3 provisionally).
- **Dowels:** 4 pieces of 1.75 mm filament, about 6 mm each (hole 1.95 mm), with a drop of glue if needed.
- Assembly: solder on strips → solder cable to J1 and route it through the window → board into the shell
  → push on caps with dowels, bend strips → (C) slide into the adapter, cable in the slot.

## 7. Software (short overview, details in [software-konzept.md](software-konzept.md))

- Firmware: **Rust, std on ESP-IDF** (esp-idf-svc / esp-idf-hal); game logic as a hardware-free crate that also
  runs in the browser (WebAssembly) and in PC tests. Architecture: [firmware-architecture.md](firmware-architecture.md).
- Wi-Fi: known network, otherwise own access point with captive portal.
- External buttons: BLE BTHome passive (e.g. Shelly BLU Button).
- Roles: game master (selects mode, starts release, marks eliminated players),
  players (boosts etc.).
- Game modes as JSON in flash; create and name custom modes.
- Mode change locked while the lever is "on" or a round is running.
- **Model profiles**:

| Profile | U_nom | 100 % equals | Turbo limit (proposal) | Players |
|---|---|---|---|---|
| Louie old | 1.5 V | 1.5 V motor voltage | 2.5 V | 4 |
| Louie new | 3.0 V | 3.0 V | 4.0 V | 4 |
| Chewie | 3.0 V | 3.0 V | 4.0 V | 3 |

The turbo limits are estimates and will be set during operation.

## 8. Open items

- [ ] Radio test: put a prototype board with a metal spring in front of the antenna into the compartment, check RSSI (offene-punkte.md T4)
- [ ] New model: check whether a diode is in series (lever detection)
- [ ] Contacts at the board ends and retention of the board in the AA compartment (half shell?)
- [ ] Open items of the charger board L1–L6 ([ladeplatine.md](ladeplatine.md))
- [ ] AP2112K with an empty battery: dropout about 250 mV at 600 mA → below about 3.5 V battery 3V3 drops slightly; ESP32-C6 runs from 3.0 V
- [ ] Checks before ordering the main board ([hauptplatine-c6.md](hauptplatine-c6.md) chapter 7)
- [ ] Optional: measure motor current (turbo limit, battery size)
- [ ] Optional: buy a *Salto Sammy Pro* as reference (contact mechanics)

## 9. Next steps

1. Pre-order checks with an ESP32-C6 dev board, the lab supply and the real Louie (motor current, lever network,
   strapping, deep-sleep wake, ADC dividers); no motor driver on the breadboard, stall tests on the prototype
   ([test-hardware.md](test-hardware.md) 4).
2. Firmware skeleton in Rust on the test setup ([firmware-architecture.md](firmware-architecture.md)).
3. Finish routing the main board (hauptplatine-c6.md 11.7) and order it; charger board; printed parts.

## Appendix A: Market research (status 2026-10)

Commercial modules for the battery compartment (all without Wi-Fi/app, not programmable):

- [Salto Sammy](https://www.saltosammy.de/produkt/salto-sammy-tuning-modul/): two boards in
  AA form (one bridge, one electronics), external 9 V block, random flight profiles, about €13.50.
- [Salto Sammy Pro](https://www.saltosammy.de/produkt/salto-sammy-pro/): additionally reverse,
  mode selection via the original lever (switch 1×/2×/3×), about €17–25.
- Loopomator (Blasterparts): according to the manufacturer fits Louie and Chewie, 4× AA, about €15–19.
- CrazyLoops: eBay, details unknown.

Open source projects (selection):

- [KevinSwayzee/looping_louie](https://github.com/KevinSwayzee/looping_louie): ESP32 + L293D,
  web UI via Raspberry Pi and MQTT, good safety logic (watchdog, ramps).
- [MADXhh/LoopingLouieAdvanced](https://github.com/MADXhh/LoopingLouieAdvanced) (MIT):
  ESP32, random states, ramps against brownout.
- [AimoLeffers/looping_louie_plus](https://github.com/AimoLeffers/looping_louie_plus) (GPL-3):
  ATtiny85 + MOSFET, everything in the base, original switch stays.
- [XPerianer/Looping_Louie_EV](https://github.com/XPerianer/Looping_Louie_EV) (GPL-3):
  boost buttons per player, game modes as plugins.

**No** project was found with a Wi-Fi web UI directly on the ESP (without a Pi), several
roles/clients, custom game modes and open KiCad data for a battery compartment insert.

## Appendix B: Legacy project state v1 (tag `v1-legacy`)

Legacy: describes the old v1 (MicroPython on ESP8266), not the current design.

- Hardware (Fritzing, `pcb/LoopingLouie-pcb.fzz`): Wemos D1 mini (ESP8266), N-MOSFET as
  low-side switch + freewheeling diode (forward only), 5 V switching regulator, 2 switches, 2 LEDs, potentiometer.
  Supply 9 V block. KiCad project practically empty.
- Software (MicroPython): Wi-Fi with AP fallback, motor PWM with ramp, buttons, LED, timer
  work. Game logic (`game/`) and web UI (`webinterface/`) unfinished.
- PWM limit for the 1.5 V motor on the 9 V block: `MIN_SPEED = 100`, `MAX_SPEED = 200`
  (of 1023) in `looping_louie/webinterface/chatgpt.py` (in tag `v1-legacy`).
