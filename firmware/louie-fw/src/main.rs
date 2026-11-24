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
/// Below this VSYS no start (placeholder, A5). Rev B (LDO TPS7A2633, docs/main-board-c6.md 2.7): dropout about 0.27 V
/// typ (0.45 V max) at a 380 mA radio peak, so 3V3 stays above 3.0 V down to about VSYS 3.3-3.45 V.
/// Final value from the prototype test (review R-B2: filtered reading, hysteresis).
const VSYS_MIN_MV: u32 = 3500;
/// Stall: current above the limit for this long → brake (placeholders until the prototype, test-hardware.md 6)
const STALL_MA: u32 = 1500;
/// USB plugged in and VSYS above this (4 × AA above the USB voltage): the cells feed through the body diode of Q1, which
/// does not block then (docs/main-board-c6.md 2.7). Lower stall limit so Q1 sees at most approx. 0.6 W for STALL_MS.
const USB_AA_VSYS_MV: u32 = 5200;
const STALL_MA_USB_AA: u32 = 800;
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

const HELP: [(&str, &str); 7] = [
    ("+/-", "setpoint ± 250 mV (sign = direction)"),
    ("0", "setpoint 0"),
    ("s", "sweep on/off (± 3 V, 8 s)"),
    ("b/c", "stop mode brake / coast"),
    ("r", "clear stall"),
    ("p", "panic (tests restart rule E15)"),
    ("h", "this help"),
];

fn main() -> anyhow::Result<()> {
    louie_fw::init("louie-fw bring-up (LED mode)");
    let mut bring_up = BringUp::new()?;
    let mut tick: u32 = 0;
    loop {
        bring_up.step(tick)?;
        tick = tick.wrapping_add(1);
        std::thread::sleep(std::time::Duration::from_millis(TICK_MS as u64));
    }
}

/// Hardware and state of the bring-up loop; `step` runs one 10 ms tick.
struct BringUp {
    motor: hw::MotorPwm,
    adc: hw::Adc,
    buttons: Vec<(usize, Button)>,
    state: State,
    stop_mode: StopMode,
    sweep: bool,
    setpoint_mv: i32,
    output_mv: i32,
    /// lever level of the current tick (true = closed)
    lever: bool,
    vsys_mv: u32,
    isen_ma: u32,
    over_ms: u32,
}

impl BringUp {
    fn new() -> anyhow::Result<Self> {
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
        console::menu(&HELP);
        if !BOARD.motor_led_mode {
            log::warn!("board {} drives a real DRV8213: setpoints move the motor", BOARD.name);
        }
        let state = if diag::is_unexpected_reset() { State::Locked } else { State::LeverOpen };
        if state == State::Locked {
            log::warn!("unexpected reset: motor locked until the lever goes open → closed");
        }
        Ok(Self {
            motor,
            adc,
            buttons,
            state,
            stop_mode: StopMode::Brake,
            sweep: false,
            setpoint_mv: 0,
            output_mv: 0,
            lever: hw::level(p.sense),
            vsys_mv: 0,
            isen_ma: 0,
            over_ms: 0,
        })
    }

    fn step(&mut self, tick: u32) -> anyhow::Result<()> {
        let p = &BOARD.pins;
        let now = tick.wrapping_mul(TICK_MS);
        if let Some(k) = console::poll_key() {
            self.on_key(k);
        }
        if self.sweep {
            self.setpoint_mv = sweep_setpoint(now);
        }
        self.poll_buttons();
        if tick % 5 == 0 {
            self.measure()?;
        }
        self.read_lever();

        // state transitions (Locked and Stall are left only by lever edge / key)
        let prev = self.state;
        self.state = self.next_state();
        if self.state == State::Run {
            self.drive();
            self.check_stall();
        }
        if self.state != State::Run {
            self.stop();
        }
        if self.state != prev {
            log::info!("state {prev:?} → {:?}", self.state);
        }
        hw::set(p.status_led, self.status_led(now));
        if tick % 50 == 0 {
            self.log_status();
        }
        Ok(())
    }

    fn on_key(&mut self, key: u8) {
        match self.setpoint_for(key) {
            Some(mv) => self.setpoint_mv = mv,
            None => self.command(key),
        }
        if !self.sweep {
            log::info!("setpoint {} mV, stop mode {:?}, sweep {}", self.setpoint_mv, self.stop_mode, self.sweep);
        }
    }

    fn command(&mut self, key: u8) {
        match key {
            b's' => self.sweep = !self.sweep,
            b'b' => self.stop_mode = StopMode::Brake,
            b'c' => self.stop_mode = StopMode::Coast,
            b'r' if self.state == State::Stall => self.state = State::LeverOpen,
            b'p' => panic!("deliberate panic from key 'p'"),
            b'h' => console::menu(&HELP),
            _ => {}
        }
    }

    fn poll_buttons(&mut self) {
        for (n, b) in self.buttons.iter_mut() {
            if b.poll() {
                log::info!("button S{n} (IO{}) pressed", b.pin);
            }
        }
    }

