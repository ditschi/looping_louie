# Open items, assumptions and decisions

Status: 2026-11-06 · Collected list to go through together. Details are in the linked documents.

Current status in one sentence: main board with **ESP32-C6-MINI-1** (target -H8, fallback -N4), **DRV8213**,
**USB-C (J4)**, **4 layers**, single-sided assembly; firmware in **Rust** (std on ESP-IDF). Authoritative:
[main-board-c6.md](main-board-c6.md), [hardware-concept.md](hardware-concept.md),
[firmware-architecture.md](firmware-architecture.md).

**Numbers:** F/A numbers stay fixed because other documents refer to them. Missing numbers are done or were
dropped by the switch to C6/DRV8213/4 layers (history: [decision-history.md](decision-history.md)).
New: T = tests (breadboard, measurement on the Louie or prototype board), S = software and operation.

---

## 1. Next steps

| Step | Content | Reference |
|---|---|---|
| 1 | **Buy the dev board** (Waveshare ESP32-C6-DEV-KIT-N8 or ESP32-C6-DevKitC-1-N8; no motor driver board) and **run the pre-order checks** 4.1–4.5: motor current on the lab supply, lever network on the real Louie, boot/strapping/wake, IO18/IO19 levels (F17), ADC dividers (T1, T5, part of T2; A2–A5). Software tests in LED mode (T3, T7, T8) run in parallel | [test-hardware.md](test-hardware.md) 2, 4, 5 |
| 2 | **Finish routing the current version** (with pads and DNP footprints on the bottom), see F15 | [main-board-c6.md](main-board-c6.md) 11.7 |
| 3 | **Check before ordering** (F13, F14, A9, A11, inspect the layout in the GUI) | [main-board-c6.md](main-board-c6.md) 11.6 |
| 4 | **Order the prototype batch** (F16) | [cost-estimate.md](cost-estimate.md), [test-hardware.md](test-hardware.md) |
| 5 | **Set up the firmware in Rust**: core crate (game logic, hardware-free) with PC tests and WebAssembly preview, then the ESP-IDF part | [firmware-architecture.md](firmware-architecture.md) |

---

## 2. Open questions (your decision)

| # | Question | Options | Recommendation |
|---|---|---|---|
| F1 | **Antenna and end contact at the same end.** The module antenna is at one end of the board; the battery contact (metal) and the OUT_A trace in the edge strip are there too. The antenna keep-out applies on all layers ([main-board-c6.md](main-board-c6.md) 2.6). | a) leave as is, check with an RSSI test · b) module variant with external antenna (u.FL) as plan B · c) route the contact at the antenna end with a wire on the outside | a) with RSSI test T4 |
| F3 | **End contacts (mechanics).** Provisional: nickel strip 4 × 0.15 mm on BT1/BT2, bent around on the outside through the slot of the cap ([hardware-concept.md](hardware-concept.md) 6). | a) nickel strip (provisional) · b) battery contact clips (e.g. Keystone SMD) · c) brass cap/rivet · d) spring plate | a) test on the printed part; contact pressure also for the bridge (L4) |
| F4 | **Sleeve in the AA compartment** (`sleeve.scad`): below J4 the cable window removes the edge rail as a support, so plug forces go into the solder tabs. | a) shorter and deeper window · b) support rail between J1 and J5 | test on the printed part ([main-board-c6.md](main-board-c6.md) chapter 6) |
| F13 | **Get a real quote.** All costs are extrapolations. | Gerber (`just fab`) into the JLC calculator (website and JLCONE), stack-up JLC04081H-3313, 0.8 mm; read off price and lead time | before ordering ([cost-estimate.md](cost-estimate.md) 5.7) |
| F14 | **Module H8 or N4.** -H8 (8 MB) is the target and has been available at JLC since 2026-11-06 (620 pcs). Both are pin- and footprint-compatible. | a) H8 · b) N4 | H8 (headroom for OTA, languages, Zigbee); with embedded UI, languages and WASM the firmware will probably be 1.6–2.0 MB; OTA on N4 only with a `www` partition or without OTA ([firmware-architecture.md](firmware-architecture.md)) |
| F17 | **Reset level of motor inputs.** During reset, internal pull-ups on IO18/IO19 pull IN1/IN2 HIGH → the DRV8213 brakes briefly (no start-up). | a) leave as is · b) external 3.3 k pull-downs on IN1/IN2 (coast also during reset, approx. 1 mA per pin when HIGH) | measure in [test-hardware.md](test-hardware.md) 4.4 (reset, boot **and deep sleep**, with and without `gpio_hold_en`): a) if deep sleep gives a reliable LOW and the boot HIGH window is < approx. 0.5 s; otherwise b). Reason: IN1 = IN2 = HIGH in deep sleep keeps the DRV8213 braking, SENSE stays 0 V and the lever wake fails ([main-board-c6.md](main-board-c6.md) 3.2) |
| F15 | **Routing of the current version.** With the pads and DNP footprints on the bottom, our own router does not yet route the board completely. | Proposals 1–4 in [main-board-c6.md](main-board-c6.md) 11.7 (fewer footprints under the module, improve the router, Freerouting as a pre-stage, move parts) | status and rounds: 11.7 |
| F16 | **Prototype batch:** quantity, module (F14), assemble LIS2DH12 or not, manufacturer. | 5 / 10 / 30 pcs; JLC Economic PCBA (single-sided) | after F13 and the pre-order checks ([test-hardware.md](test-hardware.md) 4); T3 does not gate the order; costs: [cost-estimate.md](cost-estimate.md), [test-hardware.md](test-hardware.md) 7 |

