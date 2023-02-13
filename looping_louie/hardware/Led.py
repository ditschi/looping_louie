import time
import machine

try:
    from hardware.hw_config import ONBOARD_LED_PIN
except ImportError:
    import sys
    sys.path.append('/hardware/')
    from hw_config import ONBOARD_LED_PIN


class Led:
    def __init__(self, pin: int, pin_state_on=True):
        self.__pin = pin
        self.__pin_state_on = pin_state_on
        self.__led = machine.Pin(self.__pin, machine.Pin.OUT)
        self.off()

    @property
    def active(self):
        print(f"DEBUG | LED {self.__pin} value is {self.__led.value()}")
        return bool(self.__led.value()) == self.__pin_state_on

    def on(self):
        if self.__pin_state_on:
            self.__led.on()
        else:
            self.__led.off()
        # value = int(not self.pin_state_on)
        # self.__led.value(value)
        print(f"DEBUG | LED {self.__pin} turned on")

    def off(self):
        if self.__pin_state_on:
            self.__led.off()
        else:
            self.__led.on()
        # value = int(not self.pin_state_on)
        # self.__led.value(value)
        print(f"DEBUG | LED {self.__pin} turned off")

    def toggle(self):
        if self.active:
            self.off()
        else:
            self.on()

    def blink(self, count, interval_ms=300):
        self.on()
        sleep_time = interval_ms/1000
        for _ in range((count*2)-1):
            time.sleep(sleep_time)
            self.toggle()
        self.off()


class DimmableLed:
    def __init__(self, pin: int, pin_state_on=True):
        self.__pin = pin
        self.__pin_state_on = pin_state_on
        self.brightness_percent = None
        self.__init_pwm()
        self.off()

    def __init_pwm(self):
        self.__pwm = machine.PWM(machine.Pin(self.__pin))
        self.__pwm.freq(1000)
        self.__pwm.duty(0)

    @property
    def active(self):
        off_value = 0 if self.__pin_state_on else 1023
        return self.__pwm.duty() != off_value

    def set_brightness(self, percent):
        print(f"DEBUG | LED {self.__pin}  brightness set to {percent} percent")
        pwm_value = self.__get_pwm_value(percent)
        self.__pwm.duty(pwm_value)
        self.brightness_percent = percent

    def on(self, brightness_percent=100):
        self.set_brightness(brightness_percent)

    def off(self):
        self.set_brightness(0)

    def __get_pwm_value(self, percent: int):
        # duty cycle is between 0 (all off) and 1023 (all on)
        result = (1023 / 100) * percent
        if not self.__pin_state_on:
            result = 1023 - result
        return int(result)

    def toggle(self, brightness_percent=100):
        if self.active:
            self.off()
        else:
            self.on(brightness_percent)

    def blink(self, count, brightness_percent=100, interval_ms=300):
        self.on(brightness_percent)
        sleep_time = interval_ms/1000
        for _ in range((count*2)-1):
            time.sleep(sleep_time)
            self.toggle(brightness_percent)
        self.off()


class OnboardLed(DimmableLed):
    def __init__(self):
        super().__init__(ONBOARD_LED_PIN, pin_state_on=True)


# RGB LED -- https://randomnerdtutorials.com/micropython-ws2812b-addressable-rgb-leds-neopixel-esp32-esp8266/
# import neopixel
# led_count = 1
# led_strip_pin = 1
# led_strip = neopixel.NeoPixel(machine.Pin(led_strip_pin), led_count)
# # turn on led 0
# led_strip[0] = (255, 0, 0)
# led_strip.write()
