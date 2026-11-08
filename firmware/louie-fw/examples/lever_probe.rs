//! Pre-order check 4.2 (docs/test-hardware.md): lever network R3/R4/R5 on the real Louie, edges and deep-sleep wake
//! on SENSE (IO3).
//!
//! IO3 runs WITHOUT internal pull-up/pull-down: a 45 k pull-up would read HIGH with the lever open.
//! Auto cycle (key 'c'): sleep → lever closes → wake (counted) → wait until the lever opens → sleep again.
//! If the lever is still closed when going to sleep (special case, main-board-c6.md 2.5), the fallback chosen
//! with 'c' (wake on LOW) or 't' (timer every 5 s) applies.

use core::sync::atomic::Ordering;

use louie_fw::board::BOARD;
use louie_fw::console;
use louie_fw::diag::{self, RTC_COUNTER, RTC_MODE};
use louie_fw::hw::{self, Pull};
use louie_fw::sleep::{self, Wake};

const MODE_NONE: u32 = 0;
/// auto cycle, lever closed at sleep → wake on LOW
const MODE_CYCLE_LOW: u32 = 1;
/// auto cycle, lever closed at sleep → timer 5 s
const MODE_CYCLE_TIMER: u32 = 2;
const TIMER_FALLBACK_MS: u64 = 5000;

fn sleep_for_lever(sense: i32, mode: u32) -> anyhow::Result<()> {
    let closed = hw::level(sense);
    let wake = if !closed {
        Wake { high: vec![sense], ..Default::default() }
    } else if mode == MODE_CYCLE_TIMER {
        log::info!("lever closed when going to sleep: timer fallback {TIMER_FALLBACK_MS} ms");
        Wake { timer_ms: Some(TIMER_FALLBACK_MS), ..Default::default() }
    } else {
        log::info!("lever closed when going to sleep: wake on LOW (lever opens)");
        Wake { low: vec![sense], ..Default::default() }
    };
    sleep::deep_sleep(&wake)?;
    Ok(())
}

fn main() -> anyhow::Result<()> {
    louie_fw::init("lever_probe (test-hardware.md 4.2)");
    let sense = BOARD.pins.sense;
    hw::input(sense, Pull::None)?;

    let mode = RTC_MODE.load(Ordering::Relaxed);
    if mode != MODE_NONE {
        let cause = diag::wake_cause();
        if cause == esp_idf_svc::sys::esp_sleep_source_t_ESP_SLEEP_WAKEUP_EXT1 && hw::level(sense) {
            let n = RTC_COUNTER.fetch_add(1, Ordering::Relaxed) + 1;
            log::info!(">>> wake #{n} by lever closed (IO3 HIGH)");
        } else {
            log::info!(">>> wake by {} · lever {}", diag::wake_cause_name(cause), level_name(hw::level(sense)));
        }
        log::info!("auto cycle running: 'x' within 2 s stops it");
        if console::wait_key(2000) == Some(b'x') {
            RTC_MODE.store(MODE_NONE, Ordering::Relaxed);
            log::info!("auto cycle stopped after {} wake-ups", RTC_COUNTER.load(Ordering::Relaxed));
        } else {
            // wait up to 3 s for the lever to open, otherwise test the special case "closed at sleep"
            for _ in 0..300 {
                if !hw::level(sense) {
                    break;
                }
                std::thread::sleep(std::time::Duration::from_millis(10));
            }
            sleep_for_lever(sense, mode)?;
        }
    }

    console::menu(&[
        ("c", "auto cycle: sleep, count wake-ups on lever close (closed at sleep → wake on LOW)"),
        ("t", "auto cycle as 'c', but closed at sleep → timer 5 s"),
        ("s", "sleep once (ANY_HIGH, or LOW if closed)"),
        ("z", "reset counters"),
    ]);
    log::info!("logging IO3 edges every 10 ms; lever {}", level_name(hw::level(sense)));

    let mut last = hw::level(sense);
    let mut last_ms = diag::uptime_ms();
    let mut closings: u32 = 0;
    loop {
        let now_level = hw::level(sense);
        if now_level != last {
            let now = diag::uptime_ms();
            if now_level {
                closings += 1;
            }
            log::info!("IO3 {} after {} ms · closings {closings}", level_name(now_level), now - last_ms);
            last = now_level;
            last_ms = now;
        }
        match console::poll_key() {
            Some(k @ (b'c' | b't')) => {
                let m = if k == b't' { MODE_CYCLE_TIMER } else { MODE_CYCLE_LOW };
                RTC_MODE.store(m, Ordering::Relaxed);
                RTC_COUNTER.store(0, Ordering::Relaxed);
                log::info!("auto cycle started: toggle the lever 20 ×, the count appears after every wake");
                sleep_for_lever(sense, m)?;
            }
            Some(b's') => sleep_for_lever(sense, MODE_CYCLE_LOW)?,
            Some(b'z') => {
                closings = 0;
                RTC_COUNTER.store(0, Ordering::Relaxed);
                log::info!("counters reset");
            }
            _ => {}
        }
        std::thread::sleep(std::time::Duration::from_millis(10));
    }
}

fn level_name(closed: bool) -> &'static str {
    if closed {
        "HIGH (closed)"
    } else {
        "LOW (open)"
    }
}
