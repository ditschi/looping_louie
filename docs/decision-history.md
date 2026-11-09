# Decision history

Status: 2026-11-06 · This is a short record of **what was planned or investigated earlier and then rejected or replaced**, and why.
The other documents describe only the current state. The full old text is in Git: commit
`dc555c7` (last state before the cleanup on 2026-11-06), the 2-layer board in commit `c45c6de`, the C3 state in
earlier commits of the former branch `v2` (merged into `main` on 2026-11-08), the old MicroPython/ESP8266 version in tag `v1-legacy`.

"Source" names the document and section **before** the cleanup. Old German section titles are kept in quotes so they
can be found in Git.

## Main changes at a glance

| Date | Topic | New | Before / rejected |
|---|---|---|---|
| 2026-11-01 | Assembly | single-sided machine assembly, 0402, bottom pads only | 0603, double-sided, hand soldering on the bottom |
| 2026-11-02 | Controller | ESP32-C6-MINI-1 (H8 target, N4 fallback) | ESP32-C3-MINI-1-N4 |
| 2026-11-02 | Motor driver | DRV8213 | DRV8833 in parallel |
| 2026-11-02 | USB | USB-C directly on the main board (variant E) | only on the charger board |
| 2026-11-02 | Wireless buttons | BTHome BLE passive | 433 MHz, ESP-NOW, BLE connection |
| 2026-11-03 | Layers | 4 layers | 2 layers (13 connections unrouted) |
| 2026-11-05 | Power bank | keep awake by firmware | hardware load pulse Q2/R17/R18 |
| 2026-11-06 | Firmware | Rust (std on ESP-IDF) | MicroPython (+ C++ as plan B) |
| 2026-11-06 | Mode preview | in the browser via WebAssembly | on the server or JS interpreter |
| 2026-11-06 | License | PolyForm Noncommercial (software), CC BY-NC-SA 4.0 (hardware/docs) | – (previously open) |


## 1. Controller

### Controller ESP32-C3 → ESP32-C6 (2026-11-02)
- Decision: ESP32-C6-MINI-1 in the same footprint (target -H8, fallback -N4); C3 rejected.
- Rejected: ESP32-C3-MINI-1 – because about half as much free RAM with Wi-Fi + BLE, no free GPIO, ADC only up to approx. 2.5 V, no 802.15.4, C3-MINI-1-N4 NRND at LCSC.
- Footprint comparison C3/C6: pads identical (pad 49 max. 5 µm), C6 has fewer NC pads; KiCad footprint `RF_Module:ESP32-C6-MINI-1` not used because of a 43 × 20 mm keepout in the courtyard and a missing 3D model.
- Source: main-board-c6.md 2.1, hardware-concept.md 5.5

### Flash candidates and 4 MB under MicroPython (2026-11-02)
- Decision: plan for -H8 (8 MB), -N4 as fallback without layout change.
- Rejected: C6FH8 chip-down design (own RF tuning and RED testing, several k€), NORA-W406 (only 4 MB, different footprint), Ai-Thinker ESP-C6-12F/XIAO-C6 (too wide).
- Superseded: partition table for MicroPython v1.29 (app 1.81 MiB; OTA with 4 MB would leave only approx. 190 KB file system). No longer applies because MicroPython is rejected.
- Source: main-board-c6.md 1

### Controller alternatives with more RAM (2026-11-02)
- Decision: ESP32-C6-MINI-1 (same dimensions 13.2 × 16.6 mm and same pad grid as C3-MINI-1, 512 KB SRAM, 259 instead of 126 KB free IDF heap with Wi-Fi+BLE, approx. +1 USD).
- Rejected: staying with C3 (pin reserve 0, RAM tight, N4 NRND); C5-MINI-1 and S3-MINI-1 – 15.4 mm wide, do not fit in the AA sleeve (Ø 14.5); C61 – no MicroPython port, less internal SRAM; C3 + PSRAM – not supported by the chip.
- Source: analysis-wireless-controllers.md section 3.1–3.3 and 3b.8

