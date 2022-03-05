import time, sys
sys.path.append('..')

from src.profile import Profile
from src.utils import Utils
from pprint import pprint

Utils = Utils()
ronin_address = Utils.get_all_ronin_address()[0]
Profile = Profile(ronin_address)

print('Get axies data for account : ' + ronin_address)
pprint(Profile.get_axies_data(ronin_address))
print('\n-----\n')

print('Get data for profile : ' + ronin_address)
pprint(Profile.get_profile_data())
print('\n-----\n')

print('Get axies image line')
print(Profile.get_axies_imageline())
print('\n-----\n')

name = Profile.get_profile_name(ronin_address)
print('Get profile name : ', name)
print('\n-----\n')

print('Do you want to rename account : ' + ronin_address + "? yes/no")
res = ""
yes_list = ['Yes', 'yes', 'y', 'Y']
no_list = ['No', 'no', 'N', 'n']
while not res:
    res = input()
    if res not in yes_list and res not in no_list:
        res = ""
    elif res in yes_list:
        print('Please enter the new name for your account : ')
        new_name = input()
        print('Renaming account from : ' + name + ' to : ' + new_name)
        pprint(Profile.rename_account(new_name))
        time.sleep(5)
        print('Get profile name again to see if it changed : ' + Profile.get_profile_name(ronin_address))
    elif res in no_list:
        break
print('\n-----\n')

print('Get activity log for account : ' + ronin_address)
pprint(Profile.get_activity_log())
print('\n-----\n')

print('Get public profile for : ' + ronin_address)
pprint(Profile.get_public_profile(ronin_address))
print('\n-----\n')

print('Get rank and MMR for account ' + ronin_address)
pprint(Profile.get_rank_mmr(ronin_address))
print('\n-----\n')

print('Get estimated daily SLP for account : ' + ronin_address)
print(Profile.get_daily_slp())
print('\n-----\n')

print('Get SLP balance for account : ' + ronin_address)
print(Profile.get_slp_balance(ronin_address))
print('\n-----\n')

print('Get last claim for account : ' + ronin_address)
print(Profile.get_last_claim(ronin_address))
print('\n-----\n')

print('Get account balances for : ' + ronin_address)
print(Profile.get_account_balances(ronin_address))
print('\n-----\n')

print('Get balance for all account in secret.yaml : ')
print(Profile.get_all_accounts_balances())
print('\n-----\n')

print('Get amount of axies in the account : ' + ronin_address)
print(Profile.get_number_of_axies())
print('\n-----\n')

print('Get amount of eggs for : ' + ronin_address)
print(Profile.get_eggs(ronin_address))
print('\n-----\n')

print('Update all axies local data : ' + ronin_address)
print(Profile.get_slp_balance(ronin_address))
print('\n-----\n')

print('Get all axies data stored locally for : ' + ronin_address)
print(Profile.get_all_axies())
print('\n-----\n')

print('Get all plant axies in the account')
print(Profile.get_all_axie_class('plant'))
print('\n-----\n')


