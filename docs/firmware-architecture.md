# Firmware architecture (Rust, std on ESP-IDF)

Status: 2026-11-09 · Draft, revised after critical review; basis for starting the implementation. Mode catalog and
UI package added 2026-11-09 (6.4).
Language decision: [firmware-language.md](firmware-language.md). Functional basis:
[software-concept.md](software-concept.md) (network, roles, game, protocol section 7),
[web-ui-concept.md](web-ui-concept.md), [mode-builder.md](mode-builder.md) (schema 2),
[device-pairing.md](device-pairing.md), [idea-wireless-buttons.md](idea-wireless-buttons.md).
Hardware: [main-board-c6.md](main-board-c6.md) 2.3–2.5 (pin assignment, wake-up), test setup: [test-hardware.md](test-hardware.md).
Earlier versions of individual decisions: [decision-history.md](decision-history.md) 8.

Markers: **(verified)** = source read (below), **(unverified)** = estimate or rule of thumb, measure in the test
setup.

## Summary

- **One firmware** for the breadboard (ESP32-C6-DevKitC-1-N8, same GPIO numbers as the board except IO14) and the real
  board. The differences live in a **board definition**, selected by Cargo feature (`board-louie-v1`,
  `board-devkitc-c6`; optionally `board-devkitm-c6`). The firmware detects or switches optional parts (sensor, LED chain, buttons) at runtime.
- **Cargo workspace with five crates:** `louie-core` (no_std + alloc, game logic), `louie-proto` (messages),
  `louie-app` (app layer free of hardware and network: actor loop, sessions, permissions, hub, REST router),
  `louie-fw` (ESP-IDF) and `louie-sim` (PC, axum). Plus `louie-wasm` for the mode preview in the browser.
  **Game logic and app layer including the actor loop run unchanged on ESP, PC and (core) in the browser;**
  httpd and axum are only adapters.
- **Concurrency with FreeRTOS threads** (`std::thread`, each with a fixed stack size), no async executor on
  the ESP. The app is a single "actor" in the game thread (50 ms tick) and handles **only
  state changes**; expensive stateless work (PBKDF2, JSON, validation, file I/O) runs beforehand in the httpd task
  or in a worker.
- **Motor safety at the very bottom and independent:** separate thread with the highest app priority, ramps and limits,
  500 ms without setpoint → 0, emergency stop as an atomic bypassing the channel, stall via IPROPI → off, task watchdog with
  panic, second dead-man timer via `esp_timer`. **No start after an unexpected reset** until the lever goes open → closed. The
  lever disconnects the motor in hardware anyway.
- **Network:** STA with AP fallback, captive DNS and DHCP option 114, mDNS, `EspHttpServer` with **one** WebSocket
  `/ws` and REST. One JSON state for all clients, at most 10/s during the game, **own non-blocking
  send path with backpressure** (not `EspHttpWsDetachedSender::send()`).
- **Modes are data, the core owns the catalog:** The core provides hardware abstraction, safety layer and the mode
  interpreter (the vocabulary of building blocks). Game flows are JSON programs. They come from three sources:
  1–2 fallback modes in the firmware, the modes shipped with the **UI package**, and own modes in LittleFS. The core
  reads all of them into **one catalog**, validates them, offers them without a phone (lever gesture, buttons) and
  plays exactly one current program. Selection is **by reference**, not by uploading JSON (6.4).
- **UI package:** web UI, languages and the modes that belong to this UI, with a manifest (version, protocol and
  schema range). V1 embeds it in the firmware; later it moves to the `www` partition and can be updated
  separately, so the same core can run different UIs or games (6.4).
- **Storage:** H8 (8 MB) with OTA is the target. On N4 (4 MB) it gets tight with embedded web files
  (realistically 1.6–2.0 MB): there OTA only if the measurement in step 0 fits, otherwise a separate `www` partition or
  update via USB. User data in LittleFS, Wi-Fi credentials and hotspot password in NVS.
- **Tests:** golden tests for modes (JSON → curve) on the PC, same core in the simulator, in the browser and (via
  checksum) on the device, hardware-in-the-loop on the test setup with fixed limits for heap and latency.

## 1. Goals and guard rails

| Goal | Consequence for the architecture |
|---|---|
| One firmware for test setup and board | Board definition per feature, HAL as traits, no pin numbers outside `board/` |
| As much logic as possible on the controller | Permissions, limits, joker accounts, mode interpreter and validation run on the ESP. The UI only displays and sends requests |
| Server is the single source of truth | one state in the game thread, all clients get the same JSON |
| Motor safety independent of network and logic | separate motor thread with watchdog, limits in the lowest layer; lever in series with the motor |
| A slow client slows nobody down | Sending to WebSockets is never blocking, backpressure per client, silent clients are disconnected (5.4) |
| Playable without a phone | The lever starts the lever mode; network is optional |
| The core knows all modes | One catalog in the core from firmware, UI package and LittleFS; selection by reference; offline selection without a UI (6.4) |
| Development before the board | Simulator on the PC with the same app layer and actor loop, test setup on the breadboard |
| One implementation of the mode interpreter | `louie-core` runs on ESP, PC and as WebAssembly in the browser |
| Offline | all files in flash, no CDN |

Constraints ESP32-C6-MINI-1: one RISC-V core 160 MHz, **512 KB SRAM**, 4 MB (N4) or 8 MB (H8) flash
(verified, datasheet). Free heap in the ESP-IDF example with Wi-Fi + BLE: **259 KB** (verified, ESP-Techpedia, see
[analysis-wireless-controllers.md](analysis-wireless-controllers.md)). Nothing is time-critical: LEDC generates PWM in hardware,
ramps and measurements run on a 10–50 ms grid. Scarce are **RAM** (6.3) and, on N4, **flash** (6.1).

## 2. Repo and workspace layout

```
firmware/
  Cargo.toml              workspace (host crates, stable Rust)
  Cargo.lock              checked in
  crates/
    louie-core/           no_std + alloc: game, modes (incl. serde types of the mode schema), jokers, permissions, limits, profiles
    louie-proto/          serde types for REST/WS, configuration, devices.json; TS export
    louie-app/            std, no HW or network: actor loop (thread + channels), sessions, hub, router, HAL traits, storage trait, ClientSink
    louie-sim/            PC: simulated HAL, axum/tokio as adapter, serves web/, load client
    louie-wasm/           wasm-bindgen wrapper around louie-core (preview, validation)
  louie-fw/               separate workspace: ESP-IDF, nightly, target riscv32imac-esp-espidf
    Cargo.lock            checked in
    .cargo/config.toml    target, linker = ldproxy, build-std, ESP_IDF_VERSION
    rust-toolchain.toml   dated nightly (e.g. nightly-2026-10-15) + rust-src
    sdkconfig.defaults    shared; sdkconfig.defaults.<board> per board
    partitions-4mb.csv, partitions-4mb-www.csv, partitions-8mb.csv
    src/board/            louie_v1.rs, devkitm_c6.rs, devkitc_c6.rs
    src/hal/              implementations of the HAL traits
    src/net/              wifi.rs, captive_dns.rs, mdns.rs, http.rs, ws_send.rs (adapters to louie-app)
    src/main.rs
  tests/modes/            golden tests (*.mode.json + *.curve.json)
web/                      web UI sources incl. modes/ of the default UI (output → UI package, 6.4)
```

**Why `louie-fw` is a separate workspace:** The ESP target needs nightly, `build-std` and `ldproxy`
(verified, rustc platform page, tier 3). The host crates should build with stable Rust, `cargo test` and
`wasm32-unknown-unknown`. A shared workspace would mix `.cargo/config.toml` and toolchain.
`louie-fw` includes the host crates via `path =`. The nightly is **dated** and both `Cargo.lock` files are
checked in, so that a build in one year still produces the same result.

### 2.1 What goes where

| Crate | Content | Why here |
|---|---|---|
| **louie-core** | Round state machine (ready, countdown, running, pause, end, sleep), mode interpreter schema 2 (flight plan, spice, jokers, end, meanness, upgrade schema 1 → 2) including serde types of the mode schema, validation with hints (mode-builder.md 2.8), joker accounts, cooldowns, shared lock, reverse limits, model profiles (minimum speed, centrifugal limit, cap), ramp formulas, roles → permissions, deterministic randomness (seed) | Pure functions over time and inputs. `no_std` + `alloc` is **discipline** here: the compiler prevents clock, I/O, threads and `HashMap` with a random hasher in the core. Time comes as a parameter (`now_ms: u32`) |
| **louie-proto** | `ClientMsg`/`ServerMsg` (WS), REST bodies, `Config`, `DevicesFile`, error codes; schema version; optional TS types via `ts-rs` | Shared contract for firmware, simulator and web UI. If the protocol changes, the build breaks instead of the phone |
| **louie-app** | **Actor loop** `App::run(rx, sinks, hal, store)` as a `std::thread` with channels (owns the whole state), sessions/tokens, admin login with lock, hub (one JSON state, rate 10/s, events, backpressure per client), REST router, inputs (phone, wireless button, J6) → same joker request, button pairing, persistence via trait `Store`, HAL traits, trait `ClientSink` | Shares the entire server logic **including threads, channels and backpressure** between firmware and simulator. Firmware and simulator only provide transport (httpd or axum) and HAL |
| **louie-fw** | Board definitions, HAL implementation (LEDC, ADC, GPIO, I²C, RMT), Wi-Fi/AP, captive DNS, mDNS, `EspHttpServer` + WS adapter with own send path, NimBLE scan, NVS, LittleFS, OTA, sleep, watchdog, logging | Everything that needs ESP-IDF |
| **louie-sim** | simulated HAL (motor with inertia, lever via key/UI, battery curve, buttons via keyboard), axum adapter with the same routes, serves `web/`; load client (8 WebSockets, mode "stops reading") | Development and UI tests without hardware; load client also against the real ESP |
| **louie-wasm** | `preview(mode_json, fies, seed, bots) -> curve + hints`, `validate(mode_json)` | Preview in the editor without server compute time, identical to the device (fallback `POST /api/modes/preview`) |

