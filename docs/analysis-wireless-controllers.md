# Radio and antenna (ESP32-C6): coexistence, layout, module facts

Status: 2026-11-06 · Reason: BTHome BLE buttons (passive scan, e.g. Shelly BLU) are a V1 feature, in addition
to Wi-Fi (STA or own hotspot with up to 8 phones). The controller is the **ESP32-C6-MINI-1** (target -H8,
fallback -N4). Related: [main-board-c6.md](main-board-c6.md), [idea-wireless-buttons.md](idea-wireless-buttons.md),
[firmware-architecture.md](firmware-architecture.md). Why C6 and not C3/C5/S3/C61: [decision-history.md](decision-history.md).

Markers: **(verified)** = source read or recalculated from the project files · **(unverified)** = secondary source,
estimate, or not checked in the datasheet.

**Summary**

- **One antenna for Wi-Fi + BLE is correct:** The C6 has **one** radio with **one** RF path. Wi-Fi, BLE and
  802.15.4 share it by time-division multiplexing. A second antenna gives no separation.
- **The limits are airtime and coexistence** (BLE scan + SoftAP with clients = "C1, unstable"), not the antenna.
- **Layout:** The GND fix L2 is done; there is no copper under the antenna on any of the four layers.
  Still open: the **antenna end** (plus plate or minus spring), to be decided by an RSSI test.
- **Module:** ESP32-C6-MINI-1, 8 MB (-H8) as target, 4 MB (-N4) as fallback, pin- and footprint-compatible.

---

## 1. Shared antenna for Wi-Fi and BLE

### 1.1 One radio, time-division multiplexing

| Statement | Status |
|---|---|
| The chip has **only one RF path**; Wi-Fi and BLE cannot transmit/receive at the same time; switching by time-division multiplexing | (verified) [IDF Coexistence C6][idf-coex-c6] |
| With "Wi-Fi connected", Wi-Fi and BLE each get e.g. **50 %** per period | (verified) [idf-coex-c6] |
| BLE scan + **STA connected** = Y (stable); BLE scan + **SoftAP connected** = **C1** (supported, unstable) | (verified) [idf-coex-c6] |
| Module has **one** antenna connection (MINI-1: PCB antenna, MINI-1U: U.FL) | (verified) [C6-MINI-1 datasheet][c6-mini-ds] |

**Two antennas (Wi-Fi on one, BLE on the other)?** No. There is only one RF port. With an external
RF switch the IDF can switch between two antennas (antenna diversity). But that only changes *which*
antenna the single radio uses at the moment. It does not allow simultaneous operation (unverified, diversity API
not checked in detail). A second antenna therefore adds **no capacity**, at most reception gain in a poor
position. A better position for the one antenna is enough for that.

### 1.2 What really limits

| Factor | Assessment |
|---|---|
| **Wi-Fi airtime** | 8 phones × 10 states/s ≈ 80 small frames/s, each approx. 0.1–0.3 ms incl. ACK → **approx. 2–3 % airtime** (unverified, calculation). Plus background traffic of the phones. Not a bottleneck. |
| **BLE share** | While BLE scans, Wi-Fi packets are delayed by some 10 ms (unverified). Not critical for joker buttons. |
| **Coexistence mode** | SoftAP + clients + BLE scan = C1. **Biggest risk**, only measurable (stage 0 in [idea-wireless-buttons.md](idea-wireless-buttons.md) 8). |
| `esp_coex_preference_set` | **Deprecated**, replaced by `esp_coex_status_bit_set/clear` (only for special cases such as BLE Mesh). Reachable from Rust via `esp-idf-sys`, but not needed. (verified) [Sysprogs/IDF][coex-pref] |
| **SoftAP beacon interval** | Keep the default 100 ms. The coexistence period follows the beacon (verified, [idf-coex-c6]); longer intervals worsen the phone connection. Espressif advises keeping the defaults under coexistence. |
| **Wi-Fi power saving** | With BT active, the IDF requires modem sleep (no `WIFI_PS_NONE`) (unverified). Check on the prototype. |

### 1.3 Recommended BLE scan parameters (NimBLE, e.g. via `esp32-nimble`)