---

## 3. Tests

Test setup, measurement records and scope: [test-hardware.md](test-hardware.md) (section 1: what is checked before
ordering, section 5: software in LED mode, section 6: what only the prototype board shows). No motor driver on the
breadboard: everything that needs the motor driven runs on the prototype board. Results feed into the assumptions (section 4).

| # | Test | Checks | Where (test-hardware.md) | Source |
|---|---|---|---|---|
| T1 | Wake with `WAKEUP_ANY_HIGH` on IO3 with inverted lever level; special case "lever closed when going to sleep" | A4 | pre-order 4.2 (real lever, no driver) and 4.3 (wake sources), final on the board | [main-board-c6.md](main-board-c6.md) 2.5, 7 |
| T2 | Motor current and lever on the Louie; DRV8213: current limiting, heating during stall, lever detection in autosleep (outputs Hi-Z) | A2, A4, A6 | motor current: pre-order 4.1 (lab supply), lever: 4.2; **DRV8213 part and stall detection only on the board** (6) | [main-board-c6.md](main-board-c6.md) 7 |
| T3 | Hotspot with 8 phones + BLE scan (BTHome) at the same time: heap, stability, coexistence | S7 | software setup 5.3 (does not gate the order) | [device-pairing.md](device-pairing.md) 8, [idea-wireless-buttons.md](idea-wireless-buttons.md) 10 |
| T4 | RSSI in the compartment with metal contact in front of the antenna, both mounting orientations (edge strip −y) | F1, A7 | **only on the board** (6) | [main-board-c6.md](main-board-c6.md) 7 |
| T5 | IO8 (strapping) with a player button pressed during boot | A20 | pre-order 4.3 (dev board has 10 k on IO8) | [idea-optional-hardware.md](idea-optional-hardware.md) 0b |
| T6 | Hit on the player button or knocking vs. motor vibration (LIS2DH12) | A19 | **only on the board** (6), no sensor breakout | [idea-optional-hardware.md](idea-optional-hardware.md) 6 |
| T7 | Shelly BLU: advertising interval, fixed MAC, legacy advertising; "long" when the hold time is reached or on release | – | software setup 5.3 | [idea-wireless-buttons.md](idea-wireless-buttons.md) 10 |
| T8 | Captive portal on iOS and Android | S6 | software setup 5.3 | [software-concept.md](software-concept.md) 3.2 |
| T9 | Can you feel 0.3 s jerks or the kickback (0.6 s, −30 %)? | – | **only on the board** (6), needs the motor driver | [web-ui-concept.md](web-ui-concept.md) 10, [mode-builder.md](mode-builder.md) 9 |

Charger board: open items L1–L5 in [charger-board.md](charger-board.md) 6 (connector in the new model, heating of the
MCP73831, battery polarity, contact pressure, base).

---

## 4. Assumptions (please check)