**Can the app layer be shared? Yes, and this is the most important cut.** `louie-app` knows neither
`EspHttpServer` nor axum. It provides the actor loop itself (thread, command channel, reply channels) and
talks to clients only via

```rust
pub trait ClientSink: Send {
    /// Never blocking. Err(Full) = client is lagging behind, Err(Closed) = gone.
    fn try_send(&self, frame: &Arc<str>) -> Result<(), SendError>;
    fn close(&self);
}
```

The hub creates **one** `Arc<str>` per tick and gives it to all sinks. The simulator therefore tests the real
server logic (permissions, locks, game master handover, button assignment, backpressure, timing of the channels), not
a replica. Limit: session cookies, header checks (5.5) and gzip delivery stay in the transport.

**`louie-proto` as a separate crate or as a feature in `louie-core`? Decision: separate crate** (E16). Trade-off: a
feature saves one crate, but would pull REST bodies, `Config`, `DevicesFile` and `ts-rs` into the core and thus into the
WASM. The mode types that the interpreter needs live in `louie-core` anyway; `louie-proto` only embeds
them. One more crate costs almost nothing in the workspace.

### 2.2 Data flow

```
Phone ──WS/REST──► Transport (httpd | axum) ──Req+reply channel──► ┌──────────────┐ ──setpoint (AtomicU32)──► motor thread ──► LEDC
   (pre-work in the httpd task: JSON, PBKDF2,  │ App (actor)   │ ◄──measurements── (IPROPI, VSYS, lever)
    validation, file read)                     │ 50 ms tick    │
BLE scan (BTHome) ──Cmd────────────────────────► │               │ ──Arc<str>──► ClientSink per WS (try_send)
J6 buttons, lever (ISR flags) ──Cmd────────────► │               │ ──store job──► storage thread
Net thread (Wi-Fi status) ──Cmd────────────────► └──────────────┘
WS "estop" ──────────── bypassing the channel ──────────────────────────────► ESTOP (AtomicBool) in the motor thread
```

## 3. HAL as traits

The traits live in `louie-app::hal` (std, no ESP types). Every method is non-blocking.

| Trait | Methods (selection) | Louie board | Simulator |
|---|---|---|---|
| `Motor` | `set_duty(i16 /*‰ duty cycle, −1000…1000*/)`, `brake()`, `coast()` | LEDC 20 kHz on IN1/IN2 (IO18/IO19), drive/brake: forward IN1 = 1, IN2 = PWM (1 − d) | Model with inertia, speed for the top view |
| `Lever` | `closed() -> bool`, `edges()` | SENSE IO3, level "closed" ≈ 3.0 V (main-board-c6.md 2.5) | Key / UI button |
| `Power` | `vsys_mv()`, `vbus_present()`, `usb_powered()` | VBAT_ADC IO0 (divider 470k/470k, factor 2), VBUS_DET IO4 | Slider in the UI |
| `MotorCurrent` | `ma()` | ISEN_ADC IO1, 255 mV/A (R_IPROPI 1.24 k × 205 µA/A) | from the motor model |
| `StatusLed` | `pattern(Pattern)` | IO14 | Display in the sim UI |
| `LedChain` | `enabled(bool)`, `write(&[Rgb])` | J7: data IO23 (RMT), load switch IO15 | Strip in the sim UI |
| `PlayerInputs` | `events() -> Iterator<(seat, Press)>` | J6: S1–S4 on IO5, IO20, IO21, IO8 (pull-up, debouncing) | Keys 1–4 |
| `Accel` | `motion_since_last()`, `enable_wake()` | LIS2DH12 on I²C IO6/IO7, INT IO2 (optional, detected by I²C probe) | – |
| `BleButtons` | `start_scan()`, `stop_scan()`, `events()` | NimBLE passive, BTHome parser in `louie-app` | Buttons via keyboard |
| `Clock` | `now_ms() -> u32`, `unix_time() -> Option<u64>` | `esp_timer`; Unix time only when known (5.1) | `Instant` (with time-lapse) |
| `Store` | `read(key)`, `write_atomic(key, bytes)` | LittleFS + NVS | Folder on disk |
| `Sleep` | `light_sleep(dur)`, `deep_sleep(wake: WakeSources)`, `reset_reason()` | ESP-IDF sleep API via `esp-idf-sys` | No-op with log |

Numeric values (dividers, scaling, thresholds) are **not** in the traits but in the board definition.

**Units (one per level):** The setpoint from the game to the motor thread is always a **motor voltage in mV**
(`i16`, sign = direction). Only the motor thread converts it into the **duty cycle in ‰** for `Motor::set_duty`
(`duty = U_soll / VSYS`). Model profiles and limits (cap, minimum speed, ramp in mV/s) are also in mV.
Percent only appears in the UI.

### 3.1 Board abstraction

```rust
pub struct BoardDef {
    pub name: &'static str,
    pub pins: Pins,                 // Option<GpioNum> per function
    pub vsys_divider: f32,          // 2.0 on the board
    pub ipropi_mv_per_a: u16,       // 255 (R_IPROPI 1.24 k); DevKit: same value, IO1 reads a pot
    pub vbus_divider: Option<f32>,  // None = VBUS_DET is only a switch (DevKit)
    pub options: Options,           // led_chain, player_inputs, accel_bus, rf_switch, rgb_led …
    pub flash: FlashSize,           // N4 | H8
}

```

There is only one motor driver: the **DRV8213 scheme** (IN1/IN2, drive/brake, coast = autosleep) on every board. A
`MotorDriver` enum is not needed; on the DevKit the same scheme drives two LEDs (LED mode).

- **Selection by Cargo feature** (`board-louie-v1`, `board-devkitm-c6`, `board-devkitc-c6`), exactly one active
  (`compile_error!` otherwise). Reason: the boards use different pins for the same function; a wrong assumption at
  runtime could drive one output against another. In addition, the `sdkconfig` (flash size,
  partition table) depends on the board.
- **Runtime detection only for options**: I²C probe for the LIS2DH12, LED chain and J6 according to the configuration
  (owner setting), battery present yes/no from the VSYS history. If an option is missing, the HAL returns `None` and
  the UI hides the feature.
- **Breadboard:** The test setup ([test-hardware.md](test-hardware.md)) uses the **Waveshare ESP32-C6-DEV-KIT-N8**
  (pin header identical to the ESP32-C6-DevKitC-1-N8, verified; 8 MB like the target H8) with **the same GPIO
  numbers** as the board; the only exception: the WROOM-1 module has no IO14, the status LED is on **IO10**. Optionally the DevKitM-1-N4 (same module as the board, all GPIOs).
  `board/devkitc_c6.rs` and `board/devkitm_c6.rs` take over the pins from `louie_v1.rs` and change only numeric values
  and options:
  - **Motor in LED mode:** no motor driver on the breadboard (decision 2026-11-06, decision-history.md 9). The
    firmware drives the DRV8213 scheme on IO18/IO19 unchanged; two LEDs (3V3 → 1 k → LED → pin) show direction
    (which LED lights) and speed (brightness). The motor current comes from a **potentiometer on IO1** with the same
    scaling (255 mV/A), VSYS from a potentiometer on IO0. Motor, stall thresholds and current calibration are tested on
    the prototype boards.
  - **IO4** on the DevKit is only a **switch** (USB yes/no), no divider on the 5V pin → `vbus_divider = None`.
  - **IO8:** The DevKit's RGB LED (WS2812) is on IO8 and collides with S4. **S4 cannot be used on the
    DevKit**; this is noted as a comment in the DevKit board definitions, and the option `player_inputs` reports only S1–S3. The RGB LED
    can serve as a second status indicator.
  - **IO23** is the input for the latency reference in the test setup (test-hardware.md 5.3).

  Whether the firmware fits on an N4 is shown by a build with the 4 MB partition table (6.1); it also runs on the
  8 MB board. The **XIAO ESP32-C6**
  is ruled out: only 11 GPIOs, IO3/IO14 are taken by the antenna switch (verified, Seeed wiki).

## 4. Concurrency

**Decision (recommendation): FreeRTOS threads via `std::thread`, no async executor on the ESP.**
`EspHttpServer` and NimBLE work with callbacks in their own IDF tasks; an executor would add a second
execution world without benefit. The actor loop is a `std::thread` in the simulator as well; axum handlers talk to it
only through the channels (`try_send`, never blocking in the tokio task).

| Thread | Priority (FreeRTOS) | Tick | Stack (initial) | Task |
|---|---|---|---|---|
| `motor` | 15 (above httpd, below Wi-Fi/lwIP) | 10 ms | **6 KB** | Take setpoint, apply ramp and limits, set LEDC; read IPROPI, detect stall; **500 ms without setpoint → 0**; check emergency-stop atomic; heartbeat for the second dead-man timer; registers with the task watchdog |
| `game` | 10 | 50 ms | 12 KB | App actor: process commands from the channel (state changes only, 4.2), `tick(now)`, setpoint to `motor`, state to hub, storage jobs |
| `hub` | 8 | 100 ms | 6 KB | Serialize state once into the reusable buffer, one `Arc<str>` to all `ClientSink`s (5.4); events immediately |
| httpd (IDF) | 5 (default) | – | 10 KB (esp-idf-svc default 6 KB, verified) | REST pre-work (parse JSON, PBKDF2, validation, file read) → request to `game`; WS messages → command channel; send work from `httpd_queue_work` |
| `worker` | 4 | on demand | 8 KB | long tasks that should not run in httpd (mode preview as fallback, reading a large file); one queue, result via reply channel |
| `net` | 6 | events | 8 KB | Wi-Fi state machine (STA, AP, fallback, background scan), mDNS |
| `dns` | 5 | blocking | 4 KB | Captive DNS (UDP 53), only in AP mode |
| NimBLE host (IDF) | IDF default | – | IDF | Scan callback → BTHome parser → command |
| `store` | 3 | on demand | 6 KB | Write files atomically (temp + rename), debounced 2 s |

