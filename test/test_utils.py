import sys
sys.path.append('..')

from src.utils import Utils
from pprint import pprint

Utils = Utils()
print('\n--------------------------------\nTESTING => Utilities\n\n')
print('SLP price =', Utils.get_price('slp'))
print('AXS price =', Utils.get_price('axs'))
print('ETH price =', Utils.get_price('eth'))
print('\n-----\n')

print('Get SLP price from timestamp Fri, 15 Oct 2021 17:14:37 GMT (1634318078) : ')
pprint(Utils.get_prices_from_timestamp(1634318078))
print('Get ETH price from timestamp Fri, 15 Oct 2021 17:14:37 GMT (1634318078) : ')
pprint(Utils.get_prices_from_timestamp(1634318078))
print('Get AXS price from timestamp Fri, 15 Oct 2021 17:14:37 GMT (1634318078) : ')
pprint(Utils.get_prices_from_timestamp(1634318078))
print('\n-----\n')

print('Generating random QR code at "./QR.png"')
Utils.get_qr_code('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
print('\n-----\n')

print('All the breed cost :\n')
pprint(Utils.get_breed_cost())
print('\n-----\n')

print('Get breed cost for level 0 :\n')
pprint(Utils.get_breed_cost(0))
print('\n-----\n')

print('Generating a seed phrase : ', Utils.generate_seed_phrase())
print('\n-----\n')

print('Generating random 24 characters password : ', Utils.generate_password(20))
print('\n-----\n')

print('Search config : ')
pprint(Utils.search_config('ronin_address', '0x4f3c3b9350168f3d0345bbcf06671f3ef5ca2fe3', 'private_key'))
print('\n-----\n')

print('Retrieving all ronin addresses from config : ')
pprint(Utils.get_all_ronin_address())
print('\n-----\n')