# Idea: wireless buttons as players (joker by button)

Status: 2026-11-06 · **Decided: BTHome BLE buttons (received passively) are a planned feature for V1.**
Other radio paths are rejected (briefly in 4.3, reasons in [decision-history.md](decision-history.md)). Complements
[software-concept.md](software-concept.md), [web-ui-concept.md](web-ui-concept.md) (4.2),
[mode-builder.md](mode-builder.md) (2.5, 3), [device-pairing.md](device-pairing.md) (UI and data model)
and [idea-optional-hardware.md](idea-optional-hardware.md).

Question: *Can we pair e.g. 4 physical buttons wirelessly that trigger jokers (⏩ boost, ⏪ kickback)?*

Markers: **(verified)** = backed by a source · **(unverified)** = from memory, secondary source only, or
own estimate; measure in the feasibility test. Prices are rough guide values (DE/EU, at the time of research).

---

## Short answer

- **The ESP32-C6 supports Bluetooth Low Energy 5** (no Classic Bluetooth), as scanner and as central.
  Wi-Fi and BLE share the existing antenna. **No hardware change.** **(verified)** [datasheet][c6-mini-ds]
- **Chosen: BTHome buttons that only transmit** (Shelly BLU Button1 / Tough 1 / RC Button 4). The ESP listens
  passively, no connections. Events single/double/triple/long, up to 4 keys per device.
- **Main risk:** Espressif rates **BLE scan + own hotspot with connected phones** as "supported, but
  unstable" (C1); on home Wi-Fi as stable. **(verified)** [RF Coexistence C6][idf-coex-c6] RAM is no longer a
  bottleneck on the C6 (259 KB free heap in the IDF example Wi-Fi + BLE).
- **Wired buttons** on the player inputs J6 are the reliable reference and the test tool.
- **Stages:** Stage 0 = feasibility test with 1 Shelly button on the ESP32-C6-DevKitC-1 (test-hardware.md) in the hotspot with 6–8 phones
  ([test-hardware.md](test-hardware.md)). Stage 1 = BTHome buttons in **V1**.
  Antenna, coexistence and scan parameters: [analysis-wireless-controllers.md](analysis-wireless-controllers.md).

---

## 1. What the ESP32-C6 can do over radio

| Item | Value | Source |
|---|---|---|
| Bluetooth | **BLE 5.3**; **no Classic** (no BR/EDR, no classic HID) | **(verified)** [datasheet][c6-mini-ds] |
| BLE roles | Broadcaster, observer (scanner), peripheral, central | **(verified)** [datasheet][c6-mini-ds] |
| BLE PHY | 1M, 2M, Coded PHY (long range) | **(verified)** [datasheet][c6-mini-ds] |
| Wi-Fi | 802.11 b/g/n/ax 2.4 GHz | **(verified)** [datasheet][c6-mini-ds] |
| 802.15.4 (Zigbee/Thread) | yes, same radio | **(verified)** [datasheet][c6-mini-ds] |
| Antenna | **one** antenna, one radio for Wi-Fi, BLE and 802.15.4 | **(verified)** [datasheet][c6-mini-ds] |

**Long range (Coded PHY)** is of no use to us: off-the-shelf buttons transmit on 1M PHY, the table is small, and
Coded PHY packets are long and disturb Wi-Fi. **(verified)** [RF Coexistence C6][idf-coex-c6]

---

## 2. One radio for Wi-Fi and BLE (coexistence)

The C6 switches the radio between Wi-Fi and BLE. With "Wi-Fi connected" the period starts at the beacon
(> 100 ms); Wi-Fi and BLE each get e.g. **50 %**. **(verified)** [RF Coexistence C6][idf-coex-c6]

| BLE | STA connected | SoftAP beacon | **SoftAP connected** |
|---|---|---|---|
| Scan | Y | Y | **C1** |
| Advertising | Y | Y | **C1** |
| Connected | Y | Y | **C1** |

Y = stable · **C1 = supported, performance unstable**. **(verified)** [RF Coexistence C6][idf-coex-c6]

