#!/usr/bin/env python3


TIME_MODES = ("off", "fixed", "random")



class TimeController():
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

class InfiniteTimeController():


class FixedTimeController():


class RandomTimeController():
