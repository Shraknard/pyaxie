"""
Here is a demonstration on how to use the library.
You will find a test of every functions present in pyaxie.py consecutively.
"""

import yaml # To work with our yaml secret file
import random # To generate random numbers
from pyaxie import pyaxie # Import pyaxie lib to use axie functions
from pprint import pprint # For beutiful prints

##########################
#     AUTHENTICATION     #
##########################

# Get config datas
with open("secret.yaml", "r") as file:
    config = yaml.safe_load(file)

# Get 1st scholar datas from config
ronin_address = config['scholars'][0]['ronin_address']
private_key = config['scholars'][0]['private_key']

# Get a random axie ID to test the functions
rnd_id = random.randint(10000, 1000000)

# Create a pyaxie object
pyax = pyaxie(ronin_address, private_key)

"""
# YOU HAVE TO UNCOMMENT THE FUNCTIONS THAT YOU WANT TO TEST (You can uncomment all of them to see everything)

# Once a pyax object have been created, you can access some of it's data
pprint(pyax.ronin_address)
pprint(pyax.private_key)
pprint(pyax.access_token)

##########################
#     AUTHENTICATION     #
##########################


# Get the raw message for authentication
print("\n############### Raw message ##################")
raw_message = pyax.get_raw_message()
pprint(raw_message)

# Sign the raw message with your key
print("\n############### Sign message ##################")
signed_message = pyax.sign_message(raw_message, private_key)
pprint(signed_message)

# Sumbit the message to get an access token
print("\n############### Access Token ##################")
pprint(pyax.submit_signature(signed_message, raw_message))

# Generate a QR code from the token
print("\n############### Generate QR ##################")
pyax.get_qr_code()

# Get an access token (already stored in the pyax object)
print("\n############### Access Token ##################")
pprint(pyax.get_access_token())

# Prices from axie marketplace
print("\n############### Crypto Prices ##################")
pprint("ETH = " + str(pyax.get_price('eth')))
pprint("SLP = " + str(pyax.get_price('slp')))
pprint("AXS = " + str(pyax.get_price('axs')))

# Get profile information
print("\n############### Profile Data ##################")
pprint(pyax.get_profile_data())

# Get activity log
print("\n############### Activity Log ##################")
pprint(pyax.get_activity_log())

# Get profile name
print("\n############### Profile Name ##################")
pprint(pyax.get_profile_name(pyax.ronin_address))

# Get public profile
print("\n############### Public Profile ##################")
pprint(pyax.get_public_profile(pyax.ronin_address))

# Get axie list of a given account
print("\n############### Account axies list ##################")
pprint(pyax.get_axie_brief_list(pyax.ronin_address))

# Get axie image from axie id
print("\n############### Axie image ##################")
pprint(pyax.get_axie_image(rnd_id))

# Get information about specific axie
print("\n############### Axie detail ##################")
pprint(pyax.get_axie_detail(rnd_id))

# Save axie
print("\n############### Save axie ##################")
pyax.save_axie(pyax.get_axie_detail(rnd_id))
pyax.save_axie(pyax.get_axie_detail(rnd_id + 2))
pyax.save_axie(pyax.get_axie_detail(rnd_id + 4))

# Get information about locally stored axie
print("\n############### Axie detail ##################")
pprint(pyax.axie_detail(rnd_id))

print("\n############### Check axie ##################")
pprint(pyax.check_axie(rnd_id))
pprint(pyax.get_axie_detail(rnd_id))

# Get the local list of axies
print("\n############### Axie list ##################")
pprint(pyax.axie_list())

# Update the axie list with fresh data
print("\n############### Update axie list ##################")
pprint(pyax.update_axie_list())

# Get axie datas about specific thing
print("\n############### Axie specific info from web ##################")
pprint(pyax.get_axie_class(rnd_id))
pprint(pyax.get_axie_name(rnd_id))
pprint(pyax.get_axie_parts(rnd_id))
pprint(pyax.get_axie_image(rnd_id))
pprint(pyax.get_axie_stats(rnd_id))

# Get axie datas about specific thing
print("\n############### Axie specific info local ##################")
pprint(pyax.axie_infos(rnd_id, "class"))
pprint(pyax.axie_infos(rnd_id, "name"))
pprint(pyax.axie_infos(rnd_id, "parts"))
pprint(pyax.axie_infos(rnd_id, "image"))
pprint(pyax.axie_infos(rnd_id, "stats"))

# Rename an axie (need an ID from an axie that is in your account)
print("\n############### Rename axie ##################")
pprint(pyax.rename_axie(axie_id, 'yolo'))

# Get MMR and rank for given address
print("\n############### Get MMR / Rank ##################")
pprint(pyax.get_rank_mmr(ronin_address))

# Get a list of links of all your scholar's axies
print("\n############### Get scholars axies links ##################")
pprint(pyax.get_scholars_axies_links())

# Get the ronin web3
print("\n############### Get Ronin web3 ##################")
ronin_web3 = pyax.get_ronin_web3()
pprint(ronin_web3)

# Get SLP contract
print("\n############### Get SLP contract ##################")
slp_abi_path = 'slp_abi.json'
slp_contract = pyax.get_slp_contract(ronin_web3, slp_abi_path)
pprint(slp_contract)


# Get claimed SLP balance
print("\n############### Get claimed SLP ##################")
claimed_slp = pyax.get_claimed_slp(pyax.ronin_address)
pprint(claimed_slp)

# Get unclaimed SLP balance
print("\n############### Get unclaimed SLP ##################")
unclaimed_slp = pyax.get_unclaimed_slp(pyax.ronin_address)
pprint(unclaimed_slp)


# Claim SLP for all the scholars accounts in secret.yaml and send SLP to you and your scholar
print("\n############### Payout ##################")

txns = list()
for account in config['scholars']:
    scholar = pyaxie(config['scholars'][account]['ronin_address'], config['scholars'][account]['private_key'])
    pprint(scholar.claim_slp())
    pprint(scholar.payout())

# Send 1 SLP from the pyax object (your first scholar in the list) to your personal address
print("\n############### Send 1 SLP ##################")
tx = pyax.transfer_slp(config['personal']['ronin_address'], 1)
pprint(tx)
"""