| # | Assumption | Why unverified | Alternatives considered |
|---|---|---|---|
| A1 | **Envelope:** largest radius 6.94 mm (J4) with AA radius 7.25 mm, so approx. 0.3 mm clearance; end caps clear (`just hull`). | Calculated from the STL; compartments have play, but no guarantee. | thinner sleeve, place the board lower |
| A2 | **Motor current < 1 A**; DRV8213 with 2 A current limit (R_IPROPI 1.24 k) is sufficient. | Not measured; pre-order check [test-hardware.md](test-hardware.md) 4.1 (T2). | adjust R_IPROPI (table in 4.1) |
| A3 | **AP2112K** is sufficient; with an empty battery 3V3 drops slightly (dropout approx. 250 mV at 600 mA), the C6 runs from 3.0 V. Quiescent current 55 µA. The firmware cuts off the cell at approx. 3.3–3.4 V under load. | Brownout risk during radio peaks with an empty battery; droop estimate from the stall current in [test-hardware.md](test-hardware.md) 4.1, real check only on the board. | LDO with low quiescent current (TLV75533, RT9080), buck-boost (e.g. TPS63802) |
| A4 | **Lever detection** with R3 100 k OUT_A → GND, R4 10 k OUT_B → 3V3: lever closed ≈ 3.0 V (HIGH), open 0 V; deep-sleep wake on IO3. | Depends on motor resistance, a possible diode in the new model and DRV8213 leakage currents in autosleep (T1, T2); pre-order check [test-hardware.md](test-hardware.md) 4.2, leakage final on the board. | comparator, active measuring pulse via the H-bridge |
| A5 | **Voltage divider VSYS 470k/470k** with 100 nF is accurate enough (5.5 V → 2.75 V). | High impedance, ADC input loads it; pre-order check [test-hardware.md](test-hardware.md) 4.5. Also VBUS 100k/100k gives only 2.5 V at IO4, about at VIH (0.75 × 3.3 V = 2.48 V) → digital wake check in 4.3. | 100k/100k (continuous current), divider switchable via MOSFET |
| A6 | **Current sensing via IPROPI** (R8/C14 → IO1, 255 mV/A) is sufficient for lever and hit detection while running. | ADC resolution at low currents (T2). | different R_IPROPI (also changes the current limit) |
| A7 | **Wi-Fi and BLE range** is sufficient despite the motor and metal contacts nearby. | See F1 (T4). | module variant with external antenna |
| A9 | **Design rules 4 layers:** 0.15 mm trace/clearance, via 0.3/0.5 mm; JLCPCB multilayer allows 0.09/0.09 mm ([main-board-c6.md](main-board-c6.md) 11.2). | Other manufacturers (Aisler, PCBWay) have their own limits. | cross-check before ordering |
| A11 | **Footprint of the ESP32-C6-MINI-1** (own, `lcsc:WIFIM-SMD_ESP32-C6-MINI-1`; pads identical to the KiCad footprint) matches the datasheet. | Only compared against the KiCad footprint ([main-board-c6.md](main-board-c6.md) 2.1), not directly against the datasheet. | **check before ordering** |
| A12 | **Loopin' Chewie** has 2 × AA. | Not seen. | otherwise not supported |
| A13 | **Bottom side:** only pads, test points and DNP footprints in the pocket (\|y\| ≤ 5.2 mm); tallest part U6 (TPS22918) 1.45 mm per TI with 2.0 mm pocket depth. | `just hull` reports a violation of the 1.5 mm limit with the generic 3D model (1.64 mm). | correct the model; assemble U6 only when needed |
| A14 | **Service access:** flashing via USB-C J4 (USB-Serial-JTAG); emergency path via J3 (EN, TXD, BOOT, GND, RXD) and test points TP1–TP4. | – | Tag-Connect footprint (larger) |
| A16 | **Current paths** (BAT_IN → Q1 → VSYS → VM, OUT_A/OUT_B) on outer layers ≥ 0.3–0.5 mm, battery-motor path pre-routed (31 mV at 2 A); the routing gate checks the width per IPC-2221. | Check the via count per layer change on the finished routing (one 0.3 mm via carries roughly 1 A). | second via in parallel, wider traces |
| A17 | **GND vias directly in the module's center pads** (7 pcs) and thermal vias in the DRV8213 exposed pad, unfilled. | Solder can wick away during assembly. | filled vias (extra cost), vias next to the pads |
| A18 | **Sensor INT on IO2** (J2, LP GPIO, wakes from deep sleep): LIS2DH12 INT1 is push-pull; IO2 is not a strapping pin on the C6. | Reset polarity (CTRL_REG6) not checked in the datasheet. | open-drain source, BMA400 |
| A19 | **Hit on the player button** stands out from the running motor. | Not measured (T6). | evaluate only during motor pauses, high-pass |
| A20 | **IO8 as player input S4** (strapping, 10 k pull-up) does not disturb boot: for SPI boot the level does not matter, only download mode needs 1. | Button pressed at power-up not tested (T5). | do not press S4 during boot; different pin |

---

## 5. Software and operation (open)