    fn measure(&mut self) -> anyhow::Result<()> {
        let p = &BOARD.pins;
        self.vsys_mv = (self.adc.read_avg(p.vsys_adc, 4)?.mv_mean as f32 * BOARD.vsys_divider) as u32;
        self.isen_ma = self.adc.read_avg(p.isen_adc, 4)?.mv_mean * 1000 / BOARD.ipropi_mv_per_a as u32;
        Ok(())
    }

    /// Read the lever once per tick; on an edge log it, open → closed unlocks after an unexpected reset (E15).
    fn read_lever(&mut self) {
        let lever = hw::level(BOARD.pins.sense);
        if lever == self.lever {
            return;
        }
        log::info!("lever {}", if lever { "closed" } else { "open" });
        if lever && self.state == State::Locked {
            log::info!("lever edge open → closed: motor unlocked");
            self.state = State::LeverOpen;
        }
        self.lever = lever;
    }

    /// Ramp the output towards the setpoint and set the duty cycle d = U / VSYS (0 V: stop mode).
    fn drive(&mut self) {
        let max_step = RAMP_MV_PER_S * TICK_MS as i32 / 1000;
        self.output_mv += (self.setpoint_mv - self.output_mv).clamp(-max_step, max_step);
        if self.output_mv != 0 {
            let duty = (self.output_mv * 1000 / self.vsys_mv.max(1) as i32).clamp(-1000, 1000);
            self.motor.set_duty(duty as i16);
            return;
        }
        match self.stop_mode {
            StopMode::Brake => self.motor.brake(),
            StopMode::Coast => self.motor.coast(),
        }
    }

    /// Current above the stall limit for STALL_MS → Stall.
    fn check_stall(&mut self) {
        let stall_ma = self.stall_limit_ma();
        if self.motor.duty() == 0 || self.isen_ma <= stall_ma {
            self.over_ms = 0;
            return;
        }
        self.over_ms += TICK_MS;
        if self.over_ms >= STALL_MS {
            self.state = State::Stall;
            log::warn!("stall: {} mA > {stall_ma} mA for {STALL_MS} ms → brake, clear with 'r'", self.isen_ma);
        }
    }

    fn stop(&mut self) {
        self.output_mv = 0;
        self.over_ms = 0;
        match self.state {
            // lever open = no current path anyway; coast = DRV8213 autosleep, SENSE readable (main-board-c6.md 2.5)
            State::LeverOpen | State::LowBattery | State::Locked => self.motor.coast(),
            State::Stall => self.motor.brake(),
            State::Run => unreachable!(),
        }
    }

    fn log_status(&self) {
        log::info!(
            "{:?} set {} mV out {} mV duty {}‰ · VSYS {} mV · ISEN {} mA · lever {} · USB {} · heap {} B",
            self.state,
            self.setpoint_mv,
            self.output_mv,
            self.motor.duty(),
            self.vsys_mv,
            self.isen_ma,
            if self.lever { "closed" } else { "open" },
            if hw::level(BOARD.pins.vbus_det) { "yes" } else { "no" },
            diag::heap().free
        );
    }

    /// New setpoint for the keys +, - and 0 (± one step, limited), None for other keys.
    fn setpoint_for(&self, key: u8) -> Option<i32> {
        match key {
            b'+' => Some((self.setpoint_mv + SETPOINT_STEP_MV).min(SETPOINT_MAX_MV)),
            b'-' => Some((self.setpoint_mv - SETPOINT_STEP_MV).max(-SETPOINT_MAX_MV)),
            b'0' => Some(0),
            _ => None,
        }
    }

    /// Next state from lever and VSYS; Locked and Stall are left only by lever edge or key.
    fn next_state(&self) -> State {
        match self.state {
            State::Locked | State::Stall => self.state,
            _ if !self.lever => State::LeverOpen,
            _ if self.vsys_mv < VSYS_MIN_MV => State::LowBattery,
            _ => State::Run,
        }
    }

    /// Lower stall limit while 4 × AA feed through the body diode of Q1 (USB plugged in, VSYS above USB_AA_VSYS_MV).
    fn stall_limit_ma(&self) -> u32 {
        if hw::level(BOARD.pins.vbus_det) && self.vsys_mv > USB_AA_VSYS_MV {
            STALL_MA_USB_AA
        } else {
            STALL_MA
        }
    }

    /// Status LED: Run 4 Hz, Locked double blink, Stall on, otherwise 1 Hz heartbeat.
    fn status_led(&self, now: u32) -> bool {
        match self.state {
            State::Run => (now / 125) % 2 == 0,
            State::Locked => matches!(now % 1000, 0..=99 | 200..=299),
            State::Stall => true,
            _ => now % 1000 < 50,
        }
    }
}

/// Sweep setpoint: triangle −A … +A over SWEEP_PERIOD_MS.
fn sweep_setpoint(now: u32) -> i32 {
    let phase = (now % SWEEP_PERIOD_MS) as i32;
    let half = SWEEP_PERIOD_MS as i32 / 2;
    let tri = if phase < half { phase } else { SWEEP_PERIOD_MS as i32 - phase };
    (tri * 4 * SWEEP_AMPLITUDE_MV / SWEEP_PERIOD_MS as i32) - SWEEP_AMPLITUDE_MV
}
