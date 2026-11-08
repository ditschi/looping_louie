//! Reset reason, wake cause, boot counter in RTC memory, heap figures.

use core::sync::atomic::{AtomicU32, Ordering};

use esp_idf_svc::sys;

use crate::board::BOARD;

/// Boots since the last reset that was not a deep-sleep wake. `.rtc.data` (LP memory) keeps its value through deep
/// sleep; the bootloader re-initialises it on every other reset (power-on, software, panic, watchdog).
#[link_section = ".rtc.data"]
static BOOT_COUNT: AtomicU32 = AtomicU32::new(0);

/// Free counter for the probes (e.g. wake-ups in a sleep cycle). Same lifetime as `BOOT_COUNT`.
#[link_section = ".rtc.data"]
pub static RTC_COUNTER: AtomicU32 = AtomicU32::new(0);

/// Mode flag for the probes that must survive deep sleep (0 = none).
#[link_section = ".rtc.data"]
pub static RTC_MODE: AtomicU32 = AtomicU32::new(0);

pub fn reset_reason() -> sys::esp_reset_reason_t {
    unsafe { sys::esp_reset_reason() }
}

pub fn reset_reason_name(r: sys::esp_reset_reason_t) -> &'static str {
    #[allow(non_upper_case_globals)]
    match r {
        sys::esp_reset_reason_t_ESP_RST_POWERON => "power-on",
        sys::esp_reset_reason_t_ESP_RST_EXT => "external pin",
        sys::esp_reset_reason_t_ESP_RST_SW => "software (esp_restart)",
        sys::esp_reset_reason_t_ESP_RST_PANIC => "panic/abort",
        sys::esp_reset_reason_t_ESP_RST_INT_WDT => "interrupt watchdog",
        sys::esp_reset_reason_t_ESP_RST_TASK_WDT => "task watchdog",
        sys::esp_reset_reason_t_ESP_RST_WDT => "other watchdog",
        sys::esp_reset_reason_t_ESP_RST_DEEPSLEEP => "deep-sleep wake",
        sys::esp_reset_reason_t_ESP_RST_BROWNOUT => "brownout",
        sys::esp_reset_reason_t_ESP_RST_SDIO => "SDIO",
        // USB (11), JTAG (12), eFuse (13), power glitch (14), CPU lockup (15) in ESP-IDF 5.x
        _ => "other",
    }
}

/// Reset that the motor must not follow with a start (docs/firmware-architecture.md E15).
pub fn is_unexpected_reset() -> bool {
    !matches!(
        reset_reason(),
        sys::esp_reset_reason_t_ESP_RST_POWERON
            | sys::esp_reset_reason_t_ESP_RST_DEEPSLEEP
            | sys::esp_reset_reason_t_ESP_RST_SW
    )
}

pub fn wake_cause() -> sys::esp_sleep_wakeup_cause_t {
    unsafe { sys::esp_sleep_get_wakeup_cause() }
}

pub fn wake_cause_name(c: sys::esp_sleep_wakeup_cause_t) -> &'static str {
    #[allow(non_upper_case_globals)]
    match c {
        sys::esp_sleep_source_t_ESP_SLEEP_WAKEUP_UNDEFINED => "none (not a deep-sleep wake)",
        sys::esp_sleep_source_t_ESP_SLEEP_WAKEUP_EXT1 => "ext1 (GPIO level)",
        sys::esp_sleep_source_t_ESP_SLEEP_WAKEUP_TIMER => "timer",
        sys::esp_sleep_source_t_ESP_SLEEP_WAKEUP_GPIO => "GPIO",
        _ => "other",
    }
}

/// GPIOs that triggered the ext1 wake (bit n = GPIOn).
pub fn ext1_status() -> u64 {
    unsafe { sys::esp_sleep_get_ext1_wakeup_status() }
}

/// GPIO numbers set in a bit mask, as text ("IO3 IO5").
pub fn mask_pins(mask: u64) -> String {
    let pins: Vec<String> = (0..64).filter(|n| mask & (1u64 << n) != 0).map(|n| format!("IO{n}")).collect();
    if pins.is_empty() {
        "-".into()
    } else {
        pins.join(" ")
    }
}

pub fn uptime_us() -> i64 {
    unsafe { sys::esp_timer_get_time() }
}

pub fn uptime_ms() -> u32 {
    (uptime_us() / 1000) as u32
}

pub fn boot_count() -> u32 {
    BOOT_COUNT.load(Ordering::Relaxed)
}

pub struct Heap {
    pub free: u32,
    pub min_free: u32,
    pub largest_block: u32,
}

pub fn heap() -> Heap {
    unsafe {
        Heap {
            free: sys::esp_get_free_heap_size(),
            min_free: sys::esp_get_minimum_free_heap_size(),
            largest_block: sys::heap_caps_get_largest_free_block(sys::MALLOC_CAP_8BIT) as u32,
        }
    }
}

/// Log a block with firmware, board, reset reason, wake cause and heap. Counts the boot.
pub fn banner(name: &str) {
    let boots = BOOT_COUNT.fetch_add(1, Ordering::Relaxed) + 1;
    let rr = reset_reason();
    let wc = wake_cause();
    let h = heap();
    log::info!("==== {name} v{} · board {} ====", env!("CARGO_PKG_VERSION"), BOARD.name);
    log::info!("reset reason: {} ({rr}) · boot #{boots} in this deep-sleep chain", reset_reason_name(rr));
    if wc == sys::esp_sleep_source_t_ESP_SLEEP_WAKEUP_EXT1 {
        log::info!("wake cause: {} by {}", wake_cause_name(wc), mask_pins(ext1_status()));
    } else {
        log::info!("wake cause: {}", wake_cause_name(wc));
    }
    log::info!(
        "uptime at banner: {} ms · heap free {} B, min {} B, largest block {} B",
        uptime_ms(),
        h.free,
        h.min_free,
        h.largest_block
    );
}