| Parameter | Value | Reason |
|---|---|---|
| Type | **passive** (no scan request) | BTHome is fully in the advertising → less airtime |
| Interval / window | **100 ms / 30–50 ms** (duty 30–50 %) | Shelly transmits for 1 s after each press (verified, idea-wireless-buttons.md 4.1) → ≥ 3 windows per press. Stack defaults are too slow for buttons (unverified) → set explicitly. |
| Duration | Continuous scan (no end), **only in READY/RUNNING** and only with paired buttons | Otherwise: BLE off, full airtime for Wi-Fi |
| Duplicate filter | **off** | Otherwise the controller filter drops follow-up packets from the same address and thus later presses (unverified, check per stack). The firmware filters duplicates via the BTHome packet ID. |
| Filter | In the scan callback, check service UUID `0xFCD2` and known MAC immediately; pass only matches to the game logic via a channel | little work in the BLE task |
| PHY | 1M, **no Coded PHY** | Coded PHY packets occupy the radio for a long time (verified, [idf-coex-c6]) |

Window = interval (100 % duty) is allowed; the coexistence scheduler cuts it anyway. The test should compare 30 % and 100 %
(missed presses vs. WebSocket latency).

---

## 2. Radio layout check (4-layer board)

### 2.1 Espressif rules (MINI modules with PCB antenna)

| Rule | Status |
|---|---|
| PCB antenna **outside** the base board, feed point close to the edge; otherwise cut out the base board under and next to the antenna | (verified) [HW Design Guidelines][hdg-c3] |
| **≥ 15 mm clearance in all directions** to metal in the enclosure | (verified) [hdg-c3] |
| No copper under the antenna on **all layers**; module **not centered** with cutouts | (verified) [hdg-c3], [c6-mini-ds] |
| Plenty of ground and **dense GND vias** at the module near the antenna | (verified) [hdg-c3] |
| Enclosure affects the antenna → measure the end product | (verified) [hdg-c3] |

The guideline was read in the C3 version; for the C6-MINI-1 (same form factor, same antenna at the module end)
it applies the same way (unverified). In the AA format, "antenna beyond the edge" and "15 mm clear" **cannot be
met**: there is a battery contact at both ends. The goal is therefore: avoid everything avoidable and measure the
unavoidable.

### 2.2 Findings

Coordinates in mm relative to the board center, antenna at −x (from `louie-main.kicad_pcb`, verified 2026-11-06).

| # | Finding | Rating | Location |
|---|---|---|---|
| L1 | Keepout "Antenna" from x = −19.85 to −14.6 (5.2 mm), all four layers: no copper fill, no vias, no traces; "Antenna bottom" additionally without components | **OK** | `gen_main_pcb.py` `antenna_keepout()` |
| L2 | Edge strip 1.2 mm at the **−y** edge ("Antenna edge", y = −6.75 … −5.55): no fill, no vias, traces allowed. So there is **no GND strip** under the antenna any more; 0 mm² copper fill in the keepouts on all four layers | **done** | `antenna_keepout()` (`ANTENNA_TRACK_STRIP`, `ANTENNA_TRACK_SIDE = −1`); [main-board-c6.md](main-board-c6.md) 11 |
| L3 | Trace **OUT_A** (motor PWM) on B.Cu in the edge strip (y = −6.15) to end contact BT1 | **Risk**, unavoidable (the end contact must be connected). At the edge and thin is already the best position. | `route.py`/board |
| L4 | Board end in front of the antenna 3.15 mm (−23 … −19.85, keepout "Antenna end"): no fill, no vias, but **pad BT1 (2 × 2 mm, bottom) at x = −21.4** plus **nickel strip** around the edge. The metal sits 1.5–3 mm in front of the antenna end, behind it the plus plate or spring of the compartment. | **Risk** (main risk, inherent) | `placement.py` (BT1), [hardware-concept.md](hardware-concept.md) 6.1 |
| L5 | GND vias in the module's center pads; **In1.Cu is a continuous GND layer** 0.1 mm under the module up to the antenna | **OK** (better than the earlier 2-layer board) | `module_ground_vias()`, main-board-c6.md 11 |
| L6 | FR4 under the antenna (0.8 mm) and in front of the antenna not cut out | **OK/accepted** (a cutout would break the end-contact mechanics). Slight detuning (unverified) | `board_outline.py` |
| L7 | Ground plane behind the antenna approx. 26 × 13.5 mm, about λ/4 long | **OK** for an inverted-F antenna (unverified, rule of thumb) | – |
| L8 | Installation: board sits in the **open printed shell**, in the old Louie in the plastic C-cell adapter | **OK** as long as **no carbon/metal filament** is used (conductive, detunes). Note in `hardware/mechanics/README.md`. | `sleeve.scad` |
| L9 | Motor/gearbox in the game center, battery compartment under the base plate. Plastic is not critical; motor and wires are small metal parts a few cm away | **Low risk** (unverified), measure | – |

### 2.3 Actions

