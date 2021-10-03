#!/usr/bin/env python3
import sys

SPEED_MODES = ("fixed", "constant_increase", "constant_decrease", "random", "random_increase", "random_decrease")
TIME_MODES = ("off", "fixed", "random")


class GameMode(object):
    def __init__(self, name, speed_config, time_config):
        self.name = name
        self.speed = speed_config
        self.time = time_config


class Speed(object):
    current = 0

    def __init__(self, mode, start, minimum=0, maximum=0,
                 fixed_change=0, min_change=0, max_change=0, change_rate=0, change_delay=0):
        if mode not in SPEED_MODES:
            print(f"[E] speed mode '{mode} not supported.")
        self.mode = mode
        self.start = start
        self.minimum = minimum
        self.maximum = maximum
        self.fixed_change = fixed_change
        self.min_change = min_change
        self.max_change = max_change
        self.change_rate = change_rate
        self.change_delay = change_delay

        if mode not in SPEED_MODES:
            print(f"[E] Specified speed mode {mode} not supported")
            sys.exit(1)


class Time(object):
    mode = None
    current = None
    min_delay = None
    max_delay = None
    fixed = None

    def __init__(self, mode, fixed=0, min_delay=0, max_delay=0):
        if mode not in TIME_MODES:
            print(f"[E] time mode '{mode} not supported.")
        self.mode = mode
        self.fixed = fixed
        self.min_delay = min_delay
        self.max_delay = max_delay

        if mode not in TIME_MODES:
            print(f"[E] Specified speed mode {mode} not supported")
            sys.exit(1)