- **Channels:** `std::sync::mpsc::sync_channel` (bounded, e.g. 32 entries) for commands to `game`. If the
  channel is full, the request is rejected with "busy", never blocked.
- **Setpoint slot:** one `AtomicU32` (upper 16 bits setpoint in mV as `i16`, lower 16 bits sequence number). The
  motor thread sees from the change of the sequence that `game` is alive (dead-man timer), without a lock.
- **Emergency stop:** `ESTOP: AtomicBool`, set directly in the WS handler (httpd task) or by lever and stall,
  read in the motor thread **before** every LEDC write. Reset only by the actor after confirmation in the UI.
- **State for REST GET:** `Arc<Mutex<Snapshot>>` with a version counter; the lock is held only to copy the `Arc`,
  never while sending.
- **Priorities** on the ESP via `ThreadSpawnConfiguration` (esp-idf-hal) → `esp_pthread_set_cfg`. The setting
  applies **to all following threads that the calling thread starts** (thread-local, with `inherit` also for
  their children) until it is reset (verified, IDF `pthread.c`). Therefore: set, spawn, immediately
  `ThreadSpawnConfiguration::default().set()` again. Wi-Fi and lwIP tasks (IDF) stay higher.
- **Game tick 50 ms**: `tick` computes the mode setpoint, jokers, spice, round end. The motor thread smooths at 10 ms.
- **Short inputs** (J6 buttons, lever edges) only set a flag/counter in the ISR; `game` reads it on each
  tick. So no press is lost.
- **Time:** `now_ms` is `u32` and overflows after 49.7 days. All differences with `wrapping_sub`, never `<` on
  points in time; a unit test starts the clock shortly before `u32::MAX`.

### 4.1 Motor safety

1. **Hardware:** lever in series with the motor; DRV8213 current limit 2 A. **Levels on IN1/IN2 around
   reset (verified, C6 datasheet v1.5 tab. 2-1/2-2, DRV8213 datasheet tab. 8-2):** During reset, IO18
   and IO19 (like IO18–IO23) have the internal **pull-up (approx. 45 k)** enabled. Against the internal 200 k pull-down of the
   DRV8213 this gives approx. 3.3 V × 200/245 ≈ 2.7 V > V_IH 1.45 V, so **IN1 = IN2 = 1 = brake** (both low-side
   on), no drive. After reset both pins are input only without pull → 200 k pulls to 0 → **coast**,
   then autosleep. The earlier statement "pull-downs → motor off during reset" is therefore only true after reset; during reset
   the driver brakes briefly. Hardware finding: see 13 and main-board-c6.md 3.2 (still to be updated there).
2. **Start order in `main`:** first of all IO18/IO19 as output to 0 (coast), then set up LEDC with duty cycle 0,
   only after that Wi-Fi, BLE and file system.
3. **Motor thread:** the only place that writes LEDC. Limits from the model profile (admin), maximum ramp
   (mV/s), direction change only via stop, reverse limits (burst duration, gap, share). It takes setpoints in
   mV and computes `duty = U_soll / VSYS` itself.
4. **Emergency stop:** `ESTOP` (see 4) takes effect in the next 10 ms cycle, independent of channel and game thread.
5. **Dead-man timer:** 500 ms without a new setpoint sequence → ramp to 0. If the game thread hangs, the motor stops.
6. **Manual motor control** (`workshop.motor`, workshop): every command carries its **own validity period
   (1 s)**. Without repetition the setpoint drops to 0, even if the game thread keeps running and the phone loses the
   connection.
7. **Stall:** current above threshold for longer than x ms (≤ 0.5 s, main-board-c6.md 3) → off, error to `game`,
   round stops, UI shows the reason.
8. **Task watchdog (TWDT):** `motor` and `game` register; `CONFIG_ESP_TASK_WDT_PANIC=y` and
   `CONFIG_ESP_TASK_WDT_TIMEOUT_S=2` in `sdkconfig.defaults`. The IDF defaults are **without panic** and **5 s**
   (verified, Kconfig 5.5): without this setting the TWDT would only log.
9. **Second dead-man timer (`esp_timer`, 20 ms):** checks the heartbeat of the motor thread; if it is missing > 100 ms, the
   callback sets both LEDC channels directly to 0 (`ledc_stop`, idle level 0). Catches a hung motor thread
   before the TWDT fires after 2 s.
10. **Panic:** `panic = "abort"` → restart. A Rust panic hook first sets LEDC to 0 and writes the message to
    RTC memory (`RTC_NOINIT`); no NVS in the panic hook (unverified whether this is safe). **C panics** (exception,
    TWDT panic, stack overflow, `abort` in IDF) bypass the Rust hook: until the reset, LEDC keeps driving with the
    last duty cycle, possibly longer while a core dump is written to flash (unverified, measure in HIL).
    Fallback if this is too long: wrap the panic handler via `-Wl,--wrap=esp_panic_handler` and stop LEDC there
    (unverified), or core dump only to RAM/UART.
11. **Restart after an unexpected reset (brownout, WDT, panic):** No start just because the lever is "closed"
    at startup. After every reset except power-on and an intended restart (`reset_reason()`), the motor only starts
    after an **edge lever open → closed** or a start in the UI. A **restart counter in RTC memory** counts
    unexpected resets; from 3 within 60 s the motor stays locked until the lever is opened and
    closed again, and the UI shows "Supply interrupted" (idea-power-bank.md). This avoids a
    brownout loop (start → dip → reset → start).
12. **Brownout shortly after an OTA update:** see 7 (motor locked until the new image is marked valid).

### 4.2 Router context: who computes what

**Pattern (E14):** The actor in the `game` thread handles **only state changes**. Every REST or WS request
runs like this:

1. **httpd task (pre-work, stateless):** check headers (5.5), read the body and parse JSON, limit sizes,
   PBKDF2 for the admin login, validate mode JSON with `louie-core`, read files. Longer than about 50 ms
   (preview fallback, large files) → to `worker`.
2. **Request to the actor:** fully checked structure plus reply channel (`sync_channel(1)`) via the
   command channel; httpd waits for the reply with a **timeout of 500 ms**, otherwise 503 "busy".
3. **Actor:** checks permissions against the current state, changes it, replies. No JSON parsing, no hash,
   no file I/O in the 50 ms tick; saving goes as a job to `store`.
4. **Reply:** httpd serializes and sends. The actor holds no lock meanwhile.

PBKDF2 takes noticeable time on the C6 depending on the iteration count (unverified, measure; target ≤ 300 ms), so never in the actor.

### 4.3 Stacks and memory guards

- **The default stack is small:** Rust `std::thread` on ESP-IDF without `Builder::stack_size` passes the
  pthread default `CONFIG_PTHREAD_TASK_STACK_SIZE_DEFAULT` = **3072 bytes** (verified, Rust std
  `sys/thread/unix.rs` and IDF Kconfig). Because std always passes pthread attributes, **these override the
  stack size from `ThreadSpawnConfiguration`** (verified, IDF `pthread.c`). Therefore **every** thread starts with
  `thread::Builder::new().name(..).stack_size(..)`; a Clippy lint or code review rule forbids bare
  `thread::spawn` in `louie-fw`.
- `CONFIG_ESP_SYSTEM_HW_STACK_GUARD` is the default on the C6 (verified, Kconfig 5.5) and stays on; plus the
  FreeRTOS canary.
- Diagnostics show the **high-water mark** per thread (`uxTaskGetStackHighWaterMark`); target ≥ 1 KB reserve after
  the 2 h load test, otherwise increase the stack.

## 5. Network

### 5.1 Wi-Fi, hotspot, captive portal, mDNS, time

| Building block | Implementation | Status |
|---|---|---|
| STA + AP at the same time | `EspWifi` with `Configuration::Mixed` (STA + AP); test Wi-Fi in AP+STA mode (software-concept.md 3.3) | (unverified, check API name in step 0) |
| Startup sequence, fallback | `net` thread as a state machine per software-concept.md 3.1; no change during a round | – |
| AP clients | `max_connection` 8 (ESP-IDF allows up to 10); DHCP server hands out 8 addresses by default (`LWIP_DHCPS_MAX_STATION_NUM`) | (verified, software-concept.md 3.2; Kconfig 5.5) |
| Hotspot password | **random at first start** (e.g. 10 characters without confusable characters) from the hardware RNG, in NVS; output on the console at first start and for the sticker; do not derive from the MAC (every beacon broadcasts the MAC) | Decision E17 |
| Captive DNS | own small DNS server (std `UdpSocket`, about 100 lines, answers all A queries with 192.168.4.1) or crate `edge-captive` 0.8 (std feature) | (verified, crates.io) |
| Captive portal via DHCP | **Option 114** (captive portal URI, RFC 8910) via `esp_netif_dhcps_option(… ESP_NETIF_CAPTIVEPORTAL_URI …)`; the IDF example `captive_portal` enables it via Kconfig | (verified, IDF 5.5 `esp_netif_types.h` and example) |
| Captive detection by phones | Until a client's first page request, the probe URLs (Android `/generate_204`, Apple `/hotspot-detect.html`, Windows `/connecttest.txt`) redirect to `/`; **after that** (flag per client IP) the firmware answers with "success" (204 or the expected page). Otherwise the phone stays in the restricted portal window or keeps switching back and forth | (unverified, check behaviour per Android/iOS version on the test setup; Android may keep "no internet" and use mobile data in parallel) |
| mDNS | `EspMdns` from esp-idf-svc, component `espressif/mdns` via `remote_component` in `Cargo.toml`. Name **`louie-xxxx.local`** (unique with two devices), plus alias `louie.local` as long as no second device claims it | (verified); alias mechanism (delegate host) (unverified) |
| Time | In AP mode there is no SNTP. The browser sends its time (`Date.now()`) in the first WS message; the server takes it as long as nothing better is available (SNTP in STA mode). Time only for logs and file timestamps, never for game logic | – |
| BLE + SoftAP with clients | Coexistence according to Espressif "supported, unstable" (C1); BLE scan only while a mode with jokers runs and buttons are paired | (verified, coexistence table C6) |