1. **L2 (done):** `antenna_keepout()` has an additional rule area over the edge strip, on all
   layers, with **copper fill and vias forbidden, traces allowed**. This keeps the OUT_A trace possible, and
   there is no GND fill under the antenna. The edge strip is at the −y edge because OUT_A runs from the DRV8213
   (module corner −y) there to BT1 without crossing (electrically equivalent, unverified).
2. **Decide the antenna end (open):** The mounting direction does not matter electrically (software calibration). For radio,
   the **flat plus plate** is probably better than the **minus spring**: the spring is a metal coil
   a few mm long, i.e. a possible parasitic radiator (unverified). In the RSSI test, measure **both directions**
   and mark the result on cap and shell (arrow "antenna"). Test setup: [test-hardware.md](test-hardware.md).
3. Optional: make BT1 as small as mechanically possible (e.g. 1.5 × 2 mm) and the nickel strip only as long as needed.
4. After every layout change, check that only BT1 and OUT_A lie between x = −23 and −14.6 (DRC and
   area evaluation in pcbnew).

### 2.4 Additional antenna?

| Variant | Assessment |
|---|---|
| Second **PCB trace antenna** on the bottom | **No.** The module already has a tuned antenna and only one RF port. A trace antenna would need MINI-1U or a chip-down design, a matching network (π network), tuning with a VNA, and a free area of approx. 15 × 5 mm. That area does not exist. |
| **C6-MINI-1U-H4** (13.2 × 12.5 mm, U.FL, C20627095) + FPC antenna | **Plan B if the RSSI test turns out poor.** Advantage: module 4.1 mm shorter (room for components), antenna can go **out of the compartment** (e.g. FPC under the base plate, with the cable through the lid gap). Disadvantages: only **4 MB** (a 1U-H8 is not listed at LCSC), manual assembly, connector can come off, one more part when giving it away. Cost: U.FL approx. 0.1–0.3 USD, FPC antenna with 50–100 mm cable approx. 1–3 USD (unverified). U.FL height approx. 1.2 mm fits. |
| Mini chip antenna on a cable in the compartment | **No**, sits in the same poor spot as the module antenna. |

---

## 3. Module choice

Board width 13.5 mm, AA sleeve Ø 14.5 mm (`board_outline.py`). **Modules 15.4 mm wide do not fit**
(C5-MINI-1, S3-MINI-1). The choice is the **ESP32-C6-MINI-1** (13.2 × 16.6 × 2.4 mm): target **-H8** (8 MB), fallback
**-N4** (4 MB), both pin- and footprint-compatible. Sourcing, footprint and pin assignment: [main-board-c6.md](main-board-c6.md)
(summary, 2.1–2.3). Rejected alternatives and reasons: [decision-history.md](decision-history.md).

---

## 3b. ESP32-C6 in detail

Sources: datasheets ESP32-C6 v1.5 and C6-MINI-1 v1.5 (PDF read), ESP-IDF docs.

### 3b.1 GPIOs, strapping, ADC

| Feature | C6-MINI-1 | Status |
|---|---|---|
| Exposed GPIOs | **22** (IO0–9, 12–23) | (verified) |
| Strapping | IO8, IO9 (boot mode), IO4/IO5 (SDIO edge only), IO15 (JTAG source, only effective with eFuse). **IO2 is not a strapping pin** | (verified) |
| ADC | ADC1 on **IO0–6** (7 channels), 12 bit | (verified) |
| ADC range 11 dB | **0–3300 mV**, ±40 mV | (verified) |
| Deep-sleep wake by pin | LP-GPIO **IO0–7** | (verified) |
| Native USB (Serial/JTAG) | **IO12/IO13 (pad 17/18)** | (verified) |
| JTAG pins | IO4–IO7 (MTMS/MTDI/MTCK/MTDO); not critical because JTAG runs over USB | (verified, datasheet 2.3.4) |

Consequences: The sensor INT on IO2 does not block boot. The ADC range up to 3.3 V allows the VBAT divider
680k/470k (6.6 V → 2.7 V, [main-board-c6.md](main-board-c6.md) 2.7). The authoritative pin assignment is in [main-board-c6.md](main-board-c6.md) 2.3,
free GPIOs and their use in [idea-optional-hardware.md](idea-optional-hardware.md).

### 3b.2 LP core and LP peripherals

| Statement | Status |
|---|---|
| LP RISC-V up to 20 MHz, 16 KB LP SRAM, keeps running in deep sleep | (verified) [C6-DS] |
| LP core reaches **LP-GPIO0–7, LP-I²C (master only), LP-UART**; woken by LP timer, LP IO, HP CPU, ETM, LP-UART | (verified) [idf-lpcore] |
| **ADC in deep sleep:** no LP ADC API for the C6 in the IDF docs; Espressif forum: LP ADC example only for P4 | (unverified) [lp-forum] |

