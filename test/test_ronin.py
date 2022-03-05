import sys
sys.path.append('..')

from src.ronin import Ronin
from src.utils import Utils
from pprint import pprint

Utils = Utils()
ronin_address = Utils.get_all_ronin_address()[0]
Ronin = Ronin(ronin_address)
web3 = Ronin.get_ronin_web3()

print('\n--------------------------------\nTESTING => Ronin interactions\n\n')

print('Retrieving Axie contract')
axie_contract = Ronin.get_axie_contract(web3)
pprint(axie_contract)
print('\n-----\n')

print('Getting authentication raw message.')
raw_message = Ronin.get_raw_message()
print(raw_message)
print('\n-----\n')

print('Signing the raw message.')
signed_message = Ronin.sign_message(raw_message, Utils.search_config('ronin_address', ronin_address, 'private_key'))
print(signed_message)
print('\n-----\n')

print('Submitting signature to get authentication token.')
auth_token = Ronin.submit_signature(signed_message, raw_message, ronin_address)
print(auth_token)
print('\n-----\n')

print('Get authentication token function (all the step above in one feature)')
print(Ronin.get_access_token())
print('\n-----\n')

print('Get receipt for transasction : 0xf0f805fa64a5192d91e7bae77fd4b2fc0a5405d83791482850618b86890edb89')
pprint(Ronin.get_receipt('0xf0f805fa64a5192d91e7bae77fd4b2fc0a5405d83791482850618b86890edb89'))
print('\n-----\n')

print('Get SLP contract.')
slp_contract = Ronin.get_slp_contract(web3)
pprint(slp_contract)
print('\n-----\n')

print('Do you want to claim the SLP for : ' + ronin_address + "? yes/no")
res = ""
yes_list = ['Yes', 'yes', 'y', 'Y']
no_list = ['No', 'no', 'N', 'n']
while not res:
    res = input()
    if res not in yes_list and res not in no_list:
        res = ""
    elif res in yes_list:
        print('Claiming SLP for : ' + ronin_address)
        print(Ronin.claim_slp())
    elif res in no_list:
        break
print('\n-----\n')

print('Do you want to transfer 1 SLP from : ' + ronin_address + "? (I'll ask you to specify a 'to address') yes/no")
res = ""
while not res:
    res = input()
    if res not in yes_list and res not in no_list:
        res = ""
    elif res in yes_list:
        print('Enter the ronin address to send 1 SLP to : ')
        to_address = input()
        print('Sending 1 SLP.\nFrom address : ' + ronin_address + '\nto address : ' + to_address)
        print(Ronin.transfer_slp(to_address, 1))
    elif res in no_list:
        break
print('\n-----\n')

print('Do you want to payout for all accounts in the config file ? yes/no')
res = ""
while not res:
    res = input()
    if res not in yes_list and res not in no_list:
        res = ""
    elif res in yes_list:
        print('Starting payout for all accounts in secret.yaml file ')
        print(Ronin.payout())
    elif res in no_list:
        break
print('\n-----\n')

print('Do you want to see all the transactions for : ' + ronin_address + ' ? yes/no')
res = ""
while not res:
    res = input()
    if res not in yes_list and res not in no_list:
        res = ""
    elif res in yes_list:
        print(Ronin.ronin_txs(ronin_address))
    elif res in no_list:
        break