**Sockets:** `max_open_sockets` = **14–16** (8 player WS + game master + spectators + 3–4 short-lived HTTP),
`CONFIG_LWIP_MAX_SOCKETS=24` (default 10, verified) and `CONFIG_LWIP_MAX_ACTIVE_TCP` ≥ 20 (default 16,
verified). Calculation: httpd reserves 3 internally (verified, IDF docs `max_open_sockets`), DNS 1, mDNS 1–2 (unverified)
→ 16 + 3 + 3 = 22, rest reserve. The web UI is bundled into **2–3 files** (HTML, JS, CSS; languages and WASM
only on demand) so that one page load does not open 10 connections.

**`lru_purge_enable` (default in esp-idf-svc: on, verified):** If all slots are taken, httpd closes, on a
new connection, the session that has gone longest **without incoming data**. The counter is only increased on
receive, not on send (verified, IDF `httpd_sess.c`). A spectator who only receives is therefore
**cut first**. This is why every client sends an acknowledgement every 5 s (5.4); this keeps it "fresh". In addition,
14–16 slots leave room for short-lived HTTP connections.

### 5.2 HTTP and WebSocket

- **`EspHttpServer`** (esp-idf-svc): REST handler per route, all of which lead into the same `louie-app` router
  (pre-work per 4.2); `ws_handler` for `/ws`. Since esp-idf-svc **0.52** `ws_handler` has an argument for
  subprotocols, since **0.53** the server has `keep_alive`/`so_linger` (verified, changelog).
- **Sending to WebSockets:** **not** via `EspHttpWsDetachedSender::send()`, but via the own send path
  in 5.4 (E13).
- **WebSocket handshake in newer IDF versions:** From **ESP-IDF 5.5.5 and 6.0.1** httpd **no longer** calls the URI handler
  during the handshake (verified, `httpd_uri.c`; 5.5.4 and 6.0 still do). Then the
  esp-idf-svc handler never sees `EspHttpWsConnection::New`, `is_new()` is never true, and handshake headers can no longer be read in the
  handler. The firmware therefore does **not** rely on `is_new()`: a client counts as connected only
  with its **first message** (`hello` with token, protocol version and time); only then
  is its `ClientSink` created.
- **Static files:** gzip from the UI package (embedded in the firmware or in the `www` partition, 6.4),
  `Content-Encoding: gzip`, `Cache-Control` with version hash in the file name. If the installed package does not fit
  the firmware, the fallback UI from the firmware is served (6.4).
- **No HTTPS** (rationale software-concept.md 2.4).
- **Admin password:** salted, iterated hash (PBKDF2-SHA-256) on the server, computed in the httpd task
  (4.2); without HTTPS the browser lacks Web Crypto.

### 5.3 Protocol

The basis is software-concept.md section 7. Additions the firmware knows from the start:

- from web-ui-concept.md 8: WS `request_lead`, `handover`, `release_lead`, `request_join`, `allow_players`, `kick`,
  `leader_plays`, `chick_lost`, `estop`; state `multiplayer`, `leader_plays`, `lead_policy`; permissions
  `modes.select`, `modes.tweak`, `workshop.dry`, `workshop.motor`.
- **First WS message** of the client: `{"t":"hello","token":"…","proto":N,"now":<ms since 1970>}`. Without a valid
  token only spectator permissions.
- **Acknowledgement:** Every server message carries a sequence number `seq`. The client acknowledges received
  state messages with `{"t":"ack","seq":N}` (the newest is enough) and, without state traffic, sends an acknowledgement at least
  every 5 s (5.4).
- `workshop.motor`: `{"t":"motor","mv":…,"valid_ms":1000}`; without repetition → 0 after 1 s (4.1).
- Wireless buttons ([device-pairing.md](device-pairing.md)): `GET/POST/DELETE /api/admin/devices` (pairing,
  learn mode 30 s), assignment as a WS command of the game master; event
  `{"t":"event","kind":"joker","seat":2,"src":"button"}`; in the state optionally per player
  `"button":{"rssi":-71,"battery":90}`.
- **Mode selection by reference** (6.4): `{"t":"select_mode","src":"ui","id":"gewitter","hash":"…","fies":3}` with
  `modes.select`; "this round" sliders as `{"t":"tweak",…}` with `modes.tweak`. A complete mode JSON
  ("play this round only", mode-builder.md 4.7) only with "Create modes" ≥ Drafts. `GET /api/modes` returns the
  merged catalog (source, status, hints).
- **Preview** is computed by the browser with `louie-wasm`. The server checks on save (`POST/PUT /api/modes`) with
  the same core and returns the same hints. `POST /api/modes/preview` stays as a **fallback** (e.g. if
  the WASM does not load); it calls the same core function in the `worker`, so it only costs compute time, no code.
- Protocol version: `GET /api/state` and the first WS message return `proto` (integer). If it does not match the
  UI in the browser cache, the UI reloads.

**State rate:** on change, at most 10/s during the game. **One JSON string for all clients**, serialized once per tick into
a **reusable buffer** (no new `String` per tick) and distributed as `Arc<str>`.
Session-specific data (own role, own joker points) is in the shared state under the player ID; the phone
picks its own entry. Size with 8 players with jokers, buttons and permissions is more like **1.5–3 KB** (unverified;
the earlier estimate of 400–800 bytes was too low). Calculation: 1.5–3 KB × 10/s × 10 clients ≈ 150–300 KB/s
(unverified). Still acceptable for Wi-Fi, but noticeable in hotspot mode with BLE scan; fallback: split the state into "fast" (setpoint,
time, events) and "slow" (players, permissions, only on change), or rate 5/s (13).

### 5.4 Send path and backpressure

**Finding (verified, source code esp-idf-svc 0.53 `http/server.rs` and IDF 5.5 `esp_http_server`):**
`EspHttpWsDetachedSender::send()` queues work into the httpd task via `httpd_queue_work` and **waits
without its own time limit on a condvar** until it is done. The work calls `httpd_ws_send_frame_async`, which in the
httpd task writes via `send()` with `SO_SNDTIMEO` = `send_wait_timeout`; esp-idf-svc sets this value **fixed to
5 s** (not configurable). Consequences:

- A hanging phone (iOS in the background, Wi-Fi gone without FIN, full TCP window) blocks the **httpd task for up to
  5 s per frame** and the sending `hub` thread for just as long. All other clients freeze too.
- Calling `send()` **from inside an httpd handler** makes the httpd task wait for work that only it can
  do → **deadlock**.
- If the sender holds a lock that `game` or a handler needs, the whole system stops.

**Solution (E13): own send path in `louie-fw/src/net/ws_send.rs`.**

1. The hub puts **one** `Arc<str>` per tick into a slot per client (`ClientSink::try_send`, only swap pointers)
   and queues **one** `httpd_queue_work` job; it does not wait for it.
2. The job runs in the httpd task and sends the frame to all clients whose slot is new. For each WS session
   a send function with **`MSG_DONTWAIT`** is registered via `httpd_sess_set_send_override` (verified, API
   exists; behaviour on partial writes (unverified), check in step 3). If it cannot write everything immediately,
   the session is closed via `httpd_sess_trigger_close` (half a frame breaks the stream
   anyway). The client reconnects.
3. **Backpressure at application level:** Each client acknowledges the sequence number (5.3). If a client has **more than
   2 state frames** unacknowledged, it gets no new ones until the acknowledgement arrives; then directly the
   newest state (older ones expire). This keeps the TCP buffer of a healthy client small, and `MSG_DONTWAIT`
   only fails for clients that really hang.
4. **15 s without a message** from the client → `httpd_sess_trigger_close`. In addition TCP keepalive via `keep_alive`
   in the server configuration (since esp-idf-svc 0.53, verified), e.g. 10 s idle, 3 × 5 s.
5. **Rules in the code:** never hold a lock while sending; never `EspHttpWsDetachedSender::send()` in
   httpd context; the hub never blocks.
6. In the simulator the axum adapter implements `ClientSink` with a tokio `mpsc` of capacity 2 and
   `try_send`; so the same behaviour applies.
7. **Test:** The load client has a mode **"stops reading"** (socket open, no reading, no acknowledgement).
   Expectation: the other 7 clients see no gap > 200 ms, the hanging one is disconnected after ≤ 15 s.

Fallback if `httpd_sess_set_send_override` does not work cleanly with WS sessions: the send function stays
default, but `send_wait_timeout` set to 1 s via an own server configuration through `esp-idf-sys`, with the same
acknowledgement logic; or an own WS server on raw sockets only for `/ws` (13).

### 5.5 Security in the local network

No HTTPS, so only what works without encryption protects:

- **Host header** must be `192.168.4.1`, the STA IP, `louie-xxxx.local` or `louie.local`; otherwise 421/403.
  Protects against **DNS rebinding** (a foreign page re-resolves its name to the Louie IP).
- **Origin header** on all writing REST requests (`POST/PUT/DELETE`) must match one of these hosts
  (CSRF). If it is missing (old browsers), allow only for requests without a cookie.
- **WebSocket:** The **token comes in the first WS message**, not via cookie. A foreign page that
  opens `ws://louie.local/ws` (cross-site WebSocket) does not have the token and stays a spectator. An origin check
  during the handshake is not directly possible with esp-idf-svc (5.2); optionally via the IDF pre-handshake callback
  (`CONFIG_HTTPD_WS_PRE_HANDSHAKE_CB_SUPPORT`, IDF ≥ 5.4, verified) with own URI registration via
  `esp-idf-sys` (unverified, estimate effort in step 3).
- **Cookie** (admin session for REST): `HttpOnly; SameSite=Strict; Path=/`.
- **OTA for admin only**, size limited to the slot size; **project name** (`louie-fw`) and
  **board** in the app header are checked before `EspOta::complete()` is called; wrong image → abort without restart.
- **UI package update (from stage 2, 6.4) for admin only**, same checks: size ≤ `www`, manifest and hash of the whole
  package before it is activated. A UI package has full access to all controls of the logged-in user, so it is treated
  like firmware (optional signature as below).
