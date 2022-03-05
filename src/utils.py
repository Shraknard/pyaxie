import qrcode, string, random, datetime, json, yaml, requests

from pycoingecko import CoinGeckoAPI
from mnemonic import Mnemonic
from PIL import Image


class Utils:

    def __init__(self):
        with open("../secret.yaml", "r") as file:
            self.config = yaml.safe_load(file)

        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36','authorization': ""}
        self.url = "https://axieinfinity.com/graphql-server-v2/graphql"
        return

    def get_price(self, currency):
        """
        Get the price in USD for 1 ETH / SLP / AXS
        :return: The price in US of 1 token
        """
        body = {"operationName": "NewEthExchangeRate", "variables": {},
                "query": "query NewEthExchangeRate {\n  exchangeRate {\n    " +
                currency.lower() + " {\n      usd\n      __typename\n    }\n    __typename\n  }\n}\n"}
        r = requests.post(self.url, headers=self.headers, json=body)
        try:
            json_data = json.loads(r.text)
        except ValueError as e:
            return e
        return json_data['data']['exchangeRate'][currency.lower()]['usd']

    def get_prices_from_timestamp(self, timestamp):
        """
        Get prices for AXS, SLP and ETH at given date
        :param timestamp: date in unix timestamp format
        :return: Dict with the prices of currencies at given date
        """
        cg = CoinGeckoAPI()
        dt = datetime.datetime.fromtimestamp(timestamp)

        price_history = cg.get_coin_history_by_id(id='smooth-love-potion', date=dt.date().strftime('%d-%m-%Y'), vsCurrencies=['usd'])
        slp_price = price_history['market_data']['current_price']['usd']

        price_history = cg.get_coin_history_by_id(id='axie-infinity', date=dt.date().strftime('%d-%m-%Y'), vsCurrencies=['usd'])
        axs_price = price_history['market_data']['current_price']['usd']

        price_history = cg.get_coin_history_by_id(id='ethereum', date=dt.date().strftime('%d-%m-%Y'), vsCurrencies=['usd'])
        eth_price = price_history['market_data']['current_price']['usd']

        return {'slp': slp_price, 'axs': axs_price, 'eth': eth_price, 'date': timestamp}

    def get_qr_code(self, access_token):
        """
        Function to create a QRCode from an access_token
        """
        img = qrcode.make(access_token)
        name = 'QRCode-' + str(datetime.datetime.now()) + '.png'
        img.save(name)
        return name

    def get_breed_cost(self, nb=-1):
        """
        Get the breeding cost
        :param nb: breed lvl (0-6)
        :return: List with data about the breeding costs
        """
        breeds = {0: 300, 1: 450, 2: 750, 3: 1200, 4: 1950, 5: 3150, 6: 5100}
        axs = self.get_price('axs')
        slp = self.get_price('slp')
        total = 0
        res = dict()

        for i in range(0, 7):
            breed_price = int((breeds[i] * slp) * 2 + axs)
            total += breed_price
            res[i] = {'price': breed_price, 'total_breed_price': total, 'average_price': int(total / (1 + i))}

        if nb <= -1:
            return res

        return [res[nb]]

    def generate_seed_phrase(self):
        """
        Generate a 12 words seed phrase based on bip39
        :return:
        """
        mnemo = Mnemonic("english")
        return mnemo.generate(strength=128)

    def generate_password(self, n=0):
        """
        Generate a random password
        :param n: password length
        :return: a password
        """
        n = 20 if n <= 10 else n
        chars = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation.replace(';', '')
        res = ""
        for i in range(n):
            res += random.choice(chars)
        return res

    def merge_images(self, path1, path2, path3, name):
        """
        Merge 3 axies pictures into one image in line
        :param path1: Path of the 1st axie image (usually './img/axies/AXIE-ID.jpg')
        :param path2: Path of the 2nd axie image
        :param path3: Path of the 3rd axie image
        :param name: Name of the scholar
        :return: Path of the freshly created image
        """
        img = Image.open(path1).convert("RGBA")
        img2 = Image.open(path2).convert("RGBA")
        img3 = Image.open(path3).convert("RGBA")
        dst = Image.new('RGB', (img.width * 3, img.height)).convert("RGBA")
        final = './axie_data/img/axies/' + name + '.png'

        dst.paste(img, (0, 0))
        dst.paste(img2, (img.width, 0))
        dst.paste(img3, (img.width * 2, 0))
        dst.save(final)
        return final

    #######################################
    # CONFIG INTERACTIONS
    #######################################

    def search_config(self, key, value, res_key):
        """
        Search the config for a specific value based on a info you already have.
        :param key: The key (let's say 'ronin_address' if you already have it)
        :param value: Value of the ronin address you have (ex : 0x:000...123)
        :param res_key: The key for the value you are searching for (ex: 'private_key' if you want the private)
        :return: The value corresponding to the res_key or None if value is not found in the config
        """
        data = next((self.config['accounts'][i][res_key] for i in self.config['accounts'] if self.config['accounts'][i][key] == value), None)
        if not data:
            return ''
        return data

    def get_all_ronin_address(self):
        """
        Get all the ronin address in the scholarship (secret.yaml)
        :return: list of address
        """
        l = list()
        for account in self.config['accounts']:
            l.append(self.config['accounts'][account]['ronin_address'])
        return l