import time
import machine

try:
    from looping_louie.hardware.Timer import Timer
    from looping_louie.hardware.hw_config import MOTOR_TIMER, DEFAULT_SPEED_PERCENT, \
        DEFAULT_MAXIMUM_SPEED_CHANGE, DEFAULT_SPEED_CHANGE_DELAY_MS
except ImportError:
    import sys
    sys.path.append('/hardware/')
    from Timer import Timer
    from hw_config import MOTOR_TIMER, DEFAULT_SPEED_PERCENT, \
        DEFAULT_MAXIMUM_SPEED_CHANGE, DEFAULT_SPEED_CHANGE_DELAY_MS


class MotorConfig:
    def __init__(self, limit_speedchange: bool = True, max_change: int = DEFAULT_MAXIMUM_SPEED_CHANGE,
                 change_delay_ms: int = DEFAULT_SPEED_CHANGE_DELAY_MS):
        self.limit_speedchange = limit_speedchange
        self.max_change = max_change
        self.change_delay_ms = change_delay_ms


def __get_pwm_value(percent: int):
    # duty cycle is between 0 (all off) and 1023 (all on)
    result = (1023 / 100) * percent
    return int(result)


class Motor:
    def __init__(self, pin: int, config: MotorConfig = MotorConfig()):
        self.__pin = pin
        self.__config = config
        self.__init_hw()
        self.speed_current = 0
        self.speed_set = 0
        self.__speed_next = None

    def __init_hw(self):
        self.__motor_pin = machine.Pin(self.__pin)
        self.__pwm = machine.PWM(self.__motor_pin)
        self.__pwm.freq(1000)
        self.__pwm.duty(0)
        self.__timer = Timer(MOTOR_TIMER, self.__timer_handler) if MOTOR_TIMER else None

    def __timer_handler(self, _=None):
        self.__change_speed()

    @property
    def running(self):
        return self.speed_set != 0

    def start(self, speed_in_percent: int = DEFAULT_SPEED_PERCENT):
        print(f"DEBUG | Motor {self.__pin} starting with {speed_in_percent}% speed")
        self.set_speed_in_percent(speed_in_percent)

    def stop(self):
        print(f"DEBUG | Motor {self.__pin} stopping")
        self.set_speed_in_percent(0)

    def set_speed_in_percent(self, speed_in_percent: int):
        if speed_in_percent < 0:
            speed_in_percent = 0
        elif speed_in_percent > 100:
            speed_in_percent = 100

        print(f"DEBUG | Motor {self.__pin} now running with {speed_in_percent}% speed")
        self.speed_set = speed_in_percent
        self.__change_speed()

    def set_config(self, config: MotorConfig):
        self.__config = config

    def __change_speed(self):
        self.__set_next_speed_using_limit()
        self.__set_pwm()

        # fallback loop without timer interrupt
        if self.__config.limit_speedchange and not self.__timer and self.speed_current != self.speed_set:
            print(f"DEBUG | Motor {self.__pin} using sleep() to limit speed change")
            sleep_time = self.__config.change_delay_ms/1000
            time.sleep(sleep_time)
            self.__change_speed()

    def __set_pwm(self):
        print(f"DEBUG | Motor {self.__pin}  updating PWM to match a speed of {self.__speed_next}%")
        pwm_value = __get_pwm_value(self.__speed_next)
        self.__pwm.duty(pwm_value)
        self.speed_current = self.__speed_next

    def __set_next_speed_using_limit(self):
        if not self.__config.limit_speedchange:
            print(f"DEBUG | Motor {self.__pin} speed change limit disabled")
            self.__speed_next = self.speed_set
            return
        speed_change = self.speed_set - self.speed_current
        if not abs(speed_change) > self.__config.max_change:
            print(f"DEBUG | Motor {self.__pin} speed change ({speed_change}%) is already below maximum of {self.__config.max_change}%")
            self.__speed_next = self.speed_set
            return

        if self.speed_set > self.speed_current:  # speed increase
            next_speed = self.speed_current + self.__config.max_change
            next_speed = self.speed_set if next_speed > self.speed_set else next_speed
        else:  # speed decrease
            next_speed = self.speed_current - self.__config.max_change
            next_speed = self.speed_set if next_speed < self.speed_set else next_speed
        self.__speed_next = next_speed
        print(f"DEBUG | Motor {self.__pin} next limited speed is {next_speed}% (goal is {self.speed_set}%)")

        if next_speed != self.speed_set:
            delay = self.__config.change_delay_ms if self.__config.change_delay_ms else DEFAULT_SPEED_CHANGE_DELAY_MS
            if self.__timer:
                # start timer so interrupt changes speed again
                print(f"DEBUG | Motor {self.__pin} starting timer for limited speed change")
                self.__timer.start(delay)




