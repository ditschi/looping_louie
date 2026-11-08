//! Pre-order check 4.5 (docs/test-hardware.md): ADC accuracy of the VSYS divider (IO0, 470 k / 470 k + 100 nF) and
//! the VBUS divider (IO4, 100 k / 100 k). Also shows IO1 (ISEN pot in LED mode).
//!
//! Samples at 10 Hz like the firmware (one conversion every 100 ms) and logs once per second: mean, min, max of
//! the pin voltage and the input voltage with the nominal ratio. Enter the measured ratio of the drawer resistors
//! in the table of test-hardware.md, not here.

use louie_fw::board::BOARD;
use louie_fw::console;
use louie_fw::hw::{Adc, AdcStats};

/// Nominal divider ratios (input = pin × ratio)
const VSYS_RATIO: f32 = 2.0;
const VBUS_RATIO: f32 = 2.0;

#[derive(Default)]
struct Acc {
    n: u32,
    sum: u32,
    min: u32,
    max: u32,
}

impl Acc {
    fn add(&mut self, mv: u32) {
        if self.n == 0 {
            self.min = mv;
            self.max = mv;
        }
        self.n += 1;
        self.sum += mv;
        self.min = self.min.min(mv);
        self.max = self.max.max(mv);
    }

    fn line(&self, name: &str, ratio: f32) -> String {
        let mean = self.sum / self.n.max(1);
        format!(
            "{name}: pin {mean} mV (min {} max {} p-p {}) → in {:.0} mV",
            self.min,
            self.max,
            self.max - self.min,
            mean as f32 * ratio
        )
    }
}

fn main() -> anyhow::Result<()> {
    louie_fw::init("adc_probe (test-hardware.md 4.5)");
    let p = &BOARD.pins;
    let adc = Adc::new(&[p.vsys_adc, p.isen_adc, p.vbus_det])?;

    console::menu(&[
        ("f", "fast mode on/off: 64 conversions back to back per channel (loads C13, shows the drop)"),
        ("h", "this help"),
    ]);

    let mut fast = false;
    let (mut vsys, mut isen, mut vbus) = (Acc::default(), Acc::default(), Acc::default());
    let mut tick: u32 = 0;
    loop {
        match console::poll_key() {
            Some(b'f') => {
                fast = !fast;
                log::info!("fast mode {fast}");
            }
            Some(b'h') => log::info!("f = fast mode"),
            _ => {}
        }
        if fast {
            for (name, pin, ratio) in [("VSYS IO0", p.vsys_adc, VSYS_RATIO), ("VBUS IO4", p.vbus_det, VBUS_RATIO)] {
                let s: AdcStats = adc.read_avg(pin, 64)?;
                log::info!(
                    "{name} burst 64: raw {} · pin {} mV (min {} max {}) → in {:.0} mV",
                    s.raw_mean,
                    s.mv_mean,
                    s.mv_min,
                    s.mv_max,
                    s.mv_mean as f32 * ratio
                );
            }
            std::thread::sleep(std::time::Duration::from_millis(1000));
            continue;
        }

        vsys.add(adc.read(p.vsys_adc)?.1);
        isen.add(adc.read(p.isen_adc)?.1);
        vbus.add(adc.read(p.vbus_det)?.1);
        tick += 1;
        if tick % 10 == 0 {
            log::info!("{}", vsys.line("VSYS IO0", VSYS_RATIO));
            log::info!("{}", vbus.line("VBUS IO4", VBUS_RATIO));
            let isen_mv = isen.sum / isen.n.max(1);
            log::info!(
                "ISEN IO1: pin {isen_mv} mV → {} mA (LED mode pot)",
                isen_mv * 1000 / BOARD.ipropi_mv_per_a as u32
            );
            (vsys, isen, vbus) = (Acc::default(), Acc::default(), Acc::default());
        }
        std::thread::sleep(std::time::Duration::from_millis(100));
    }
}
