import requests, json, os, datetime, yaml
from utils import Utils
from ronin import Ronin
from PIL import Image
from io import BytesIO


class Axie:
    def __init__(self):
        self.axie_data_path = './axie_data/data/axies/'
        self.axie_img_path = './axie_data/img/axies/'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36','authorization': ""}
        self.url = "https://axieinfinity.com/graphql-server-v2/graphql"
        return

    def get_axie_owner(self, axie_id):
        """
        Get the owner of an axie (address)
        :param axie_id: axie id
        :param axie_data: details of the axie or empty
        :return: Address of the owner
        """
        axie_data = self.get_axie_detail(axie_id)
        return axie_data['owner'].replace('ronin:', '0x')

    def get_axie_image_link(self, axie_id):
        """
        Get the image link to an axie
        :param axie_id: String ID of the axie you are targeting
        :return: Link to the image
        """
        body = {"operationName": "GetAxieMetadata", "variables": {"axieId": axie_id},
                "query": "query GetAxieMetadata($axieId: ID!) {\n  axie(axieId: $axieId) {\n" +
                "    id\n    image\n    __typename\n  }\n}\n"}
        try:
            r = requests.post(self.url, headers=self.headers, json=body)
            json_data = json.loads(r.text)
        except ValueError as e:
            return e
        return json_data['data']['axie']['image']

    def download_axie_image(self, axie_id):
        """
        Download the image of an axie and return the path
        :param axie_id: ID of the axie
        :return: Path of the image
        """
        axie_id = str(axie_id)
        path = self.axie_img_path + axie_id + '.png'

        if not os.path.exists(self.axie_data_path):
            os.mkdir(self.axie_data_path)

        if os.path.exists(path):
            return path

        img_data = requests.get('https://storage.googleapis.com/assets.axieinfinity.com/axies/' +
                                axie_id + '/axie/axie-full-transparent.png').content
        if len(img_data) <= 500:
            path = self.axie_data_path + 'egg.png'
            if not os.path.exists(path):
                response = requests.get('https://cdn.coinranking.com/nft/0xF5b0A3eFB8e8E4c201e2A935F110eAaF3FFEcb8d/177886.png')
                img_data = Image.open(BytesIO(response.content))
            else:
                return path
        with open(path, 'ab') as img:
            img.write(img_data)
        return path

    def save_axie(self, axie_data):
        """
        Save locally the details of an axie
        :param axie_data: Data of the axie to save
        :param axie_list: Path of the axie_list file
        """
        axie_id = axie_data['id']
        path = self.axie_data_path + str(axie_id) + '.json'

        try:
            if not os.path.exists(self.axie_data_path):
                os.mkdir(self.axie_data_path)

            with open(path, 'w') as outfile:
                json.dump(axie_data, outfile)

        except ValueError as e:
            return e
        return path

    def get_axie_detail(self, axie_id):
        """
        Get informations about an Axie based on its ID
        :param axie_id: string ID of the axie
        :return: A dict with the adata of the axie
        """
        path = self.axie_data_path + str(axie_id) + '.json'

        if not os.path.exists(self.axie_data_path):
            os.mkdir(self.axie_data_path)

        if os.path.exists(path):
            with open(path, "r") as file:
                json_data = json.load(file)
            return json_data

        body = {"operationName": "GetAxieDetail", "variables": {"axieId": axie_id},
                "query": "query GetAxieDetail($axieId: ID!) {\n  axie(axieId: $axieId) {\n    ...AxieDetail\n" +
                "    __typename\n  }\n}\n\nfragment AxieDetail on Axie {\n  id\n  image\n  class\n  chain\n" +
                "  name\n  genes\n  owner\n  birthDate\n  bodyShape\n  class\n  sireId\n  sireClass\n  matronId\n" +
                "  matronClass\n  stage\n  title\n  breedCount\n  level\n  figure {\n    atlas\n    model\n    image\n" +
                "    __typename\n  }\n  parts {\n    ...AxiePart\n    __typename\n  }\n  stats {\n    ...AxieStats\n" +
                "    __typename\n  }\n  auction {\n    ...AxieAuction\n    __typename\n  }\n  ownerProfile {\n" +
                "    name\n    __typename\n  }\n  battleInfo {\n    ...AxieBattleInfo\n    __typename\n  }\n" +
                "  children {\n    id\n    name\n    class\n    image\n    title\n    stage\n    __typename\n" +
                "  }\n  __typename\n}\n\nfragment AxieBattleInfo on AxieBattleInfo {\n  banned\n  banUntil\n  level\n" +
                "  __typename\n}\n\nfragment AxiePart on AxiePart {\n  id\n  name\n  class\n  type\n  specialGenes\n" +
                "  stage\n  abilities {\n    ...AxieCardAbility\n    __typename\n  }\n  __typename\n}\n\n" +
                "fragment AxieCardAbility on AxieCardAbility {\n  id\n  name\n  attack\n  defense\n  energy\n" +
                "  description\n  backgroundUrl\n  effectIconUrl\n  __typename\n}\n\nfragment AxieStats on AxieStats {" +
                "\n  hp\n  speed\n  skill\n  morale\n  __typename\n}\n\nfragment AxieAuction on Auction {\n" +
                "  startingPrice\n  endingPrice\n  startingTimestamp\n  endingTimestamp\n  duration\n  timeLeft\n" +
                "  currentPrice\n  currentPriceUSD\n  suggestedPrice\n  seller\n  listingIndex\n  state\n  __typename\n}\n"}
        try:
            r = requests.post(self.url, headers=self.headers, json=body)
            json_data = json.loads(r.text)
        except ValueError:
            return None

        self.save_axie(json_data['data']['axie'])
        return json_data['data']['axie']

    def get_axie_name(self, axie_id):
        """
        Get the name of an axie based on his ID
        :param axie_id: The id of the axie
        :return: Name of the axie
        """
        body = {"operationName": "GetAxieName", "variables": {"axieId": axie_id},
                "query": "query GetAxieName($axieId: ID!) {\n  axie(axieId: $axieId) {\n    ...AxieName\n" +
                "    __typename\n  }\n}\n\nfragment AxieName on Axie {\n  name\n  __typename\n}\n"}
        try:
            r = requests.post(self.url, headers=self.headers, json=body)
            json_data = json.loads(r.text)
        except ValueError as e:
            return e
        return json_data['data']['axie']['name']

    def get_axie_stats(self, axie_id):
        """
        Get axie 4 basic stats (HP, morale, skill, speed)
        :param axie_id: String ID of the axie
        :return: Dict with the stats
        """
        data = self.get_axie_detail(axie_id)
        return data['stats']

    def get_axie_parts(self, axie_id):
        """
        Get axies body parts from an axie ID
        :param axie_id: String ID of the axie
        :return: Dict with the differents body parts
        """
        data = self.get_axie_detail(axie_id)
        return data['parts']

    def get_axie_class(self, axie_id):
        """
        Get the class of an axie based on it's ID
        :param axie_id: String ID of the axie
        :return: Dict with the differents body parts
        """
        data = self.get_axie_detail(axie_id)
        return data['class']

    def get_axie_children(self, id):
        """
        Get the children of an axie on given id OR given axie data
        :param id: id of the axie
        :return: list of id of the children
        """
        axie = self.get_axie_detail(id)
        l = list()
        if 'children' in str(axie):
            for children in axie['children']:
                l.append(int(children['id']))
        return l

    def get_latest_breed_children(self, children):
        """
        Get the children from the last breed WITH SAME PARENTS
        (based 24h around last children bred) for an axie on given id OR given axie data
        :param children: list of children ID
        :param children_data: children data
        :return: list of children from last breed
        """
        one_day = 86400
        res, l = [], []

        for axie in children:
            child = self.get_axie_detail(axie)
            l.append({'date': child['birthDate'], 'id': child['id'], 'matronId': child['matronId'],
                      'sireId': child['sireId']})

        l = sorted(l, key=lambda i: i['date'], reverse=True)
        latest = l[0]['date']
        for axie in l:
            if (latest + one_day) - axie['birthDate'] <= 0:
                res.append(axie['id'])
        return res

    def rename_axie(self, axie_id, new_name):
        """
        Rename an axie
        :param axie_id: The id of the axie to rename
        :param new_name: The new name of the axie
        :return: True/False or error
        """
        body = {"operationName": "RenameAxie", "variables": {"axieId": str(axie_id), "name": str(new_name)},
                "query": "mutation RenameAxie($axieId: ID!, $name: String!) {\n" +
                "  renameAxie(axieId: $axieId, name: $name) {\n    result\n    __typename\n  }\n}\n"}
        try:
            r = requests.post(self.url, headers=self.headers, json=body)
            json_data = json.loads(r.text)
        except ValueError as e:
            return e
        if json_data['data'] is None:
            return False
        return json_data['data']['renameAxie']['result']

    def get_axie_total_breed_cost(self, axie_id):
        """
        Get the price in $ you spent to breed an axie (based on prices history at time of breed)
        :param axie_id: ID of the axie you want to evaluate
        :return:
        """
        if not isinstance(axie_id, int):
            return "Error in axie ID."

        txs = Ronin.ronin_txs(self.get_axie_owner(axie_id))
        children = self.get_axie_children(axie_id)
        total = 0
        l = list()
        for i in txs:
            if len(i['logs']) == 4 and len(i['logs'][3]['topics']) > 1 and int(i['logs'][3]['topics'][1], 16) in children:
                prices = Utils.get_prices_from_timestamp(i['timestamp'])
                slp_price = int(i['logs'][1]['data'], 16) * prices['slp']
                axs_price = prices['axs']
                l.append({'date': datetime.datetime.fromtimestamp(i['timestamp']).strftime('%d-%m-%Y'),
                          'axs_price': round(prices['axs'], 2), 'slp_price': round(prices['slp'], 2),
                          'breed_cost': round(slp_price + axs_price, 2), 'axs_cost': round(axs_price, 2),
                          'slp_cost': round(slp_price, 2), 'axie_id': int(i['logs'][3]['topics'][1], 16)})
                total += slp_price + axs_price
        res = dict()
        res['total_breed_cost'] = round(total, 2)
        res['average_breed_cost'] = round(total / len(children), 2)
        res['details'] = l
        return res