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
        resume_cycle(sense, mode)?;
    }

    console::menu(&[
        ("c", "auto cycle: sleep, count wake-ups on lever close (closed at sleep → wake on LOW)"),
        ("t", "auto cycle as 'c', but closed at sleep → timer 5 s"),
        ("s", "sleep once (ANY_HIGH, or LOW if closed)"),
        ("z", "reset counters"),
    ]);
    log::info!("logging IO3 edges every 10 ms; lever {}", level_name(hw::level(sense)));

    let mut edges = Edges::new(hw::level(sense));
    loop {
        edges.poll(hw::level(sense));
        if let Some(k) = console::poll_key() {
            on_key(k, sense, &mut edges)?;
        }
        std::thread::sleep(std::time::Duration::from_millis(10));
    }
}

/// Woken from the auto cycle: count a lever wake, then stop on 'x' or go back to sleep.
fn resume_cycle(sense: i32, mode: u32) -> anyhow::Result<()> {
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
        return Ok(());
    }
    wait_lever_open(sense);
    sleep_for_lever(sense, mode)
}

/// Wait up to 3 s for the lever to open, otherwise the special case "closed at sleep" is tested.
fn wait_lever_open(sense: i32) {
    for _ in 0..300 {
        if !hw::level(sense) {
            break;
        }
        std::thread::sleep(std::time::Duration::from_millis(10));
    }
}

/// IO3 edge log: level, time of the last edge, number of closings.
struct Edges {
    last: bool,
    last_ms: u32,
    closings: u32,
}

impl Edges {
    fn new(level: bool) -> Self {
        Self { last: level, last_ms: diag::uptime_ms(), closings: 0 }
    }

    fn poll(&mut self, level: bool) {
        if level == self.last {
            return;
        }
        let now = diag::uptime_ms();
        if level {
            self.closings += 1;
        }
        log::info!("IO3 {} after {} ms · closings {}", level_name(level), now - self.last_ms, self.closings);
        self.last = level;
        self.last_ms = now;
    }
}

fn on_key(key: u8, sense: i32, edges: &mut Edges) -> anyhow::Result<()> {
    match key {
        b'c' | b't' => {
            let m = if key == b't' { MODE_CYCLE_TIMER } else { MODE_CYCLE_LOW };
            RTC_MODE.store(m, Ordering::Relaxed);
            RTC_COUNTER.store(0, Ordering::Relaxed);
            log::info!("auto cycle started: toggle the lever 20 ×, the count appears after every wake");
            sleep_for_lever(sense, m)?;
        }
        b's' => sleep_for_lever(sense, MODE_CYCLE_LOW)?,
        b'z' => {
            edges.closings = 0;
            RTC_COUNTER.store(0, Ordering::Relaxed);
            log::info!("counters reset");
        }
        _ => {}
    }
    Ok(())
}

fn level_name(closed: bool) -> &'static str {
    if closed {
        "HIGH (closed)"
    } else {
        "LOW (open)"
    }
}
