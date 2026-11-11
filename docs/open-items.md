# Open items, assumptions and decisions

Status: 2026-11-11 · Collected list to go through together. Details are in the linked documents.

Current status in one sentence: main board with **ESP32-C6-MINI-1** (target -H8, fallback -N4), **DRV8213**,
**USB-C (J4)**, **LDO TPS7A2633** for 3.3 V (rev B, the design to order), **4 layers**, single-sided
assembly, routed completely; firmware in **Rust** (std on ESP-IDF). Authoritative:
[main-board-c6.md](main-board-c6.md), [hardware-concept.md](hardware-concept.md),
[firmware-architecture.md](firmware-architecture.md).

**Numbers:** F/A numbers stay fixed because other documents refer to them. Missing numbers are done or were
dropped by the switch to C6/DRV8213/4 layers (history: [decision-history.md](decision-history.md)).
New: T = tests (breadboard, measurement on the Louie or prototype board), S = software and operation.
R = findings of the concept and hardware review of 2026-11-10 ([review-2026-11-10.md](review-2026-11-10.md)); the
rated list and the recommended order live there and are not repeated here.

---

## 1. Next steps

| Step | Content | Reference |
|---|---|---|
| 1 | **Buy the dev board** (Waveshare ESP32-C6-DEV-KIT-N8 or ESP32-C6-DevKitC-1-N8; no motor driver board) and **run the pre-order checks** 4.1–4.5: motor current on the lab supply, lever network on the real Louie, boot/strapping/wake, IO18/IO19 levels (F17), ADC dividers (T1, T5, part of T2; A2–A5). Software tests in LED mode (T3, T7, T8) run in parallel | [test-hardware.md](test-hardware.md) 2, 4, 5 |
| 2 | ~~Finish routing~~ **done:** rev B (LDO TPS7A2633) routed completely, ERC 0, DRC 0, 0 unconnected, 149 vias, 3V3 to the module 48 mΩ; rev A (SPX3819) on `main` likewise as fallback (F15) | [main-board-c6.md](main-board-c6.md) 11.4 |
| 3 | ~~Delta review of the 3.3 V block~~ **done 2026-11-11** for the LDO (wiring review 9); the buck findings W18–W21 (wiring review 8) are gone with the LDO (F29). Then the remaining wiring-review items F20–F25 | [wiring-review.md](wiring-review.md) 9 |
| 3a | **Order preparation:** check before ordering (F13, F14, A9, A11, inspect the layout in the GUI), real quote with Gerber/BOM/CPL (`just fab`), stock of TPS7A2633 (809 on 2026-11-11) and the H8 at order time | [main-board-c6.md](main-board-c6.md) 7, [cost-estimate.md](cost-estimate.md) |
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
| F19 | ~~SENSE overvoltage~~ **decided 2026-11-09:** R5 = 470 k (about 6 µA clamp current at 6.6 V; wiring review W1) | – | done; check the lever level on the prototype (A4) |
| F20 | **VBUS node and VBUS_DET** (W2, W3): Schottky leakage lifts the 200 k VBUS node when warm (Q1 only partly on, false VBUS_DET); 100k/100k is below VIH min at 4.75 V. Same topology on the charger (R105). | a) leave as is · b) 10–22 k bleed VBUS_J4 → GND and R14 → 68 k; charger R105 → 10–22 k | b) |
| F21 | **J2 INT sharing** (W5): INT1 is push-pull, so an external switch on J2 INT conflicts with a fitted U4. SA0 part **decided 2026-11-09:** SA0 on 3V3, I²C address 0x19 (W4). | a) external switch only with U4 DNP (document) · b) ≥ 10 k series resistor U4 INT1 → /INT | a) |
| F22 | **Parts close to the pins** (W6, W7, W8): EN RC about 7 mm from EN pad 8 (state `32a3535`; about 12 mm after the 6.6 V power-path change, wiring review 7), no capacitor near the module 3V3 pad (nearest 14 mm), C15 about 6 mm from the LIS2DH12. | a) leave as is and test on the prototype · b) C12 next to EN pad 8, 100 nF (+10 µF) at pad 3, C15 next to U4 pins 9/10 | b) as far as the layout allows; it touches placement.py and the routing session (F15) |
| F23 | **Missing footprints recommended by the datasheets** (W9, W10, W11): 100 nF at USBLC6 VBUS pin 5 (main and charger), 22–33 Ω series resistors in USB D+/D−, 10 k pull-up on IO9 (BOOT). | each: add or accept | add the IO9 pull-up and the 100 nF at U5; USB series resistors only if there is space |
| F24 | **Low cell, 3V3 below 3.0 V** (W12, review R-B2): the LDO drops about 0.27 V typ / 0.45 V max at the 380 mA radio peak; no supervisor, only the EN RC and the C6 brownout reset. | a) firmware: cut-off on the **filtered, low-load** VSYS at **3.4–3.5 V** (warn at 3.6 V), placeholder `VSYS_MIN_MV = 3500`, brownout detector as last resort · b) additionally a DNP footprint for a 3.0 V supervisor on EN | a); rule and thresholds in [main-board-c6.md](main-board-c6.md) 2.7, final numbers from test-hardware.md 4.1 (sag) and T12 (A3) |
| F25 | **BOM details** (N2, N3, N13): D1 has no specific part (dark at 1 k if VF is high); C101/C102 4.7 µF 0603 fall below the required 4.7 µF under DC bias; voltages missing for C10–C14, C16; U6 only together with R22. | – | choose a D1 part with known VF (or R9 220–330 Ω); C101/C102 → 10 µF; complete parts.csv |
| F26 | ~~Q1 with USB and 4 × AA~~ merged into **F28** (wiring review W15) | – | see F28 |
| F27 | **LDO details** (W13, W14, W16, W17): U3 is now the TPS7A2633 (rev B, F18), stable with 1–100 µF ceramics per TI; its checks are T10–T15 ([test-hardware.md](test-hardware.md) 4.7). U6 (LED LDO, DNP) stays SPX3819 adjustable at 3.95 V with C18 2.2 µF, F1 dropped. Still open: stability of U6 with MLCC outputs and the short datasheet review of the adjustable U6 circuit (R23/R24, C18). | – | U6 only matters when J7 is fitted; check together with the LED option |
| F15 | ~~Routing of the current version~~ **done 2026-11-10/11:** own router, rev A after a 120-attempt long run, rev B with the LDO in 7 of 8 attempts; both 0 unconnected, DRC 0 | – | done; result and baseline: [main-board-c6.md](main-board-c6.md) 11.4 |
| F18 | ~~Input voltage above 5.5 V~~ **decided 2026-11-09:** VSYS 3.0–6.6 V for 4 × AA (divider 680k/470k, C1/C2 16 V, LED LDO SPX3819 adjustable 3.95 V instead of load switch U6, F1 and JP1 dropped); no 9 V block. **3.3 V regulator decided 2026-11-11: low-Iq LDO TPS7A2633 in WSON-6** (rev B = the design to order; low standby with Li-ion over the whole range). The buck TPS62162 tried the same day was dropped because of W21; rev A with the SPX3819 stays on `main` as fallback ([proposal-supply-standby.md](proposal-supply-standby.md), [decision-history.md](decision-history.md)) | – | done; all supply numbers in [main-board-c6.md](main-board-c6.md) 2.7. Open: LCSC number of the adjustable SPX3819 (U6), part number of C8, availability 47 µF 16 V, tests T10–T15 |
| F28 | **Power path USB + 4 × AA.** Q1 only blocks while the battery is below VBUS; with 4 × AA above approx. 5.2 V the cells feed through its body diode even with USB plugged in (stall: up to approx. 1.6 W in Q1). Today: use USB without AA cells, firmware lowers the stall limit to 0.8 A (main-board-c6.md 2.7). | a) keep (documentation + firmware) · b) ideal-diode / power-mux IC instead of D2/Q1 (new part, layout in the USB area) | a) for this revision; b) in a later revision |
| F29 | ~~Buck block findings W18–W21~~ **decided 2026-11-11: option A**, LDO TPS7A2633 instead of the buck ([proposal-supply-standby.md](proposal-supply-standby.md)); with it W18–W21 no longer apply (no inductor, no switch node, no PWM mode) | – | done; the LDO block has its own delta review (wiring review 9) |
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
| T10 | LDO: 3V3 ripple and noise at VSYS 3.7 / 5.0 / 6.6 V, no load and 300 mA, and with the motor PWM running (PSRR about 50 dB at 1 kHz, less at 20 kHz); scope at C9, 20 MHz limit; pass ≤ 30 mV p-p | A21 | **only on the board**, 4.7 | [main-board-c6.md](main-board-c6.md) 2.7 |
| T11 | LDO: load step 0 → 300 mA with C9 22 µF; pass dip ≤ 150 mV, recovery ≤ 100 µs, no ringing | A21 | **only on the board**, 4.7 | same |
| T12 | LDO: dropout, sweep VSYS 4.0 → 3.0 V at 150 mA and 380 mA, read 3V3; pass 3V3 ≥ 3.0 V down to VSYS ≈ 3.3 V (150 mA) and ≈ 3.45 V (380 mA); **sets the cut-off numbers** | A3, F24 | **only on the board**, 4.7 | same |
| T13 | Board standby in deep sleep at VSYS 3.5 / 3.7 / 4.0 / 6.0 V (also in LDO dropout); pass ≤ 40 µA everywhere | A3 | **only on the board**, 4.7 | same |
| T14 | LDO temperature: Wi-Fi hotspot with clients (about 150 mA average) at VSYS 6.4–6.6 V for 15 min, U3 case temperature; pass < 80 °C at 25 °C ambient in free air, then once in the closed compartment | A21 | **only on the board**, 4.7 | same |
| T15 | ADC noise on VBAT_ADC and ISEN_ADC at 10 Hz with the motor running and stopped (supply ripple through the LDO) | A21, A6 | **only on the board**, 4.7 | same |