### C3 → C6: pin reassignment and added value (2026-11-02)
- Decision: switch to C6 before ordering (+7 GPIOs, ADC up to 3.3 V instead of 2.5 V, IO2 not strapping, deep-sleep wake by sensor INT, PCNT/MCPWM/LP core/802.15.4).
- Rejected: the pin proposal "C3 today → C6 new" (3.2/3b.1) – replaced by main-board-c6.md 2.3 (DRV8213 instead of DRV8833, J6/J7).
- Source: analysis-wireless-controllers.md 3.2, 3b.1, 3b.3, 3b.5 (C3 comparison columns)


## 2. Motor driver and lever

### Motor driver DRV8833 → DRV8213 (2026-11-02)
- Decision: DRV8213DSG (IPROPI, ITRIP, autosleep, WSON-8 2 × 2).
- Rejected: DRV8833 in parallel (HTSSOP-16 approx. 38 mm², shunt + VINT/VCP + nSLEEP/nFAULT, 8 components, 4 GPIOs, 1.40 USD) – because approx. 39 mm² more area, 2 more GPIOs, more expensive; DRV8212/DRV8837 – no current sensing/limiting.
- The DRV8833 was planned as a fallback (nSLEEP on IO20 with 100 k pull-down, nFAULT on IO21); IO20/IO21 are player inputs today.
- Source: main-board-c6.md 3.1/3.2, 5.4, hardware-concept.md 5.1

### Lever levels and MicroPython wake-up (2026-11-02)
- Decision: R3 100 k OUT_A → GND, R4 10 k OUT_B → 3V3, "lever closed" = HIGH, wake with ANY_HIGH.
- Rejected: old level (lever closed = 0.3 V, WAKEUP_ALL_LOW) – because of MicroPython bug #17334 on the C6; the argument no longer applies with Rust, the new level stays.
- Source: main-board-c6.md 2.5, hardware-concept.md 5.2


## 3. Board: layout, layers, assembly

### Rework package C6 + variant E + board A (2026-11-02)
- Decision: rework done (schematic S1–S12, layout L1–L12, BOM); LIS2DH12 stayed on top contrary to the package (assembly-optional, decision of the project owner).
- Deviations (among others antenna edge strip −y, own footprints for U1/U2/J4/D2, R4/C15 to the right of J4, J1 only BAT_IN/GND) are implemented in the board.
- Area balance board A: DRV8213 freed approx. 39 mm², sensor relocation approx. 9 mm²; with that, variant E fit.
- Source: main-board-c6.md 5.4, 6, 8.2, 8.3

### Main board 2 layers → 4 layers (2026-11-03)
- Decision: 4 layers (JLC04081H-3313, In1 continuous GND), rules 0.15/0.15 mm, via 0.3/0.5 mm.
- Rejected: 2 layers – 13 unrouted connections (best of 12 Freerouting runs, spread 12–25), bottlenecks: north-south crossings in the middle, long east-west buses to the sensor, bottom side also the GND plane (islands). 2-layer rules: 0.13/0.13 mm, default trace 0.15, via 0.3/0.6 mm (JLC 0.10/0.10 + 30 %); older rules 0.15/0.2 mm from commit 90fb77e.
- Comparison: 4 layers 0 unrouted, GND In1 434 mm² in one piece, +€3/+€6/+€10 per order (5/10/30 pcs, unverified), +1–3 working days.
- Rejected stackups: B (L3 as 3V3 plane, only 2 signal layers), C (L2+L3 GND), D (GND outside, components on L1 impossible).
- Source: main-board-c6.md 8.1, 9, 11.1, 11.5, 11.6; 2-layer board in commit c45c6de

### Bottleneck at the right module pins: placement V1 and ADC pre-routes (2026-11-09)
- Decision: R6/R7 next to C13 at the ADC pin, R2/C12 at the top right module corner, `preroute_adc_stubs()` locks the short ADC connections; this took the board from 5–9 to 0–2 unconnected per attempt.
- Rejected: pin swap SENSE ↔ IO5 (V2) – gain within the spread (−0.4 ± 1.6 open per attempt over 12 pairs) and it changes pinout, firmware and docs; USB pair on In2 – worse (blocks the most important crossing layer); fanout keep-clear zone in front of all module pads – displaced GND vias, IO8 open in 17 of 18 attempts; moving J2 – no free space on the bottom outside the bottleneck (pre-routes); finer JLC rules 0.1/0.1 mm – free at JLC but not needed; R2/C12 stacked horizontally – blocked pads 22–25.
- Source: main-board-c6.md 11.9

