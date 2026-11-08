//! Breadboard with the Waveshare ESP32-C6-DEV-KIT-N8 (or Espressif ESP32-C6-DevKitC-1-N8): same GPIO numbers as
//! the board, docs/test-hardware.md 3.
//!
//! - IO14 does not exist on the WROOM-1 module: status LED on IO10.
//! - IO8 carries the onboard WS2812 (DI via 0 R) and a 10 k pull-up. S4 cannot be used here; only S1–S3.
//! - IO4 is only a switch in LED mode (no divider on the 5V pin).
//! - IO23 is the latency reference input from device B.

use super::{BoardDef, Pins};

pub const BOARD: BoardDef = BoardDef {
    name: "devkitc-c6",
    pins: Pins {
        vsys_adc: 0,
        isen_adc: 1,
        accel_int: 2,
        sense: 3,
        vbus_det: 4,
        buttons: [Some(5), Some(20), Some(21), None],
        i2c_sda: 6,
        i2c_scl: 7,
        boot_button: 9,
        status_led: 10,
        led_chain_enable: 15,
        motor_in1: 18,
        motor_in2: 19,
        io23: 23,
        rgb_led: Some(8),
    },
    // pot wiper = VSYS / 2, same factor as the board
    vsys_divider: 2.0,
    // pot simulates IPROPI with the same scale (R_IPROPI 1.24 k × 205 µA/A)
    ipropi_mv_per_a: 255,
    vbus_divider: None,
    motor_led_mode: true,
};
