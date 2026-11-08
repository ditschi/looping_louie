# louie-fw – ESP32-C6 firmware, step 0

Status: 2026-11-07 · **Written, not built yet** (toolchain setup on the dev machine still open, see "First build").

Step 0 of [firmware-architecture.md](../../docs/firmware-architecture.md) 11: board definition, bring-up in LED mode and
the test binaries for the pre-order checks in [test-hardware.md](../../docs/test-hardware.md) 4. Rust std on ESP-IDF
v5.5.5, target `riscv32imac-esp-espidf`, dated nightly (`rust-toolchain.toml`).

| Binary | Command | Purpose |
|---|---|---|
| `louie-fw` (bring-up) | `just fw-run` | LED mode (test-hardware.md 5.1): setpoint in mV → DRV8213 scheme on IO18/IO19 with ramp, lever gate, VSYS cut-off, stall from the ISEN pot, restart rule E15 |
| `lever_probe` | `just fw-run lever_probe` | 4.2: IO3 edges without internal pulls, deep-sleep wake ANY_HIGH, special case "lever closed at sleep" |
| `boot_probe` | `just fw-run boot_probe` | 4.3: reset reason, wake cause, levels of IO2/3/4/5/8/9/15 at start, wake cases 7–10 with automatic repeat |
| `pin_probe` | `just fw-run pin_probe` | 4.4 (F17): IO18/IO19 LOW first thing in `main`, deep sleep with/without `gpio_hold_en`, panic/WDT/software reset |
| `adc_probe` | `just fw-run adc_probe` | 4.5: VSYS (IO0) and VBUS (IO4) dividers at 10 Hz, mean/min/max per second; burst mode |

Every binary starts with a banner: firmware, board, reset reason, wake cause (with the ext1 pins), boot number in the
current deep-sleep chain, heap. Commands are single keys on the console (`h` or the menu at start).

## Layout

```
src/board/       board definitions (only place with pin numbers): devkitc_c6.rs (default), louie_v1.rs
src/hw.rs        GPIO, debounced button, ADC oneshot + calibration, motor PWM (LEDC 20 kHz, 10 bit)
src/sleep.rs     deep sleep with ext1 wake per pin level + timer
src/diag.rs      reset reason, wake cause, counters in RTC memory, heap
src/console.rs   non-blocking single keys from UART0
src/main.rs      bring-up (LED mode)
examples/        pre-order probes
```

The wrappers call the ESP-IDF C API through `esp-idf-svc::sys` directly. The HAL traits of the real firmware
(`louie-app::hal`) come in step 2/4 and build on what proves itself here.

Board selection: feature `board-devkitc-c6` (default) or `board-louie-v1`
(`just fw-build louie-v1`). The board variant still lacks its own sdkconfig (console on USB-Serial-JTAG).

## Serial ports (Waveshare ESP32-C6-DEV-KIT-N8)

The board has **one USB-C port with a CH334F hub**: two serial devices appear (schematic, verified):

| Device | USB ID | Linux | Use |
|---|---|---|---|
| CH343P USB-UART on UART0 (IO16/IO17), auto-reset via DTR/RTS | `1a86:55d3` | `/dev/ttyACM*`, `/dev/serial/by-id/usb-1a86_*` | **primary console, keys for the probes**; stays connected during deep sleep |
| ESP32-C6 USB-Serial-JTAG (IO12/IO13) | `303a:1001` | `/dev/ttyACM*`, `/dev/serial/by-id/usb-Espressif_*` | flashing, log output only (secondary console); disappears during deep sleep |

`just fw-ports` lists both. Flash and monitor on the **CH343 port** for all probes with deep sleep:
`just fw-run boot_probe /dev/serial/by-id/usb-1a86_…`. The user must be in the `dialout` group.

- **RESET button resets the USB hub too** (D3 to CH334 RESET#, schematic): both ports disappear briefly, the monitor
  loses the connection and the ROM log of that boot. For reset series (4.3 case 1) use a terminal that reconnects
  (e.g. `tio`), or the software restart (`r`) where the case allows it. Effect on the monitor: unverified.
- The hub and the CH343 are powered only from USB VBUS (Q1/Q2 switch); fed via the 5V pin they are off.

## First build

Prerequisites (Ubuntu): `rustup` with the nightly from `rust-toolchain.toml` and `rust-src`, `ldproxy`, `espflash`,
`python3-venv`, `git`; `esp-idf-sys` downloads ESP-IDF v5.5.5 and its tools into `~/.espressif` on the first build
(10–20 min). `setup.sh` (section "Firmware") installs the Rust part.

**Path with spaces:** the repo path contains spaces ("uCPU und Elektronik", "Looping Louie"). ESP-IDF does not support
spaces in its paths (ESP-IDF getting-started guide). Therefore ESP-IDF goes to `~/.espressif` (`.cargo/config.toml`) and
`just fw-*` puts the Cargo target directory (where the ESP-IDF CMake project is generated) at
`~/.cache/louie-fw/target`. Whether that is enough is **unverified**; if the first build still fails on paths,
work from a clone without spaces (e.g. `~/src/looping-louie`).

## What was checked

- Pin header P1/P2 of the Waveshare board against its schematic: same order as the Espressif DevKitC-1 (J1/J3).
- ESP-IDF v5.5 API used here against the headers: `esp_sleep_enable_ext1_wakeup_with_level_mask` (C6 has per-pin
  ext1 level), `gpio_hold_en` in deep sleep (C6: `SOC_GPIO_SUPPORT_HOLD_SINGLE_IO_IN_DSLP`), `adc_oneshot_io_to_channel`,
  curve-fitting calibration per channel, `LEDC_AUTO_CLK`.
- **Not checked:** compilation (bindgen names of the ESP-IDF constants, `esp-idf-svc` 0.53 API), behaviour on the board.
