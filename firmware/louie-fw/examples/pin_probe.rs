//! Pre-order check 4.4 (docs/test-hardware.md, F17): level of IO18/IO19 (DRV8213 IN1/IN2) during reset, boot and
//! deep sleep. Wiring: LEDs removed, 200 k from IO18 and IO19 to GND each (DRV8213 input pull-down), scope on the pins.
//!
//! The first thing in `main` drives both pins LOW and releases a hold from a previous sleep. The logged time is
//! only the app part (esp_timer starts after ROM and bootloader); the full HIGH window comes from the scope,
//! triggered on EN rising.

use core::sync::atomic::Ordering;

use louie_fw::board::BOARD;
use louie_fw::console;
use louie_fw::diag::{self, RTC_COUNTER, RTC_MODE};
use louie_fw::hw;
use louie_fw::sleep::{self, Wake};

const SLEEP_MS: u64 = 10_000;
const MODE_CYCLE_HOLD: u32 = 1;
const CYCLES: u32 = 10;

fn sleep_with(hold: bool) -> anyhow::Result<()> {
    let p = &BOARD.pins;
    for pin in [p.motor_in1, p.motor_in2] {
        hw::set(pin, false);
        hw::hold(pin, hold)?;
    }
    log::info!(
        "IO18/IO19 LOW, hold {} → measure IO18, IO19 (and SENSE with the lever closed) now",
        if hold { "ON" } else { "OFF" }
    );
    sleep::deep_sleep(&Wake { timer_ms: Some(SLEEP_MS), ..Default::default() })?;
    Ok(())
}

fn main() -> anyhow::Result<()> {
    let p = &BOARD.pins;
    // before logger and banner: every µs counts
    for pin in [p.motor_in1, p.motor_in2] {
        hw::output(pin, false)?;
        hw::hold(pin, false)?;
    }
    let driven_us = diag::uptime_us();

    louie_fw::init("pin_probe (test-hardware.md 4.4, F17)");
    log::info!(
        "IO18/IO19 driven LOW {driven_us} µs after esp_timer start (app part only, scope gives the full window)"
    );

    if RTC_MODE.load(Ordering::Relaxed) == MODE_CYCLE_HOLD {
        let n = RTC_COUNTER.fetch_add(1, Ordering::Relaxed) + 1;
        log::info!(">>> sleep cycle {n} / {CYCLES} with hold done");
        if n < CYCLES && console::wait_key(1000) != Some(b'x') {
            sleep_with(true)?;
        }
        RTC_MODE.store(0, Ordering::Relaxed);
        log::info!("cycle finished after {n} sleeps");
    }

    console::menu(&[
        ("w", "case b: deep sleep 10 s WITHOUT hold"),
        ("h", "case c: deep sleep 10 s WITH gpio_hold_en LOW"),
        ("n", "case c × 10 in a row (check the level after 10 cycles)"),
        ("r", "case a: software reset (esp_restart)"),
        ("p", "case a: panic"),
        ("d", "case a: interrupt watchdog reset"),
    ]);
    loop {
        match console::poll_key() {
            Some(b'w') => sleep_with(false)?,
            Some(b'h') => sleep_with(true)?,
            Some(b'n') => {
                RTC_MODE.store(MODE_CYCLE_HOLD, Ordering::Relaxed);
                RTC_COUNTER.store(0, Ordering::Relaxed);
                sleep_with(true)?;
            }
            Some(b'r') => unsafe { esp_idf_svc::sys::esp_restart() },
            Some(b'p') => panic!("deliberate panic (pin_probe case a)"),
            Some(b'd') => {
                log::info!("spinning with interrupts off → interrupt watchdog");
                esp_idf_svc::hal::interrupt::free(|| loop {
                    core::hint::spin_loop();
                });
            }
            _ => {}
        }
        std::thread::sleep(std::time::Duration::from_millis(20));
    }
}
