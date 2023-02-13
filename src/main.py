
# import machine
# import socket
# import time
# import network
# from hardware.Motor import MotorConfig
# from hardware.LoopingLouie import LoopingLouie
# from hardware.Led import OnboardLed
try:
    from hardware.Motor import MotorConfig
    from hardware.LoopingLouie import LoopingLouie
    from hardware.Led import OnboardLed
except ImportError:
    import sys
    sys.path.append('/hardware/')
    from Motor import MotorConfig
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


def main():
    print("main()")
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
