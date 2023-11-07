#!/usr/bin/env python3
import random


class TimeConfig:
    def __init__(self, time_sec: int):
        self.time_sec: int = time_sec


class TimeControllerConstantChange(TimeConfig):
    def __init__(self, start_time_sec: int = 0, end_time_sec: float = 10 * 1000, change_sec: float = 1,
                 reverse_at_limit = False):
        super().__init__(start_time_sec)
        self.start_time_sec = start_time_sec
        self.end_time_sec = end_time_sec
        self.change_sec = change_sec
        self.reverse_at_limit = reverse_at_limit
        self.reversed = False

    def __next__(self):
        self.time_sec = self.time_sec + self.change_sec if self.__is_increase else self.time_sec - self.change_sec

        if self._max_reached():
            self.time_sec = self.__currrent_end
            if self.reverse_at_limit:
                self.reversed = not self.reversed if self.reverse_at_limit else self.reversed
        return self.time_sec

    @property
    def __is_increase(self):
        return self.__currrent_start < self.__currrent_end

    @property
    def __currrent_start(self):
        return self.start_time_sec if not self.reversed else self.end_time_sec

    @property
    def __currrent_end(self):
        return self.end_time_sec if not self.reversed else self.start_time_sec

    def _max_reached(self):
        if self.__is_increase:
            return self.time_sec >= self.__currrent_end
        return self.time_sec <= self.__currrent_end

    def get_next_time(self):
        if self.__is_increase:
            return self.time_ms_set

class TimeConfigLinear(TimeConfig):
    change_in_ms: int = False
    start_ms: int = 500
    end_ms: int = 10*1000

    @property
    def __is_increase(self):
        return self.start_ms < self.end_ms

    def get_next_time(self):
        if self.__is_increase:

            return self.time_ms_set

class TimeConfigRandom(TimeConfig):
    allow_increase: bool = True
    allow_decrease: bool = True
    min_time_sec = 0.5
    max_time_sec = 10 * 1000
    max_change_sec = 0

    def __post_init__(self):
        pass

    def get_next_time(self):
        return self.__get_change_value

    @property
    def __is_increase(self):
        if self.allow_increase and self.allow_decrease:
            return bool(random.getrandbits(1))
        return self.allow_increase

    def __get_change_value(self):

        min_change = self.change_ms_min if self.change_ms_min else 0
        max_change = self.change_ms_max if self.change_ms_max else 0
        change = random.randint(min_change, max_change)