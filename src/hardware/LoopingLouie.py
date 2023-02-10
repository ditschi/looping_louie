import os
try:
    from hardware.Button import Button
    from hardware.Motor import Motor, MotorConfig
    from hardware.Timer import Timer
    from hardware.hw_config import MOTOR_TIMER, GAME_TIMER, ON_OFF_BUTTON_PIN, MOTOR_PIN
except ImportError:
    import sys
    sys.path.append('/hardware/')
    from Button import Button
    from Motor import Motor, MotorConfig
    from Timer import Timer
    from hw_config import MOTOR_TIMER, GAME_TIMER, ON_OFF_BUTTON_PIN, MOTOR_PIN


class LoopingLouie():
    def __init__(self, on_off_switch_interrupt_handler, gameplay_timer_interrupt_handler, motor_config: dict = None):
        self.motor = Motor(MOTOR_PIN, motor_config)
        self.start_stop_button = Button(ON_OFF_BUTTON_PIN, on_off_switch_interrupt_handler)
        self.game_timer = Timer(GAME_TIMER, gameplay_timer_interrupt_handler)

    def init_new_game(self, game_config):
        pass

    def set_motor_config(self, config: MotorConfig):
        self.motor.set_config(config)

    def start_game_timer(self, config: TimeConfig):
        periodic = config["periodic"] or False
        if config["random"]:

        #self.timer.start(, )







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