- **Home Wi-Fi (STA)**: stable. **Own hotspot with up to 8 phones = C1** → biggest risk, only measuring helps.
- Espressif advises keeping the default scan parameters under coexistence. **(verified)** [RF Coexistence C6][idf-coex-c6]
  For buttons, however, they are too sparse. Conflict of goals → in the test, try windows of 30…100 ms at 100 ms interval
  (parameters: [analysis-wireless-controllers.md](analysis-wireless-controllers.md) 1.3).
- WebSocket latency: at 50 % BLE share, Wi-Fi packets shift by some 10 ms **(unverified)**. For
  10 status updates/s not critical, as long as nothing is lost.
- Rule: BLE scan **only in READY/RUNNING and only when buttons are paired**. Without buttons, BLE stays off.

---

## 3. BLE in the firmware (Rust on ESP-IDF)

| Item | Status |
|---|---|
| Stack | **NimBLE** from ESP-IDF; in Rust first via the NimBLE wrapper of `esp-idf-svc` 0.53, fallback crate `esp32-nimble` ([firmware-architecture.md](firmware-architecture.md) E8) |
| Scan | passive, set interval/window explicitly, duplicate filter off (details: analysis-wireless-controllers.md 1.3) |
| Parser | BTHome decoding (UUID, objects, packet ID, button events) as a pure function in the hardware-free core crate → testable on the PC |
| AES-CCM | for encrypted BTHome buttons: mbedTLS in ESP-IDF has CCM; alternatively RustCrypto crates `aes` + `ccm` **(unverified: not tried yet)** |
| RAM | IDF example Wi-Fi + BLE: **259 KB** free heap on the C6 **(verified)** [techpedia]. In the test, measure the largest free block under load. |

---

## 4. The options

### 4.1 BLE BTHome buttons (transmit only) – chosen

**Protocol** **(verified)** [BTHome format][bthome-format]: service UUID `0xFCD2`; first byte: bit 0 =
encrypted, bit 2 = "trigger-based"; object `0x00` = **packet ID** (evaluate only on change → duplicates gone);
object `0x3A` = button: `0x01` press, `0x02` double, `0x03` triple, `0x04` long, `0x80` held.

**Shelly BLU Button1** **(verified)** [user manual][shelly-manual], [Shelly BLE API][shelly-api]:
transmits BTHome for **1 second** after a press; **LED ring and buzzer** show the number of presses; AES-CCM
possible; CR2032 up to 2 years; range up to 10 m indoors; 36 × 36 × 6 mm. **Multi-click window adjustable**:
800 / 550 / 300 / 150 / 90 / 55 ms. Configuration: hold 10 s → connectable via GATT for 1 min.

**Shelly BLU RC Button 4 / Wall Switch 4**: **every packet contains all 4 keys** as four `0x3A` objects at
fixed positions; same events and click setting. **(verified)** [RC Button 4 API][shelly-rc4]

**Passive is enough:** The BTHome data is in the advertising. In Home Assistant, passive scanning resolved delays
with Shelly buttons **(verified, forum)** [simon42][simon42] → observe in the test as well.

**Latency** button → motor:

| Step | Time |
|---|---|
| Button waits for a possible 2nd click | 55 / 300 / 800 ms (setting) |
| Packet sent and received (advertising interval, scan window, 50 % airtime) | approx. 20–100 ms **(unverified)** |
| Callback, parser, game logic, motor task | approx. 1–10 ms **(unverified)** |
| **Total** | **approx. 80–170 ms** (55 ms) · **approx. 330–420 ms** (300 ms) · approx. 0.9 s (800 ms) |

For comparison: the hold button on the phone triggers after `hold_ms` **400 ms** (mode builder 2.5). A button with a
300 ms window is therefore **as fast as the phone**.

**Double-click problem**: With single = ⏩, double = ⏪, **every** single press waits for the window, and below
300 ms children cannot double-click reliably. Solutions: (1) **one key per joker** (RC Button 4,
window 55 ms) – recommended; (2) one button, only one joker; (3) single = ⏩, **long = ⏪** (whether "long" comes when the
hold time is reached or on release: **(unverified)**); (4) single/double with 300 ms.

**Reliability**: 1 s of repeats + packet ID → missed presses unlikely; **measure** in hotspot mode
(C1). Two quick single jokers can arrive as a double click.

