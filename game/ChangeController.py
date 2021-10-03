#!/usr/bin/env python3

import sys
from abc import ABC, abstractmethod
import random


change_types = {
    "Constant": {"Value"},
    "Constant to End": {"Start", "End"},
    "Random to End": {"Start", "End",  "Minimum Change", "Maximum Change"},
    "Random": {"Start", "Minimum", "Maximum", "Minimum Change", "Maximum Change"},
    }



class ChangeController(ABC):
    """Class for controlling a changing value"""
    def __init__(self):
        self.current = None

    @abstractmethod
    def get_new_value(self):
        """Returns the (next) value"""
        pass


class Deactivated(ChangeController):
    """Not used value"""

    def get_new_value(self):
        return None

class Constant(ChangeController):
    """Not changing value"""

    def __init__(self, value):
        self.value = value

    def get_new_value(self):
        return self.value


class ToEndController(ChangeController):
    def __init__(self, start=0, end=100):
        self.start = start
        self.current = start
        self.end = end

    @property
    def _is_increase(self):
        return self.start < self.end

    @property
    def _end_is_reached(self,):
        if self._is_increase:
            return True if self.current >= self.end else False
        else:
            return True if self.current <= self.end else False

    def _get_next_value(self, change):
        if self._is_increase:
            self.current += change
        else:
            self.current -= change

        if self._end_is_reached:
            self.current = self.end

        return self.current

class MinMaxChangeController(ChangeController):
    """Change within a certain range"""

    def __init__(self, limit_1, limit_2=None, min_change=None, max_change=None):
        self._limit_1 = limit_1
        self._limit_2 = limit_2 if limit_2 else self._limit_1
        self._min_change = min_change
        self._max_change = max_change

    @property
    def upper_limit(self):
            return max(self._limit_1, self._limit_2)

    @property
    def lower_limit(self):
            return min(self._limit_1, self._limit_2)


    @property
    def min_change(self):
        return self._min_change if self._min_change else 0

    @property
    def max_change_down(self):
        if self._max_change:
            return self._max_change
        return abs(self.current - self.lower_limit)

    @property
    def max_change_up(self):
        if self._max_change:
            return self._max_change
        return abs(self.current - self.upper_limit)


class ConstantToEnd(ToEndController):
    """Constant change until end is reached"""

    def __init__(self, start=0, end=100, change_rate=1):
        super.__init__(start, end)
        self.change_rate = change_rate

    def get_new_value(self):
        return self._get_next_value(self.change_rate)


class RandomToEnd(ToEndController, MinMaxChangeController):
    """Random change until end is reached"""

    def __init__(self, start=0, end=0, min_change=None, max_change=None):
        ToEndController.__init__(self, start, end)
        MinMaxChangeController.__init__(self, limit_1=end, min_change=min_change, max_change=max_change)


    def get_new_value(self):
        change = random.randint(self.min_change, self.max_change_up)

        return self._get_next_value(change)


class Random(ChangeController, MinMaxChangeController):
    """Random increase and decrease"""

    def __init__(self, start=None, min=0, max=100, min_change=None, max_change=None):
        MinMaxChangeController.__init__(self, limit_1=min, limit_2=max, min_change=min_change, max_change=max_change)
        self.min = min
        self.max = max
        self.current = start if start else random.randint(self.min, self.max)


    @staticmethod
    def _random_increase_decrease():
        if random.randint(0, 1) == 1:
            return True
        return False

    def get_new_value(self):
        while True:
            if self._random_increase_decrease():
                speed_change = random.randint(self.min_change, self.max_change_up)
                new_speed = self.current + speed_change
            else:
                speed_change = random.randint(self.min_change, self.max_change_down)
                new_speed = self.current - speed_change

            if self.max <= new_speed <= self.max:
                self.current = new_speed
                return self.current
