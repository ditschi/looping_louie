//! GPIO, ADC (oneshot + curve-fitting calibration) and the motor PWM on LEDC.

use esp_idf_svc::sys::{self, esp, EspError};

use crate::board::Gpio;

// ---------------------------------------------------------------------------------------------------------------
// GPIO

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum Pull {
    None,
    Up,
    Down,
}

pub fn input(pin: Gpio, pull: Pull) -> Result<(), EspError> {
    let cfg = sys::gpio_config_t {
        pin_bit_mask: 1u64 << pin,
        mode: sys::gpio_mode_t_GPIO_MODE_INPUT,
        pull_up_en: if pull == Pull::Up {
            sys::gpio_pullup_t_GPIO_PULLUP_ENABLE
        } else {
            sys::gpio_pullup_t_GPIO_PULLUP_DISABLE
        },
        pull_down_en: if pull == Pull::Down {
            sys::gpio_pulldown_t_GPIO_PULLDOWN_ENABLE
        } else {
            sys::gpio_pulldown_t_GPIO_PULLDOWN_DISABLE
        },
        intr_type: sys::gpio_int_type_t_GPIO_INTR_DISABLE,
        ..Default::default()
    };
    esp!(unsafe { sys::gpio_config(&cfg) })
}

/// Push-pull output. The level is written before the driver is enabled, so the pin does not glitch.
pub fn output(pin: Gpio, high: bool) -> Result<(), EspError> {
    set(pin, high);
    let cfg = sys::gpio_config_t {
        pin_bit_mask: 1u64 << pin,
        mode: sys::gpio_mode_t_GPIO_MODE_OUTPUT,
        pull_up_en: sys::gpio_pullup_t_GPIO_PULLUP_DISABLE,
        pull_down_en: sys::gpio_pulldown_t_GPIO_PULLDOWN_DISABLE,
        intr_type: sys::gpio_int_type_t_GPIO_INTR_DISABLE,
        ..Default::default()
    };
    esp!(unsafe { sys::gpio_config(&cfg) })?;
    set(pin, high);
    Ok(())
}

pub fn set(pin: Gpio, high: bool) {
    unsafe { sys::gpio_set_level(pin, high as u32) };
}

pub fn level(pin: Gpio) -> bool {
    unsafe { sys::gpio_get_level(pin) != 0 }
}

/// Latch the current pad state (also through deep sleep on the C6, SOC_GPIO_SUPPORT_HOLD_SINGLE_IO_IN_DSLP).
pub fn hold(pin: Gpio, on: bool) -> Result<(), EspError> {
    esp!(unsafe {
        if on {
            sys::gpio_hold_en(pin)
        } else {
            sys::gpio_hold_dis(pin)
        }
    })
}

/// Debounced button (to GND, active LOW). Call `poll` every 10 ms; returns true once per press.
pub struct Button {
    pub pin: Gpio,
    stable: bool,
    count: u8,
}

impl Button {
    pub fn new(pin: Gpio) -> Result<Self, EspError> {
        input(pin, Pull::Up)?;
        Ok(Self { pin, stable: false, count: 0 })
    }

    pub fn poll(&mut self) -> bool {
        let pressed = !level(self.pin);
        if pressed == self.stable {
            self.count = 0;
            return false;
        }
        self.count += 1;
        if self.count < 3 {
            return false;
        }
        self.count = 0;
        self.stable = pressed;
        pressed
    }

    pub fn is_pressed(&self) -> bool {
        self.stable
    }
}

// ---------------------------------------------------------------------------------------------------------------
// ADC

/// ADC1 oneshot with one calibration per channel (the C6 calibrates per channel).
/// Attenuation 12 dB: input range about 0–3.3 V (unverified for the C6, check against the multimeter in 4.5).
pub struct Adc {
    unit: sys::adc_oneshot_unit_handle_t,
    channels: Vec<(Gpio, sys::adc_channel_t, sys::adc_cali_handle_t)>,
}