### Supply up to 6.6 V for 4 × AA (2026-11-09)
- Decision: VSYS 3.0–6.6 V: LDO SPX3819-3.3 (pin-compatible with AP2112K), divider 680k/470k, 16 V capacitors, LED option with LDO SPX3819 adjustable at 3.95 V (R23/R24, C18) instead of load switch TPS22918, F1 and JP1 dropped; USB + 4 × AA: Q1 does not block above approx. 5.2 V, documented, firmware lowers the stall limit (F28).
- Rejected: TPS7A2633 (WSON-6, 2 µA, 18 V) – new footprint, low stock, 3× price; standby with SPX3819 still approx. 9 months (14500) / 2 years (4 × AA); 9 V block / 2S – switching regulator, 2S charger, and the snap terminals do not fit next to the board in a 9 V shell; fixed 5.0 V LED LDO – V5 LED types would need V_IH 3.15 V, above the guaranteed ESP32 V_OH 2.64 V, and there is no room for a level shifter on the bottom; PTC F1 – U6 limits at 0.8–0.95 A itself, a 0.5 A PTC would hardly trip; PWM limiting alone for the LEDs – limits current, not the supply voltage.
- Source: main-board-c6.md 2.7, open-items.md F18

### Introduction of the 4-layer trial in the generator (2026-11-03)
- Process: first a separate project `hardware/main-board-4l/` with selectable layer count (`just pcb einseitig 4`, `four-layer`, `images-4l`), then taken over unchanged (byte-identical) into `hardware/main-board/`; `placement_zweiseitig.py` (C3 state) removed, `placement_einseitig.py` → `placement.py`.
- Freerouting 2.5.0 stayed at 10–18 unrouted signal connections on 4 layers → own router `route_fix.py`.
- Source: main-board-c6.md 11 (introduction), 11.3

### ESD USBLC6-2SC6: stub → pass-through (2026-11-02)
- Decision: D+/D− routed through U5 (J4 → pin 1/3 → pin 6/4 → module).
- Rejected: stub (branch to the ESD, pins 6/4 open) – per ST DS4260 Fig. 7 "Unsuitable layout", every stub adds L·di/dt to the clamping voltage.
- Source: main-board-c6.md 10

### Assembly strategy board A (2026-11-01)
- Decision: single-sided machine assembly with 0402 passives, bottom only solder pads/test points/DNP footprints.
- Rejected: option 1 with 0603 (does not fit), option 2 (hand soldering on the bottom), option 3 (double-sided assembly, expensive).
- Source: hardware-concept.md 4.1

### Layout variants of the main board (2026-11-01)
- Decision: single-sided machine assembly, passives 0402 (then "variant 1b", solder pads instead of JST); today 4 layers, bottom only pads/test points/DNP.
- Rejected: variant 1 (single-sided, 0603) – did not fit (12 parts left over); variant 2 (top machine, bottom hand, 0603) – fallback `placement_zweiseitig.py` removed on 2026-11-03.
- State at the time (C3/DRV8833, 2 layers): 40 components, DRV8833 rotated by 90°, Freerouting left 4–6 connections unrouted, the rest was to be routed in the GUI.
- Source: open-items.md, former section "Main board layout status"

### Early layout decisions for the C3/DRV8833 state (2026-11-01)
- Decision at the time: DRV8833 footprint without built-in 0.2 mm thermal vias; DRV8833 rotated; VSYS as a pre-routed 0.4 mm bus bar; Freerouting export without copper fills; end-contact pads 2 × 2 mm (3 × 3 mm collided with the antenna keepout); one 0402 row at the module.
- Rejected: script routing "unrealistic" – later an own router `route_fix.py` with keep-best gate after all (standard today).
- Source: open-items.md "Decisions made"

