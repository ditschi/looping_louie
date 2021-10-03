#!/usr/bin/env python3

import sys
from gamemode import gamemode
from hw_control import hw_control


default_game = gamemode.GameMode(gamemode.Speed("fixed", start=75), gamemode.Time("off"), gamemode.Time("off"))


class LoopingLouie(object):
    def __init__(self):
        self.hw = hw_control.LoopingLouie(self.on_off_switch_interrupt_handler, self.gameplay_timer_interrupt_handler)
        self.game = Game(self.hw, default_game)

    def on_off_switch_interrupt_handler(self, button):
        if button.value() == 0:
            self.game.stop()
        elif button.value() == 1:
            self.game.start()
        else:
            print(f"[E] Invalid Button state '{button.value()}'.")
            sys.exit(1)
        pass

    def gameplay_timer_interrupt_handler(self):
        self.game.update()


class Game(object):
    def __init__(self, hw: hw_control.LoopingLouie, game_config: gamemode.GameMode):
        self.active = False
        self.hw = hw
        self.game_config = game_config

    def start(self):
        self.game_config.speed.current = self.game_config.speed.start
        # start motor with initial speed
        self.hw.motor.start(self.game_config.speed.start)
        # set needed timer
        self.hw.game_timer.start(self.game_config.time)
        self.active = True

    def stop(self):
        self.hw.motor.stop()
        self.hw.game_timer.stop()
        self.active = False

    def update(self):
        self.__update_speed__()
        self.__update_time__()

    def __update_speed__(self):
        self.game_config.speed.current = self.hw.motor.update()

    def __update_time__(self):
        self.game_config.time.current = self.hw.game_timer.update()
