import logging

import netifaces as ni

# Setup Logger
logger = logging.getLogger()

def get_ip_address() -> str:

    # Get gateway of the network
    gws = ni.gateways()
    try:
        default_gw_name = gws["default"][ni.AF_INET][1]
        # Get the ip in the default gateway
        ip = ni.ifaddresses(default_gw_name)[ni.AF_INET][0]["addr"]
    except KeyError:
        ip = "127.0.0.1"

    return ip
