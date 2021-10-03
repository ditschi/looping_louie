#!/usr/bin/env python3

import os
import machine
from gamemode import gamemode
from hw_control import hw_config

MOTOR_PIN = 0
START_STOP_SWITCH_PIN = 0


class LoopingLouie(object):
    def __init__(self, on_off_switch_interrupt_handler, gameplay_timer_interrupt_handler):
        self.motor = Motor(hw_config.MOTOR_PIN)
        self.start_stop_button = Button(hw_config.ON_OFF_BUTTON_PIN, on_off_switch_interrupt_handler)
        self.game_timer = Timer(hw_config.GAME_TIMER, gameplay_timer_interrupt_handler)


class Motor(object):
    def __init__(self, pin):
        self.motor_pin = machine.Pin(pin)
        self.motor_pwm = machine.PWM(self.motor_pin)
        self.motor_pwm.freq(500)
        self.motor_pwm.duty(0)
        self.delay_timer = Timer(hw_config.DELAY_TIMER, self._delay_timer_handler)
        self.speed_config = None
        self.new_speed = 0
        self.current_speed = 0

    def _delay_timer_handler(self):
        raise NotImplementedError

    def start(self, speed_in_percent):
        self.speed_config = speed_config
        self.new_speed = speed_config.start
        return self.__set_speed__()

    def stop(self):
        self.new_speed = 0
        self.__set_speed__()
        self.speed_config = Nonup

    def set_speed(self, speed):
        if not self.speed_config.change_rate:
            pwm_value = get_pwm_value(self.new_speed)
            self.motor_pwm.duty(pwm_value)
        else:
            next_speed = self.current_speed
            if self.new_speed > self.current_speed:
                next_speed += self.speed_config.change_rate
                if self.new_speed > next_speed:
                    next_speed = self.new_speed

            elif self.new_speed < self.current_speed:
                next_speed -= self.speed_config.change_rate
                if self.new_speed < next_speed:
                    next_speed = self.new_speed

            # duty cycle is between 0 (all off) and 1023 (all on)
            pwm_value = get_pwm_value(next_speed)
            self.motor_pwm.duty(pwm_value)
            self.speed_config.current = next_speed

            if next_speed == self.new_speed:
                return self.new_speed

            # start delay timer -> the interrupt re-triggers the speed update
            self.delay_timer.delay(self.speed_config.change_delay)





class Timer(object):
    def __init__(self, timer: int, interrupt_handler=None):
        self.timer = machine.Timer(timer)
        self.interrupt_handler = interrupt_handler

    @staticmethod
    def _seconds_to_period(seconds):
        return seconds * 1000

    def start(self, time_in_ms):
        period = self._seconds_to_period(seconds)

    def _start_periodic_timer(self, time_ms)
        self.timer.init(period=time_ms, mode=machine.Timer.PERIODIC, callback=self.interrupt_handler)

    def _start_oneshot_timer(self, time_ms)
            self.timer.init(period=time_ms, mode=machine.Timer.ONE_SHOT, callback=self.interrupt_handler)

    def stop(self):
        self.timer.deinit()

    def update(self, time_ms):
        self.start(time_ms)


class Button(object):
    def __init__(self, pin, interrupt_handler):
        self.button = machine.Pin(pin, machine.Pin.IN)
        self.button.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=interrupt_handler)


def get_random(minimum, maximum):
    if maximum < minimum:
        real_maximum = minimum
        minimum = maximum
        maximum = real_maximum
    max_int_value = 4294967295
    rand = int(os.urandom(4).hex(), 16)
    # y = mx + b
    value = ((rand - minimum) / max_int_value) * (maximum - minimum) + minimum
    return int(value)


def get_pwm_value(percent):
    result = (1023 / 100) * percent
    return int(result)
