"""
Get the list of every axies present on your scholars accounts
"""

import yaml
from pyaxie import pyaxie
from pprint import pprint
# Load the config
with open("secret.yaml", "r") as file:
    config = yaml.safe_load(file)

# Create a pyaxie instance with the first scholar set up in your config
l = list()
for account in config['scholars']:
    scholar = pyaxie(config['scholars'][account]['ronin_address'], config['scholars'][account]['private_key'])
    print('Getting datas for', scholar.name)
    axie_list = scholar.get_axie_list(scholar.ronin_address)
    for a in axie_list:
        l.append(scholar.axie_link(a['id']))

pprint(l)