- **Optional signed images without Secure Boot:** `CONFIG_SECURE_SIGNED_APPS_NO_SECURE_BOOT` is available on the C6
  (RSA or ECDSA V2 scheme, verified, Kconfig 5.5). Protects against foreign images over the network, not against
  USB. Costs key management; decision after step 6.
- Hotspot password: see 5.1.

## 6. Storage

### 6.1 Partition tables (proposal)

**N4 (4 MB), default with OTA:**

| Name | Type | Offset | Size |
|---|---|---|---|
| nvs | data/nvs | 0x9000 | 0x5000 (20 KB) |
| otadata | data/ota | 0xE000 | 0x2000 |
| phy_init | data/phy | 0x10000 | 0x1000 |
| coredump | data/coredump | 0x11000 | 0xF000 (60 KB) |
| ota_0 | app | 0x20000 | 0x1E0000 (1.875 MiB) |
| ota_1 | app | 0x200000 | 0x1E0000 (1.875 MiB) |
| storage | data/littlefs | 0x3E0000 | 0x20000 (128 KB) |

**N4, plan B with `www` partition** (`partitions-4mb-www.csv`): ota_0 / ota_1 each **0x1B0000 (1.6875 MiB)** from
0x20000 and 0x1D0000, **`www` (data, own subtype value) 0x60000 (384 KB)** from 0x380000, `storage` 0x3E0000
with 0x20000; rest as above. The web files then live not in the app but in `www`.

**H8 (8 MB):** ota_0 / ota_1 each **0x300000 (3 MiB)** from 0x20000 and 0x320000, `storage` 0x620000 with
**0x1E0000 (1.875 MiB)**; rest as N4. **From stage 2 (6.4):** `storage` 0x620000 with **0x160000 (1.375 MiB)**, **`www`
0x780000 with 0x80000 (512 KB)** for the separately updatable UI package.

- **Realistic size estimate:** code with esp-idf-svc, Wi-Fi + NimBLE + httpd + mDNS + serde_json,
  `opt-level = "s"`, LTO: **1.3–1.7 MB** (unverified; Wi-Fi+BLE firmwares in C are about 1.2–1.6 MB, Rust std and
  serde come on top). **Plus the embedded files:** web UI gzip ≤ 100 KB, languages about 100 KB, WASM gzip
  60–120 KB → **app image realistically 1.6–2.0 MB** (unverified). One slot on N4 holds 1.875 MiB = 1.97 MB.
- **Measurement in step 0 with placeholder assets** (random data in the target sizes, gzip-resistant), so that the number
  does not only arrive at the end. Decision afterwards:
  - App ≤ 1.8 MiB → N4 with OTA as above.
  - Code alone ≤ 1.65 MiB, too large with files → **plan B `www` partition**. Update in two steps
    (first `www`, then app) with a **version check**: the app knows the hash of the matching `www` build; if it does
    not match, it serves a small emergency page from the firmware (≤ 10 KB) with an upload for `www`. A rollback of the app
    leaves `www` in place, so every app must still start with the previous `www` build (protocol version, 5.3).
  - Larger → N4 **without OTA** (one large app slot, update via USB) or H8.
- Zigbee (+0.5–0.8 MB, main-board-c6.md 4) only fits on H8.
- The table is tight on N4: 128 KB file system is enough for `config.json`, `devices.json` and 30 own modes
  at ≤ 2 KB each, but not for web UI and languages. These therefore live in the firmware or in `www` (6.2).

### 6.2 What is stored where

| Content | Location | Rationale |
|---|---|---|
| **UI package** (manifest, web UI in 2–3 files gzip ≤ 100 KB, languages about 100 KB, `modes/index.json` + `modes/*.json`) | **V1: in the firmware** (`include_bytes!`); from stage 2 and on N4 plan B: `www` | 6.4; V1 updated together with the firmware, rollback included |
| Fallback UI (lobby, mode pick, start/stop, update page; H8 ≤ 30 KB, N4 emergency page ≤ 10 KB) | in the firmware | served when the UI package is missing or does not fit (6.4) |
| Fallback modes (Classic, optionally one more) | in the firmware | lever mode on a fresh device or after a broken `current.json` |
| `louie_core.wasm` (gzip, 60–120 KB) | **in the firmware**; N4 plan B: `www`, but as part of the firmware release with the hash known to the app, never from the UI package | built from `louie-core`, so preview and device must come from the same build |
| `current.json` (reference + copy of the current program + meanness) | LittleFS | written on selection (never during a round); loaded at boot, so the lever plays the last selection |
| `config.json` (model profile, limits, permissions, admin hash, power) | LittleFS | write atomically (temp + rename) |
| `devices.json` (paired buttons) | LittleFS | device-pairing.md 7 |
| `modes/*.json` (own modes) | LittleFS | source `own` in the catalog (6.4) |
| Wi-Fi credentials, hotspot password (random, 5.1) | **NVS** (encrypted if flash encryption comes later) | robust against power loss, never in Git |
| Last panic reason, recent errors, restart counter | **RTC memory (`RTC_NOINIT`)**, moved to NVS at the next start | survives software reset and brownout without flash writes in the failure case |

File system: **LittleFS** via the component `joltwallet/littlefs`, included via `remote_component`;
esp-idf-svc offers `MountedLittlefs` for it (verified, source code). Not SPIFFS: slow, no real
directories, not power-loss safe.

**Flash writes block:** On the single-core C6 every erase/write in flash (NVS, LittleFS, OTA,
core dump) halts all tasks whose code is not in IRAM, per sector erase in the range of tens of ms
(unverified). LEDC keeps running in hardware, but motor thread, dead-man timer and Wi-Fi stall. Measure in HIL
(jitter of the motor thread while `store` writes and during OTA); never batch writes during a round,
OTA only without a round.

### 6.3 RAM budget

Starting point: **259 KB free** with Wi-Fi + BLE initialized (verified, ESP-Techpedia example). From this
(all unverified, measure in step 0 and 3):

| Item | Estimate | Remark |
|---|---|---|
| Thread stacks (`motor` 6, `game` 12, `hub` 6, `worker` 8, `net` 8, `dns` 4, `store` 6 KB) | about 50 KB | 4.3; end the `main` task after startup or keep it small |
| httpd task + sessions | 10 KB + about 0.5–1 KB per session → about 20–25 KB | with 16 sessions |
| lwIP per TCP connection | PCB + occupied buffers; upper bound `TCP_SND_BUF` + `TCP_WND` = 5760 + 5760 B (IDF default, verified) | **worst case about 11 KB per connection**, × 12 = 135 KB. Backpressure (5.4) keeps the send buffer at ≤ 2 frames (≤ 6 KB); typically about 2–4 KB per connection → 25–50 KB |
| Wi-Fi buffers in AP with 8 clients (dynamic TX/RX) | 20–50 KB | Peaks when sending to all; limit `ESP_WIFI_DYNAMIC_TX_BUFFER_NUM` if needed |
| NimBLE host (scan) | mostly included in the starting value, scan buffer about 5 KB | |
| mDNS, DNS, LittleFS cache, NVS cache | about 15–25 KB | |
| App state with 8 players | **1.5–3 KB** | plus the parsed current mode 2–5 KB, sessions 8 × 0.2 KB |
| JSON buffers | 2 × 4 KB, **reused** (hub, REST reply) | no allocation per tick |
| Log ring buffer | about 5 KB | 50 entries |
| **Typical total** | **about 150–200 KB** | remaining 60–110 KB |

**Test criterion (HIL, 2 h load client with 8 WS and one hanging client):** free heap **≥ 60 KB**, largest
free block **≥ 16 KB**, both without a downward trend in the last hour. If this is missed: sessions to 12,
`TCP_SND_BUF`/`TCP_WND` to 2–3 MSS, split the state (5.3), BLE scan only when needed.

### 6.4 Mode catalog and UI package

**Layers.** The core is not a game; it is a player for game programs:

| Layer | Runs on | Content |
|---|---|---|
| HAL | ESP (`louie-fw`) | LEDC, ADC, GPIO, BLE … (3) |
| Safety layer | ESP, cannot be bypassed | model profile, owner limits, ramps, dead-man timer, emergency stop (4.1); applies to **every** command, also `workshop.motor` |
| Mode runtime | ESP (`louie-core`) | plays **one** program: flight plan segments, spice, jokers, end (mode-builder.md 2); joker accounts and permissions |
| Mode catalog | ESP (`louie-app`) | knows all available programs, validates, selects, stores the current one |
| Web UI | browser | displays, editor, sends selection and player inputs |

The **vocabulary** of the runtime (segment types, spice kinds, joker kinds, schema version) is the core's API. A new
program from existing building blocks is pure data and needs no firmware update; a new building block needs one.
A game flow is never executed in the browser: background tabs are throttled or stopped, several phones would need
one "executing" phone, and permissions and timing must stay on the device anyway.

**Catalog sources:**

| Source `src` | Location | Content | Writable |
|---|---|---|---|
| `fw` | app image | Classic (default lever mode), optionally one more | no |
| `ui` | UI package `modes/index.json` + `modes/<id>.json` | the modes this UI brings (V1: the built-in modes of web-ui-concept.md 6.2) | only by replacing the package |
| `own` | LittleFS `modes/<id>.json` | modes saved in the editor | per permission (mode-builder.md 7) |

- A mode is identified by **`src` + `id`**; the same `id` in two sources is allowed. A reference also carries the
  **hash** of the program, so a selection never silently plays a changed program.
- **At boot** the core reads only the indexes (`id`, `name`, `icon`, `desc`, `schema`, `needs`, hash; for `own`
  built by scanning once and kept in RAM, about 100 B per mode). Only the current program is parsed completely
  (6.3).
- **Validation:** every program is validated with `louie-core` when the package is installed and when an own mode is saved.
  Programs with an unknown schema or building block get `status: "incompatible"` with a hint and are not offered.
  This also covers a firmware rollback: an older core hides modes that use newer building blocks.
