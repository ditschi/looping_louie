//! Deep sleep with ext1 wake per pin level (C6: SOC_PM_SUPPORT_EXT1_WAKEUP_MODE_PER_PIN) and optional timer.
//!
//! ext1 works only on the LP GPIOs IO0–IO7 (SOC_GPIO_DEEP_SLEEP_WAKE_VALID_GPIO_MASK). Deep sleep is a restart:
//! after the wake the program starts again at `main`.

use std::io::Write;

use esp_idf_svc::sys::{self, esp, EspError};

use crate::board::Gpio;

#[derive(Default)]
pub struct Wake {
    /// Wake when one of these pins is HIGH (external pull-down, e.g. SENSE, INT, VBUS_DET)
    pub high: Vec<Gpio>,
    /// Wake when one of these pins is LOW, external circuit only (e.g. SENSE with the lever closed)
    pub low: Vec<Gpio>,
    /// Wake when one of these pins is LOW, internal LP pull-up on (button to GND)
    pub low_pullup: Vec<Gpio>,
    pub timer_ms: Option<u64>,
}

fn mask(pins: &[Gpio]) -> u64 {
    pins.iter().fold(0, |m, &p| m | (1u64 << p))
}

/// Configure the wake sources and enter deep sleep. Returns only on a configuration error.
pub fn deep_sleep(wake: &Wake) -> Result<(), EspError> {
    let high = mask(&wake.high);
    let low = mask(&wake.low) | mask(&wake.low_pullup);
    if high | low != 0 {
        esp!(unsafe { sys::esp_sleep_enable_ext1_wakeup_with_level_mask(high | low, high) })?;
    }
    // Levels during sleep come from the LP IO (RTC IO) pulls. Pins with an external circuit keep the internal
    // pulls off, so that the measurement sees the board circuit only.
    for &p in wake.high.iter().chain(&wake.low) {
        esp!(unsafe { sys::rtc_gpio_pullup_dis(p) })?;
        esp!(unsafe { sys::rtc_gpio_pulldown_dis(p) })?;
    }
    for &p in &wake.low_pullup {
        esp!(unsafe { sys::rtc_gpio_pulldown_dis(p) })?;
        esp!(unsafe { sys::rtc_gpio_pullup_en(p) })?;
    }
    if !wake.low_pullup.is_empty() {
        // keep the LP IO pulls powered (unverified whether the C6 needs this, see ESP-IDF example ext_wakeup)
        esp!(unsafe {
            sys::esp_sleep_pd_config(
                sys::esp_sleep_pd_domain_t_ESP_PD_DOMAIN_RTC_PERIPH,
                sys::esp_sleep_pd_option_t_ESP_PD_OPTION_ON,
            )
        })?;
    }
    if let Some(ms) = wake.timer_ms {
        esp!(unsafe { sys::esp_sleep_enable_timer_wakeup(ms * 1000) })?;
    }
    log::info!(
        "deep sleep: wake on HIGH {} / LOW {} / timer {}",
        crate::diag::mask_pins(high),
        crate::diag::mask_pins(low),
        wake.timer_ms.map_or("-".to_string(), |ms| format!("{ms} ms"))
    );
    let _ = std::io::stdout().flush();
    // let the UART FIFO drain
    std::thread::sleep(std::time::Duration::from_millis(50));
    unsafe { sys::esp_deep_sleep_start() }
}
