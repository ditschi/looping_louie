from dataclasses import dataclass
import time
import machine

try:
    from hardware.Timer import Timer
    from hardware.hw_config import MOTOR_TIMER, DEFAULT_SPEED_PERCENT, DEFAULT_MAXIMUM_SPEED_CHANGE, DEFAULT_SPEED_CHANGE_DELAY_MS
except ImportError:
    import sys
    sys.path.append('/hardware/')
    from Timer import Timer
    from hw_config import MOTOR_TIMER, DEFAULT_SPEED_PERCENT, DEFAULT_MAXIMUM_SPEED_CHANGE, DEFAULT_SPEED_CHANGE_DELAY_MS


@dataclass
class MotorConfig:
    limit_speedchange: bool = True
    max_change: int = DEFAULT_MAXIMUM_SPEED_CHANGE
    change_delay_ms: int = DEFAULT_SPEED_CHANGE_DELAY_MS


class Motor():
    def __init__(self, motor_pin: int, config: MotorConfig=MotorConfig()):
        self.motor_pin = motor_pin
        self.config = config
        self.__init_hw()
        self.speed_current = 0
        self.speed_set = 0
        self.speed_next

    def __init_hw(self):
        self.machine_pin = machine.Pin(self.motor_pin)
        self.pwm = machine.PWM(self.machine_pin)
        self.pwm.freq(500)
        self.pwm.duty(0)
        self.timer = Timer(MOTOR_TIMER, self.__timer_handler) if MOTOR_TIMER else None

    def __timer_handler(self):
        self.__change_speed()

    def start(self, speed_in_percent: int = DEFAULT_SPEED_PERCENT):
        self.pwm.freq(500)
        self.set_speed_in_percent(speed_in_percent)

    def stop(self):
        self.set_speed_in_percent(0)

    def set_speed_in_percent(self, speed_in_percent: int):
        if speed_in_percent < 0:
            speed_in_percent = 0
        elif speed_in_percent > 100:
            speed_in_percent = 100

        self.speed_set = speed_in_percent
        self.__change_speed()

    def set_config(self, config: MotorConfig):
        self.config = config

    def __change_speed(self):
        self.__set_next_speed_using_limit()
        self.__set_pwm()

        # fallback loop without timer interrupt
        if not self.timer and self.speed_current != self.speed_set:
            time.sleep(self.config.change_delay_ms)
            self.__change_speed()

    def __set_pwm(self):
        pwm_value = __get_pwm_value(self.speed_next)
        self.pwm.duty(pwm_value)
        self.speed_current = self.speed_next

    def __set_next_speed_using_limit(self):
        if not self.config.max_change or not abs(self.speed_set - self.speed_current) > self.config.max_change:
            # No max_change configured or change is already in limits
            self.speed_next = self.speed_set
            return

        if self.speed_set > self.speed_current:  # speed increase
            next_speed = self.speed_current + self.config.max_change
            next_speed = self.speed_set if next_speed > self.speed_set else next_speed
        else:  # speed decrease
            next_speed = self.speed_current - self.config.max_change
            next_speed = self.speed_set if next_speed < self.speed_set else next_speed
        self.next_speed = next_speed

        if next_speed != self.speed_set:
            delay = self.config["change_delay_ms"] if self.config["change_delay_ms"] else DEFAULT_SPEED_CHANGE_DELAY_MS
            if self.timer:
                # start timer so interrupt changes speed again
                self.timer.start(delay)


def __get_pwm_value(percent: int):
    # duty cycle is between 0 (all off) and 1023 (all on)
    result = (1023 / 100) * percent
    return int(result)
