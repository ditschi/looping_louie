
import game.ChangeController.ChangeController as ChangeController

class Game:
    def __init__(self, hardware, speed:ChangeController, time: ChangeController = None):
        self.hardware = hardware
        self.speed = speed
        self.time = time

    def start(self):
        pass

    def update(self):
        new_speed = self.speed.get_new_value()
        new_time = self.time.get_new_value()
        self.hardware.set_speed(new_speed)
        self.hardware.set_timer(new_time)
