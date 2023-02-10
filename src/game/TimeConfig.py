#!/usr/bin/env python3
from dataclasses import dataclass
from abc import ABC, abstractmethod
import random

@dataclass
class TimeConfig(ABC):
    time_ms_set: int = None

    @abstractmethod
    def get_next_time(self):
        pass


@dataclass
class TimeConfigFixed(TimeConfig):
    time_ms: int = None
    fixed: bool = False

    def get_next_time(self):
        return self.time_ms

@dataclass
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

@dataclass
class TimeConfigRandom(TimeConfig):
    allow_increase: bool = True
    allow_decrease: bool = True
    change_ms_min: int = 50
    change_ms_max: int = None
    time_ms_min: int = 500
    time_ms_max: int = 10*1000

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