### Development guide: 0603 as smallest package, C3/DRV8833 symbols (until 2026-11-02)
- Decision: main board 0402 (machine-assembled), own symbols ESP32-C6-MINI-1, DRV8213DSG, LIS2DH12.
- Rejected: "0603 as the smallest size so that everything stays hand-solderable" – does not fit in the AA format; own symbols ESP32-C3-MINI-1 and DRV8833 in parallel (the generator still creates them as a fallback).
- Source: development.md "Parts", "Schematic"


## 4. Power supply and USB-C

### USB-C on the main board: variants (2026-11-02)
- Decision: variant E – USB-C J4 on A (flashing and 5 V operation incl. motor), power path D2/Q1, pads for charger board (BAT_IN) and cell (J5).
- Rejected: A (only charger board with USB-C, no reverse-polarity protection on A), B (charger board without USB, charging only with open compartment), C (only cell directly, deep discharge/loose cells), D (charge controller on A – does not fit, heat), F (fallback without connector, not needed), G (charger board via USB-C cable – battery voltage on VBUS dangerous or boost needed, lid does not close).
- Also rejected: USB mux TS3USB221, connector at the end face (end contact/cap), mid-mount and vertical connectors, LM66100 as VBUS diode (1.5 A too little), buck-boost instead of LDO, second VBUS pad (VBUS_EXT), D+/D− on J1 (flashing only via J4), divider R7 330 k (C6 ADC measures up to 3.3 V).
- Source: idea-usb-c-main-board.md 5–7

### Idea I1: USB-C rechargeable AA cells as supply (rejected 2026-11-01)
- Rejected: one cell delivers 1.5 V, ≥ 3 V is needed; one compartment is occupied by the main board; would only work with a boost converter.
- Source: open-items.md "Ideas" I1

### Ideas I2 (USB-C on the main board) and I3 (optional pads on the bottom) (2026-11-01 … 11-04)
- Decision: I2 implemented as J4 lying flat at the long edge (idea-usb-c-main-board.md, variant E); I3 implemented as J2/J3/J6/J7 and DNP footprints on the bottom (idea-optional-hardware.md 0/0b).
- Rejected: vertical USB-C connector (6–10 mm height does not fit in the AA sleeve).
- Source: open-items.md "Ideas" I2/I3

### Hardware load pulse for power banks Q2/R17/R18 (2026-11-05)
- Decision: no hardware load pulse; the firmware keeps the power bank awake (timer wake-up plus short radio burst, idea-power-bank.md solution D). IO22 stays free.
- Rejected: AO3400A + 47 Ω/1 W (2512) on VBUS_J4, gate IO22, R18 gate pull-down (first 100 k, then 4.7–10 k because of the 45 k pull-up on IO22 during reset) – because 47 Ω at 5 V (approx. 100 mA) is the same stimulus as a Wi-Fi burst of the C6 (80–120 mA), the motor cannot serve as the load (the lever disconnects it), and the footprints blocked the routing.
- Source: idea-optional-hardware.md 0.3 (N1), 0.4, 0b.4–0b.6; main-board-c6.md 11.7

### Charger board: USB data over the cable to the main board (2026-11-02)
- Decision: flashing only via J4 of the main board; J103-2/3 (D+/D−) of the charger board stay free, 2 wires are enough.
- Done: open item L6 "USB data transfer over the 4-wire cable" dropped. The reason "no GPIO free for charge detection" came from the C3 state.
- Source: charger-board.md 2 and 6 (L6)


## 5. Optional hardware and pads

### Optional hardware: research for the ESP32-C3 (2026-11-01)
- Decision: the research (candidates K1–K16, pin assignment I²C on IO8/IO2, INT on RXD GPIO20, top 4 with LIS2DH12 hand-solder footprint, MAX17048, button on IO9) applied to the rejected C3 with hardly any free pins and is superseded.
- Rejected: C3 rules (IO2 strapping must be 1 at reset, deep-sleep wake only GPIO0–5, component height 1.0–1.2 mm before the sleeve pocket, DRV8833 with parallel channels, light sleep 130 µA) – because the C6 has more free GPIOs, IO2 is no longer a strapping pin, and the sleeve has a 2 mm deep pocket.
- The LIS2DH12 now sits on top (U4, machine-assembled), INT on IO2 (LP-GPIO, deep-sleep wake).
- Source: idea-optional-hardware.md sections 1–6 and source list

