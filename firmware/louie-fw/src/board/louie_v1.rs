//! Main board v1 (ESP32-C6-MINI-1, DRV8213), pin assignment from docs/main-board-c6.md 2.3.
//! Not tested yet: there is no board. sdkconfig for the board (console on USB-Serial-JTAG) is still missing.

use super::{BoardDef, Pins};

pub const BOARD: BoardDef = BoardDef {
    name: "louie-v1",
    pins: Pins {
        vsys_adc: 0,
        isen_adc: 1,
        accel_int: 2,
        sense: 3,
        vbus_det: 4,
        buttons: [Some(5), Some(20), Some(21), Some(8)],
        i2c_sda: 6,
        i2c_scl: 7,
        boot_button: 9,
        status_led: 14,
        led_chain_enable: 15,
        motor_in1: 18,
        motor_in2: 19,
        io23: 23,
        rgb_led: None,
    },
    // R6/R7 680 k / 470 k (VSYS up to 6.6 V for 4 x AA, docs/main-board-c6.md 2.7)
    vsys_divider: 2.447,
    ipropi_mv_per_a: 255,
    // R14/R15 100 k / 100 k; may change after docs/test-hardware.md 4.3
    vbus_divider: Some(2.0),
    motor_led_mode: false,
};
