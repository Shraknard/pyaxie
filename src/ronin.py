import json, yaml, requests, math, datetime, time

from eth_account.messages import encode_defunct
from datetime import timedelta
from web3 import Web3, exceptions
from web3.auto import w3


class Ronin:

    def __init__(self, ronin_address, private_key):
        """
            Init the class variables, we need a ronin address and its private key
            :param ronin_address: The ronin address
            :param private_key: Private key belonging to the ronin account
            """
        with open("../secret.yaml", "r") as file:
            config = yaml.safe_load(file)

        self.config = config
        self.url_api = config['url_api']
        self.ronin_address = ronin_address.replace('ronin:', '0x')
        self.private_key = private_key
        self.access_token = self.get_access_token()
        self.account_id = 0
        self.slp_contract = None
        self.ronin_web3 = self.get_ronin_web3()
        self.slp_abi_path = '../ABI/slp_abi.json'
        self.axie_abi_path = '../ABI/axie_abi.json'
        self.slp_contract = self.get_slp_contract(self.ronin_web3)
        self.url = "https://axieinfinity.com/graphql-server-v2/graphql"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
        self.name = "you"

        for scholar in config['scholars']:
            if config['scholars'][scholar]['ronin_address'] == ronin_address:
                self.payout_percentage = config['scholars'][scholar]['payout_percentage']
                self.personal_ronin = config['scholars'][scholar]['personal_ronin'].replace('ronin:', '0x')
                self.name = scholar
                break
            else:
                self.payout_percentage = 0
                self.personal_ronin = None

    def get_ronin_web3(self):
        """
        :return: Return the ronin web3
        """
        return Web3(Web3.HTTPProvider('https://proxy.roninchain.com/free-gas-rpc'))

    def get_axie_contract(self, ronin_web3):
        """
        Get the axie contract to interact with
        :param ronin_web3: ronin web 3
        :return: Interactive axie contract
        """
        slp_contract_address = "0x32950db2a7164ae833121501c797d79e7b79d74c"
        with open(self.axie_abi_path) as f:
            try:
                slp_abi = json.load(f)
            except ValueError as e:
                return e
        contract = ronin_web3.eth.contract(address=w3.toChecksumAddress(slp_contract_address), abi=slp_abi)
        self.slp_contract = contract
        return contract

    def get_raw_message(self):
        """
        Ask the API for a message to sign with the private key (authenticate)
        :return: message to sign
        """
        body = {"operationName": "CreateRandomMessage", "variables": {},
                "query": "mutation CreateRandomMessage {\n  createRandomMessage\n}\n"}

        r = requests.post(self.url, headers=self.headers, data=body)
        try:
            json_data = json.loads(r.text)
        except ValueError as e:
            return e
        return json_data['data']['createRandomMessage']

    def sign_message(self, raw_message, private=''):
        """
        Sign a raw message
        :param raw_message: The raw message from get_raw_message()
        :param private: The private key of the account
        :return: The signed message
        """
        if not private:
            private = self.private_key
        pk = bytearray.fromhex(private)
        try:
            message = encode_defunct(text=raw_message)
            hex_signature = w3.eth.account.sign_message(message, private_key=pk)
            return hex_signature
        except 'JSONDecodeError' as e:
            return e

    def submit_signature(self, signed_message, raw_message, ronin_address=''):
        """
        Function to submit the signature and get authorization
        :param signed_message: The signed message from sign_message()
        :param raw_message: The raw message from get_row_message()
        :param ronin_address: THe ronin address of the account
        :return: The access token
        """
        if not ronin_address:
            ronin_address = self.ronin_address

        body = {"operationName": "CreateAccessTokenWithSignature", "variables": {
            "input": {"mainnet": "ronin", "owner": "User's Eth Wallet Address", "message": "User's Raw Message",
                      "signature": "User's Signed Message"}},
                "query": "mutation CreateAccessTokenWithSignature($input: SignatureInput!) {  createAccessTokenWithSignature(input: $input) {    newAccount    result    accessToken    __typename  }}"}
        body['variables']['input']['signature'] = signed_message['signature'].hex()
        body['variables']['input']['message'] = raw_message
        body['variables']['input']['owner'] = ronin_address
        r = requests.post(self.url, headers=self.headers, json=body)

        try:
            json_data = json.loads(r.text)
        except ValueError as e:
            return e
        return json_data['data']['createAccessTokenWithSignature']['accessToken']

    def get_access_token(self):
        """
        Get an access token as proof of authentication
        :return: The access token in string
        """
        if not self.private_key:
            self.private_key = Utils.search_config('ronin_address', self.ronin_address, 'private_key')

        msg = self.get_raw_message()
        signed = self.sign_message(msg)
        if "JSONDecodeError" in signed:
            print("Error getting the signed message, trying again.")
            token = self.get_access_token()
        else:
            token = self.submit_signature(signed, msg)

        self.access_token = token
        self.headers['authorization'] = 'Bearer ' + token
        return token

    def get_receipt(self, txn):
        """
        Get the receipt from a transaction hash (works even if ronin explorer doesn't)
        :param txn: transaction hash
        :return: blockchain info
        """
        try:
            receipt = self.ronin_web3.eth.get_transaction_receipt(txn)
        except ValueError as e:
            return e
        return receipt

    def get_slp_contract(self, ronin_web3):
        """
        :param ronin_web3: ronin web3 object
        :param slp_abi_path: ABI for SLP
        :return: The contract to interact with
        """
        slp_contract_address = "0xa8754b9fa15fc18bb59458815510e40a12cd2014"
        with open(self.slp_abi_path) as f:
            try:
                slp_abi = json.load(f)
            except ValueError as e:
                return e
        contract = ronin_web3.eth.contract(address=w3.toChecksumAddress(slp_contract_address), abi=slp_abi)
        self.slp_contract = contract
        return contract

    def claim_slp(self):
        """
        Claim SLP on the account.
        :return: Transaction of the claim
        """
        if datetime.datetime.utcnow() + timedelta(days=-14) < datetime.datetime.fromtimestamp(self.Profile.get_last_claim()):
            return 'Error: Too soon to claim or already claimed'

        slp_claim = {
            'address': self.ronin_address,
            'private_key': self.private_key,
            'state': {"signature": None}
        }
        access_token = self.access_token
        custom_headers = self.headers.copy()
        custom_headers["authorization"] = f"Bearer {access_token}"
        response = requests.post(self.url_api + f"clients/{self.ronin_address}/items/1/claim", headers=custom_headers, json="")

        if response.status_code != 200:
            print(response.text)
            return

        result = response.json()["blockchain_related"]["signature"]
        if result is None:
            return 'Error: Nothing to claim'

        checksum_address = w3.toChecksumAddress(self.ronin_address)
        nonce = self.ronin_web3.eth.get_transaction_count(checksum_address)
        slp_claim['state']["signature"] = result["signature"].replace("0x", "")
        claim_txn = self.slp_contract.functions.checkpoint(checksum_address, result["amount"], result["timestamp"],
                                                           slp_claim['state']["signature"]).buildTransaction(
            {'gas': 1000000, 'gasPrice': 0, 'nonce': nonce})
        signed_txn = self.ronin_web3.eth.account.sign_transaction(claim_txn, private_key=bytearray.fromhex(
            self.private_key.replace("0x", "")))

        self.ronin_web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn = self.ronin_web3.toHex(self.ronin_web3.keccak(signed_txn.rawTransaction))
        return txn if self.wait_confirmation(txn) else "Error : Transaction " + str(
            txn) + "reverted by EVM (Ethereum Virtual machine)"

    def transfer_slp(self, to_address, amount):
        """
        Transfer SLP from pyaxie ronin address to the to_address
        :param to_address: Receiver of the SLP. Format : 0x
        :param amount: Amount of SLP to send
        :return: Transaction hash
        """
        if amount < 1 or not Web3.isAddress(to_address):
            return {"error": "Make sure that the amount is not under 1 and the **to_address** is correct."}

        transfer_txn = self.slp_contract.functions.transfer(w3.toChecksumAddress(to_address), amount).buildTransaction({
            'chainId': 2020,
            'gas': 100000,
            'gasPrice': Web3.toWei('0', 'gwei'),
            'nonce': self.ronin_web3.eth.get_transaction_count(w3.toChecksumAddress(self.ronin_address))
        })
        private_key = bytearray.fromhex(self.private_key.replace("0x", ""))
        signed_txn = self.ronin_web3.eth.account.sign_transaction(transfer_txn, private_key=private_key)

        self.ronin_web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn = self.ronin_web3.toHex(self.ronin_web3.keccak(signed_txn.rawTransaction))
        return txn if self.wait_confirmation(txn) else "Error : Transaction " + str(
            txn) + " reverted by EVM (Ethereum Virtual machine)"

    def wait_confirmation(self, txn):
        """
        Wait for a transaction to finish
        :param txn: the transaction to wait
        :return: True or False depending if transaction succeed
        """
        while True:
            try:
                receipt = self.get_receipt(txn)
                success = True if receipt["status"] == 1 else False
                break
            except exceptions.TransactionNotFound:
                time.sleep(5)
        return success

    def payout(self):
        """
        Send money to the scholar and to the manager/academy or directly to manager if manager called
        :return: List of 2 transactions hash : scholar and manager
        """
        self.claim_slp()

        txns = list()
        slp_balance = self.Profile.get_slp_balance()
        scholar_payout_amount = math.ceil(slp_balance * self.payout_percentage)
        academy_payout_amount = slp_balance - scholar_payout_amount

        if slp_balance < 1:
            return ["Error: Nothing to send.", "Error: Nothing to send."]

        if self.payout_percentage == 0:
            print("Sending all the {} SLP to you : {} ".format(academy_payout_amount, self.config['personal']['ronin_address']))
            txns.append(str(self.transfer_slp(self.config['personal']['ronin_address'], academy_payout_amount + scholar_payout_amount)))
            txns.append("Nothing to send to scholar")
            return txns
        else:
            print("Sending {} SLP to {} : {} ".format(academy_payout_amount, "You", self.config['personal']['ronin_address']))
            txns.append(str(self.transfer_slp(self.config['personal']['ronin_address'], academy_payout_amount)))

            print("Sending {} SLP to {} : {} ".format(scholar_payout_amount, self.name, self.personal_ronin))
            txns.append(str(self.transfer_slp(self.personal_ronin, scholar_payout_amount)))
        return txns

    def ronin_txs(self, ronin_address):
        """
        Get all the transactions (up to 10k) from an account
        :param ronin_address: The ronin address of the account
        :return: Dict with all the transactions
        """
        url = "https://explorer.roninchain.com/api/txs/" + str(ronin_address) + "?size=10000"
        response = requests.get(url, headers=self.headers)

        try:
            json_data = json.loads(response.text)
        except ValueError as e:
            return e
        return json_data['results']