### Optional hardware: rejected candidates (2026-11-01 to 2026-11-04)
- Rejected: BMA400 (the reason was the IO2 strapping of the C3), MMA8452Q (being phased out), WS2812 on the board (invisible in the battery compartment), I²S microphone ICS-43434 (3 pins, sound hole, closed compartment), piezo buzzer on the board (≥ 1.9 mm high), MAX17048 on the board (VBAT is already measured, the cell sits at the charger board), SHT40/light sensor (pointless in the compartment), Qwiic connector (approx. 2.9 mm high), universal pad block with 10 pads (25 mm long, both module edges), TVS diodes on the pads, assembled parts on the bottom (double-sided PCBA).
- Source: idea-optional-hardware.md 0.3, 0.4 ("not worth it"), 3–5

### Optional pads with 2 layers (2026-11-03)
- Decision at the time: with 2 layers no additional pads as long as 13 connections are unrouted (bottom = GND plane).
- Superseded: 2 layers is rejected, 4 layers is standard (GND continuous on In1, bottom free for pads).
- Source: idea-optional-hardware.md 0.5 and comparison columns in 0.1/0.2

### Optional pads: first proposal section 0 vs. 0b (2026-11-03)
- Decision: assignment per 0b: J6 "players" = 3V3, IO5, IO20, IO21, IO8, GND; J3-5 = RXD (IO17); IO8 = S4, IO15 = enable of load switch U6 for J7; VLED via U6 (DNP) or JP1.
- Rejected: first proposal J6 = 3V3, RXD, IO20, IO21, GND with IO5 on J3-5 and "do not break out IO8/IO15" – because four player inputs are needed on one block and IO8 (pull-up R11 present) is uncritical as an input; J7 only via JP1 to VSYS – because addressable LEDs draw quiescent current even when dark.
- Source: idea-optional-hardware.md 0.2–0.4, 0b.5

### RC footprints on the player inputs S2–S4 (2026-11-05)
- Decision: J6 are plain pads; only IO5 keeps the DNP input circuit R19/R20/C16 (N4).
- Rejected: R23/R24 10 k pull-ups and C18–C20 10 nF on S2–S4 – because internal pull-ups (45 k) plus 1 kΩ in the cable are enough and the footprints blocked the via positions next to the module (routing 37–50 unrouted).
- Source: idea-optional-hardware.md 0b.4, 0b.6

### Optional pads: deviations during implementation (2026-11-04)
- J6 first planned at y ≈ +0.6 or y = 0, then y = −1.3 (pad 1 was under R6, VBAT_ADC without via space); further moves see main-board-c6.md 11.7. J7, TP3/TP4, R22 moved so that the router keeps via positions under the module. PTC F1 on the board instead of in the cable. U6 QOD open (ERC). J2 moved to y = +4.3 (pads were outside the sleeve pocket).
- Source: idea-optional-hardware.md 0b.6 (deviation table)


## 6. Cost

### Cost change compared to the C3 state (2026-11-02)
- Result: components approx. +0.45 USD (N4) / +2.3 USD (H8) per board, net 2 more extended types (+6.1 USD per order) → approx. +1.1 / +2.9 USD per board at 10 pcs (incl. USB-C stage 0.37 USD).
- Part prices (10 pcs, LCSC/JLC 2026-11-02): C6-N4 3.60, H8 approx. 5.4 (Mouser €4.70, unverified), DRV8213 0.93, USB-C stage (J4 0.19, U5 0.05, D2 0.04, Q1 0.08).
- Source: main-board-c6.md 7

### Cost estimate: scenario B double-sided assembly (2026-11-01)
- Decision: single-sided assembly only (Economic PCBA).
- Rejected: scenario B (Standard PCBA) – +60–70 USD one-time (setup 51 instead of 8 USD, stencil 16 instead of 1.5 USD), panel ≥ 70 × 70 mm with edge rails, in practice at least 10 pcs; 10 pcs ≈ €143 instead of ≈ €94, 100 pcs ≈ €385 instead of ≈ €340 (C3 state).
- Source: cost-estimate.md section 1, 2.1, 2.2, 2.5

