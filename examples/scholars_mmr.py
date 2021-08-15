"""
Get the rank and MMR for all the scholars, sorted by best to worst.
"""

import yaml
from pyaxie import pyaxie

# Load the config
with open("secret.yaml", "r") as file:
    config = yaml.safe_load(file)

# Create a pyaxie instance with the first scholar set up in your config
print("Getting rank and mmr for all the scholars... The more scholars you have, the longer it will be.")
l = list()
for account in config['scholars']:
    scholar = pyaxie(config['scholars'][account]['ronin_address'], config['scholars'][account]['private_key'])
    print('Getting datas for', scholar.name)
    rank_mmr = scholar.get_rank_mmr(scholar.ronin_address)
    rank_mmr['name'] = scholar.name
    l.append(rank_mmr)

print("\nSCHOLAR SORTED BY RANK \n")
ranks = sorted(l, key=lambda k: k['rank'])
for r in ranks:
    print("{} | {}".format(r['name'], r['rank']))

print("\nSCHOLAR SORTED BY MMR\n")
mmrs = reversed(sorted(l, key=lambda k: k['mmr']))
for m in mmrs:
    print("{} | {}".format(m['name'], m['mmr']))
