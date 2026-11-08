//! Pre-order check 4.3 (docs/test-hardware.md): boot and strapping with the board's external parts, deep-sleep
//! wake on IO3 / IO2 / IO4 / IO5.
//!
//! At every start it logs reset reason, wake cause and the levels of the strapping and wake pins. The ROM log on
//! the CH343 port additionally shows the boot mode (`boot:0x..`), e.g. for cases 2, 4 and 5.
//! Wake cases 7–10 repeat automatically (sleep again 2 s after each wake) until 'x' is pressed.

use core::sync::atomic::Ordering;

use louie_fw::board::BOARD;
use louie_fw::console;
use louie_fw::diag::{self, RTC_COUNTER, RTC_MODE};
use louie_fw::hw::{self, Pull};
use louie_fw::sleep::{self, Wake};

/// Case numbers as in the table of test-hardware.md 4.3 (0 = none)
fn wake_for_case(case: u32) -> Option<Wake> {
    let p = &BOARD.pins;
    let s1 = p.buttons[0].expect("S1");
    Some(match case {
        7 => Wake { high: vec![p.sense], ..Default::default() },
        8 => Wake { high: vec![p.accel_int], ..Default::default() },
        9 => Wake { high: vec![p.vbus_det], ..Default::default() },
        // mixed levels: S1 LOW together with the HIGH sources (per-pin ext1 level on the C6)
        10 => Wake { high: vec![p.sense, p.accel_int, p.vbus_det], low_pullup: vec![s1], ..Default::default() },
        _ => return None,
    })
}

fn log_levels() {
    let p = &BOARD.pins;
    let s1 = p.buttons[0].expect("S1");
    log::info!(
        "levels: IO2 INT {} · IO3 SENSE {} · IO4 VBUS {} · IO5 S1 {} · IO8 S4/RGB {} · IO9 BOOT {} · IO15 {}",
        bit(p.accel_int),
        bit(p.sense),
        bit(p.vbus_det),
        bit(s1),
        bit(8),
        bit(p.boot_button),
        bit(p.led_chain_enable)
    );
}

fn bit(pin: i32) -> u8 {
    hw::level(pin) as u8
}

fn main() -> anyhow::Result<()> {
    louie_fw::init("boot_probe (test-hardware.md 4.3)");
    let p = &BOARD.pins;
    let s1 = p.buttons[0].expect("S1");
    // external pull-downs (R22, VBUS divider, 100 k on SENSE/INT) → no internal pulls; buttons → pull-up;
    // IO8 has its own 10 k pull-up on the dev board and the board
    for pin in [p.accel_int, p.sense, p.vbus_det, p.led_chain_enable, 8] {
        hw::input(pin, Pull::None)?;
    }
    for pin in [s1, p.boot_button] {
        hw::input(pin, Pull::Up)?;
    }
    log_levels();

    let case = RTC_MODE.load(Ordering::Relaxed);
    if let Some(wake) = wake_for_case(case) {
        if diag::wake_cause() == esp_idf_svc::sys::esp_sleep_source_t_ESP_SLEEP_WAKEUP_EXT1 {
            let n = RTC_COUNTER.fetch_add(1, Ordering::Relaxed) + 1;
            log::info!(">>> case {case}: wake #{n} by {}", diag::mask_pins(diag::ext1_status()));
        } else {
            log::warn!(">>> case {case}: start without ext1 wake ({})", diag::wake_cause_name(diag::wake_cause()));
        }
        log::info!("release the wake source; sleeping again in 2 s, 'x' stops");
        if console::wait_key(2000) == Some(b'x') {
            RTC_MODE.store(0, Ordering::Relaxed);
            log::info!("case {case} stopped after {} wake-ups", RTC_COUNTER.load(Ordering::Relaxed));
        } else {
            sleep::deep_sleep(&wake)?;
        }
    }

    console::menu(&[
        ("7", "case 7: deep sleep, wake on IO3 HIGH (lever)"),
        ("8", "case 8: deep sleep, wake on IO2 HIGH (INT button)"),
        ("9", "case 9: deep sleep, wake on IO4 HIGH (VBUS 0 → 5 V)"),
        ("a", "case 10: deep sleep, wake on IO2/IO3/IO4 HIGH or IO5 LOW (S1)"),
        ("l", "live levels on/off (case 11: IO4 at 4.75 / 5.0 / 5.25 V)"),
        ("r", "software restart"),
    ]);

    let mut live = false;
    let mut last = String::new();
    loop {
        match console::poll_key() {
            Some(k @ (b'7' | b'8' | b'9' | b'a')) => {
                let case = if k == b'a' { 10 } else { (k - b'0') as u32 };
                RTC_MODE.store(case, Ordering::Relaxed);
                RTC_COUNTER.store(0, Ordering::Relaxed);
                sleep::deep_sleep(&wake_for_case(case).expect("case"))?;
            }
            Some(b'l') => {
                live = !live;
                last.clear();
            }
            Some(b'r') => unsafe { esp_idf_svc::sys::esp_restart() },
            _ => {}
        }
        if live {
            let now: String = [p.accel_int, p.sense, p.vbus_det, s1, 8, p.boot_button, p.led_chain_enable]
                .iter()
                .map(|&pin| char::from(b'0' + bit(pin)))
                .collect();
            if now != last {
                log_levels();
                last = now;
            }
        }
        std::thread::sleep(std::time::Duration::from_millis(20));
    }
}