### Cost estimate: C3/DRV8833 BOM and 2 layers (2026-11-01/02)
- Decision: calculation switched to C6/DRV8213/4 layers (delta calculation, partly "outdated, recalculate").
- Rejected/superseded: component table C3-MINI-1-N4 (C2838502, 1.29/1.09/1.05/1.01 USD), DRV8833PWPR (0.64/0.51/0.45 USD), JST SM04B (connector dropped); note C3-N4 NRND at Mouser, successor N4X; 2-layer prices (0.8 mm without surcharge) and section 5.7 "assessment/recommendation 2 vs. 4 layers" (small extra cost, large benefit → 4 layers, decided 2026-11-03).
- Source: cost-estimate.md 2.3, 4, 5.1, 5.7


## 7. Wireless buttons

### Wireless buttons: choice of radio path (2026-11-02)
- Decision: BTHome BLE buttons (Shelly BLU), received passively; wired buttons as reference/test.
- Rejected: ESP-NOW (DIY button with LiPo, WiZmote; was plan B) – no added value, extra effort for button hardware; 433/868 MHz EV1527 – receiver RXB6 + 17 cm antenna in the base, pins, fixed code/replay, 6 mA without enable; BLE connection buttons (iTag, HID, Flic 2) – connections shaky in the hotspot (C1), Flic protocol complex; Zigbee as button radio next to Wi-Fi – coordinator + SoftAP/BLE scan not supported (X), only as a separate operating mode (idea-zigbee-operation.md); nRF24 – extra radio, 5 pins; IR – line of sight, identical remotes cannot be told apart.
- Source: idea-wireless-buttons.md 4.2–4.8, 5 (overall comparison), 8 (plan B/C)

### Wireless buttons under MicroPython (2026-11-02, rejected 2026-11-06)
- Finding at the time: `bluetooth`/aioble, override scan default 1.28 s/11.25 ms, `cryptolib` without AES-CCM, RAM problems on the C3 (17 KB free after BLE start, ENOBUFS from the 4th socket); firmware plan `net/ble.py`, `net/espnow.py`, `inputs.py`, `store.py`; feasibility test on XIAO ESP32-C3 with Microdot.
- Rejected: MicroPython – see decision firmware language Rust; test now on XIAO ESP32-C6 with Rust.
- Source: idea-wireless-buttons.md 1, 3, 8, 9


## 8. Firmware language and architecture

### Firmware in hardware-concept.md (2026-11-06)
- Decision: Rust (std on ESP-IDF), see firmware-architecture.md.
- Rejected: MicroPython + Microdot (previous recommendation), Arduino/PlatformIO with ESPAsyncWebServer.
- Source: hardware-concept.md 7

### MicroPython on the C6 (2026-11-02, rejected 2026-11-06)
- Finding at the time: app 1.81 MiB (C3 1.61 MiB) > 1.5 MiB OTA slot with 4 MB; open C6 bugs #19396 lightsleep, #17334 WAKEUP_ALL_LOW, #18101 aioble scan OSError -519, #19208 no gpio_deep_sleep_hold, #18859 Wi-Fi+BLE heap; no LP core access, no 802.15.4, MCPWM missing.
- Rejected: MicroPython – see decision firmware language Rust.
- Source: analysis-wireless-controllers.md 3b.2, 3b.4, 3b.6

### NeoPixel timing with MicroPython (2026-11-03)
- Superseded with MicroPython: `neopixel`/`machine.bitstream` via RMT, `machine.PWM`, `Pin.IRQ`, ADC only single readings from a Python loop (1–5 kHz), wake-up with bug #17334 for `WAKEUP_ALL_LOW`.
- Still valid: RMT generates the signal in hardware (C6: 4 RMT channels), the motor uses LEDC; the firmware is now Rust on ESP-IDF.
- Source: idea-optional-hardware.md 0b.1 (formerly "Timing with MicroPython on the C6"), 0b.2, 0b.3

