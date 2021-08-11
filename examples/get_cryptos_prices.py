"""
Display Axie's prices for AXS, SLP and ETH
"""

import yaml
from pyaxie import pyaxie

# Load the config
with open("secret.yaml", "r") as file:
    config = yaml.safe_load(file)

# Create a pyaxie instance with the first scholar set up in your config
pyax = pyaxie(config['personal']['ronin_address'])

# Display Axie's prices for AXS, SLP and ETH
print("ETH = " + str(pyax.get_price('eth')))
print("SLP = " + str(pyax.get_price('slp')))
print("AXS = " + str(pyax.get_price('axs')))
