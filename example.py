"""
Here is a demonstration on how to use the library.
You will find a test of every functions consecutively.

The function names starting with 'get_' are using http request
The other are working locally but you have to save_axie()
"""

import yaml # To work with our yaml secret file
import random
from pyaxie import pyaxie # Import pyaxie lib to use axie functions
from pprint import pprint

##########################
#     AUTHENTICATION     #
##########################

# Get config datas
with open("secret.yaml", "r") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

# Get datas from config
ronin_address = config['personnal']['ronin_address']
private_key = config['personnal']['private_key']

# Get a random axie ID to test the functions
rnd_id = random.randint(10000, 1000000)

# Create a pyaxie object
pyaxie = pyaxie(ronin_address, private_key)

# Once a pyaxie object have been created, you can access some of it's data
pprint(pyaxie.ronin_address)
pprint(pyaxie.private_key)
pprint(pyaxie.access_token)

##########################
#     AUTHENTICATION     #
##########################

# Get the raw message for authentication
pprint("############### Raw message ##################")
raw_message = pyaxie.get_raw_message()
pprint(raw_message)

# Sign the raw message with your key
pprint("############### Sign message ##################")
signed_message = pyaxie.sign_message(raw_message)
pprint(signed_message)

# Sumbit the message to get an access token
pprint("############### Access Token ##################")
pprint(pyaxie.submit_signature(signed_message, raw_message))

# Generate a QR code from the token
pprint("############### Generate QR ##################")
pyaxie.get_qr_code()

# Get an access token (already stored in the pyaxie object)
pprint("############### Access Token ##################")
pprint(pyaxie.get_access_token())

# Eth price from axie marketplace
pprint("############### ETH Price ##################")
pprint(pyaxie.get_eth_price())

# Get profile information
pprint("############### Profile Data ##################")
pprint(pyaxie.get_profile_data())

# Get activity log
pprint("############### Activity Log ##################")
pprint(pyaxie.get_activity_log())

# Get profile name
pprint("############### Profile Name ##################")
pprint(pyaxie.get_profile_name("0x8644da68ff6ac82cb88ce43fde655a62c905e13f"))

# Get public profile
pprint("############### Public Profile ##################")
pprint(pyaxie.get_public_profile('0x8644da68ff6ac82cb88ce43fde655a62c905e13f'))

# Get axie list of a given account
pprint("############### Account axies list ##################")
pprint(pyaxie.get_axie_brief_list("0x8644da68ff6ac82cb88ce43fde655a62c905e13f"))

# Get axie image from axie id
pprint("############### Axie image ##################")
pprint(pyaxie.get_axie_image(rnd_id))

# Get information about specific axie
pprint("############### Axie detail ##################")
pprint(pyaxie.get_axie_detail(rnd_id))

# Save axie
pprint("############### Save axie ##################")
pyaxie.save_axie(pyaxie.get_axie_detail(rnd_id))
pyaxie.save_axie(pyaxie.get_axie_detail(rnd_id + 2))
pyaxie.save_axie(pyaxie.get_axie_detail(rnd_id + 4))

# Get information about locally stored axie
pprint("############### Axie detail ##################")
pprint(pyaxie.axie_detail(rnd_id))

pprint("############### Check axie ##################")
pprint(pyaxie.check_axie(rnd_id))
pprint(pyaxie.get_axie_detail(rnd_id))

# Get the local list of axies
pprint("############### Axie list ##################")
pprint(pyaxie.axie_list())

# Update the axie list with fresh data
pprint("############### Update axie list ##################")
pprint(pyaxie.update_axie_list())

# Get axie datas about specific thing
pprint("############### Axie specific info from web ##################")
pprint(pyaxie.get_axie_class(rnd_id))
pprint(pyaxie.get_axie_name(rnd_id))
pprint(pyaxie.get_axie_parts(rnd_id))
pprint(pyaxie.get_axie_image(rnd_id))
pprint(pyaxie.get_axie_stats(rnd_id))

# Get axie datas about specific thing
pprint("############### Axie specific info local ##################")
pprint(pyaxie.axie_infos(rnd_id, "class"))
pprint(pyaxie.axie_infos(rnd_id, "name"))
pprint(pyaxie.axie_infos(rnd_id, "parts"))
pprint(pyaxie.axie_infos(rnd_id, "image"))
pprint(pyaxie.axie_infos(rnd_id, "stats"))
