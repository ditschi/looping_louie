import time
import machine
from hw_config import ONBOARD_LED_PIN


class Led():
    def __init__(self, led_pin: int):
        self.led_pin = led_pin
        self.__init()
        self.active = None

    def __init(self):
        self.machine_pin = machine.Pin(ONBOARD_LED_PIN, machine.Pin.OUT)

    def on(self):
        self.led_pin.on()
        self.active = True

    def off(self):
        self.led_pin.off()
        self.active = False

    def toggle(self):
        if self.active:
            self.off()
        else:
            self.on()

    def blink(self, count, interval_seconds=0.3):
        self.off() # for ESP onboard led on/off are reversed
        for _ in range(count):
            self.on()  # for ESP onboard led on/off are reversed
            time.sleep(interval_seconds)
            self.off()  # for ESP onboard led on/off are reversed
            time.sleep(interval_seconds)


class OnboardLed():
    def __init__(self):
        self.led = Led(ONBOARD_LED_PIN)

    @property
    def active(self):
        return self.led.active

    def on(self):
        self.led.off()  # for ESP onboard led on/off are reversed

    def off(self):
        self.led.off()  # for ESP onboard led on/off are reversed

    def toggle(self):
        if self.active:
            self.off()
        else:
            self.on()

    def blink(self, count, interval_seconds=0.3):
        self.off() # for ESP onboard led on/off are reversed
        for _ in range(count):
            self.on()  # for ESP onboard led on/off are reversed
            time.sleep(interval_seconds)
            self.off()  # for ESP onboard led on/off are reversed
            time.sleep(interval_seconds)
