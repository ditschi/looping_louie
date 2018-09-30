#!/usr/bin/env python3

"""
Startup script for ESP8266
This script will attempt scan for available known networks (configured in known_networks.py) and tries to connect if
possible. After connecting we set a the last digit of the IP to a known value (LAST_IP_ELEMENT).
The connection is indicated by flashing the onboard LED three times.

If connecting to a known network is not possible we open a Access point to be able to connect to the ESP8266.
The turned on onboard LED indicates the open access point.
"""

# mpfshell -o ttyUSB0
# picocom /dev/ttyUSB0 -b115200
import network
import time
import machine
from known_networks import KNOWN_NETWORKS

AP_ESSID = "LouieConnect"
AP_PASS = "LoopingLouie"

ONBOARD_LED_PIN = 2   # Onboard Led Esp8266
LAST_IP_ELEMENT = 66  # Last element of the IP addres which is set as static IP


sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)


debug_output = ""


def output(text):
    global debug_output
    debug_output += text + "\n"
    print(text)


def main():
    try:
        available_networks = known_networks_available()
        if available_networks:
            for network in available_networks:
                connect_to_network(network)
                if sta_if.isconnected():
                    # we have a connection. We can stop...
                    break

        # we tried everything to connect to a known network
        if not sta_if.isconnected():
            # still not connected. Probably no known network is available
            # we open a access point to be able to connect
            open_access_point()
            onboard_led_on()
        else:
            onboard_led_blink(3)

    finally:
        output("Boot finished!")
        write_log_file()
        print("Boot logfile saved.")


def write_log_file():
    global debug_output
    f = open('boot.log', 'w')
    f.write(debug_output)
    f.close()


def known_networks_available():
    output("Checking for available known networks")
    sta_if.active(True)
    networks = sta_if.scan()

    known_and_available = []

    for network in networks:
        for known in KNOWN_NETWORKS:
            if known[0] in network[0]:
                known_and_available.append(known)
    return known_and_available


def connect_to_network(network):
    await_connection_delay = 10
    if sta_if.isconnected():
        output("Already connected")
        return

    output("Trying to connect to network '{}'...".format(network[0]))
    sta_if.active(True)
    sta_if.connect(network[0], network[1])
    for i in range(await_connection_delay):
        time.sleep(1)
        if sta_if.isconnected():
            output("Successfully connected to '{}'".format(network[0]))
            set_ip_address(LAST_IP_ELEMENT)

            return
    output("[E] Could not connect to any known network")
    return 1


def set_ip_address(last_value):
    ifconfig = sta_if.ifconfig()
    current_ip = ifconfig[0]

    # generating new ip with known ending
    new_ip = current_ip.split(".")
    new_ip[3] = str(last_value)
    new_ip = ".".join(new_ip)

    # replacing IP in current config
    lst = list(ifconfig)
    lst[0] = new_ip
    ifconfig = tuple(lst)

    # setting new IP
    sta_if.ifconfig(ifconfig)
    #sta_if.config(config=ifconfig)
    output("IP was changed to '{}'".format(new_ip))
    print(sta_if.ifconfig())



def onboard_led_on():
    led = machine.Pin(ONBOARD_LED_PIN, machine.Pin.OUT)
    led.off()  # for ESP onboard led on/off are reversed


def onboard_led_blink(count):
    led = machine.Pin(ONBOARD_LED_PIN, machine.Pin.OUT)
    for i in range(count):
        led.off()  # for ESP onboard led on/off are reversed
        time.sleep(0.3)
        led.on()  # for ESP onboard led on/off are reversed
        time.sleep(0.3)


def open_access_point():
    output("Activating access point '{}'".format(AP_ESSID))
    ap_if.active(True)

    ifconfig = ap_if.ifconfig()

    # generating new ip with known ending
    new_ip = "192.168.0.1"

    # replacing IP in current config
    lst = list(ifconfig)
    lst[0] = new_ip
    ifconfig = tuple(lst)

    # settung up access point
    ap_if.ifconfig(ifconfig)
    ap_if.config(essid=AP_ESSID, authmode=network.AUTH_WPA_WPA2_PSK, password=AP_PASS)
    output("Access point '{}' open.  -> available under '{}'".format(AP_ESSID, new_ip))


main()