- **Current program:** selecting writes `current.json` (reference and a copy of the program), only in READY/END
  and with the lever off (software-concept.md 5.1). At boot the core plays this copy even if the source has
  disappeared in the meantime; if the copy is broken or incompatible → fallback mode `fw:classic`, hint in the UI.
- **Offline selection:** `config.json` holds an `offline_order` (admin favourites, default: catalog order `fw`, `ui`,
  `own`). Lever gesture "next mode" (ideas.md modi-39), paired buttons or J6 step through this list without a
  phone; the status LED or a short motor twitch confirms. External clients (Home Assistant, a native app) use the
  same `GET /api/modes`.
- **Permissions:** select by reference with `modes.select`, sliders "this round" with `modes.tweak`, a complete JSON
  only with "Create modes" ≥ Drafts (5.3). So a game master who may only select cannot upload arbitrary programs.

**UI package format** (one image for `www`, the same layout embedded in V1):

```json
{
  "pkg": "louie-ui", "name": "Family", "version": "1.4.0",
  "proto": [3, 4], "schema": [2, 2], "requires": ["jokers", "buttons"],
  "files": { "index.html": "…hash", "app.js": "…hash", "modes/index.json": "…hash" }
}
```

The firmware serves the package only if its own protocol version lies in `proto` and it supports `schema` and
`requires` (capability flags of the firmware); otherwise it serves the fallback UI with the hint "UI package does
not fit this firmware" and keeps the `ui` modes that still validate. `louie_core.wasm` is **not** part of the UI
package (6.2).

**Stages:**

| Stage | What | Why |
|---|---|---|
| **1 (V1)** | One release: the UI package is embedded in the firmware, but read through the same package reader (manifest, `modes/index.json`). Catalog, selection by reference, `current.json`, `offline_order` already as above | no compatibility matrix, rollback includes the UI; later only the storage location changes |
| **2 (when a second UI or game exists)** | Package in the `www` partition (6.1), separate update `POST /api/admin/ui`, several packages available for download, only one installed | same core for different UIs or games |

**`www` has no A/B slot:** During writing and after an interrupted write the fallback UI is served; the package is
activated only after the hash over all files matches. The game keeps working, because the current program lives in
`current.json`.

## 7. Updates, logging, diagnostics, errors

- **OTA with rollback:** `POST /api/admin/update` streams the image into `EspOta::initiate_update()` →
  `write()` → `complete()`; restart. Bootloader with `CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE`. The new firmware
  runs in state `PENDING_VERIFY`; every reset before confirmation sets it to `ABORTED` and the bootloader
  starts the old one (verified, IDF OTA docs). The new one calls `mark_running_slot_valid()` when Wi-Fi or AP is running,
  the web server responds and all threads are alive (about 10–30 s), otherwise `mark_running_slot_invalid_and_reboot()`
  or watchdog → old version (verified, esp-idf-svc `ota.rs`).
- **Brownout in the first seconds after an update:** Because every reset before confirmation rolls back,
  a motor start on a weak battery would discard a good firmware. Therefore: **motor locked while the image
  is `PENDING_VERIFY`**; the self-test does not need the motor. If the firmware rolls back anyway and the
  reset reason was brownout, the old version shows "Update discarded due to supply interruption, repeat with a USB power
  supply".
- **UI package update (stage 2, 6.4):** `POST /api/admin/ui` streams the package into `www` (first erased and marked
  invalid, fallback UI meanwhile), then hash and manifest check, then activation and catalog reload without restart.
  Same conditions as the firmware update (lever off, no round). A firmware rollback leaves `www` in place; the
  manifest check decides whether the package is still served.
- **Update file:** one `.bin` from `espflash save-image`; the UI checks board name and version in the app header
  before uploading, the server checks again (5.5). Updates only with lever "off" and no running round.
- **USB:** flashing and console via J4 (USB-Serial-JTAG), `espflash flash --monitor`.
- **Logging:** `log` crate with `EspLogger`; ring buffer of the last 50 warnings/errors in RAM, available via
  `GET /api/admin/diag` and live in the workshop area. The **last 8 errors** are also stored in
  `RTC_NOINIT` and so survive a crash.
- **Diagnostics:** VSYS, VBUS, motor current, lever, RSSI, free heap and largest block, stack high-water mark of the
  threads, reset reason and restart counter (brownout → status card "Supply interrupted", idea-power-bank.md),
  uptime, version, **golden checksum** (8).
- **Error handling:** Errors in network or storage never stop the game thread. Broken JSON file →
  load backup `.bak`, otherwise defaults, notice in the UI. Core dump partition for analysis after a crash
  (mind the write duration, 4.1 item 10).
- **Power** (idea-power-bank.md, software-concept.md 6.4):
  - **There is no light sleep in hotspot mode.** Modem sleep (and thus automatic light sleep with Wi-Fi) only works
    in STA mode (verified, IDF Wi-Fi guide 5.5: "Modem-sleep mode works in station-only mode"); as an AP
    the radio must send beacons. Light sleep between rounds is therefore only possible in STA mode (`WIFI_PS_MIN_MODEM`).
  - **Deep sleep is a restart:** After wake-up, bootloader, app start and Wi-Fi setup run again; until the
    hotspot is visible again takes about 2–5 s (unverified, measure); phones must reconnect. Wake-up via SENSE (IO3,
    `ANY_HIGH`), VBUS_DET (IO4) and optionally INT (IO2). After a wake-up, 4.1 item 11 does not count as "unexpected".
  - On USB `WIFI_PS_NONE` and no deep sleep; power bank keep-alive as test mode (timer wake-up + radio burst).
    Special case lever closed when falling asleep: timer wake-up every 5 s (main-board-c6.md 2.5). Check all sleep paths on the
    test setup.

## 8. Tests

| Level | What | Where |
|---|---|---|
| Unit | `louie-core`: interpreter per segment type, meanness scaling, joker accounts, locks, reverse limits, permissions, time overflow `u32` | `cargo test` on the PC |
| **Golden** | `tests/modes/<name>.mode.json` + meanness + seed + bot strategy → `<name>.curve.json` (setpoint every 100 ms, events, hints). Deviation = test failure; `UPDATE_GOLDEN=1` rewrites | `cargo test`; the same files optionally against the JS interpreter in the PoC (with tolerance, see below) |
| App | Scenarios via `louie-app` with simulated clock and real actor loop: game master handover, timeouts, button assignment, admin lock, backpressure with slow `ClientSink` | `cargo test` |
| Protocol | Serialization `louie-proto` ↔ example JSON from the docs; generate TS types and check them in the web UI | `cargo test`, `tsc` |
| Simulator | Whole system with web UI, several browsers, load client (also "stops reading") | `just sim` |
| WASM | Same golden files in the browser build (`wasm-bindgen-test`) | `just wasm-test` |
| UI package | every `modes/*.json` of the package validates with `louie-core` of every firmware version in the manifest range; golden curves for the default package | `cargo test`, CI |
| Device | `GET /api/admin/diag/golden` computes the `fw` modes and the modes of the installed UI package on the ESP and returns a checksum per curve; must match the PC checksum | HIL |
| Hardware-in-the-loop | Test setup: load client (8 WS, 10/s, one hanging), BLE button simulator, measurement of heap/largest block (6.3), latency, jitter, flash writes, sleep/wake-up, stall (simulated by pot; real motor on the prototype board), emergency stop, reset behaviour | [test-hardware.md](test-hardware.md) 4, 5 |

**Determinism:** The core computes time in ms (`u32`, `wrapping_sub`), randomness from its own small PRNG with
seed, sine/exponential function via the crate `libm`, collections with fixed order (**`BTreeMap`, never
`HashMap`** in the core). So ESP, PC and WASM deliver bit-identical curves. The **JS PoC** computes with `f64` and its own
order; comparisons with it use a tolerance (e.g. ±1 mV or ±1 tick for events). Only Rust core, WASM and device
must be bit-identical.

**CI idea:** On every push `cargo fmt --check`, `clippy`, `cargo test` (host crates), WASM build and
golden tests; firmware build in the container `espressif/idf-rust` (unverified, check image name and tag with IDF 5.5 and
our dated nightly) with a size check (abort if the app exceeds the limit from 6.1). HIL
stays manual.

## 9. Toolchain

| Tool | Purpose | Note |
|---|---|---|
| `rustup` nightly (dated, in `rust-toolchain.toml`) + `rust-src` | ESP target `riscv32imac-esp-espidf` (tier 3, `build-std`) | **espup is not needed for RISC-V** (only for Xtensa); Clang ≥ 11 is required (verified, esp-idf-template). Raise the nightly only deliberately and with a golden/HIL run |
| Rust stable | Host crates, WASM | |
| `ldproxy` | Linker wrapper for ESP-IDF | `cargo install ldproxy` |
| `espflash` | Flashing, monitor, `save-image` for OTA | `cargo install espflash` |
| `cargo-generate` + `esp-idf-template` | Scaffold for `louie-fw` | once |
| ESP-IDF | `esp-idf-sys` downloads it itself on the first build; version pinned in `.cargo/config.toml` (`ESP_IDF_VERSION`, exact tag) | **v5.5.x** (E7); mind the WS handshake change from 5.5.5 (5.2) |
| `sccache` | Cache for Rust compilation output | saves time on clean builds and in CI (unverified how much with `build-std`) |
| `wasm-bindgen-cli` + `wasm-opt` | Build and shrink `louie-wasm` | `wasm-pack` optional; the rustwasm organization was dissolved in 2025, wasm-bindgen is still maintained (verified) |

**Profiles:** `dev` for `louie-fw` **without LTO**, `opt-level = "s"` (otherwise it does not fit and runs too slowly),
`debug = true`; `release` with LTO `fat`, `codegen-units = 1`, `panic = "abort"`. Size measurements only in
release.

**Build times (unverified, rules of thumb):** first firmware build 10–20 min (download and build ESP-IDF),
then 30–90 s incremental, longer with LTO in release. Flashing via USB-Serial-JTAG about 10–20 s. Host tests in
seconds. Therefore: develop logic in the simulator, flash the ESP only for HAL and network.

