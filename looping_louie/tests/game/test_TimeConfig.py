import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from game.TimeConfig import TimeControllerConstantChange


class TestTimeControllerConstantChange:
    def test_initial_time(self):
        time_config = TimeControllerConstantChange(10, 100, 5)
        assert 10 == time_config.time_sec
        time_config = TimeControllerConstantChange(123, 0, 5)
        assert 123 == time_config.time_sec

    def test_next_time_at_limit(self):
        time_config = TimeControllerConstantChange(10, 100, 5)
        time_config.time_sec = 90
        assert next(time_config) == 95
        assert next(time_config) == 100
        assert next(time_config) == 100

    def test_next_time_at_limit_with_reversed(self):
        time_config = TimeControllerConstantChange(0, 100, 5)
        time_config.time_sec = 90
        time_config.reverse_at_limit = True
        assert next(time_config) == 95
        assert next(time_config) == 100
        assert next(time_config) == 95
        time_config.time_sec = 10
        assert next(time_config) == 5
        assert next(time_config) == 0
        assert next(time_config) == 5

    def test_stays_inside_limit(self):
        time_config = TimeControllerConstantChange(0, 100, 1000)
        assert next(time_config) == 100
        assert next(time_config) == 100
        time_config.reversed = True
        assert next(time_config) == 0
        assert next(time_config) == 0

    def test__max_reached(self):
        time_config = TimeControllerConstantChange(10, 100, 5)
        time_config.time_sec = 100
        assert time_config._max_reached()

        time_config.time_sec = 99
        assert not time_config._max_reached()

    def test__max_reached_reversed(self):
        time_config = TimeControllerConstantChange(10, 100, 5)
        time_config.reversed = True

        time_config.time_sec = 100
        assert not time_config._max_reached()

    def test_higher_start_value(self):
        time_config = TimeControllerConstantChange(100, 10, 5)
        assert 95 == next(time_config)
        assert 90 == next(time_config)

        time_config.time_sec = 20
        assert 15 == next(time_config)
        assert 10 == next(time_config)
        assert 10 == next(time_config)

        time_config.reversed = True
        assert 15 == next(time_config)
        time_config.time_sec = 90
        assert 95 == next(time_config)
        assert 100 == next(time_config)
        assert 100 == next(time_config)
