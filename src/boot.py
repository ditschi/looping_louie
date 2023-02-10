#!/usr/bin/env python3

# picocom /dev/ttyUSB0 -b115200
from hw_control import led
from wifi import wifi



def main():
    wifi.connect()
        # we tried everything to connect to a known network
    if wifi.is_connected():
        led.onboard_led_blink(3)
    else:
        # still not connected. Probably no known network is available
        # we open a access point to be able to connect
        wifi.open_access_point()
        led.onboard_led_on()


main()
