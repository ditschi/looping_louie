#!/usr/bin/env python3

import unittest
import sys


class MockMachine(object):
    class Pin(object):
        IRQ_RISING = 0
        IRQ_FALLING = 0

        @staticmethod
        def __init__(dummy):
            pass

    class PWM(object):
        @staticmethod
        def __init__(dummy):
            pass

        @staticmethod
        def freq(dummy):
            return dummy

        @staticmethod
        def duty(dummy):
            return dummy

    class Timer(object):
        PERIODIC = 0
        ONE_SHOT = 0

        def __init__(self, timer):
            self.timer = timer
            self.period = None

        def init(self, period, mode, callback):
            self.period = period
            callback()

        def deinit(self):
            self.period = None
            pass


sys.modules['machine'] = MockMachine()

try:
    from hw_control import hw_control
    from gamemode import gamemode
except:
    import os
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from hw_control import hw_control
    from gamemode import gamemode


def get_all_modes():
    all_modes = []
    for speed_mode in gamemode.SPEED_MODES:
        speed_config = gamemode.Speed(mode=speed_mode, start=50, minimum=25, maximum=75,
                                      fixed_change=5, min_change=5, max_change=30, change_rate=5, change_delay=5)
        for time_mode in gamemode.TIME_MODES:
            time_config = gamemode.Time(mode=time_mode, fixed=5, min_delay=500, max_delay=2000)

            test_gamemode = gamemode.GameMode(f"{speed_mode}::{time_mode}", speed_config, time_config)
            all_modes.append(test_gamemode)

    return all_modes


class TestMotor(unittest.TestCase):
    def setUp(self):
        self.motor = hw_control.Motor(1)
        self.motor.__set_speed__ = self.set_speed_mock


    def set_speed_mock(self):
        self.motor.current_speed = self.motor.new_speed
        self.motor.speed_config.current = self.motor.new_speed
        return self.motor.current_speed

    def test_start(self):
        for mode_config in get_all_modes():
            try:
                result = self.motor.start(mode_config.speed)
                self.assertEqual(result, mode_config.speed.start)
                self.assertEqual(self.motor.speed_config.current, mode_config.speed.start)
                self.assertEqual(self.motor.current_speed, mode_config.speed.start)

            except Exception as ex:
                print(f"error testing motor: {mode_config.name}")
                raise ex

    def test_stop(self):
        for mode_config in get_all_modes():
            try:
                self.motor.speed_config = mode_config.speed
                self.motor.stop()
                self.assertEqual(self.motor.current_speed, 0)
                self.assertEqual(self.motor.speed_config, None)
            except Exception as ex:
                print(f"error testing motor: {mode_config.name}")
                raise ex

    def test_update(self):
        for mode_config in get_all_modes():
            try:
                self.motor.start(mode_config.speed)
                for i in range(2000):
                    old_speed = self.motor.current_speed
                    self.motor.update()
                    if self.motor.speed_config.mode == "fixed":
                        self.assertEqual(self.motor.current_speed, old_speed)
                        self.assertEqual(self.motor.speed_config.current, old_speed)
                    elif self.motor.speed_config.mode == "constant_increase":
                        self.assertEqual(self.motor.new_speed, old_speed + self.motor.speed_config.fixed_change)
                        self.assertEqual(self.motor.current_speed, old_speed + self.motor.speed_config.fixed_change)
                        self.assertEqual(self.motor.speed_config.current, old_speed + self.motor.speed_config.fixed_change)
                    elif self.motor.speed_config.mode == "constant_decrease":
                        self.assertEqual(self.motor.new_speed, old_speed - self.motor.speed_config.fixed_change)
                        self.assertEqual(self.motor.current_speed, old_speed - self.motor.speed_config.fixed_change)
                        self.assertEqual(self.motor.speed_config.current, old_speed - self.motor.speed_config.fixed_change)
                    elif self.motor.speed_config.mode == "random":
                        self.assertIsNot(self.motor.current_speed, old_speed)
            except Exception as ex:
                print(f"error testing motor: {mode_config.name}")
                raise ex


class TestTimer(unittest.TestCase):
    def setUp(self):
        self.timer = hw_control.Timer(1, self.interrupt_mock)

    def interrupt_mock(self):
        pass

    def test_start(self):
        for mode_config in get_all_modes():
            try:
                self.timer.start(mode_config.time)
                self.assertEqual(self.timer.time_config, mode_config.time)
                if mode_config.time.mode == "fixed":
                    self.assertEqual(self.timer.period, mode_config.time.fixed)
                if mode_config.time.mode == "random":
                    self.assertLessEqual(self.timer.period, mode_config.time.max_delay)
                    self.assertGreaterEqual(self.timer.period, mode_config.time.min_delay)
            except Exception as ex:
                print(f"error testing timer: {mode_config.name}")
                raise ex


class TestGetRandom(unittest.TestCase):
    def test_no_range(self):
        for i in range(5000):
            result = hw_control.get_random(1, 1)
            self.assertEqual(result, 1)

    def test_small_range(self):
        for i in range(5000):
            result = hw_control.get_random(1, 5)
            self.assertLessEqual(result, 5)
            self.assertGreaterEqual(result, 1)

    def test_percent(self):
        for i in range(5000):
            result = hw_control.get_random(0, 100)
            self.assertLessEqual(result, 100)
            self.assertGreaterEqual(result, 0)

    def test_offset_range(self):
        for i in range(5000):
            result = hw_control.get_random(25, 100)
            self.assertLessEqual(result, 100)
            self.assertGreaterEqual(result, 25)

    def test_big_range(self):
        for i in range(2000):
            result = hw_control.get_random(500, 999999)
            self.assertLessEqual(result, 999999)
            self.assertGreaterEqual(result, 500)

    def test_min_max_switched(self):
        result = hw_control.get_random(100, 1)
        self.assertLessEqual(result, 100)
        self.assertGreaterEqual(result, 0)

    def test_different(self):
        not_different_cnt = 0
        old_value = None
        for i in range(5000):
            result = hw_control.get_random(0, 100)
            if old_value is result:
                not_different_cnt += 1
        self.assertLessEqual(not_different_cnt, 5)

class TestPwmValue(unittest.TestCase):
    def test_min(self):
        result = hw_control.get_pwm_value(0)
        self.assertEqual(result, 0)

    def test_max(self):
        result = hw_control.get_pwm_value(100)
        self.assertEqual(result, 1023)

    def test_middle(self):
        result = hw_control.get_pwm_value(50)
        self.assertEqual(result, 511)


if __name__ == '__main__':
    unittest.main()