**Other BLE advertisers**: Xiaomi/Mijia buttons transmit encrypted (MiBeacon), key only via the
Xiaomi cloud **(unverified)** → not recommended.

### 4.2 Wired (reference and test)

The main board has player inputs **S1–S4 on J6** (IO5, IO20, IO21, IO8; pin assignment
[main-board-c6.md](main-board-c6.md) 2.3). Arcade buttons directly to GND, **no port expander**. Latency
< 10 ms, 100 % reliable, no batteries, cost approx. €5–15 for 4 buttons and cable. Disadvantage: cables across the
table. Good as a **test tool** for the game logic ("button player") and as an emergency solution if BLE does not hold up in the hotspot.
Details: [idea-optional-hardware.md](idea-optional-hardware.md).

### 4.3 Rejected options (summary)

| Option | Why not |
|---|---|
| BLE connection buttons (iTag, BLE HID, Flic 2) | Connections drop in hotspot mode (C1), max. approx. 3 iTags; Flic 2 protocol is complex; many cheap shutter buttons are Classic |
| ESP-NOW (DIY, WiZmote) | DIY button with LiPo needed, off-the-shelf devices hardly available; no added value over BTHome |
| 433/868 MHz (EV1527) | Receiver + 17 cm antenna in the base, extra pins, fixed code (replay trivial) |
| Zigbee | Coordinator + hotspot or + BLE scan not supported (X). Only as a separate operating mode: [idea-zigbee-operation.md](idea-zigbee-operation.md) |
| nRF24, infrared | Extra radio/pins or line of sight needed; identical IR remotes cannot be told apart |

---

## 5. Cost and key data BTHome (4 players)

| | BLE BTHome | Wired (J6) |
|---|---|---|
| Extra HW on the Louie | **none** | buttons, cable |
| Cost 4 buttons | €60–100 (e.g. 1 × RC Button 4 much cheaper) **(unverified)** | €5–15 |
| Latency | 80–420 ms (click window) | **< 10 ms** |
| Range | 10 m indoors | cable |
| Reliability | good, in the hotspot **C1** (measure) | perfect |
| Foreign devices/security | MAC filter, optional AES + counter | – |
| Button battery | CR2032, up to 2 yr. | – |

---

## 6. Pairing and devices with several keys (technical facts)

UI, permissions and data model: [device-pairing.md](device-pairing.md). Only the technology here.

### 6.1 How the firmware detects device, key and event

| Option | Device ID | Key | Event | Multi-click detection |
|---|---|---|---|---|
| BTHome | **MAC** (+ optional 16-byte key) | position of the `0x3A` object (1…n) | in the packet: 1×, 2×, 3×, long, held | **in the button** (click window) |
| Wired | input S1–S4 | input | edges | in the Louie |

The key count of a BTHome device follows from the **number of `0x3A` objects** in the packet (RC Button 4 = 4,
Button1 = 1). **(verified)** [RC Button 4 API][shelly-rc4]

### 6.2 Pairing flow (technical)

1. Louie enters **learning mode** (e.g. 30 s): BLE scan open, all events of **unknown** devices are
   collected (MAC, key, event, RSSI, time).
2. Only what was **pressed during learning mode** is reported (not: whatever happens to be on the air), plus an
   RSSI threshold (e.g. > −70 dBm **unverified**) so that the neighbor's button does not win.
3. For multi-key devices: "Press each key once" → Louie collects the key numbers.
4. Save the device (ID, type, key count), then set the **assignment** (6.3).
5. For BTHome with key: enter the key or set it via GATT **(unverified)**; from then on check the counter.

### 6.3 Splitting one device across several players

Technically this works because every key is detected separately. The game logic only sees
"input (device, key, event) → player, joker slot".

- **RC Button 4 = 4 players with 1 joker each** or **2 players with ⏪/⏩ each**. BTHome reports the state of **all four
  keys in every packet** → simultaneous presses by two players both arrive. **(verified)** [RC Button 4 API][shelly-rc4]
- Only practical if the players sit **next to each other** (device lies between them). A 4-key
  remote for 4 seats around the table does not work physically.

