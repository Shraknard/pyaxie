# Pyaxie documentation

## Install

- Just download the .zip or use `git clone https://github.com/vmercadi/pyaxie.git`
- Next you have to install the requirements with `pip install -r requirements.py`
- Then, make sure that you have filled the `secret.yaml` file with your personnal and scholar informations.
You can add as much scholars as you want by copy/past the `scholars1` part. Don't forget to change the name !


## Usage

To use the lib, we have to instantiate a pyaxie object.

```
from pyaxie import pyaxie

scholar = pyaxie(config['scholars']['scholar1']['ronin_address'], config['scholars']['scholar1']['private_key'])
```

When you instanciate a pyaxie object, it will already have some accessible datas :

```
config              # Dictionary with secret.yaml datas
ronin_address       # Address from instantiation
private_key         # Private key from instantiation (or '')
headers             # Headers for requests
url                 # Graphql URL
access_token        # Access token generated (if a private key has been given)
account_id          # ID of the Axie account
email               # email of the account (for scholars accounts only)
payout_percentage   # payout percentage from 0 to 1 (for scholars accounts only)
personal_ronin      #  (for scholars accounts only)
name                # Name of the account
slp_contract        # the SLP contract object
ronin_web3          # Web3 object for ronin
axie_list_path      # Path to local axie list file
slp_track_path      # Path to slp track file
slp_abi_path        # Path to the SLP's ABI
```

You can access them by doing something like : `scholar.ronin_address`

If you want to call pyaxie functions, you can do it the same way : `scholar.get_qr_code()`

And that's it !  

### [You can find the list of functions here.](https://github.com/vmercadi/pyaxie/documentation/functions.md)

## Tips 
- You will find some pre-made scripts in [the examples folder](https://github.com/vmercadi/pyaxie/examples).
- Don't be in a hurry, sometimes the requests can take some time. 
- When you transfer SLP, make sure you filled correctly every fields and try with 1 SLP first to ensure it works well.