### Firmware language: MicroPython → Rust (2026-11-06)
- Decision: Rust, std on ESP-IDF (esp-idf-svc/-hal/-sys), hardware-free core also for PC and WASM.
- Rejected: MicroPython + Microdot + aioble (recommendation from 2026-11-01/02 with own build, frozen modules,
  16 sockets) – because slow for preview/bots, no OTA in 4 MB (binary 1.81 MiB > 1.5 MiB slot), C6 bugs
  (deep-sleep wake #17334, BLE scan endurance #18101), no Zigbee; the learning-curve argument no longer applies (code by Claude).
- Source: firmware-language.md summary, 2, 8.1; software-concept.md 2.2–2.3; full text in Git (commit dc555c7
  or working state before the cleanup on 2026-11-06)

### Scoring matrix of the languages (2026-11-02)
- Result at the time: MicroPython 89, C++ 96, Rust std 73, Rust no_std 72 (weighted, max. 120); Rust lost mainly
  on learning curve and maturity of the radio part.
- Rejected: the matrix as basis for the decision – because the weights (learning curve of a Python hobbyist) no longer apply.
- Source: firmware-language.md 7

### C++ (Arduino-ESP32 / ESP-IDF) as plan B (2026-11-02)
- Decision: C++ only as a fallback for parts that do not work in Rust (via FFI).
- Rejected: C++ as main firmware (Arduino-ESP32 3.3.12, NimBLE-Arduino 2.5.2, ESPAsyncWebServer 3.12.1; core as
  C++17 library, Emscripten for WASM) – because no memory safety, more scaffolding for simulator and WASM.
- Source: firmware-language.md 3, 5 (H2)

### Rust no_std (esp-hal + esp-radio + Embassy) (2026-11-02)
- Decision: re-evaluate later, once esp-radio 1.0 and coex are stable.
- Rejected for now: esp-radio 1.0.0-beta.1, coex unstable, trouble-host 0.8, picoserve 0.20, esp-hal-ota 0.7 –
  because exactly AP + BLE + many clients are the least mature.
- Source: firmware-language.md 4.2

### Hybrids and preview location (2026-11-02 → 2026-11-06)
- Decision: preview in the browser via WASM from the Rust core.
- Rejected: H1 Rust core in MicroPython, H3 MicroPython WASM (gzip approx. 195 KB), H4 preview only on the server
  (`POST /api/modes/preview`, then recommended for V1) – because of two toolchains or ESP compute time; with Rust
  unnecessary. The JS interpreter stays only in the PoC.
- Source: firmware-language.md 5

### Firmware architecture after review: BLE crate (2026-11-06)
- Decision: NimBLE wrapper from esp-idf-svc 0.53 first, esp32-nimble 0.13 as fallback (E8).
- Rejected: esp32-nimble 0.13 as first choice – because it depends on esp-idf-svc 0.53 anyway and is only tested
  on the C6 with IDF 5.3.6.
- Source: firmware-architecture.md 12 (E8)

### Firmware architecture after review: WebSocket sending (2026-11-06)
- Decision: own non-blocking send path with acknowledgements and backpressure (E13).
- Rejected: `EspHttpWsDetachedSender::send()` from the hub thread – because it blocks httpd and hub for up to 5 s per frame
  and deadlocks in the httpd context.
- Source: firmware-architecture.md 5.4

### Firmware architecture after review: N4 with OTA (2026-11-06)
- Decision: H8 as target; N4 after measurement with OTA, with a `www` partition or without OTA (E11).
- Rejected: "N4 with OTA supported" as the normal case – because the app with embedded web files will realistically be
  1.6–2.0 MB.
- Source: firmware-architecture.md 6.1

### Hotspot password (2026-11-06)
- Decision: random on first start, in NVS (E17).
- Rejected: password derived from the MAC (software-concept.md 3.2) – because the MAC is sent in every beacon.
- Source: firmware-architecture.md 5.1

### MicroPython memory and radio details on the C3 (2026-11-02)
- Figures at the time: C3 free heap Wi-Fi+BLE 126–178 KB, MicroPython start heap 64 KB, only 17 KB free after BLE
  (#14293), ENOMEM from IDF heap (#7038); aioble scan, espnow, RMT TX only (433 MHz not feasible in Python).
- Rejected: as a planning basis – because C3 and MicroPython are rejected.
- Source: firmware-language.md 1, 2.1–2.5

### Firmware layers in Python (2026-11-01)
- Decision: crates louie-core / louie-proto / louie-app / louie-fw / louie-sim / louie-wasm (firmware-architecture.md).
- Rejected: `firmware/main.py`, `louie/hal/*.py`, `core/*.py`, `net/`, `web/` (Microdot), `store.py`, pytest,
  `hal/buttons_ble.py`; `just flash`/`just upload` with mpremote.
- Source: software-concept.md 8.1, 9; firmware-language.md 9

### Update strategy "stage 1: files over Wi-Fi" (2026-11-01)
- Decision: real OTA with two app slots and rollback, web UI in the firmware.
- Rejected: Python files and web UI by file upload, MicroPython only via USB – because MicroPython is rejected.
- Source: software-concept.md 8.3

### Constraints ESP32-C3 in the software concept (2026-11-01)
- Decision: ESP32-C6-MINI-1 (512 KB SRAM, 4/8 MB flash).
- Rejected: C3-MINI-1-N4 (400 KB SRAM, 4 MB), expansion stage 0 "feasibility test MicroPython on XIAO ESP32-C3",
  nFAULT of the DRV8833 (DRV8213 has no nFAULT, stall detection via IPROPI).
- Source: software-concept.md 2.1, 8.1, 10

### Language options table in the software concept (2026-11-01)
- Rejected: table MicroPython/Arduino/ESP-IDF C/Rust/ESPHome with pros/cons – replaced by firmware-language.md.
- Source: software-concept.md 2.2


## 9. Tests and open items

### Breadboard prototype with C3 (2026-10-31)
- Superseded: prototype with XIAO ESP32-C3 + DRV8833 module; replaced by test-hardware.md (C6/DRV8213). Open item "check strapping pins against C3 datasheet" done with the C6 (main-board-c6.md 2.4).
- Source: hardware-concept.md 8, 9

### Motor driver on the breadboard (rejected 2026-11-06)
- Rejected: motor driver variants on the breadboard (Pololu MP6550, DRV8833 + INA219, low-side MOSFET + shunt) – motor tests run on the prototype boards; the breadboard is only for pre-order checks and software (LED mode).
- Source: test-hardware.md (previous version, sections 4.2/4.3)

### Open items done or made moot by C6/DRV8213/4 layers (2026-11-01 … 11-06)
- Done/dropped: F2 cable exit J1 (→ solder pads, cable window in the sleeve), F5 strapping pull-ups C3 (C6: IO2 not strapping, IO8 10 k stays), F6 LED D1 on the bottom (status LED now assembled on top), F7 thickness (0.8 mm, JLC04081H-3313), F8 assembly strategy (single-sided), F10 charger board parts (verified 2026-11-01), F11 Freerouting rework, F12 C3-N4 discontinued/N4X.
- Assumptions dropped: A8 USB over the 4-wire cable (flashing only via J4), A10 thermal vias DRV8833 (now A17 for DRV8213), A15 minimum trace 0.13 mm (4 layers: 0.15 mm). Reworded for C6/DRV8213: A1, A2, A4, A6, A11, A13, A14, A16, A17, A18.
- Source: open-items.md "Open questions", "Assumptions"

### Feasibility test MicroPython on XIAO ESP32-C3 (2026-11-02)
- Decision: the feasibility test moves, language-neutral, to test-hardware.md (C6 board, Rust).
- Rejected: test "louie-probe" in MicroPython with C++ reference, scenarios S1–S5, abort criteria for both heaps
  (`gc.mem_free`, `idf_heap_info`), decision table MicroPython/C++ – because MicroPython and C3 are rejected.
- Source: firmware-language.md 8.2–8.5, software-concept.md 2.3 item 2

## 10. License

### License for software, hardware and docs (2026-11-06)
- Decision: software PolyForm Noncommercial 1.0.0, hardware and docs CC BY-NC-SA 4.0, commercial use only with
  permission (LICENSE).
- Rejected: CERN-OHL-S/-P (hardware) and MIT/Apache-2.0/GPL (firmware) – because they allow commercial use;
  CC BY-NC-SA for the code too – because Creative Commons advises against CC licenses for software; share-alike for the
  software too – not wanted (changes to the code may stay private).
- Source: open-items.md F9