Consequences: The **lever** does not need the LP core; waking via LP-GPIO is a normal ESP-IDF function. **Polling the LIS2DH12
in deep sleep** (I²C on IO6/IO7 = LP-I²C) would work with an LP program in C (ESP-IDF ULP LP-Core), built along in the
ESP-IDF build of the Rust firmware (unverified, not tried). **Monitoring the battery voltage in deep
sleep** is not practical; wake briefly by timer instead.

### 3b.3 Peripherals

| Block | C6 | Use for Louie |
|---|---|---|
| LEDC | 6 channels | Motor PWM (IN1/IN2), LED |
| MCPWM | 1 unit, 3 timers/3 operators | Dead time, synchronous sampling of motor current (option) |
| PCNT | 4 units × 2 channels | e.g. speed from current ripple (option) |
| RMT | 4 channels TX/RX | e.g. WS2812 chain (option) |
| ADC | 12 bit, 7 channels, threshold interrupt, 2 filters | VBAT, IPROPI, VBUS |
| Timer | 2 × 54 bit + systimer | – |
| Other | 2 × TWAI (CAN), SDIO slave, ETM, PARLIO, LP-UART, 802.15.4 | 802.15.4: [idea-zigbee-operation.md](idea-zigbee-operation.md) |

(verified, [C6-DS]) All blocks are reachable via ESP-IDF, from Rust via `esp-idf-hal` or `esp-idf-sys`.

### 3b.4 Flash and OTA

| Item | Finding | Status |
|---|---|---|
| C6-MINI-1 variants | **N4** (4 MB, 85 °C), **H4** (4 MB, 105 °C), **H8** (8 MB, 105 °C). **N8 does not exist**. MINI-1U (13.2 × 12.5 mm, U.FL) the same. Flash in the chip (C6FH4/C6FH8) | (verified) [c6-mini-ds] |
| Availability H8 | JLC C42403058: **620 pcs** (2026-11-06; still 0 on 2026-11-02), listed at 12.37 USD | (verified) |
| OTA with 4 MB | Standard IDF table `two_ota` has 2 × 1 MB app slots; a custom table with 2 × approx. 1.9 MB fits, then little room is left for data | (unverified, define table for the Rust firmware) |
| OTA with 8 MB | 2 × 3 MB app + approx. 2 MB data comfortably | (unverified, calculation) |

The size of the Rust firmware (Wi-Fi + BLE + HTTP/WebSocket) is only known after the first build; define the
partition table after that ([firmware-architecture.md](firmware-architecture.md)).

### 3b.5 Power consumption (module or chip datasheet, 3.3 V, 25 °C)

| State | C6 | Status |
|---|---|---|
| Wi-Fi TX 11b 1 Mbit/s, peak (module) | 382 mA | (verified) |
| Wi-Fi RX HT20 (module) | 78 mA | (verified) |
| BLE TX 19 dBm / RX (module) | 309 / 73 mA | (verified) |
| Modem sleep 160 MHz, CPU running (clocks off/on) | 27 / 38 mA | (verified) |
| Light sleep | 180 µA (35 µA with peripherals powered down) | (verified) |
| Deep sleep | 7 µA | (verified) |

In deep sleep the quiescent current of the 3.3 V regulator dominates (buck TPS62162 17 µA, board approx. 25 µA,
main-board-c6.md 2.7). TX peak 382 mA: regulator and buffer are enough (TPS62162 1 A). **Wi-Fi 6 / TWT** only works in **STA mode** (verified, IDF example `itwt`). In hotspot mode with
8 phones it brings nothing. Whether the C6 SoftAP speaks 802.11ax does not matter for phones anyway (unverified).

### 3b.6 Free heap (ESP-IDF examples)

| Example (IDF 5.5, unoptimized) | Free heap C6 | Status |
|---|---|---|
| Wi-Fi STA | 321 KB | (verified) [techpedia] |
| Wi-Fi + BLE ("provision", coexistence) | **259 KB** | (verified) [techpedia] |

SRAM 512 KB, no PSRAM. For Wi-Fi + BLE + 8 WebSockets that is plenty of reserve; still measure the
largest free block under load in the feasibility test ([idea-wireless-buttons.md](idea-wireless-buttons.md) 8).

### 3b.7 Price and availability (2026-11-02)

