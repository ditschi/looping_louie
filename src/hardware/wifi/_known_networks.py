import yaml

def get_known_and_available(available_networks):
    known_and_available = []

    for available_network in available_networks:
        for known in get_known_networks():
            if known.key in available_network[0]:
                known_and_available.append(known)
    return known_and_available

def get_known_networks(filename="networks.yml"):
    return load_network_config(filename)['networks']

def save_network_config(filename, config):
    with open(filename, "w") as file:
        yaml.dump(config, file)

def load_network_config(filename):
    with open(filename, "r") as file:
        return yaml.load(file)
