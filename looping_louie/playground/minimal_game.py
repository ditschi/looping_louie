def short_press():
    speed = (motor.speed_set + 20) % 100
    motor.set_speed_in_percent(speed)


def long_press():
    if motor.running:
        motor.stop()
    else:
        motor.start(100)


def main():




if __name__ in "__main__":
    main()