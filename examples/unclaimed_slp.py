"""
Get the amount of unclaimed SLP for every scholars in the secret.yaml file
"""

import yaml
from pyaxie import pyaxie

# Load the config
with open("secret.yaml", "r") as file:
    config = yaml.safe_load(file)

# Create a pyaxie instance with the first scholar set up in your config
for account in config['scholars']:
    scholar = pyaxie(config['scholars'][account]['ronin_address'], config['scholars'][account]['private_key'])
    unclaimed_slp = scholar.get_unclaimed_slp(scholar.ronin_address)
    print("{} unclaimed SLP for {} : {}".format(unclaimed_slp, scholar.name, scholar.ronin_address))