### 6.4 Technical fields per device

In addition to the data model in [device-pairing.md](device-pairing.md) 7, the firmware needs per BTHome device:

| Field | Purpose | Storage |
|---|---|---|
| `addr` | MAC (filter in the scan callback) | persistent |
| `keys` | key count (number of `0x3A` objects) | persistent |
| `key` | 16-byte AES key or empty | persistent |
| `click_ms` | configured click window (for the latency display) | persistent |
| `pid` | last packet ID (duplicates) | RAM only |
| `counter` | last BTHome counter with encryption (replay protection) | write rarely (spare the flash) |
| `bat`, `rssi`, `seen` | battery, signal, last seen | RAM only |

An input may belong to only **one** player (checked on save). Storage location and format (NVS or file):
[firmware-architecture.md](firmware-architecture.md).

---

## 7. Integration into the concept: buttons as players

The principle stays: **a player is a device** (web-ui-konzept 4.2) – phone **or button (group)**.

- They count towards the **number of players** (default 4, up to 8). Quotas, cooldown, shared lock as with the phone.
  The game logic does not distinguish between devices.
- **Feedback without a display**: Shelly blinks/beeps itself on every press. Whether the joker was **accepted**
  is shown by the motor (that is the fun part) and the **ticker** on all phones ("🔴 Rocket: ⏩!" / "no ⏩ left"; PoC: „🔴 Rakete: ⏩!“ / „kein ⏩ mehr“).
  Optional status LED on the Louie.
- **Dropping out**: the game master marks the button player, or a dedicated key/long press (see data model).
- **Advantages**: children without a phone can play, no phone battery, no Wi-Fi joining, no screen distraction.
  **Party rotation**: the button stays at the seat; "🔄 Switch player" (PoC: „🔄 Spielerwechsel“) works the same way.
- **Limits**: max. 2 jokers per player (fits the rule in mode builder 2.5); no ghost layout visible.
- **Protocol**: `players[]` gets `"dev":"phone"|"button"`, `"bat":80`; event
  `{"t":"event","kind":"boost","seat":2,"src":"button"}`; REST `GET/POST/DELETE /api/devices` and
  `POST /api/devices/learn` (start learning mode/fetch result).

---

## 8. Stages and abort criteria

| Stage | Content | Result |
|---|---|---|
| **0 – Feasibility** | ESP32-C6-DevKitC-1 with Rust test firmware, **1 Shelly BLU RC Button 4** (or Button1). **Hotspot with 6–8 phones** + WebSockets + passive BLE scan. Measure: largest free heap block, missed presses (count 100), latency button → GPIO, WebSocket ping, phone disconnects. Same test in STA mode. Setup: [test-hardware.md](test-hardware.md) | Yes/no BLE in the hotspot |
| 0b | Wired buttons on J6 as game logic test | Button player in code |
| **1 – V1** | BTHome scanner, learning mode, device list, assignment | Buttons as players |
| 1b | Encryption + counter, battery display | Party-ready |

**Abort criteria for BLE (stage 0):**

- Largest free heap block < 20 KB, or memory error/crash in a 30 min endurance run (Wi-Fi + 8 WebSockets + scan).
- More than **1 in 100** presses missed (hotspot, 8 phones).
- Latency button → motor **> 500 ms** median or > 800 ms (95 %) with a 300 ms window; > 250 ms with 55 ms.
- Phones lose the WebSocket connection or updates stall > 1 s.

If only the hotspot case fails: BLE buttons **only on home Wi-Fi**, wired buttons on J6 in the hotspot.

---

## 9. Impact

**Hardware**: none. Keep the antenna end clear ([analysis-wireless-controllers.md](analysis-wireless-controllers.md) 2).

**Firmware** (structure: [firmware-architecture.md](firmware-architecture.md)):

- BLE scanner as its own task, only active when devices are paired **and** phase READY/RUNNING (or learning mode).
- BTHome parser, duplicate filter and mapping (device, key, event) → player + joker slot in the
  hardware-free core crate; produces the same request as a phone via WebSocket.
- Motor task with watchdog unchanged; the game logic only sees "player n wants joker k".
- Simulator/browser preview: key presses by keyboard or click, without radio.