| # | Question | Proposal | Source |
|---|---|---|---|
| S1 | Start via the lever directly, or only after release as the default? | – | [software-concept.md](software-concept.md) 11 |
| S2 | Hotspot with password or open by default? | with password | [software-concept.md](software-concept.md) 11 |
| S3 | Define lever gestures (force hotspot, admin reset), rule out confusion with normal play; can toggling 3× be detected reliably? | status LED shows the window | [software-concept.md](software-concept.md) 11, [web-ui-concept.md](web-ui-concept.md) 10 |
| S4 | Users may save modes: on by default? | on | [software-concept.md](software-concept.md) 11 |
| S5 | "Who may control": is "everyone" as the default safe enough for parties? | – | [web-ui-concept.md](web-ui-concept.md) 10 |
| S6 | Captive portal behavior on iOS and Android | in test (T8) | [software-concept.md](software-concept.md) 11 |
| S7 | How many simultaneous clients are safe? | 8 | [software-concept.md](software-concept.md) 11 |
| S8 | Mode builder: test ⏪/⏩ left/right with children; keep the joker count the same across meanness levels?; vibration is missing on iPhones – is the fill ring enough? | – | [mode-builder.md](mode-builder.md) 9 |
| S9 | Device pairing: keep the assignment across restarts? May the game master pair devices? One device with two Louies? | – | [device-pairing.md](device-pairing.md) 8, [idea-wireless-buttons.md](idea-wireless-buttons.md) 10 |
| S10 | Set the Shelly key via GATT from the Louie (pairing without the Shelly app)? | – | [idea-wireless-buttons.md](idea-wireless-buttons.md) 10 |

---

## 6. Decisions made

Reasons and rejected alternatives: [decision-history.md](decision-history.md).

| Topic | Decision | Reference |
|---|---|---|
| Controller | ESP32-C6-MINI-1, target -H8, fallback -N4 (ESP32-C3 rejected) | [main-board-c6.md](main-board-c6.md) |
| Motor driver | DRV8213DSG with IPROPI, current limiting, autosleep (DRV8833 rejected) | [main-board-c6.md](main-board-c6.md) 3 |
| USB | USB-C J4 on the main board, flashing only via J4; charger board separate | [main-board-c6.md](main-board-c6.md) 2.4, [charger-board.md](charger-board.md) |
| Layers, thickness | 4 layers, JLC04081H-3313, 0.8 mm (2 layers rejected; formerly F7) | [main-board-c6.md](main-board-c6.md) 11 |
| Assembly | single-sided machine assembly (top), bottom only pads, test points, DNP (formerly F8) | [main-board-c6.md](main-board-c6.md) 11.7 |
| Pinout | authoritative: [main-board-c6.md](main-board-c6.md) 2.3 (sensor INT IO2, I²C IO6/IO7, J6 players, J7 LED, IO22 free) | – |
| Cable J1 | solder pads instead of a connector, cable through the window of the sleeve (formerly F2) | [hardware-concept.md](hardware-concept.md) 6 |
| Boards in the compartment | one main board + plain bridge or charger board in the second compartment | [hardware-concept.md](hardware-concept.md) |
| License (formerly F9) | software: PolyForm Noncommercial 1.0.0; hardware and docs: CC BY-NC-SA 4.0; commercial use only with permission | [LICENSE](../LICENSE) |
| Firmware | Rust, std on ESP-IDF; game logic as a hardware-free crate (ESP, PC, WebAssembly); C++ only as fallback (MicroPython rejected) | [firmware-architecture.md](firmware-architecture.md) |
| Mode preview | in the browser via WebAssembly from the Rust core crate | [firmware-architecture.md](firmware-architecture.md) |
| External buttons | BLE BTHome passive (Shelly BLU); 433 MHz, ESP-NOW, Zigbee rejected as button radio | [idea-wireless-buttons.md](idea-wireless-buttons.md) |
| Command runner | `just` | [development.md](development.md) |
| Schematic, layout | generated by script (`just schematic`, `just pcb`); own symbols because of pin types (ERC) | [development.md](development.md) |
| Routing | own router `route_fix.py` with keep-best gate and routing score | [development.md](development.md), [routing-score.md](routing-score.md) |
| Silkscreen | reference designators only on the fab layer (cannot be placed legibly on 13.5 mm) | – |

---

## 7. Ideas

Ideas live in their own documents; only the references are here.

- [ideas.md](ideas.md) – collection of ideas (game modes, UI, committee)
- [idea-optional-hardware.md](idea-optional-hardware.md) – additional hardware on the bottom (sections 0/0b implemented)
- [idea-usb-c-main-board.md](idea-usb-c-main-board.md) – USB-C and cell directly on the main board (basis for J4/J5)
- [idea-power-bank.md](idea-power-bank.md) – power supply via a power bank in the base (open items P1–P4)
- [idea-wireless-buttons.md](idea-wireless-buttons.md) – wireless buttons as players
- [idea-zigbee-operation.md](idea-zigbee-operation.md) – Zigbee operation in the home Wi-Fi (open items there)