| Part | LCSC 1/10/100 pcs (USD) | Stock LCSC / JLC | JLC type |
|---|---|---|---|
| **C6-MINI-1-N4 (C5736265)** | **4.14 / 3.63 / 3.02** | 1,380 / 3,921 | Extended |
| C6-MINI-1-H4 (C6553337) | JLC 4.45 / 3.81 | – / 534 | Extended |
| C6-MINI-1U-H4 (C20627095) | JLC 4.20 / 3.76 | – / 3,938 | Extended |
| C6-MINI-1-H8 (C42403058) | JLC 12.37 | – / 0 | Extended |

(verified, LCSC and JLC parts API.) **Test board:** **ESP32-C6-DevKitC-1-N8** (8 MB, same GPIO numbers except IO14), see [test-hardware.md](test-hardware.md).
The XIAO ESP32-C6 is not suitable (IO3/IO14 are used by the antenna switch).

---

## 4. Conclusion

| Topic | Status |
|---|---|
| **(a) Antenna** | **No action needed** for Wi-Fi + BLE: one radio, one antenna is correct. No second antenna, no trace antenna. The remaining risk is the **mounting position** (metal at the antenna end). Secure it with an RSSI test with spring and plate. Plan B: C6-MINI-1U + FPC antenna outside the compartment. |
| **(b) Layout** | **Done:** L2 (no copper under the antenna on all four layers, edge strip −y only for OUT_A). **Open:** decide the antenna end by measurement (probably plus plate), mark it on the cap. **Keep:** OUT_A at the edge, BT1 pad, GND layer In1. No conductive filaments. |
| **(c) Controller** | **Decided: ESP32-C6-MINI-1**, target -H8 (8 MB, comfortable OTA), fallback -N4. Firmware in Rust on ESP-IDF ([firmware-architecture.md](firmware-architecture.md)). |
| **(d) Coexistence** | BLE scan only with paired buttons and only in READY/RUNNING, passive, 1M PHY. Measure hotspot + BLE scan (C1) in the feasibility test. |

---

## Sources

[idf-coex-c6]: https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-guides/coexist.html
[coex-pref]: https://sourcevu.sysprogs.com/espressif/esp-idf/symbols/esp_coex_preference_set
[hdg-c3]: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html
[c6-mini-ds]: https://documentation.espressif.com/esp32-c6-mini-1_mini-1u_datasheet_en.html
[techpedia]: https://docs.espressif.com/projects/esp-techpedia/en/latest/esp-friends/advanced-development/system/ram-usage.html
[C6-DS]: https://www.espressif.com/sites/default/files/documentation/esp32-c6_datasheet_en.pdf
[idf-lpcore]: https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-reference/system/ulp-lp-core.html
[lp-forum]: https://esp32.com/viewtopic.php?p=135957

- Espressif, RF Coexistence ESP32-C6: <https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-guides/coexist.html>
- `esp_coex_preference_set` deprecated: <https://sourcevu.sysprogs.com/espressif/esp-idf/symbols/esp_coex_preference_set>
- Espressif Hardware Design Guidelines, PCB layout (C3 version read): <https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html>
- Datasheets: [C6-MINI-1/1U](https://documentation.espressif.com/esp32-c6-mini-1_mini-1u_datasheet_en.html), SoC [ESP32-C6 v1.5](https://www.espressif.com/sites/default/files/documentation/esp32-c6_datasheet_en.pdf) (pins, strapping, ADC, current)
- ESP-Techpedia, RAM usage per chip: <https://docs.espressif.com/projects/esp-techpedia/en/latest/esp-friends/advanced-development/system/ram-usage.html>
- ESP-IDF LP-Core (C6): <https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-reference/system/ulp-lp-core.html>; LP ADC only P4 (forum): <https://esp32.com/viewtopic.php?p=135957>
- ESP-IDF Wi-Fi driver C6 (iTWT station only): <https://docs.espressif.com/projects/esp-idf/en/v5.5.2/esp32c6/api-guides/wifi.html>
- LCSC/JLC parts: [C6-MINI-1-N4 C5736265](https://lcsc.com/product-detail/C5736265.html), [C6-MINI-1-H4 C6553337](https://jlcpcb.com/partdetail/C6553337), [C6-MINI-1-H8 C42403058](https://jlcpcb.com/partdetail/C42403058), [C6-MINI-1U-H4 C20627095](https://jlcpcb.com/partdetail/C20627095)
- Seeed XIAO ESP32-C6: <https://www.seeedstudio.com/Seeed-Studio-XIAO-ESP32C6-p-5884.html>, <https://wiki.seeedstudio.com/xiao_esp32c6_getting_started/>
