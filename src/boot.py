
#!/usr/bin/env python3

# picocom /dev/ttyUSB0 -b115200  (exit = ctrl + a q)

try:
    from hardware.Led import OnboardLed
    from hardware import wifi
except ImportError:
    import sys
    sys.path.append('/hardware/')
    from Led import OnboardLed
    import wifi

def main():
    wifi.connect()
    led = OnboardLed()
        # we tried everything to connect to a known network
    if wifi.is_connected():
        led.blink(3)
    else:
        # still not connected. Probably no known network is available
        # we open a access point to be able to connect
        wifi.open_access_point()
        led.on()


if __name__ in "__main__":
    print("DEBUG | running boot.py")

    main()

    print("DEBUG | finished boot.py")