**WASM size (unverified):** core with serde_json 150–300 KB raw, after `wasm-opt -Oz` and gzip about 60–120 KB.
Loaded only in the editor, not at startup. If it is too large: mode input as `JsValue` via
`serde-wasm-bindgen` instead of serde_json.

## 10. justfile (proposal, not implemented yet)

| Command | Does |
|---|---|
| `just fw-build board=louie-v1` | Release build of the firmware for one board, print size (implemented) |
| `just fw-run [target] [port]` | build, flash, open monitor (bring-up or a probe; implemented, test-hardware.md 8) |
| `just fw-image board=louie-v1` | create OTA file (`espflash save-image`) |
| `just sim` | start the simulator on the PC (axum, serves `web/`) |
| `just test` | host tests incl. golden tests |
| `just golden-update` | rewrite golden files (after a deliberate change) |
| `just wasm` | build `louie-wasm`, `wasm-opt`, gzip to `web/` |
| `just web` | bundle web UI (2–3 files), gzip to `firmware/louie-fw/assets/` |
| `just load host=louie.local` | load client: 8 WebSockets against simulator or device; `stall=1` = one client stops reading |

## 11. Implementation order

| Step | Content | Done when |
|---|---|---|
| **0 – Toolchain and test setup** | `esp-idf-template` for C6, dated nightly, `Cargo.lock`; blink, LEDC 20 kHz on IO18/IO19 in **LED mode** (test-hardware.md 5), ADC (VSYS, ISEN pot), lever ISR; small test binaries for the **pre-order checks** (test-hardware.md 4: `lever_probe`, `boot_probe`, `pin_probe`, `adc_probe`); probe with Wi-Fi + NimBLE scan + httpd/WS **and placeholder assets** (UI 100 KB, languages 100 KB, WASM 120 KB) | LEDs follow the setpoint; pre-order checks 4.2–4.5 done. **Measurement points:** release app size (decision 6.1: N4 with OTA / `www` / without OTA / H8 only), free heap and largest block with Wi-Fi+BLE+httpd, stack high-water mark, PBKDF2 duration, IO18/IO19 on the oscilloscope during reset and deep sleep (test-hardware.md 4.4, F17) |
| **1 – Core** | `louie-core` with schema 2, meanness, jokers, limits; golden tests for the built-in modes and the examples from mode-builder.md 5 and 6 | `cargo test` green, curves match the PoC (tolerance, 8) |
| **2 – App and simulator** | `louie-proto`, `louie-app` with actor loop and `ClientSink`, mode catalog with package reader, selection by reference and `current.json` (6.4), `louie-sim`; switch the PoC UI to the real protocol | Game playable in the browser against the simulator; load client with a hanging client does not disturb the others |
| **3 – Network on the ESP** | STA/AP/fallback, captive DNS + option 114, mDNS, httpd + own send path (5.4), header checks (5.5), NVS, LittleFS | 8 phones on the hotspot; load client 2 h without errors, **heap ≥ 60 KB, largest block ≥ 16 KB** (6.3); hanging client disconnected after ≤ 15 s, others without gap > 200 ms; captive behaviour on Android + iOS recorded |
| **4 – Motor and power** | Motor thread with dead-man timer, emergency stop, stall, TWDT panic, second dead-man timer, restart rule; sleep/wake-up, battery/USB | HIL tests stall (motor and stall on the prototype board, test-hardware.md 6), dead-man timer, emergency stop latency (≤ 20 ms), wake-up passed; deliberate panic/WDT/brownout → no start without lever edge; jitter of the motor thread during flash writes measured |
| **5 – Wireless buttons** | NimBLE passive (wrapper from esp-idf-svc, E8), BTHome parser, pairing, assignment | Joker latency and hit rate per test-hardware.md |
| **6 – OTA and diagnostics** | Update with rollback and header check, diagnostics page, core dump, golden checksum on the device; fallback UI; separate UI package update only when stage 2 (6.4) is due | Deliberately broken firmware rolls back; reset in the first 30 s after an update → fallback with notice; golden checksum device = PC |
| **7 – WASM preview** | `louie-wasm` in the editor | Preview = device (golden tests in the browser) |
| **8 – Options** | LED chain J7, player inputs J6, accelerometer, power bank pulse | depending on assembly |

Steps 1 and 2 need no hardware and can run in parallel with step 0.

**Status step 0 (2026-11-07):** [firmware/louie-fw](../firmware/louie-fw/README.md) contains the board definitions,
the bring-up in LED mode and the four probes for test-hardware.md 4.2–4.5; written against the ESP-IDF v5.5 headers,
**not compiled yet**. Wi-Fi/NimBLE/httpd probe with placeholder assets and the size measurement are still open.

## 12. Decide before programming

| # | Question | Recommendation | Rationale |
|---|---|---|---|
| E1 | Threads or async on the ESP? | **Threads** (`std::thread` with fixed stack size), app as a synchronous actor | httpd and NimBLE are callback-based; easier to debug; same actor loop in the simulator, axum only as adapter |
| E2 | JSON or a more compact format (CBOR, binary, delta)? | **JSON** (serde_json), one buffer for all | about 150–300 KB/s with 10 clients (unverified) is acceptable, readable in the browser log; fast/slow split or delta only if the test requires it |
| E3 | Board by feature or at runtime? | **Feature** for pins, flash and motor driver, **runtime** for options | a wrong pin assumption can drive hardware; options can be detected harmlessly |
| E4 | Web server: esp-idf-svc `EspHttpServer` or `picoserve`? | **EspHttpServer**, with own WS send path (E13) | Routing, WS receive and sessions exist, no second network stack; picoserve only with a later move to no_std |
| E5 | File system | **LittleFS** (joltwallet) for user data, **NVS** for Wi-Fi and hotspot password, **UI package in the firmware** in V1 (stage 2 and N4 plan B: `www` partition, 6.4) | atomic updates, a small FS is enough on N4 |
| E6 | Repo structure | **`firmware/`** with host workspace `crates/` and separate workspace `louie-fw/`, both `Cargo.lock` checked in, dated nightly | separate toolchains (stable/nightly) without conflict, reproducible |
| E7 | ESP-IDF version | Pin **v5.5.x** to a fixed tag, check v6.x after step 0 | Honest rationale: 5.5 because of the longer maintenance period (30 months per minor version, verified, IDF support policy) and because esp-idf-svc 0.53 covers it. The esp32-nimble CI builds the C6 **only with 5.3.6** (5.5.5 only for C3/ESP32, verified) – so 5.5 is not tested there for the C6. WS handshake behaviour changed from 5.5.5 (5.2) |
| E8 | BLE crate | **NimBLE wrapper from esp-idf-svc 0.53** (GAP scan) first; fallback **esp32-nimble 0.13**, then directly `esp-idf-sys` (`ble_gap_disc`) | only passive scan needed, small surface; the wrapper comes with the same crate as the rest, esp32-nimble 0.13 depends on esp-idf-svc 0.53 anyway (verified, crates.io) and is only tested on the C6 with IDF 5.3.6. Previously the other way round (decision-history.md 8) |
| E9 | Preview | **WASM from `louie-core`**, server endpoint only as fallback (in the `worker`) | one implementation, normally no ESP compute time |
| E10 | Persistence format | JSON files with a `schema` field and migration on load | readable, back up/restore configuration as a file |
| E11 | Flash variant of the board | **H8 as the target.** N4 only after measurement in step 0: with OTA if the app stays ≤ 1.8 MiB; otherwise **`www` partition** (plan B, 6.1) or **without OTA** (USB update) | realistically 1.6–2.0 MB with embedded files; previously "N4 with OTA supported" (decision-history.md 8) |
| E12 | Firmware licence | **PolyForm Noncommercial 1.0.0** (decided 2026-11-06, [LICENSE](../LICENSE)) | free for non-commercial use, commercial use only with consent; in `Cargo.toml` `license = "PolyForm-Noncommercial-1.0.0"`; dependencies (MIT/Apache-2.0) are compatible with it. Free licences (MIT, CERN-OHL) remain rejected because they allow commercial use without consent |
| E13 | Sending to WebSockets | **Own send path** (5.4): one `httpd_queue_work` per tick, `MSG_DONTWAIT` per session, acknowledgement with sequence number, > 2 frames behind → pause, 15 s silent → close, TCP keepalive | `EspHttpWsDetachedSender::send()` blocks httpd and hub for up to 5 s per frame and can deadlock in httpd context (verified, source code) |
| E14 | Where does which work run? | **Actor only for state changes** via request + reply channel with timeout; JSON, PBKDF2, validation, file I/O beforehand in the httpd task or in the `worker` (4.2) | the 50 ms tick and the motor setpoint must never wait for expensive work |
| E15 | Restart after an unexpected reset | **No start without a lever edge open → closed**; restart counter in RTC; locked from 3 in 60 s; motor locked while a new image is unconfirmed (4.1, 7) | prevents surprise starts and brownout loops; otherwise a brownout right after an update discards a good firmware |
| E16 | `louie-proto` as a separate crate or as a feature in `louie-core`? | **Separate crate**; mode types in `louie-core` | REST bodies, `Config`, `ts-rs` do not belong in the core and WASM; one more crate costs hardly anything (2.1) |
| E17 | Hotspot password | **Random at first start**, in NVS, output for the sticker; reset via workshop or factory reset | derived from the MAC it could be computed by anyone in radio range; previously planned that way in software-concept.md 3.2 (decision-history.md 8) |
| E18 | Where do game flows live and who executes them? | **Core executes, catalog in the core.** Programs are JSON from `fw`, UI package and LittleFS; selection by reference with hash; `current.json`; offline selection; UI package separately updatable from stage 2 (6.4) | same core for different UIs and games without losing offline play, permissions and timing; flows in the browser fail on throttled tabs and several phones; previously "built-in modes in the firmware" (decision-history.md 8) |

## 13. Risks and fallbacks

