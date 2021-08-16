import requests
import json
import yaml
import qrcode
import os
import datetime
import time
import math
import sys
from datetime import timedelta

from web3 import Web3
from web3.auto import w3
from eth_account.messages import encode_defunct
from collections import namedtuple
from pprint import pprint


class pyaxie(object):

	def __init__(self, ronin_address="", private_key=""):
		"""
		Init the class variables, we need a ronin address and its private key
		:param ronin_address: The ronin address
		:param private_key: Private key belonging to the ronin account
		"""
		with open("secret.yaml", "r") as file:
			config = yaml.safe_load(file)

		self.config = config
		self.ronin_address = ronin_address
		self.private_key = private_key
		self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36', 'authorization': ""}
		self.url = "https://axieinfinity.com/graphql-server-v2/graphql"
		self.access_token = self.get_access_token()
		self.account_id = 0
		self.email = ""
		self.slp_contract = None
		self.ronin_web3 = self.get_ronin_web3()
		self.axie_list_path = config['paths']['axie_list_path']
		self.slp_track_path = config['paths']['slp_track_path']
		self.slp_abi_path = 'slp_abi.json'
		self.slp_contract = self.get_slp_contract(self.ronin_web3, self.slp_abi_path)
		self.name = "you"

		for scholar in config['scholars']:
			if config['scholars'][scholar]['ronin_address'] == ronin_address:
				self.payout_percentage = config['scholars'][scholar]['payout_percentage']
				self.personal_ronin = config['scholars'][scholar]['personal_ronin']
				self.name = scholar
				break
			else:
				self.payout_percentage = 0
				self.personal_ronin = None



	############################
	# Authentication functions #
	############################

	def get_raw_message(self):
		"""
		Ask the API for a message to sign with the private key (authenticate)
		:return: message to sign
		"""
		body = {"operationName": "CreateRandomMessage", "variables": {}, "query": "mutation CreateRandomMessage {\n  createRandomMessage\n}\n"}

		r = requests.post(self.url, headers=self.headers, data=body)
		try:
			json_data = json.loads(r.text)
		except ValueError as e:
			return e
		return json_data['data']['createRandomMessage']

	def sign_message(self, raw_message, private_key=''):
		"""
		Sign a raw message
		:param raw_message: The raw message from get_raw_message()
		:param private_key: The private key of the account
		:return: The signed message
		"""
		if private_key:
			key = private_key
		else:
			key = self.private_key
		pk = bytearray.fromhex(key)
		message = encode_defunct(text=raw_message)
		hex_signature = w3.eth.account.sign_message(message, private_key=pk)
		return hex_signature

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

		body = {"operationName": "CreateAccessTokenWithSignature", "variables": {"input": {"mainnet": "ronin", "owner": "User's Eth Wallet Address", "message": "User's Raw Message", "signature": "User's Signed Message"}}, "query": "mutation CreateAccessTokenWithSignature($input: SignatureInput!) {  createAccessTokenWithSignature(input: $input) {    newAccount    result    accessToken    __typename  }}"}
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
			return
		msg = self.get_raw_message()
		signed = self.sign_message(msg)
		token = self.submit_signature(signed, msg)
		self.access_token = token
		self.headers['authorization'] = 'Bearer ' + token
		return token

	def get_qr_code(self):
		"""
		Function to create a QRCode from an access_token
		"""
		img = qrcode.make(self.access_token)
		name = 'QRCode-' + str(datetime.datetime.now()) + '.png'
		img.save(name)
		return name

	#################################
	# Account interaction functions #
	#################################

	def get_price(self, currency):
		"""
		Get the price in USD for 1 ETH / SLP / AXS
		:return: The price in US of 1 token
		"""
		body = {"operationName": "NewEthExchangeRate", "variables": {}, "query": "query NewEthExchangeRate {\n  exchangeRate {\n    " + currency.lower() + " {\n      usd\n      __typename\n    }\n    __typename\n  }\n}\n"}
		r = requests.post(self.url, headers=self.headers, json=body)
		try:
			json_data = json.loads(r.text)
		except ValueError as e:
			return e
		return json_data['data']['exchangeRate'][currency.lower()]['usd']

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

		self.account_id = json_data['accountId']
		self.email = json_data['email']
		self.name = json_data['name']
		return json_data

	def get_activity_log(self):
		"""
		Get datas about the activity log
		:return: activity log
		"""
		body = {"operationName": "GetActivityLog", "variables": {"from": 0, "size": 6}, "query": "query GetActivityLog($from: Int, $size: Int) {\n  profile {\n    activities(from: $from, size: $size) {\n      ...Activity\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment Activity on Activity {\n  activityId\n  accountId\n  action\n  timestamp\n  seen\n  data {\n    ... on ListAxie {\n      ...ListAxie\n      __typename\n    }\n    ... on UnlistAxie {\n      ...UnlistAxie\n      __typename\n    }\n    ... on BuyAxie {\n      ...BuyAxie\n      __typename\n    }\n    ... on GiftAxie {\n      ...GiftAxie\n      __typename\n    }\n    ... on MakeAxieOffer {\n      ...MakeAxieOffer\n      __typename\n    }\n    ... on CancelAxieOffer {\n      ...CancelAxieOffer\n      __typename\n    }\n    ... on SyncExp {\n      ...SyncExp\n      __typename\n    }\n    ... on MorphToPetite {\n      ...MorphToPetite\n      __typename\n    }\n    ... on MorphToAdult {\n      ...MorphToAdult\n      __typename\n    }\n    ... on BreedAxies {\n      ...BreedAxies\n      __typename\n    }\n    ... on BuyLand {\n      ...BuyLand\n      __typename\n    }\n    ... on ListLand {\n      ...ListLand\n      __typename\n    }\n    ... on UnlistLand {\n      ...UnlistLand\n      __typename\n    }\n    ... on GiftLand {\n      ...GiftLand\n      __typename\n    }\n    ... on MakeLandOffer {\n      ...MakeLandOffer\n      __typename\n    }\n    ... on CancelLandOffer {\n      ...CancelLandOffer\n      __typename\n    }\n    ... on BuyItem {\n      ...BuyItem\n      __typename\n    }\n    ... on ListItem {\n      ...ListItem\n      __typename\n    }\n    ... on UnlistItem {\n      ...UnlistItem\n      __typename\n    }\n    ... on GiftItem {\n      ...GiftItem\n      __typename\n    }\n    ... on MakeItemOffer {\n      ...MakeItemOffer\n      __typename\n    }\n    ... on CancelItemOffer {\n      ...CancelItemOffer\n      __typename\n    }\n    ... on ListBundle {\n      ...ListBundle\n      __typename\n    }\n    ... on UnlistBundle {\n      ...UnlistBundle\n      __typename\n    }\n    ... on BuyBundle {\n      ...BuyBundle\n      __typename\n    }\n    ... on MakeBundleOffer {\n      ...MakeBundleOffer\n      __typename\n    }\n    ... on CancelBundleOffer {\n      ...CancelBundleOffer\n      __typename\n    }\n    ... on AddLoomBalance {\n      ...AddLoomBalance\n      __typename\n    }\n    ... on WithdrawFromLoom {\n      ...WithdrawFromLoom\n      __typename\n    }\n    ... on AddFundBalance {\n      ...AddFundBalance\n      __typename\n    }\n    ... on WithdrawFromFund {\n      ...WithdrawFromFund\n      __typename\n    }\n    ... on TopupRoninWeth {\n      ...TopupRoninWeth\n      __typename\n    }\n    ... on WithdrawRoninWeth {\n      ...WithdrawRoninWeth\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ListAxie on ListAxie {\n  axieId\n  priceFrom\n  priceTo\n  duration\n  txHash\n  __typename\n}\n\nfragment UnlistAxie on UnlistAxie {\n  axieId\n  txHash\n  __typename\n}\n\nfragment BuyAxie on BuyAxie {\n  axieId\n  price\n  owner\n  txHash\n  __typename\n}\n\nfragment GiftAxie on GiftAxie {\n  axieId\n  destination\n  txHash\n  __typename\n}\n\nfragment MakeAxieOffer on MakeAxieOffer {\n  axieId\n  price\n  txHash\n  __typename\n}\n\nfragment CancelAxieOffer on CancelAxieOffer {\n  axieId\n  txHash\n  __typename\n}\n\nfragment SyncExp on SyncExp {\n  axieId\n  exp\n  txHash\n  __typename\n}\n\nfragment MorphToPetite on MorphToPetite {\n  axieId\n  txHash\n  __typename\n}\n\nfragment MorphToAdult on MorphToAdult {\n  axieId\n  txHash\n  __typename\n}\n\nfragment BreedAxies on BreedAxies {\n  sireId\n  matronId\n  lovePotionAmount\n  txHash\n  __typename\n}\n\nfragment BuyLand on BuyLand {\n  row\n  col\n  price\n  owner\n  txHash\n  __typename\n}\n\nfragment ListLand on ListLand {\n  row\n  col\n  priceFrom\n  priceTo\n  duration\n  txHash\n  __typename\n}\n\nfragment UnlistLand on UnlistLand {\n  row\n  col\n  txHash\n  __typename\n}\n\nfragment GiftLand on GiftLand {\n  row\n  col\n  destination\n  txHash\n  __typename\n}\n\nfragment MakeLandOffer on MakeLandOffer {\n  row\n  col\n  price\n  txHash\n  __typename\n}\n\nfragment CancelLandOffer on CancelLandOffer {\n  row\n  col\n  txHash\n  __typename\n}\n\nfragment BuyItem on BuyItem {\n  tokenId\n  itemAlias\n  price\n  owner\n  txHash\n  __typename\n}\n\nfragment ListItem on ListItem {\n  tokenId\n  itemAlias\n  priceFrom\n  priceTo\n  duration\n  txHash\n  __typename\n}\n\nfragment UnlistItem on UnlistItem {\n  tokenId\n  itemAlias\n  txHash\n  __typename\n}\n\nfragment GiftItem on GiftItem {\n  tokenId\n  itemAlias\n  destination\n  txHash\n  __typename\n}\n\nfragment MakeItemOffer on MakeItemOffer {\n  tokenId\n  itemAlias\n  price\n  txHash\n  __typename\n}\n\nfragment CancelItemOffer on CancelItemOffer {\n  tokenId\n  itemAlias\n  txHash\n  __typename\n}\n\nfragment BuyBundle on BuyBundle {\n  listingIndex\n  price\n  owner\n  txHash\n  __typename\n}\n\nfragment ListBundle on ListBundle {\n  numberOfItems\n  priceFrom\n  priceTo\n  duration\n  txHash\n  __typename\n}\n\nfragment UnlistBundle on UnlistBundle {\n  listingIndex\n  txHash\n  __typename\n}\n\nfragment MakeBundleOffer on MakeBundleOffer {\n  listingIndex\n  price\n  txHash\n  __typename\n}\n\nfragment CancelBundleOffer on CancelBundleOffer {\n  listingIndex\n  txHash\n  __typename\n}\n\nfragment AddLoomBalance on AddLoomBalance {\n  amount\n  senderAddress\n  receiverAddress\n  txHash\n  __typename\n}\n\nfragment WithdrawFromLoom on WithdrawFromLoom {\n  amount\n  senderAddress\n  receiverAddress\n  txHash\n  __typename\n}\n\nfragment AddFundBalance on AddFundBalance {\n  amount\n  senderAddress\n  txHash\n  __typename\n}\n\nfragment WithdrawFromFund on WithdrawFromFund {\n  amount\n  receiverAddress\n  txHash\n  __typename\n}\n\nfragment WithdrawRoninWeth on WithdrawRoninWeth {\n  amount\n  receiverAddress\n  txHash\n  receiverAddress\n  __typename\n}\n\nfragment TopupRoninWeth on TopupRoninWeth {\n  amount\n  receiverAddress\n  txHash\n  receiverAddress\n  __typename\n}\n"}
		r = requests.post(self.url, headers=self.headers, json=body)
		try:
			json_data = json.loads(r.text)
		except ValueError as e:
			return e
		return json_data['data']['profile']['activities']

	def get_profile_name(self, ronin_address=''):
		"""
		Get the profile name of a ronin address
		:param ronin_address: The target ronin account
		:return: The name of the account
		"""
		if ronin_address == '':
			ronin_address = self.ronin_address
		body = {"operationName": "GetProfileNameByRoninAddress", "variables": {"roninAddress": ronin_address}, "query": "query GetProfileNameByRoninAddress($roninAddress: String!) {\n  publicProfileWithRoninAddress(roninAddress: $roninAddress) {\n    accountId\n    name\n    __typename\n  }\n}\n"}
		r = requests.post(self.url, headers=self.headers, json=body)
		try:
			json_data = json.loads(r.text)
		except ValueError as e:
			return e
		return json_data['data']['publicProfileWithRoninAddress']['name']

	def get_public_profile(self, ronin_address=''):
		"""
		Get infos about the given ronin address
		:param ronin_address: The target ronin account
		:return: Public datas of the ronin account
		"""
		if ronin_address == '':
			ronin_address = self.ronin_address
		body = {"operationName": "GetProfileByRoninAddress", "variables": {"roninAddress": ronin_address}, "query": "query GetProfileByRoninAddress($roninAddress: String!) {\n  publicProfileWithRoninAddress(roninAddress: $roninAddress) {\n    ...Profile\n    __typename\n  }\n}\n\nfragment Profile on PublicProfile {\n  accountId\n  name\n  addresses {\n    ...Addresses\n    __typename\n  }\n  __typename\n}\n\nfragment Addresses on NetAddresses {\n  ethereum\n  tomo\n  loom\n  ronin\n  __typename\n}\n"}
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
		r = requests.get("https://game-api.skymavis.com/game-api/last-season-leaderboard", params=params)

		try:
			json_data = json.loads(r.text)
			if not json_data['success']:
				return {'mmr': 0, 'rank': 0}
		except ValueError as e:
			return e
		return {'mmr': int(json_data['items'][1]['elo']), 'rank': int(json_data['items'][1]['rank'])}



	#############################################
	# Functions to interact with axies from web #
	#############################################

	def get_axie_list(self, ronin_address=''):
		"""
		Get informations about the axies in a specific account
		:param ronin_address: The ronin address of the target account
		:return: Data about the axies
		"""
		if ronin_address == '':
			ronin_address = self.ronin_address
		body = {"operationName": "GetAxieBriefList", "variables": {"from": 0, "size": 24, "sort": "IdDesc", "auctionType": "All", "owner": ronin_address, "criteria": {"region": None, "parts": None, "bodyShapes": None, "classes": None, "stages": None, "numMystic": None, "pureness": None, "title": None, "breedable": None, "breedCount": None, "hp":[],"skill":[],"speed":[],"morale":[]}},"query":"query GetAxieBriefList($auctionType: AuctionType, $criteria: AxieSearchCriteria, $from: Int, $sort: SortBy, $size: Int, $owner: String) {\n  axies(auctionType: $auctionType, criteria: $criteria, from: $from, sort: $sort, size: $size, owner: $owner) {\n    total\n    results {\n      ...AxieBrief\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment AxieBrief on Axie {\n  id\n  name\n  stage\n  class\n  breedCount\n  image\n  title\n  battleInfo {\n    banned\n    __typename\n  }\n  auction {\n    currentPrice\n    currentPriceUSD\n    __typename\n  }\n  parts {\n    id\n    name\n    class\n    type\n    specialGenes\n    __typename\n  }\n  __typename\n}\n"}
		r = requests.post(self.url, headers=self.headers, json=body)
		try:
			json_data = json.loads(r.text)
		except ValueError as e:
			return e
		return json_data['data']['axies']['results']

	def get_axie_image(self, axie_id):
		"""
		Get the image link to an axie
		:param axie_id: String ID of the axie you are targeting
		:return: Link to the image
		"""
		body = {"operationName": "GetAxieMetadata", "variables": {"axieId": axie_id}, "query": "query GetAxieMetadata($axieId: ID!) {\n  axie(axieId: $axieId) {\n    id\n    image\n    __typename\n  }\n}\n"}
		r = requests.post(self.url, headers=self.headers, json=body)
		try:
			json_data = json.loads(r.text)
		except ValueError as e:
			return e
		return json_data['data']['axie']['image']

	def get_axie_detail(self, axie_id):
		"""
		Get informations about an Axie based on its ID
		:param axie_id: string ID of the axie
		:return: A dict with the adatas of the axie
		"""
		body = {"operationName": "GetAxieDetail", "variables": {"axieId": axie_id}, "query": "query GetAxieDetail($axieId: ID!) {\n  axie(axieId: $axieId) {\n    ...AxieDetail\n    __typename\n  }\n}\n\nfragment AxieDetail on Axie {\n  id\n  image\n  class\n  chain\n  name\n  genes\n  owner\n  birthDate\n  bodyShape\n  class\n  sireId\n  sireClass\n  matronId\n  matronClass\n  stage\n  title\n  breedCount\n  level\n  figure {\n    atlas\n    model\n    image\n    __typename\n  }\n  parts {\n    ...AxiePart\n    __typename\n  }\n  stats {\n    ...AxieStats\n    __typename\n  }\n  auction {\n    ...AxieAuction\n    __typename\n  }\n  ownerProfile {\n    name\n    __typename\n  }\n  battleInfo {\n    ...AxieBattleInfo\n    __typename\n  }\n  children {\n    id\n    name\n    class\n    image\n    title\n    stage\n    __typename\n  }\n  __typename\n}\n\nfragment AxieBattleInfo on AxieBattleInfo {\n  banned\n  banUntil\n  level\n  __typename\n}\n\nfragment AxiePart on AxiePart {\n  id\n  name\n  class\n  type\n  specialGenes\n  stage\n  abilities {\n    ...AxieCardAbility\n    __typename\n  }\n  __typename\n}\n\nfragment AxieCardAbility on AxieCardAbility {\n  id\n  name\n  attack\n  defense\n  energy\n  description\n  backgroundUrl\n  effectIconUrl\n  __typename\n}\n\nfragment AxieStats on AxieStats {\n  hp\n  speed\n  skill\n  morale\n  __typename\n}\n\nfragment AxieAuction on Auction {\n  startingPrice\n  endingPrice\n  startingTimestamp\n  endingTimestamp\n  duration\n  timeLeft\n  currentPrice\n  currentPriceUSD\n  suggestedPrice\n  seller\n  listingIndex\n  state\n  __typename\n}\n"}
		r = requests.post(self.url, headers=self.headers, json=body)
		try:
			json_data = json.loads(r.text)
		except ValueError as e:
			return e
		return json_data['data']['axie']

	def get_axie_name(self, axie_id):
		"""
		Get the name of an axie based on his ID
		:param axie_id: The id of the axie
		:return: Name of the axie
		"""
		body = {"operationName": "GetAxieName", "variables": {"axieId": axie_id}, "query": "query GetAxieName($axieId: ID!) {\n  axie(axieId: $axieId) {\n    ...AxieName\n    __typename\n  }\n}\n\nfragment AxieName on Axie {\n  name\n  __typename\n}\n"}
		r = requests.post(self.url, headers=self.headers, json=body)
		try:
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

	def rename_axie(self, axie_id, new_name):
		"""
		Rename an axie
		:param axie_id: The id of the axie to rename
		:param new_name: The new name of the axie
		:return: True/False or error
		"""
		body = {"operationName": "RenameAxie", "variables": {"axieId": str(axie_id),"name": str(new_name) }, "query": "mutation RenameAxie($axieId: ID!, $name: String!) {\n  renameAxie(axieId: $axieId, name: $name) {\n    result\n    __typename\n  }\n}\n"}
		r = requests.post(self.url, headers=self.headers, json=body)
		try:
			json_data = json.loads(r.text)
		except ValueError as e:
			return e
		if json_data['data'] is None:
			return json_data['errors']['message']
		return json_data['data']['renameAxie']['result']

	###############################################
	# Functions to interact with stored axie data #
	###############################################

	def save_axie(self, axie_data):
		"""
		Save an axie details to the local axie_list
		:param axie_data:
		:param axie_list: Path of the axie_list file
		"""
		axie_list = self.axie_list()
		axie_id = axie_data['id']
		if axie_list:
			axie_list.update({axie_id: axie_data})
		else:
			axie_list = {axie_id: axie_data}
		f = open(self.axie_list_path, 'a')
		yaml.safe_dump(axie_list, f)
		f.close()

	def check_axie(self, axie_id):
		"""
		Check if we have this axie data locally
		:param axie_id: String of the ID of the axie to check
		:return: Data of the axie or None if not locally
		"""
		with open(self.axie_list_path) as f:
			data = yaml.safe_load(f)

		for val in data:
			if val == str(axie_id):
				return val
		return []

	def update_axie_list(self):
		"""
		Update the local axie_list with the new datas
		"""
		axie_list = self.axie_list()
		new = {}

		for axie in axie_list:
			new[axie['id']] = self.get_axie_detail(axie['id'])
		with open(self.axie_list_path, 'w') as outfile:
			yaml.safe_dump(new, outfile)

	def axie_list(self):
		"""
		Get the list of axies stored locally
		:return: List of axie data
		"""
		if os.stat(self.axie_list_path).st_size > 3:
			f = open(self.axie_list_path, 'r')
			data = yaml.safe_load(f)
			f.close()
			if data:
				return data
		return None

	def axie_detail(self, axie_id):
		"""
		Retrieve local details about an axie
		:param axie_id: The ID of the axie
		:return: Informations about the axie
		"""
		data = self.axie_list()
		if data:
			return data[str(axie_id)]
		return None

	def axie_infos(self, axie_id, key):
		"""
		Retrieve locally specific informations (key) about axie
		:param axie_id: String ID of the axie
		:param key: 'parts' or 'class' or 'stats' (list on documentation)
		:return: Information about the axie
		"""
		if self.check_axie(axie_id):
			return self.axie_detail(axie_id)[key]
		return "This axie is not registered : " + str(axie_id)

	def axie_link(self, axie_id):
		"""
		Return an URL to the axie page
		:param axie_id: String of the axie ID
		:return: URL of the axie
		"""
		url = 'https://marketplace.axieinfinity.com/axie/'
		return url + str(axie_id)

	###################
	# Ronin functions #
	###################

	def get_ronin_web3(self):
		"""
		:return: Return the ronin web3
		"""
		web3 = Web3(Web3.HTTPProvider('https://proxy.roninchain.com/free-gas-rpc'))
		return web3

	def get_slp_contract(self, ronin_web3, slp_abi_path):
		"""
		:param ronin_web3: ronin web3 object
		:param slp_abi_path: ABI for SLP
		:return: The contract to interact with
		"""
		slp_contract_address = "0xa8754b9fa15fc18bb59458815510e40a12cd2014"
		with open(slp_abi_path) as f:
			try:
				slp_abi = json.load(f)
			except ValueError as e:
				return e
		contract = ronin_web3.eth.contract(address=w3.toChecksumAddress(slp_contract_address), abi=slp_abi)
		self.slp_contract = contract
		return contract

	def get_claimed_slp(self, address=''):
		"""
		:param address: Ronin address to check
		:return: The amount of claimed SLP
		"""
		if address == '':
			address = self.ronin_address
		response = requests.get(f"https://game-api.skymavis.com/game-api/clients/{address}/items/1",
								headers=self.headers,
								data="")
		try:
			data = json.loads(response.text)
		except ValueError as e:
			return e
		return int(data['blockchain_related']['balance'])

	def get_unclaimed_slp(self, address=''):
		"""
		:param address: Ronin address to check
		:return: The amount of unclaimed SLP
		"""
		if address == '':
			address = self.ronin_address
		response = requests.get(f"https://game-api.skymavis.com/game-api/clients/{address}/items/1", headers=self.headers, data="")
		try:
			result = response.json()
		except ValueError as e:
			return e
		return int(result["total"] - result['blockchain_related']['balance'])

	def get_last_claim(self, address=''):
		"""
		Return the last time SLP was claimed for this account
		:param address: Ronin address
		:return: Time in sec
		"""
		if address == '':
			address = self.ronin_address

		response = requests.get(f"https://game-api.skymavis.com/game-api/clients/{address}/items/1", headers=self.headers, data="")
		try:
			result = response.json()
		except ValueError as e:
			return e

		return int(result["last_claimed_item_at"])

	def claim_slp(self):
		"""
		Claim SLP on the account.
		:return: Transaction of the claim
		"""
		print("\nClaiming SLP for : ", self.name)

		if datetime.datetime.utcnow() + timedelta(days=-14) < datetime.datetime.fromtimestamp(self.get_last_claim()):
			return 'Too soon to claim'

		slp_claim = {
			'address': self.ronin_address,
			'private_key': self.private_key,
			'state': {"signature": None}
		}
		access_token = self.access_token
		custom_headers = self.headers.copy()
		custom_headers["authorization"] = f"Bearer {access_token}"
		response = requests.post(f"https://game-api.skymavis.com/game-api/clients/{self.ronin_address}/items/1/claim",
								 headers=custom_headers, json="")

		if response.status_code != 200:
			print(response.text)
			return

		result = response.json()["blockchain_related"]["signature"]
		checksum_address = w3.toChecksumAddress(self.ronin_address)
		nonce = self.ronin_web3.eth.get_transaction_count(checksum_address)
		slp_claim['state']["signature"] = result["signature"].replace("0x", "")
		claim_txn = self.slp_contract.functions.checkpoint(checksum_address, result["amount"], result["timestamp"],
													  slp_claim['state']["signature"]).buildTransaction(
			{'gas': 1000000, 'gasPrice': 0, 'nonce': nonce})
		signed_txn = self.ronin_web3.eth.account.sign_transaction(claim_txn, private_key=bytearray.fromhex(
			self.private_key.replace("0x", "")))

		self.ronin_web3.eth.send_raw_transaction(signed_txn.rawTransaction)
		return self.ronin_web3.toHex(self.ronin_web3.keccak(signed_txn.rawTransaction))

	def transfer_slp(self, to_address, amount):
		"""
		Transfer SLP from pyaxie ronin address to the to_address
		:param to_address: Receiver of the SLP. Format : 0x
		:param amount: Amount of SLP to send
		:return: Transaction hash
		"""
		if amount < 1 or len(to_address) < 20:
			return {"error": "Make sure that the amount is not under 1 and a to_address is correctly set."}

		transfer_txn = self.slp_contract.functions.transfer(w3.toChecksumAddress(to_address), amount).buildTransaction({
			'chainId': 2020,
			'gas': 100000,
			'gasPrice': Web3.toWei('0', 'gwei'),
			'nonce': self.ronin_web3.eth.get_transaction_count(w3.toChecksumAddress(self.ronin_address))
		})
		private_key = bytearray.fromhex(self.private_key.replace("0x", ""))
		signed_txn = self.ronin_web3.eth.account.sign_transaction(transfer_txn, private_key=private_key)
		self.ronin_web3.eth.send_raw_transaction(signed_txn.rawTransaction)
		return self.ronin_web3.toHex(self.ronin_web3.keccak(signed_txn.rawTransaction))

	def payout(self):
		"""
		Send money to the scholar and to the manager/academy or directly to manager if manager called
		:return: List of 2 transactions hash : scholar and manager
		"""
		txns = list()
		slp_balance = self.get_claimed_slp(self.ronin_address)
		scholar_payout_amount = math.ceil(slp_balance * self.payout_percentage)
		academy_payout_amount = slp_balance - scholar_payout_amount

		if scholar_payout_amount < 1 or academy_payout_amount < 1:
			return "Nothing to send."

		try:
			print("Sending {} SLP to {} : {} ".format(scholar_payout_amount, self.name, self.personal_ronin))
			txns.append(str(self.transfer_slp(self.personal_ronin, scholar_payout_amount)))
			time.sleep(2)
		except ValueError as e:
			return e

		try:
			print("Sending {} SLP to {} : {} ".format(academy_payout_amount, "You", self.config['personal']['ronin_address']))
			txns.append(str(self.transfer_slp(self.config['personal']['ronin_address'], academy_payout_amount)))
			time.sleep(2)
		except ValueError as e:
			return e
		return txns