#[derive(Clone, Copy, Default)]
pub struct AdcStats {
    pub n: u32,
    pub raw_mean: u32,
    pub mv_mean: u32,
    pub mv_min: u32,
    pub mv_max: u32,
}

impl Adc {
    /// Configure the given GPIOs as ADC1 inputs. This switches them to analog; `level()` no longer works on them.
    pub fn new(pins: &[Gpio]) -> Result<Self, EspError> {
        let mut unit: sys::adc_oneshot_unit_handle_t = core::ptr::null_mut();
        let unit_cfg = sys::adc_oneshot_unit_init_cfg_t {
            unit_id: sys::adc_unit_t_ADC_UNIT_1,
            ulp_mode: sys::adc_ulp_mode_t_ADC_ULP_MODE_DISABLE,
            ..Default::default()
        };
        esp!(unsafe { sys::adc_oneshot_new_unit(&unit_cfg, &mut unit) })?;

        let mut channels = Vec::new();
        for &pin in pins {
            let mut unit_id: sys::adc_unit_t = 0;
            let mut chan: sys::adc_channel_t = 0;
            esp!(unsafe { sys::adc_oneshot_io_to_channel(pin, &mut unit_id, &mut chan) })?;
            let chan_cfg = sys::adc_oneshot_chan_cfg_t {
                atten: sys::adc_atten_t_ADC_ATTEN_DB_12,
                bitwidth: sys::adc_bitwidth_t_ADC_BITWIDTH_DEFAULT,
            };
            esp!(unsafe { sys::adc_oneshot_config_channel(unit, chan, &chan_cfg) })?;

            let cali_cfg = sys::adc_cali_curve_fitting_config_t {
                unit_id: sys::adc_unit_t_ADC_UNIT_1,
                chan,
                atten: sys::adc_atten_t_ADC_ATTEN_DB_12,
                bitwidth: sys::adc_bitwidth_t_ADC_BITWIDTH_DEFAULT,
            };
            let mut cali: sys::adc_cali_handle_t = core::ptr::null_mut();
            esp!(unsafe { sys::adc_cali_create_scheme_curve_fitting(&cali_cfg, &mut cali) })?;
            channels.push((pin, chan, cali));
        }
        Ok(Self { unit, channels })
    }

    fn channel(&self, pin: Gpio) -> (sys::adc_channel_t, sys::adc_cali_handle_t) {
        let &(_, chan, cali) =
            self.channels.iter().find(|c| c.0 == pin).unwrap_or_else(|| panic!("IO{pin} is not an ADC input here"));
        (chan, cali)
    }

    /// One conversion: (raw, calibrated mV at the pin).
    pub fn read(&self, pin: Gpio) -> Result<(u32, u32), EspError> {
        let (chan, cali) = self.channel(pin);
        let mut raw: i32 = 0;
        let mut mv: i32 = 0;
        esp!(unsafe { sys::adc_oneshot_read(self.unit, chan, &mut raw) })?;
        esp!(unsafe { sys::adc_cali_raw_to_voltage(cali, raw, &mut mv) })?;
        Ok((raw.max(0) as u32, mv.max(0) as u32))
    }

    /// `n` conversions back to back: mean, min, max.
    pub fn read_avg(&self, pin: Gpio, n: u32) -> Result<AdcStats, EspError> {
        let (mut raw_sum, mut mv_sum, mut mv_min, mut mv_max) = (0u32, 0u32, u32::MAX, 0u32);
        for _ in 0..n {
            let (raw, mv) = self.read(pin)?;
            raw_sum += raw;
            mv_sum += mv;
            mv_min = mv_min.min(mv);
            mv_max = mv_max.max(mv);
        }
        Ok(AdcStats { n, raw_mean: raw_sum / n, mv_mean: mv_sum / n, mv_min, mv_max })
    }
}