| Risk | Likelihood | Fallback |
|---|---|---|
| App with embedded files > 1.8 MiB → no OTA on N4 | **high** (unverified, 1.6–2.0 MB estimated) | Assemble H8; on N4 `www` partition (6.1) or without OTA; BLE logs off, `opt-level = "z"` |
| Hanging WS client blocks httpd and hub | **high without countermeasure** (verified, source code) | own send path with `MSG_DONTWAIT` and acknowledgements (5.4); fallback shorter `send_wait_timeout` via `esp-idf-sys` or own WS server on raw sockets |
| `lru_purge` cuts silently listening clients | medium (verified: counter only on receive) | acknowledgement every 5 s, 14–16 slots (5.1) |
| IDF ≥ 5.5.5 / 6.0.1: WS handler no longer called during handshake (`is_new()` never true) | certain with these versions (verified) | do not rely on `is_new()`; create the client only with its first message (5.2); origin check optionally via pre-handshake callback |
| RAM: lwIP buffers with many connections | medium | backpressure, smaller `TCP_SND_BUF`/`TCP_WND`, fewer sessions, limits from 6.3 as test criterion |
| Heap fragmentation during long operation | low–medium | reusable buffers, one `Arc<str>` for all, heap diagnostics in the HIL endurance run |
| Thread with too small a stack (std default 3 KB) | medium | `Builder::stack_size` everywhere, HW stack guard, high-water mark in diagnostics (4.3) |
| C panic or core dump: motor runs with the last duty cycle until reset | low–medium | second dead-man timer, `--wrap=esp_panic_handler` (unverified), core dump not to flash; measure in HIL |
| Reset state IO18/IO19: **brake** instead of coast during reset (internal 45 k pull-up against 200 k in the DRV8213, verified) | certain, minor consequences | no drive possible (both inputs equal). Correct the docs; if coast during reset is wanted: external pull-downs ≤ 4.7 k on IN1/IN2 (hardware, not decided) |
| UI package and firmware drift apart (stage 2) | medium | manifest ranges for `proto`/`schema`/`requires`, per-mode validation, fallback UI, CI check against all firmware versions in the range (6.4, 8) |
| Flash writes stall motor thread and Wi-Fi | medium | do not write during a round, measure jitter (6.2) |
| esp-idf-svc NimBLE wrapper (new in 0.53) immature | medium | esp32-nimble 0.13, then `esp-idf-sys` (`ble_gap_disc`, about 100 lines of FFI) |
| BLE scan + SoftAP with 8 clients unstable (C1) | medium | scan only when needed, small scan window; offer buttons only in STA mode; state rate in hotspot mode 5/s |
| Captive portal behaviour differs per phone | medium | answer probe URLs with "success" after the first request, option 114, hint "open in browser" in the portal window |
| esp-idf-* crates before 1.0, community-maintained | certain | pin versions (`Cargo.lock`, dated nightly), missing parts directly via `esp-idf-sys` (whole IDF C API available) |
| A part does not work in Rust at all (e.g. Zigbee SDK) | low | include it as an ESP-IDF component in C and call it via FFI; conversely the core as `staticlib` in a C++ firmware |
| Long build cycles slow things down | medium | logic in the simulator, ESP only for HAL/network, `dev` without LTO, `sccache` |
| WASM too large for the editor | low | `serde-wasm-bindgen`, `wasm-opt -Oz`, loading only in the editor |

Pure `no_std` (esp-hal + esp-radio + Embassy) will be re-evaluated when esp-radio 1.0 is released and
coexistence is stable. The switch would only affect `louie-fw`; core, app, protocol and web UI stay.

## Sources

- esp-idf-svc changelog (0.53.0: ESP-IDF 6.0, NimBLE wrapper GAP/GATT/L2CAP, HTTP `keep_alive`/`so_linger`;
  0.52.0 of 2026-03-09: `ws_handler` subprotocols): https://github.com/esp-rs/esp-idf-svc/blob/master/CHANGELOG.md ;
  versions (0.53.0 published on crates.io on 2026-09-15, the changelog says 2026-09-25):
  https://crates.io/crates/esp-idf-svc
- esp-idf-svc HTTP server source code (detached sender with `httpd_queue_work` + condvar, `send_wait_timeout: 5`,
  `lru_purge_enable` default, `EspHttpWsConnection::New` only on GET):
  https://github.com/esp-rs/esp-idf-svc/blob/v0.53.0/src/http/server.rs ; docs detached sender:
  https://docs.esp-rs.org/esp-idf-svc/esp_idf_svc/http/server/ws/struct.EspHttpWsDetachedSender.html
- ESP-IDF `esp_http_server` 5.5 (LRU counter only on receive in `httpd_sess.c`, `SO_SNDTIMEO` in `httpd_main.c`,
  handshake in `httpd_uri.c`, `httpd_sess_set_send_override`, `httpd_sess_trigger_close`, pre-/post-handshake
  callback in Kconfig): https://github.com/espressif/esp-idf/tree/release/v5.5/components/esp_http_server ;
  comparison of tags v5.5.4/v5.5.5/v6.0/v6.0.1 (`httpd_uri.c`)
- ESP-IDF HTTP server (`max_open_sockets`, 3 internal): https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-reference/protocols/esp_http_server.html
- ESP-IDF Kconfig 5.5: `components/esp_system/Kconfig` (`ESP_TASK_WDT_PANIC` default n, `ESP_TASK_WDT_TIMEOUT_S`
  default 5, `ESP_SYSTEM_HW_STACK_GUARD` default y), `components/pthread/Kconfig`
  (`PTHREAD_TASK_STACK_SIZE_DEFAULT` 3072), `components/lwip/Kconfig` (`LWIP_MAX_SOCKETS` 10,
  `LWIP_MAX_ACTIVE_TCP` 16, `TCP_SND_BUF`/`TCP_WND` 5760, `LWIP_DHCPS_MAX_STATION_NUM` 8),
  `components/bootloader/Kconfig.projbuild` (`SECURE_SIGNED_APPS_NO_SECURE_BOOT`): https://github.com/espressif/esp-idf/tree/release/v5.5/components
- ESP-IDF `pthread.c` (configuration thread-local, attributes override stack size):
  https://github.com/espressif/esp-idf/blob/release/v5.5/components/pthread/pthread.c
- Rust std, thread stack on espidf (`DEFAULT_MIN_STACK_SIZE = 0` → IDF default):
  https://github.com/rust-lang/rust/blob/master/library/std/src/sys/thread/unix.rs
- ESP-IDF OTA, rollback states: https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32c6/api-reference/system/ota.html
- ESP-IDF Wi-Fi guide 5.5 (modem sleep STA only, "AP Sleep"): https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32c6/api-guides/wifi.html
- ESP-IDF DHCP option 114 (`ESP_NETIF_CAPTIVEPORTAL_URI`) and example `captive_portal`:
  https://github.com/espressif/esp-idf/tree/release/v5.5/examples/protocols/http_server/captive_portal
- ESP-IDF support policy (30 months per minor version): https://github.com/espressif/esp-idf/blob/master/SUPPORT_POLICY.md
- ESP32-C6 Series Datasheet v1.5 (tab. 2-1/2-2 pin states during and after reset, R_PU 45 kΩ, tab. 3-1):
  https://documentation.espressif.com/esp32-c6_datasheet_en.pdf
- TI DRV8213 datasheet (tab. 8-2 truth table, R_PD 200 kΩ, V_IH 1.45 V, t_WAKE 250 µs):
  https://www.ti.com/lit/ds/symlink/drv8213.pdf
- esp-idf-svc OTA (`EspOta`, rollback): https://docs.rs/crate/esp-idf-svc/latest/source/src/ota.rs
- esp-idf-svc LittleFS (`MountedLittlefs`): https://docs.rs/crate/esp-idf-svc/latest/source/src/fs/littlefs.rs ;
  component: https://components.espressif.com/components/joltwallet/littlefs
- esp-idf-svc mDNS: https://docs.rs/crate/esp-idf-svc/latest/source/src/mdns.rs ; component
  https://components.espressif.com/components/espressif/mdns
- esp-idf-sys build options (`extra_components`, `remote_component`):
  https://github.com/esp-rs/esp-idf-sys/blob/master/BUILD-OPTIONS.md
- esp-idf-template (prerequisites, RISC-V without espup, IDF v5.3–v6.1 selectable):
  https://github.com/esp-rs/esp-idf-template
- rustc platform page ESP-IDF (`riscv32imac-esp-espidf`, tier 3, C6 from IDF 5.1, build-std):
  https://doc.rust-lang.org/rustc/platform-support/esp-idf.html
- esp32-nimble (0.13.0 of 2026-09-18, dependency `esp-idf-svc ^0.53.0`; CI builds C6 only with IDF 5.3.6, C3/ESP32
  also with 5.4.4/5.5.5): https://github.com/taks/esp32-nimble , https://crates.io/crates/esp32-nimble
- edge-captive 0.8.0 (std feature): https://crates.io/crates/edge-captive
- ESP-IDF coexistence C6: https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/api-guides/coexist.html
- ESP-IDF minimizing binary size: https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32c6/api-guides/performance/size.html
- ESP-Techpedia RAM usage: https://docs.espressif.com/projects/esp-techpedia/en/latest/esp-friends/advanced-development/system/ram-usage.html
- XIAO ESP32-C6 (RF switch IO3/IO14, 4 MB): https://wiki.seeedstudio.com/xiao_wifi_usage_esp32c6/ ,
  https://wiki.seeedstudio.com/xiao_esp32c6_getting_started
- ESP32-C6-DevKitC-1 (N8, RGB LED IO8): https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32c6/esp32-c6-devkitc-1/user_guide_v1.1.html
- Rust WASM code size: https://rustwasm.github.io/book/reference/code-size.html ; dissolution of the rustwasm organization:
  https://blog.rust-lang.org/inside-rust/2025/07/21/sunsetting-the-rustwasm-github-org
- ESP-IDF 6.0 (March 2026): https://www.espressif.com/en/news/ESP_IDF_6.0