Charger board: open items L1–L5 in [charger-board.md](charger-board.md) 6 (connector in the new model, heating of the
MCP73831, battery polarity, contact pressure, base).

---

## 4. Assumptions (please check)

| # | Assumption | Why unverified | Alternatives considered |
|---|---|---|---|
| A1 | **Envelope:** largest radius 6.94 mm (J4) with AA radius 7.25 mm, so approx. 0.3 mm clearance; end caps clear (`just hull`). | Calculated from the STL; compartments have play, but no guarantee. | thinner sleeve, place the board lower |
| A2 | **Motor current < 1 A**; DRV8213 with 2 A current limit (R_IPROPI 1.24 k) is sufficient. | Not measured; pre-order check [test-hardware.md](test-hardware.md) 4.1 (T2). | adjust R_IPROPI (table in 4.1) |
| A3 | **LDO TPS7A2633** (U3, rev B since 2026-11-11) is sufficient: 3.3 V down to VSYS ≈ 3.3–3.45 V at the 380 mA radio peak (dropout 0.27 V typ / 0.45 V max), below that 3V3 follows VSYS; the C6 needs 3V3 ≥ 3.0 V (not VSYS, [wiring-review.md](wiring-review.md) W12, F24). VIN up to 18 V. Quiescent current 2 µA typ (4.5 µA max), board approx. 15–18 µA over the whole range. Dissipation up to 0.47 W at 6.4 V / 150 mA in WSON-6 (θJA 73.3 K/W). The firmware cuts off at 3.4–3.5 V on the filtered VSYS ([main-board-c6.md](main-board-c6.md) 2.7). | Dropout over temperature interpolated from the table; IQ in dropout not specified; temperature on the small board not measured (T12, T13, T14). | buck TPS62840 (6.5 V max), hybrid buck + LDO ([proposal-supply-standby.md](proposal-supply-standby.md)) |
| A4 | **Lever detection** with R3 100 k OUT_A → GND, R4 10 k OUT_B → 3V3: lever closed ≈ 3.0 V (HIGH), open 0 V; deep-sleep wake on IO3. | Depends on motor resistance, a possible diode in the new model and DRV8213 leakage currents in autosleep (T1, T2); pre-order check [test-hardware.md](test-hardware.md) 4.2, leakage final on the board. | comparator, active measuring pulse via the H-bridge |
| A5 | **Voltage divider VSYS 680k/470k** with 100 nF is accurate enough (6.6 V → 2.7 V, 3.0 V → 1.23 V). | High impedance, ADC input loads it; pre-order check [test-hardware.md](test-hardware.md) 4.5. Also VBUS 100k/100k gives only 2.5 V at IO4, about at VIH (0.75 × 3.3 V = 2.48 V) → digital wake check in 4.3 (F20). | 220k/220k-class divider (more quiescent current), divider switchable via MOSFET |
| A6 | **Current sensing via IPROPI** (R8/C14 → IO1, 255 mV/A) is sufficient for lever and hit detection while running. | ADC resolution at low currents (T2). | different R_IPROPI (also changes the current limit) |
| A7 | **Wi-Fi and BLE range** is sufficient despite the motor and metal contacts nearby. | See F1 (T4). | module variant with external antenna |
| A9 | **Design rules 4 layers:** 0.15 mm trace/clearance, via 0.3/0.5 mm; JLCPCB multilayer allows 0.09/0.09 mm ([main-board-c6.md](main-board-c6.md) 11.2). | Other manufacturers (Aisler, PCBWay) have their own limits. | cross-check before ordering |
| A11 | **Footprint of the ESP32-C6-MINI-1** (own, `lcsc:WIFIM-SMD_ESP32-C6-MINI-1`; pads identical to the KiCad footprint) matches the datasheet. | Pad numbering, pin 1 position and pad nets checked against MOD Table 3-1 / Fig. 3-1 in the wiring review (2026-11-09); the EPAD dimensions in Fig. 11-1 are not self-consistent, so Espressif's footprint files remain the reference ([datasheet-facts.md](datasheet-facts.md) G1-ESP32-34). | **check before ordering** |
| A12 | **Loopin' Chewie** has 2 × AA. | Not seen. | otherwise not supported |
| A13 | **Bottom side:** only pads, test points and DNP footprints in the pocket (\|y\| ≤ 5.2 mm); tallest part U6 (LED LDO SPX3819, SOT-23-5, DNP) with 2.0 mm pocket depth. | `just hull` reports a violation of the 1.5 mm limit with the generic 3D model (1.64 mm). | correct the model; assemble U6 only when needed |
| A14 | **Service access:** flashing via USB-C J4 (USB-Serial-JTAG); emergency path via J3 (EN, TXD, BOOT, GND, RXD) and test points TP1/TP2 (VSYS, VBUS). | – | Tag-Connect footprint (larger) |
| A16 | **Current paths** (BAT_IN → Q1 → VSYS → VM, OUT_A/OUT_B) on outer layers ≥ 0.3–0.5 mm, battery-motor path pre-routed (31 mV at 2 A); the routing gate checks the width per IPC-2221. | Check the via count per layer change on the finished routing (one 0.3 mm via carries roughly 1 A). | second via in parallel, wider traces |
| A17 | **GND vias directly in the module's center pads** (7 pcs) and thermal vias in the DRV8213 exposed pad, unfilled. | Solder can wick away during assembly. | filled vias (extra cost), vias next to the pads |
| A18 | **Sensor INT on IO2** (J2, LP GPIO, wakes from deep sleep): LIS2DH12 INT1 is push-pull; IO2 is not a strapping pin on the C6. | Polarity checked 2026-11-09: CTRL_REG6 INT_POLARITY resets to 0 = active-high, INT1 always push-pull (LIS2DH12 p.38 Table 43, p.21 Table 13) → wake IO2 on HIGH, no internal pull-up. Still open: J2 sharing with an external switch (F21). | open-drain source, BMA400 |
| A19 | **Hit on the player button** stands out from the running motor. | Not measured (T6). | evaluate only during motor pauses, high-pass |
| A21 | **LDO stable and quiet with the chosen capacitors** (C8 4.7 µF 16 V 0402 at IN, C9 22 µF 10 V 0805 at OUT) and **cool enough with 4 × AA** (about 0.5 W at 6.4 V in hotspot mode). | TI specifies 1–100 µF ceramic at OUT and ≥ 1 µF at IN; effective C8 under DC bias and the temperature on this board are not measured. | larger C8 (0603/0805), more GND copper or vias at U3; buck TPS62840 |
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
