import requests, json, yaml, datetime, math, os, sys

try:
    from .utils import Utils
except ImportError:
    Utils = sys.modules['.utils.Utilz']

class Profile:

    def __init__(self, ronin_address):
        with open("../secret.yaml", "r") as file:
            config = yaml.safe_load(file)

        self.config = config
        self.ronin_address = ronin_address.replace('ronin:', '0x')
        self.private_key = Utils.search_config('ronin_address', ronin_address, 'private_key').replace('0x', '')
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36', 'authorization': ""}
        self.url = "https://axieinfinity.com/graphql-server-v2/graphql"
        self.url_api = config['url_api']
        self.axie_data_path = './axie_data/data/axies/'
        self.axie_img_path = './axie_data/img/axies/'
        self.access_token = Ronin.get_access_token()
        self.account_id = 0
        self.name = "you"

    def get_axies_data(self, ronin_address=''):
        """
        Get informations about the axies in a specific account
        :param ronin_address: The ronin address of the target account
        :return: Data about the axies
        """
        if ronin_address == '':
            ronin_address = self.ronin_address
        body = {"operationName": "GetAxieBriefList",
                "variables": {"from": 0, "size": 24, "sort": "IdDesc", "auctionType": "All", "owner": ronin_address,
                              "criteria": {"region": None, "parts": None, "bodyShapes": None, "classes": None,
                                           "stages": None, "numMystic": None, "pureness": None, "title": None,
                                           "breedable": None, "breedCount": None, "hp": [], "skill": [], "speed": [],
                                           "morale": []}},
                "query": "query GetAxieBriefList($auctionType: AuctionType, $criteria: AxieSearchCriteria, $from: Int, $sort: SortBy, $size: Int, $owner: String) {\n  axies(auctionType: $auctionType, criteria: $criteria, from: $from, sort: $sort, size: $size, owner: $owner) {\n    total\n    results {\n      ...AxieBrief\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment AxieBrief on Axie {\n  id\n  name\n  stage\n  class\n  breedCount\n  image\n  title\n  battleInfo {\n    banned\n    __typename\n  }\n  auction {\n    currentPrice\n    currentPriceUSD\n    __typename\n  }\n  parts {\n    id\n    name\n    class\n    type\n    specialGenes\n    __typename\n  }\n  __typename\n}\n"}

        try:
            r = requests.post(self.url, headers=self.headers, json=body)
            json_data = json.loads(r.text)
        except ValueError as e:
            return e
        return json_data['data']['axies']['results']

    def get_profile_data(self):
        """
        Retrieve your profile/account data
        :return: Your profil data as dict
        """
        body = {"operationName": "GetProfileBrief", "variables": {}, "query": "query GetProfileBrief {\n  profile {\n    ...ProfileBrief\n    __typename\n  }\n}\n\nfragment ProfileBrief on AccountProfile {\n  accountId\n  addresses {\n    ...Addresses\n    __typename\n  }\n  email\n  activated\n  name\n  settings {\n    unsubscribeNotificationEmail\n    __typename\n  }\n  __typename\n}\n\nfragment Addresses on NetAddresses {\n  ethereum\n  tomo\n  loom\n  ronin\n  __typename\n}\n"}
        r = requests.post(self.url, headers=self.headers, json=body)
        try:
            json_data = json.loads(r.text)
        except ValueError as e:
            return e['data']['profile']

        self.account_id = json_data['data']['profile']['accountId']
        self.name = json_data['data']['profile']['name']
        return json_data

    def get_axies_imageline(self):
        """
        Get the path to the picture containing the 3 axies merged horizontally
        :return: Path of the new picture
        """
        try:
            axies = Profile.get_axies_data(self.ronin_address)
            l = list()
            for axie in axies:
                l.append(Axie.download_axie_image(axie['id']))
            if len(l) < 3:
                return None
        except ValueError as e:
            return e
        return Utils.merge_images(l[0], l[1], l[2], self.name)

    def get_profile_name(self, ronin_address=''):
        """
        Get the profile name of a ronin address
        :param ronin_address: The target ronin account
        :return: The name of the account
        """
        if ronin_address == '':
            ronin_address = self.ronin_address
        body = {"operationName": "GetProfileNameByRoninAddress", "variables": {"roninAddress": ronin_address},
                "query": "query GetProfileNameByRoninAddress($roninAddress: String!) {\n  publicProfileWithRoninAddress(roninAddress: $roninAddress) {\n    accountId\n    name\n    __typename\n  }\n}\n"}
        r = requests.post(self.url, headers=self.headers, json=body)
        try:
            json_data = json.loads(r.text)
        except ValueError as e:
            return e
        return json_data['data']['publicProfileWithRoninAddress']['name']

    def rename_account(self, new_name):
        body = {"operationName": "RenameAxie", "variables": {"axieId": str(new_name), "name": str(new_name)},
                "query": "mutation RenameAxie($axieId: ID!, $name: String!) {\n  renameAxie(axieId: $axieId, name: $name) {\n    result\n    __typename\n  }\n}\n"}
        try:
            r = requests.post(self.url, headers=self.headers, json=body)
            json_data = json.loads(r.text)
        except ValueError as e:
            return e
        if json_data['data'] is None:
            return json_data['errors']['message']
        return json_data['data']['renameAxie']['result']

    def get_activity_log(self):
        """
        Get data about the activity log
        :return: activity log
        """
        body = {"operationName": "GetActivityLog", "variables": {"from": 0, "size": 6},
                "query": "query GetActivityLog($from: Int, $size: Int) {\n  profile {\n    activities(from: $from, size: $size) {\n      ...Activity\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment Activity on Activity {\n  activityId\n  accountId\n  action\n  timestamp\n  seen\n  data {\n    ... on ListAxie {\n      ...ListAxie\n      __typename\n    }\n    ... on UnlistAxie {\n      ...UnlistAxie\n      __typename\n    }\n    ... on BuyAxie {\n      ...BuyAxie\n      __typename\n    }\n    ... on GiftAxie {\n      ...GiftAxie\n      __typename\n    }\n    ... on MakeAxieOffer {\n      ...MakeAxieOffer\n      __typename\n    }\n    ... on CancelAxieOffer {\n      ...CancelAxieOffer\n      __typename\n    }\n    ... on SyncExp {\n      ...SyncExp\n      __typename\n    }\n    ... on MorphToPetite {\n      ...MorphToPetite\n      __typename\n    }\n    ... on MorphToAdult {\n      ...MorphToAdult\n      __typename\n    }\n    ... on BreedAxies {\n      ...BreedAxies\n      __typename\n    }\n    ... on BuyLand {\n      ...BuyLand\n      __typename\n    }\n    ... on ListLand {\n      ...ListLand\n      __typename\n    }\n    ... on UnlistLand {\n      ...UnlistLand\n      __typename\n    }\n    ... on GiftLand {\n      ...GiftLand\n      __typename\n    }\n    ... on MakeLandOffer {\n      ...MakeLandOffer\n      __typename\n    }\n    ... on CancelLandOffer {\n      ...CancelLandOffer\n      __typename\n    }\n    ... on BuyItem {\n      ...BuyItem\n      __typename\n    }\n    ... on ListItem {\n      ...ListItem\n      __typename\n    }\n    ... on UnlistItem {\n      ...UnlistItem\n      __typename\n    }\n    ... on GiftItem {\n      ...GiftItem\n      __typename\n    }\n    ... on MakeItemOffer {\n      ...MakeItemOffer\n      __typename\n    }\n    ... on CancelItemOffer {\n      ...CancelItemOffer\n      __typename\n    }\n    ... on ListBundle {\n      ...ListBundle\n      __typename\n    }\n    ... on UnlistBundle {\n      ...UnlistBundle\n      __typename\n    }\n    ... on BuyBundle {\n      ...BuyBundle\n      __typename\n    }\n    ... on MakeBundleOffer {\n      ...MakeBundleOffer\n      __typename\n    }\n    ... on CancelBundleOffer {\n      ...CancelBundleOffer\n      __typename\n    }\n    ... on AddLoomBalance {\n      ...AddLoomBalance\n      __typename\n    }\n    ... on WithdrawFromLoom {\n      ...WithdrawFromLoom\n      __typename\n    }\n    ... on AddFundBalance {\n      ...AddFundBalance\n      __typename\n    }\n    ... on WithdrawFromFund {\n      ...WithdrawFromFund\n      __typename\n    }\n    ... on TopupRoninWeth {\n      ...TopupRoninWeth\n      __typename\n    }\n    ... on WithdrawRoninWeth {\n      ...WithdrawRoninWeth\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ListAxie on ListAxie {\n  axieId\n  priceFrom\n  priceTo\n  duration\n  txHash\n  __typename\n}\n\nfragment UnlistAxie on UnlistAxie {\n  axieId\n  txHash\n  __typename\n}\n\nfragment BuyAxie on BuyAxie {\n  axieId\n  price\n  owner\n  txHash\n  __typename\n}\n\nfragment GiftAxie on GiftAxie {\n  axieId\n  destination\n  txHash\n  __typename\n}\n\nfragment MakeAxieOffer on MakeAxieOffer {\n  axieId\n  price\n  txHash\n  __typename\n}\n\nfragment CancelAxieOffer on CancelAxieOffer {\n  axieId\n  txHash\n  __typename\n}\n\nfragment SyncExp on SyncExp {\n  axieId\n  exp\n  txHash\n  __typename\n}\n\nfragment MorphToPetite on MorphToPetite {\n  axieId\n  txHash\n  __typename\n}\n\nfragment MorphToAdult on MorphToAdult {\n  axieId\n  txHash\n  __typename\n}\n\nfragment BreedAxies on BreedAxies {\n  sireId\n  matronId\n  lovePotionAmount\n  txHash\n  __typename\n}\n\nfragment BuyLand on BuyLand {\n  row\n  col\n  price\n  owner\n  txHash\n  __typename\n}\n\nfragment ListLand on ListLand {\n  row\n  col\n  priceFrom\n  priceTo\n  duration\n  txHash\n  __typename\n}\n\nfragment UnlistLand on UnlistLand {\n  row\n  col\n  txHash\n  __typename\n}\n\nfragment GiftLand on GiftLand {\n  row\n  col\n  destination\n  txHash\n  __typename\n}\n\nfragment MakeLandOffer on MakeLandOffer {\n  row\n  col\n  price\n  txHash\n  __typename\n}\n\nfragment CancelLandOffer on CancelLandOffer {\n  row\n  col\n  txHash\n  __typename\n}\n\nfragment BuyItem on BuyItem {\n  tokenId\n  itemAlias\n  price\n  owner\n  txHash\n  __typename\n}\n\nfragment ListItem on ListItem {\n  tokenId\n  itemAlias\n  priceFrom\n  priceTo\n  duration\n  txHash\n  __typename\n}\n\nfragment UnlistItem on UnlistItem {\n  tokenId\n  itemAlias\n  txHash\n  __typename\n}\n\nfragment GiftItem on GiftItem {\n  tokenId\n  itemAlias\n  destination\n  txHash\n  __typename\n}\n\nfragment MakeItemOffer on MakeItemOffer {\n  tokenId\n  itemAlias\n  price\n  txHash\n  __typename\n}\n\nfragment CancelItemOffer on CancelItemOffer {\n  tokenId\n  itemAlias\n  txHash\n  __typename\n}\n\nfragment BuyBundle on BuyBundle {\n  listingIndex\n  price\n  owner\n  txHash\n  __typename\n}\n\nfragment ListBundle on ListBundle {\n  numberOfItems\n  priceFrom\n  priceTo\n  duration\n  txHash\n  __typename\n}\n\nfragment UnlistBundle on UnlistBundle {\n  listingIndex\n  txHash\n  __typename\n}\n\nfragment MakeBundleOffer on MakeBundleOffer {\n  listingIndex\n  price\n  txHash\n  __typename\n}\n\nfragment CancelBundleOffer on CancelBundleOffer {\n  listingIndex\n  txHash\n  __typename\n}\n\nfragment AddLoomBalance on AddLoomBalance {\n  amount\n  senderAddress\n  receiverAddress\n  txHash\n  __typename\n}\n\nfragment WithdrawFromLoom on WithdrawFromLoom {\n  amount\n  senderAddress\n  receiverAddress\n  txHash\n  __typename\n}\n\nfragment AddFundBalance on AddFundBalance {\n  amount\n  senderAddress\n  txHash\n  __typename\n}\n\nfragment WithdrawFromFund on WithdrawFromFund {\n  amount\n  receiverAddress\n  txHash\n  __typename\n}\n\nfragment WithdrawRoninWeth on WithdrawRoninWeth {\n  amount\n  receiverAddress\n  txHash\n  receiverAddress\n  __typename\n}\n\nfragment TopupRoninWeth on TopupRoninWeth {\n  amount\n  receiverAddress\n  txHash\n  receiverAddress\n  __typename\n}\n"}
        r = requests.post(self.url, headers=self.headers, json=body)
        try:
            json_data = json.loads(r.text)
        except ValueError as e:
            return e
        return json_data['data']['profile']['activities']

    def get_public_profile(self, ronin_address=''):
        """
        Get infos about the given ronin address
        :param ronin_address: The target ronin account
        :return: Public data of the ronin account
        """
        if ronin_address == '':
            ronin_address = self.ronin_address
        body = {"operationName": "GetProfileByRoninAddress", "variables": {"roninAddress": ronin_address},
                "query": "query GetProfileByRoninAddress($roninAddress: String!) {\n  publicProfileWithRoninAddress(roninAddress: $roninAddress) {\n    ...Profile\n    __typename\n  }\n}\n\nfragment Profile on PublicProfile {\n  accountId\n  name\n  addresses {\n    ...Addresses\n    __typename\n  }\n  __typename\n}\n\nfragment Addresses on NetAddresses {\n  ethereum\n  tomo\n  loom\n  ronin\n  __typename\n}\n"}
        r = requests.post(self.url, headers=self.headers, json=body)
        try:
            json_data = json.loads(r.text)
        except ValueError as e:
            return e
        return json_data['data']['publicProfileWithRoninAddress']

    def get_rank_mmr(self, ronin_address=''):
        """
        Get the mmr and rank of the current account
        :return: Dict with MMR and rank
        """
        if ronin_address == '':
            ronin_address = self.ronin_address
        params = {"client_id": ronin_address, "offset": 0, "limit": 0}

        # Try multiple times to avoid return 0
        for i in range(0, 5):
            try:
                r = requests.get(self.url_api + "leaderboard", params=params)
                json_data = json.loads(r.text)
                if json_data['success']:
                    return {'mmr': int(json_data['items'][1]['elo']), 'rank': int(json_data['items'][1]['rank'])}
            except ValueError as e:
                return e
        return {'mmr': 0, 'rank': 0}

    def get_daily_slp(self):
        """
        Get the daily SLP ratio based on SLP farmed between now and last claim
        :return: Dict with ratio and date
        """
        unclaimed = self.get_slp_balance()
        t = datetime.datetime.fromtimestamp(self.get_last_claim())
        days = (t - datetime.datetime.utcnow()).days * -1
        if days <= 0:
            return unclaimed
        return int(unclaimed / days)

    def get_slp_balance(self, ronin_address=''):
        """
        :param ronin_address: Ronin address to check
        :return: The amount of claimed SLP
        """
        if ronin_address == '':
            ronin_address = self.ronin_address
        # Try multiple times to avoid return 0
        for i in range(0, 5):
            try:
                response = requests.get(self.url_api + "clients/" + ronin_address + "/items/1", headers=self.headers, data="")
                data = json.loads(response.text)
                balance = data['blockchain_related']['balance']
                if balance is not None:
                    return int(balance)
            except ValueError as e:
                return e

    def get_last_claim(self, ronin_address=''):
        """
        Return the last time SLP was claimed for this account
        :param ronin_address: Ronin address
        :return: Time in sec
        """
        if ronin_address == '':
            ronin_address = self.ronin_address

        try:
            response = requests.get(self.url_api + "clients/" + ronin_address + "/items/1", headers=self.headers, data="")
            result = response.json()
        except ValueError as e:
            return e

        return int(result["last_claimed_item_at"])

    def get_account_balances(self, ronin_address=''):
        """
        Get the different balances for a given account (AXS, SLP, WETH, AXIES)
        :param ronin_address: ronin address of the account
        :return: dict with currencies and amount
        """
        if not ronin_address:
            ronin_address = self.ronin_address

        url = "https://explorer.roninchain.com/api/tokenbalances/" + str(ronin_address).replace('ronin:', '0x')
        response = requests.get(url, headers=self.headers)

        try:
            json_data = json.loads(response.text)
        except ValueError as e:
            return {'WETH': -1, 'AXS': -1, 'SLP': -1, 'axies': -1, 'eggs': -1, 'ronin_address': ronin_address}

        res = {'WETH': 0, 'AXS': 0, 'SLP': 0, 'axies': 0, 'eggs': -1, 'ronin_address': ronin_address}
        eggs = len(self.get_eggs(ronin_address))
        for data in json_data['results']:
            if data['token_symbol'] == 'WETH':
                res['WETH'] = round(int(data['balance']) / math.pow(10, 18), 6)
            elif data['token_symbol'] == 'AXS':
                res['AXS'] = round(int(data['balance']) / math.pow(10, 18), 2)
            elif data['token_symbol'] == 'SLP':
                res['SLP'] = int(data['balance'])
            elif data['token_symbol'] == 'AXIE':
                res['axies'] = int(data['balance']) - eggs
        res['eggs'] = eggs
        return res

    def get_eggs(self, ronin_address=''):
        """
        Get list of eggs from the account
        :param ronin_address: Ronin address of the account
        :return: List of eggs data
        """
        if not ronin_address:
            ronin_address = self.ronin_address
        axies = self.get_axies_data(ronin_address.replace('ronin:', '0x'))
        eggs = list()
        for axie in axies:
            if axie['stage'] == 1:
                eggs.append(axie)
        return eggs

    def get_all_accounts_balances(self):
        """
        Get balances for all accounts in the scholarship
        :return: List of balances
        """
        l = Utils.get_all_ronin_address()
        res = list()
        for address in l:
            res.append(self.get_account_balances(address))
        return res

    def get_all_axies(self):
        """
        Get all axies data stored locally. Use update_axies_data()
        :return:
        """
        accounts = Utils.get_all_ronin_address()
        files = os.listdir(self.axie_data_path)
        res = list()
        for file in files:
            with open(self.axie_data_path + file, 'r') as f:
                json_data = json.load(f)
            if json_data['owner'] in accounts:
                res.append(json_data)
        return res

    def update_axies_data(self):
        """
        Get informations about the axies in all the accounts
        :return: List with all axies data
        """
        accounts = Utils.get_all_ronin_address()
        files = os.listdir(self.axie_data_path)
        for file in files:
            os.remove(os.path.join(self.axie_data_path, file))

        for account in accounts:
            axies = self.get_axies_data(account)
            for axie in axies:
                Axie.save_axie(axie)

    def get_all_axie_class(self, axie_class, axies_data=[]):
        """
        Return all the axies of a specific class present in the scholarship
        :param axie_class: Plant, Beast, Bird, etc...
        :return: List of axie object of the specific class
        """
        if not axies_data:
            axies_data = self.get_all_axies()
        l = list()
        for axie in axies_data:
            if axie['class'] is not None and axie['class'].lower() == axie_class.lower():
                l.append(axie)
        return l

    def get_number_of_axies(self):
        """
        Get the number of axies in the account
        :return: the number of axies
        """
        return len(self.get_all_axies())