impl Drop for Adc {
    fn drop(&mut self) {
        unsafe {
            for &(_, _, cali) in &self.channels {
                sys::adc_cali_delete_scheme_curve_fitting(cali);
            }
            sys::adc_oneshot_del_unit(self.unit);
        }
    }
}

// ---------------------------------------------------------------------------------------------------------------
// Motor PWM (DRV8213 scheme, docs/firmware-architecture.md 3)

pub const PWM_HZ: u32 = 20_000;
const PWM_BITS: u32 = 10;
/// LEDC accepts 0..=2^bits; 2^bits is a constant HIGH.
const PWM_FULL: u32 = 1 << PWM_BITS;

/// IN1/IN2 on LEDC timer 0, channels 0/1, 20 kHz, 10 bit.
///
/// Drive/brake: forward IN1 = 1, IN2 = PWM(1 − d); reverse IN1 = PWM(1 − d), IN2 = 1; brake 1/1; coast 0/0.
/// In LED mode (3V3 → 1 k → LED → pin) a LED lights while its pin is LOW: the LED of the PWM pin shows the
/// speed, brake = both off, coast = both on.
pub struct MotorPwm {
    duty_permille: i16,
}

impl MotorPwm {
    pub fn new(in1: Gpio, in2: Gpio) -> Result<Self, EspError> {
        let timer = sys::ledc_timer_config_t {
            speed_mode: sys::ledc_mode_t_LEDC_LOW_SPEED_MODE,
            duty_resolution: PWM_BITS as _,
            timer_num: sys::ledc_timer_t_LEDC_TIMER_0,
            freq_hz: PWM_HZ,
            clk_cfg: sys::soc_periph_ledc_clk_src_legacy_t_LEDC_AUTO_CLK,
            ..Default::default()
        };
        esp!(unsafe { sys::ledc_timer_config(&timer) })?;
        for (pin, channel) in [(in1, sys::ledc_channel_t_LEDC_CHANNEL_0), (in2, sys::ledc_channel_t_LEDC_CHANNEL_1)] {
            let ch = sys::ledc_channel_config_t {
                gpio_num: pin,
                speed_mode: sys::ledc_mode_t_LEDC_LOW_SPEED_MODE,
                channel,
                timer_sel: sys::ledc_timer_t_LEDC_TIMER_0,
                duty: 0,
                hpoint: 0,
                ..Default::default()
            };
            esp!(unsafe { sys::ledc_channel_config(&ch) })?;
        }
        Ok(Self { duty_permille: 0 })
    }

    fn set_channels(&self, in1: u32, in2: u32) {
        for (channel, duty) in [(sys::ledc_channel_t_LEDC_CHANNEL_0, in1), (sys::ledc_channel_t_LEDC_CHANNEL_1, in2)] {
            unsafe {
                sys::ledc_set_duty(sys::ledc_mode_t_LEDC_LOW_SPEED_MODE, channel, duty);
                sys::ledc_update_duty(sys::ledc_mode_t_LEDC_LOW_SPEED_MODE, channel);
            }
        }
    }

    /// Duty cycle in ‰, −1000…1000, sign = direction. 0 = brake (as the DRV8213 with d = 0 in drive/brake).
    pub fn set_duty(&mut self, permille: i16) {
        let d = permille.clamp(-1000, 1000);
        self.duty_permille = d;
        let pwm = (1000 - d.unsigned_abs() as u32) * PWM_FULL / 1000;
        if d >= 0 {
            self.set_channels(PWM_FULL, pwm);
        } else {
            self.set_channels(pwm, PWM_FULL);
        }
    }

    pub fn brake(&mut self) {
        self.duty_permille = 0;
        self.set_channels(PWM_FULL, PWM_FULL);
    }

    pub fn coast(&mut self) {
        self.duty_permille = 0;
        self.set_channels(0, 0);
    }

    pub fn duty(&self) -> i16 {
        self.duty_permille
    }
}
