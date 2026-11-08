# Firmware language: Rust (std on ESP-IDF)

Status: 2026-11-06 · **Decided** (project owner, 2026-11-06). Firmware structure:
[firmware-architecture.md](firmware-architecture.md). Test setup and feasibility test: [test-hardware.md](test-hardware.md).
Earlier evaluation (MicroPython recommendation, scoring matrix): [decision-history.md](decision-history.md).

## Decision

The firmware for the ESP32-C6 is written in **Rust**, variant **std on ESP-IDF**, with the crates
`esp-idf-svc`, `esp-idf-hal` and `esp-idf-sys`. The game logic is a separate, hardware-free crate. It runs on
the ESP, on the PC (tests, simulator) and as WebAssembly in the browser (mode preview).

## Rationale

- **As much logic as possible on the controller.** Permissions, limits, joker accounts and the mode interpreter run on
  the ESP. Rust is fast enough for this, including preview and bots (MicroPython would be about 10–50× slower,
  unverified).
- **One implementation of the interpreter** for device, simulator and browser. Golden tests ensure that all three
  compute the same result.
- **OTA with two app slots** is possible with ESP-IDF even on 4 MB, as long as the firmware stays below about 1.8 MiB
  (measurement in step 0, firmware-architecture.md 6.1). MicroPython at 1.81 MiB did not fit into the
  1.5 MiB slots of its OTA table (verified, [analysis-wireless-controllers.md](analysis-wireless-controllers.md) 3b).
- **Full ESP-IDF features**: Wi-Fi AP+STA, NimBLE, mDNS, OTA, sleep, watchdog. Anything the Rust crates do not
  cover is reachable directly as C API through `esp-idf-sys`, including the Zigbee SDK.
- **Memory safety** without garbage collector pauses.
- The code is mostly written by Claude; the learning-curve argument against Rust does not apply.

## Rejected alternatives

| Alternative | Why not |
|---|---|
| MicroPython + Microdot | Slow for preview/bots, no OTA in 4 MB, several C6-specific bugs (deep-sleep wake-up, continuous BLE scan), no Zigbee. |
| C++ (Arduino-ESP32 or ESP-IDF) | Mature, but without memory safety and with more scaffolding for PC simulator and WASM. **Fallback** only for parts that do not work in Rust: include via FFI. |
| Rust no_std (esp-hal + esp-radio + Embassy) | Radio part (esp-radio) still beta, Wi-Fi/BLE coexistence marked *unstable*. Re-evaluate when esp-radio 1.0 and coex are stable; only the firmware crate would be affected. |
| ESPHome | Custom game modes, roles and custom UI do not fit the concept. |
| Hybrids (Rust core in MicroPython, preview only on the server) | Two toolchains or compute time on the ESP; unnecessary with Rust. |

## External buttons

- **BLE BTHome passive** (e.g. Shelly BLU Button1, RC Button 4): The ESP only listens to advertising, no
  connections. Scanning only while a mode with jokers runs and buttons are paired.
- **433 MHz dropped** (no free GPIO, receiver needed in the base, no advantage over BLE).
  ESP-NOW, Zigbee, nRF24 and infrared were also rejected.
- Coexistence of BLE scan + own hotspot (SoftAP) with clients: according to Espressif "supported, but unstable" (C1);
  stable in the home Wi-Fi (verified). This is a property of the radio, not of the language; it is measured in the
  test setup.
- Details and pairing: [idea-wireless-buttons.md](idea-wireless-buttons.md), [device-pairing.md](device-pairing.md).

## Sources

- esp-idf-svc (0.53.0, 2026-09-15): https://github.com/esp-rs/esp-idf-svc
- esp-idf-hal (community status): https://github.com/esp-rs/esp-idf-hal ; Rust book: https://docs.espressif.com/projects/rust/book/
- esp-hal 1.0: https://developer.espressif.com/blog/2025/10/esp-hal-1/ ; esp-radio (coex unstable):
  https://docs.espressif.com/projects/rust/esp-radio/1.0.0-beta.2/esp32c3/esp_radio/index.html
- Espressif RF coexistence C6: https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-guides/coexist.html
- MicroPython ESP32 port (`partitions-4MiB-ota.csv`): https://github.com/micropython/micropython/tree/master/ports/esp32
- Shelly BLU Button (BTHome): https://shelly-api-docs.shelly.cloud/docs-ble/Devices/BLU/button
- More sources on the architecture: [firmware-architecture.md](firmware-architecture.md)
