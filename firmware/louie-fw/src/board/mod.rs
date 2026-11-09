//! Board definitions (docs/firmware-architecture.md 3.1). Pin numbers live only here.
//!
//! Exactly one board feature is active. Boards differ in pins for the same function, so a wrong guess at
//! runtime could drive an output against another one.

#[cfg(all(feature = "board-devkitc-c6", feature = "board-louie-v1"))]
compile_error!("enable exactly one board feature (board-devkitc-c6 or board-louie-v1)");
#[cfg(not(any(feature = "board-devkitc-c6", feature = "board-louie-v1")))]
compile_error!("enable one board feature (board-devkitc-c6 or board-louie-v1)");

#[cfg(feature = "board-devkitc-c6")]
mod devkitc_c6;
#[cfg(feature = "board-devkitc-c6")]
pub use devkitc_c6::BOARD;

#[cfg(feature = "board-louie-v1")]
mod louie_v1;
#[cfg(feature = "board-louie-v1")]
pub use louie_v1::BOARD;

/// GPIO number as used by ESP-IDF (`gpio_num_t`).
pub type Gpio = i32;

/// Pin per function. Numbers as on the board (docs/main-board-c6.md 2.3); the dev board differs only where noted.
pub struct Pins {
    /// VBAT_ADC: VSYS divider (main board 680 k / 470 k) + 100 nF (ADC1_CH0)
    pub vsys_adc: Gpio,
    /// ISEN_ADC: DRV8213 IPROPI via RC (ADC1_CH1)
    pub isen_adc: Gpio,
    /// INT from the LIS2DH12 (J2), LP GPIO, deep-sleep wake
    pub accel_int: Gpio,
    /// SENSE: lever, HIGH = closed, LP GPIO, deep-sleep wake
    pub sense: Gpio,
    /// VBUS_DET: VBUS divider (board) or switch (dev board), LP GPIO, deep-sleep wake
    pub vbus_det: Gpio,
    /// Player inputs S1–S4 (J6), button to GND, internal pull-up. `None` = not usable on this board
    pub buttons: [Option<Gpio>; 4],
    pub i2c_sda: Gpio,
    pub i2c_scl: Gpio,
    /// BOOT button (strapping), usable as input after boot
    pub boot_button: Gpio,
    pub status_led: Gpio,
    /// Load switch enable for the LED chain (J7), 100 k to GND on the board
    pub led_chain_enable: Gpio,
    /// DRV8213 IN1 / IN2 (LEDC PWM)
    pub motor_in1: Gpio,
    pub motor_in2: Gpio,
    /// LED chain data (board) or latency reference input from device B (dev board, docs/test-hardware.md 5.3)
    pub io23: Gpio,
    /// Onboard WS2812 on the dev board (shares IO8 with S4)
    pub rgb_led: Option<Gpio>,
}

pub struct BoardDef {
    pub name: &'static str,
    pub pins: Pins,
    /// VSYS = ADC voltage × factor
    pub vsys_divider: f32,
    /// ISEN scale: mV at the ADC per A motor current
    pub ipropi_mv_per_a: u16,
    /// VBUS = ADC voltage × factor; `None` = VBUS_DET is only a digital switch
    pub vbus_divider: Option<f32>,
    /// Motor outputs drive LEDs from 3V3 (LED on when the pin is LOW) instead of a DRV8213
    pub motor_led_mode: bool,
}
