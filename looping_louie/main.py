
# import machine
# import socket
# import time
# import network
# from hardware.Motor import MotorConfig
# from hardware.LoopingLouie import LoopingLouie
# from hardware.Led import OnboardLed
try:
    from hardware.Motor import Motor, MotorConfig
    from hardware.Button import OnboardButton
    from hardware.LoopingLouie import LoopingLouie
    from hardware.Led import OnboardLed
except ImportError:
    import sys
    sys.path.append('/hardware/')
    from Motor import Motor, MotorConfig
    from Button import OnboardButton
    from LoopingLouie import LoopingLouie
    from Led import OnboardLed


# def on_off_switch_interrupt_handler():
#     led = OnboardLed()
#     led.toggle()

# def game_timer_interrupt_handler():
#     led = OnboardLed()
#     led.toggle()

# def motor_timer_interrupt_handler():
#     led = OnboardLed()
#     led.toggle()

motor = Motor(2, MotorConfig(False, 5, 100))


def short_press():
    speed = (motor.speed_set + 20) % 100
    motor.set_speed_in_percent(speed)


def long_press():
    if motor.running:
        motor.stop()
    else:
        motor.start(100)


def main():
    button = OnboardButton(short_press, long_press)
    # motor_config = MotorConfig(limit_speedchange=False)
    # louie = LoopingLouie(on_off_switch_interrupt_handler, game_timer_interrupt_handler, motor_config=motor_config)
    # #louie.motor.start(50)
    # led = OnboardLed()
    # led.blink(5)
    # led.off()


if __name__ in "__main__":
    print("DEBUG | running main.py")
    main()
    print("DEBUG | running main.py")
