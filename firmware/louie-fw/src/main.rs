//! Bring-up in LED mode (docs/test-hardware.md 5.1, docs/firmware-architecture.md 11 step 0).
//!
//! Drives the DRV8213 scheme on IN1/IN2 from a setpoint in mV (keys or sweep), with ramp, lever gate, VSYS
//! cut-off, stall detection from the ISEN pot and the restart rule E15. On the dev board two LEDs stand in for the
//! motor, two pots for VSYS and motor current. Not the game firmware: no network, no motor thread yet.

use louie_fw::board::BOARD;
use louie_fw::hw::{self, Button, Pull};
use louie_fw::{console, diag};

const TICK_MS: u32 = 10;
/// Ramp of the motor voltage (docs/firmware-architecture.md 3: setpoint in mV, ramp in mV/s)
const RAMP_MV_PER_S: i32 = 4000;
const SETPOINT_STEP_MV: i32 = 250;
const SETPOINT_MAX_MV: i32 = 5000;
/// Below this VSYS no start (battery cut-off 3.3–3.4 V, A5; placeholder)
const VSYS_MIN_MV: u32 = 3300;
/// Stall: current above the limit for this long → brake (placeholders until the prototype, test-hardware.md 6)
const STALL_MA: u32 = 1500;
const STALL_MS: u32 = 300;
const SWEEP_PERIOD_MS: u32 = 8000;
const SWEEP_AMPLITUDE_MV: i32 = 3000;

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum State {
    /// Unexpected reset: no start until the lever goes open → closed (E15)
    Locked,
    LeverOpen,
    LowBattery,
    Run,
    Stall,
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum StopMode {
    Brake,
    Coast,
}

fn main() -> anyhow::Result<()> {
    louie_fw::init("louie-fw bring-up (LED mode)");
    let p = &BOARD.pins;

    let mut motor = hw::MotorPwm::new(p.motor_in1, p.motor_in2)?;
    motor.coast();
    hw::output(p.status_led, false)?;
    hw::input(p.sense, Pull::None)?;
    hw::input(p.vbus_det, Pull::None)?;
    let mut buttons = Vec::new();
    for (i, pin) in p.buttons.iter().enumerate() {
        if let Some(pin) = *pin {
            buttons.push((i + 1, Button::new(pin)?));
        }
    }
    let adc = hw::Adc::new(&[p.vsys_adc, p.isen_adc])?;

    let help = [
        ("+/-", "setpoint ± 250 mV (sign = direction)"),
        ("0", "setpoint 0"),
        ("s", "sweep on/off (± 3 V, 8 s)"),
        ("b/c", "stop mode brake / coast"),
        ("r", "clear stall"),
        ("p", "panic (tests restart rule E15)"),
        ("h", "this help"),
    ];
    console::menu(&help);
    if !BOARD.motor_led_mode {
        log::warn!("board {} drives a real DRV8213: setpoints move the motor", BOARD.name);
    }

    let mut state = if diag::is_unexpected_reset() { State::Locked } else { State::LeverOpen };
    if state == State::Locked {
        log::warn!("unexpected reset: motor locked until the lever goes open → closed");
    }
    let mut stop_mode = StopMode::Brake;
    let mut sweep = false;
    let mut setpoint_mv: i32 = 0;
    let mut output_mv: i32 = 0;
    let mut lever_prev = hw::level(p.sense);
    let mut vsys_mv: u32 = 0;
    let mut isen_ma: u32 = 0;
    let mut over_ms: u32 = 0;
    let mut tick: u32 = 0;

    loop {
        let now = tick.wrapping_mul(TICK_MS);

        if let Some(k) = console::poll_key() {
            match k {
                b'+' => setpoint_mv = (setpoint_mv + SETPOINT_STEP_MV).min(SETPOINT_MAX_MV),
                b'-' => setpoint_mv = (setpoint_mv - SETPOINT_STEP_MV).max(-SETPOINT_MAX_MV),
                b'0' => setpoint_mv = 0,
                b's' => sweep = !sweep,
                b'b' => stop_mode = StopMode::Brake,
                b'c' => stop_mode = StopMode::Coast,
                b'r' if state == State::Stall => state = State::LeverOpen,
                b'p' => panic!("deliberate panic from key 'p'"),
                b'h' => console::menu(&help),
                _ => {}
            }
            if !sweep {
                log::info!("setpoint {setpoint_mv} mV, stop mode {stop_mode:?}, sweep {sweep}");
            }
        }
        if sweep {
            // triangle −A … +A
            let phase = (now % SWEEP_PERIOD_MS) as i32;
            let half = SWEEP_PERIOD_MS as i32 / 2;
            let tri = if phase < half { phase } else { SWEEP_PERIOD_MS as i32 - phase };
            setpoint_mv = (tri * 4 * SWEEP_AMPLITUDE_MV / SWEEP_PERIOD_MS as i32) - SWEEP_AMPLITUDE_MV;
        }

        for (n, b) in buttons.iter_mut() {
            if b.poll() {
                log::info!("button S{n} (IO{}) pressed", b.pin);
            }
        }

        if tick % 5 == 0 {
            vsys_mv = (adc.read_avg(p.vsys_adc, 4)?.mv_mean as f32 * BOARD.vsys_divider) as u32;
            isen_ma = adc.read_avg(p.isen_adc, 4)?.mv_mean * 1000 / BOARD.ipropi_mv_per_a as u32;
        }

        let lever = hw::level(p.sense);
        if lever != lever_prev {
            log::info!("lever {}", if lever { "closed" } else { "open" });
            if lever && state == State::Locked {
                log::info!("lever edge open → closed: motor unlocked");
                state = State::LeverOpen;
            }
            lever_prev = lever;
        }

        // state transitions (Locked and Stall are left only by lever edge / key)
        let prev = state;
        state = match state {
            State::Locked | State::Stall => state,
            _ if !lever => State::LeverOpen,
            _ if vsys_mv < VSYS_MIN_MV => State::LowBattery,
            _ => State::Run,
        };

        if state == State::Run {
            let max_step = RAMP_MV_PER_S * TICK_MS as i32 / 1000;
            output_mv += (setpoint_mv - output_mv).clamp(-max_step, max_step);
            if output_mv == 0 {
                match stop_mode {
                    StopMode::Brake => motor.brake(),
                    StopMode::Coast => motor.coast(),
                }
            } else {
                // motor voltage → duty cycle: d = U / VSYS
                let duty = (output_mv * 1000 / vsys_mv.max(1) as i32).clamp(-1000, 1000);
                motor.set_duty(duty as i16);
            }
            if motor.duty() != 0 && isen_ma > STALL_MA {
                over_ms += TICK_MS;
                if over_ms >= STALL_MS {
                    state = State::Stall;
                    log::warn!("stall: {isen_ma} mA > {STALL_MA} mA for {STALL_MS} ms → brake, clear with 'r'");
                }
            } else {
                over_ms = 0;
            }
        }
        if state != State::Run {
            output_mv = 0;
            over_ms = 0;
            match state {
                // lever open = no current path anyway; coast = DRV8213 autosleep, SENSE readable (main-board-c6.md 2.5)
                State::LeverOpen | State::LowBattery | State::Locked => motor.coast(),
                State::Stall => motor.brake(),
                State::Run => unreachable!(),
            }
        }
        if state != prev {
            log::info!("state {prev:?} → {state:?}");
        }

        // status LED: Run 4 Hz, Locked double blink, Stall on, otherwise 1 Hz heartbeat
        let led = match state {
            State::Run => (now / 125) % 2 == 0,
            State::Locked => matches!(now % 1000, 0..=99 | 200..=299),
            State::Stall => true,
            _ => now % 1000 < 50,
        };
        hw::set(p.status_led, led);

        if tick % 50 == 0 {
            log::info!(
                "{state:?} set {setpoint_mv} mV out {output_mv} mV duty {}‰ · VSYS {vsys_mv} mV · ISEN {isen_ma} mA · \
                 lever {} · USB {} · heap {} B",
                motor.duty(),
                if lever { "closed" } else { "open" },
                if hw::level(p.vbus_det) { "yes" } else { "no" },
                diag::heap().free
            );
        }

        tick = tick.wrapping_add(1);
        std::thread::sleep(std::time::Duration::from_millis(TICK_MS as u64));
    }
}