---

## 10. Open items

- Advertising interval of the Shelly buttons in the 1 s transmit phase **(unverified)** – capture in the test.
- "Long" when the hold time is reached or on release? **(unverified)**
- How does C1 (BLE + SoftAP connected) show in practice? Only measuring helps.
- Set the Shelly key via GATT from the Louie (pairing without the Shelly app)? **(unverified)**
- Does Shelly BLU transmit with a **fixed MAC** (no rotating private address)? Prerequisite for pairing by MAC. **(unverified)**
- Does Shelly BLU use **legacy advertising** (BLE 4 format, 1M PHY), no extended advertising? Does the NimBLE scan need
  extended advertising? **(unverified)**
- Controller duplicate filter: does it drop follow-up packets from the same MAC despite changed data? **(unverified)**
- Combined game (2 Louies): a device paired with only one Louie.

---

## Sources

- `c6-mini-ds` – Espressif, ESP32-C6-MINI-1/1U datasheet: https://documentation.espressif.com/esp32-c6-mini-1_mini-1u_datasheet_en.html
- `idf-coex-c6` – ESP-IDF, RF Coexistence (ESP32-C6): https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-guides/coexist.html
- `techpedia` – ESP-Techpedia, RAM usage per chip: https://docs.espressif.com/projects/esp-techpedia/en/latest/esp-friends/advanced-development/system/ram-usage.html
- `bthome-format` – BTHome v2 format: https://bthome.io/format/
- `bthome-enc` – BTHome encryption: https://bthome.io/encryption/
- `shelly-api` – Shelly BLE API, BLU Button: https://shelly-api-docs.shelly.cloud/docs-ble/Devices/BLU/button
- `shelly-rc4` – Shelly BLE API, BLU RC Button 4: https://shelly-api-docs.shelly.cloud/docs-ble/Devices/BLU/wall_us
- `shelly-manual` – ShellyBLU Button1 manual (PDF): https://www.netxl.com/shelly/docs/shelly-blu-button-user-manual.pdf
- `shelly-tough` – Shelly BLU Button Tough 1 (shop DE): https://www.shelly.com/de/products/shelly-blu-button-tough-1-mocha
- `jacob-button1` – Jacob, Shelly BLU Button1: https://www.jacob.de/produkte/shelly-blu-button1-shelly-bb-r-artnr-8360883.html
- `netxl-rc4` – NetXL, Shelly BLU RC Button 4: https://www.netxl.com/controllers-and-hubs/shelly-blu-rc-button-4.md
- `simon42` – simon42 forum, BLU Button 1 active/passive scanning: https://community.simon42.com/t/erstes-shelly-geraet-und-gleich-enttaeuscht-blu-button-1/79566
- Sources for the rejected options (iTag, Flic 2, ESP-NOW, EV1527, RXB6, Zigbee, IR): Git, working state before the cleanup on 2026-11-06.

[c6-mini-ds]: https://documentation.espressif.com/esp32-c6-mini-1_mini-1u_datasheet_en.html
[idf-coex-c6]: https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-guides/coexist.html
[techpedia]: https://docs.espressif.com/projects/esp-techpedia/en/latest/esp-friends/advanced-development/system/ram-usage.html
[bthome-format]: https://bthome.io/format/
[bthome-enc]: https://bthome.io/encryption/
[shelly-api]: https://shelly-api-docs.shelly.cloud/docs-ble/Devices/BLU/button
[shelly-rc4]: https://shelly-api-docs.shelly.cloud/docs-ble/Devices/BLU/wall_us
[shelly-manual]: https://www.netxl.com/shelly/docs/shelly-blu-button-user-manual.pdf
[shelly-tough]: https://www.shelly.com/de/products/shelly-blu-button-tough-1-mocha
[jacob-button1]: https://www.jacob.de/produkte/shelly-blu-button1-shelly-bb-r-artnr-8360883.html
[netxl-rc4]: https://www.netxl.com/controllers-and-hubs/shelly-blu-rc-button-4.md
[simon42]: https://community.simon42.com/t/erstes-shelly-geraet-und-gleich-enttaeuscht-blu-button-1/79566
