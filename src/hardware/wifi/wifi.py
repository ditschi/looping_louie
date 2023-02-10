#!/usr/bin/env python3

# picocom /dev/ttyUSB0 -b115200
import hardware._known_networks as _known_networks
import network

AP_ESSID = "LouieConnect"
AP_PASS = "LoopingLouie"


sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)


debug_output = ""

def connect():
    available_networks = networks_known_and_available()
    if available_networks:
        for available_network in available_networks:
            connect_to_network(available_network.key, available_network.value)
            if sta_if.isconnected():
                # we have a connection. We can stop...
                return True
    return False


def networks_known_and_available():
    print("Checking for available known networks")
    sta_if.active(True)
    available_networks = sta_if.scan()
    return _known_networks.get_known_and_available(available_networks)


def connect_to_network(ssid, secret):
    await_connection_delay = 10
    if sta_if.isconnected():
        output("Already connected")
        return

    print(f"Trying to connect to network '{ssid}'...")
    sta_if.active(True)
    sta_if.connect(ssid, secret)
    for _ in range(await_connection_delay):
        time.sleep(1)
        if sta_if.isconnected():
            print(f"Successfully connected to '{ssid}'")
            set_ip_address(66)
            return
    print("[E] Could not connect to any known network")
    return 1

def set_ip_address(last_value):
    ifconfig = sta_if.ifconfig()
    current_ip = ifconfig[0]
    # generating new ip with known ending
    new_ip = current_ip.split(".")
    print(new_ip)
    new_ip[3] = str(last_value)
    new_ip = ".".join(new_ip)

    # replacing IP in current config
    ifconfig[0] = new_ip
    # setting new IP
    sta_if.ifconfig(ifconfig)
    print(f"IP was changed to '{new_ip}'")


def open_access_point():
    print(f"Activating access point '{AP_ESSID}'")
    ap_if.active(True)
    ifconfig = ap_if.ifconfig()
    new_ip = "192.168.0.1"
    ifconfig[0] = new_ip
    # setting new IP
    ap_if.ifconfig(ifconfig)
    ap_if.config(essid=AP_ESSID, authmode=network.AUTH_WPA_WPA2_PSK, password=AP_PASS)


def is_connected():
    return sta_if.isconnected()
