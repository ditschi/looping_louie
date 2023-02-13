import time
import network
import ujson as json


KNOWN_NETWORKS_FILEPATH = "networks.json"

AP_ESSID = "LoopingLouie"
AP_PASS = "LoopingLouie"

sta_if = network.WLAN(network.STA_IF)

def connect() -> bool:
    print("DEBUG | Trying to connect to wifi network")
    available_networks = networks_known_and_available()
    if available_networks:
        for network_ssid, network_secret in available_networks:
            connect_to_network(network_ssid, network_secret)
            if sta_if.isconnected():
                # we have a connection. We can stop...
                return True
    return False


def networks_known_and_available() -> dict:
    print("DEBUG | Checking for available known networks")
    sta_if.active(True)
    available_networks = [network[0].decode("utf-8") for network in sta_if.scan()]
    print(f"DEBUG | Found {len(available_networks)} available networks")
    for network in available_networks:
        print(f"DEBUG |  - '{network}'")

    known_networks = get_known_and_available(available_networks)
    return known_networks


def connect_to_network(ssid, secret) -> None:
    await_connection_delay = 10
    if sta_if.isconnected():
        print("INFO | Already connected to wifi network")
        return

    print(f"DEBUG | Trying to connect to network '{ssid}'")
    sta_if.active(True)
    sta_if.connect(ssid, secret)
    for _ in range(await_connection_delay):
        time.sleep(1)
        if sta_if.isconnected():
            print(f"INFO | Successfully connected to '{ssid}'")
            set_ip_address_last_value(66)
            return
    print(f"DEBUG | Could not connect to network '{ssid}'")
    return 1

def set_ip_address_last_value(last_value):
    ifconfig = list(sta_if.ifconfig())
    current_ip = ifconfig[0]
    # generating new ip with known ending
    new_ip = current_ip.split(".")
    new_ip[3] = str(last_value)
    new_ip = ".".join(new_ip)

    # replacing IP in current config
    ifconfig[0] = new_ip
    # setting new IP
    sta_if.ifconfig(ifconfig)
    print(f"DEBUG | IP was changed to '{new_ip}'")


def open_access_point():
    print(f"INFO | Activating access point '{AP_ESSID}'")
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)
    ap_if.config(essid=AP_ESSID, authmode=network.AUTH_WPA_WPA2_PSK, password=AP_PASS)
    # fixed_ip = "192.168.0.1"
    # ifconfig = list(ap_if.ifconfig())
    # ifconfig[0] = fixed_ip
    # ap_if.ifconfig(ifconfig)


def is_connected():
    return sta_if.isconnected()


def get_known_and_available(available_networks):
    known_and_available = []

    for known_network in get_known_networks().items():
        if known_network[0] in available_networks:
            known_and_available.append(known_network)
    print(f"DEBUG | Found {len(known_and_available)} known networks available")
    return known_and_available


def get_known_networks(filename=KNOWN_NETWORKS_FILEPATH):
    networks = load_network_config(filename)['networks']
    print(f"DEBUG | Found {len(networks)} known networks in configuration")
    return networks


def save_known_networks(networks):
    save_network_config(networks, filename=KNOWN_NETWORKS_FILEPATH+".test.json")


def save_network_config(networks, filename: str):
    print(f"DEBUG | Writing known networks to '{filename}'")
    with open(filename, "w") as file:
        file.write(json.dumps(networks))


def load_network_config(filename: str):
    print(f"DEBUG | Reading known networks from '{filename}'")
    with open(filename) as file:
        return json.load(file)


def add_known_network(ssid, secret, filename=KNOWN_NETWORKS_FILEPATH):
    known_networks = get_known_networks(filename)
    known_networks[ssid] = secret
    save_network_config(known_networks, filename)
