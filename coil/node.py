# node.py
import requests
import json
import sys

from urllib.parse import urlparse
from time import time

from coil.tx import Transaction, Coinbase, createInput
from coil.block import Block
from coil.chain import Chain
from coil.wallet import Wallet

def log(info):
	print(f"[Message] {info}")

def transactionFromDict(d):
	if d["inputs"] == []:
		# Coinbase Transaction
		o = d["outputs"][0]
		return Coinbase(o["address"], amount=o["amount"])
	else:
		inputs = []
		for i in d["inputs"]:
			inputs.append(createInput(i["prevTransHash"], i["index"]))

		outputs = []
		for o in d["outputs"]:
			outputs.append(createOutput(o["address"], o["amount"]))

		return Transaction(d["address"], d["signature"], inputs, outputs)

def blockFromDict(d):
	prevBlockHash = d["previousBlockHash"]
	nonce = d["nonce"]
	txs = [transactionFromDict(t) for t in d["transactions"]]
	merkleRoot = d["merkleRoot"]
	return Block(prevBlockHash, nonce, txs, merkleRoot)

def chainFromResponse(response):
	blocks = [ blockFromDict(b) for b in response ]

	# Get Genesis Block
	genesis = blocks[0]

	# This could be prettier
	creator = genesis.transactions[0].outputs[0]["address"]

	return Chain(creator, genesis=genesis, chain=blocks)

def chainFromPeers(peers):
	# Iterate through peers until a
	# valid chain is found
	peer_index = 0
	while peer_index < len(peers):
		url = "http://" + list(peers)[0] + "/chain"

		try:
			response = requests.get(url)
			return chainFromResponse(response.json())

		except requests.exceptions.RequestException:
			peer_index += 1		

	log("Could not download blockchain from peers.")

class Node(object):
	def __init__(self, creator):
		self.peers = set()
		self.chain = None
		self.host = "0.0.0.0"
		self.creator = creator

		if len(sys.argv) > 1:
			self.port = int(sys.argv[1])
		else:
			self.port = 1337

		# Read Peers
		peers = open("peers.txt", "r").readlines()
		if peers != []:
			for peer in peers:
				parsed_url = urlparse(peer.strip())
				self.peers.add(parsed_url.netloc)
				
				# Attempt to find chain from peers
				# if not, initialize a chain
				self.chain = chainFromPeers(self.peers)
				if not self.chain:
					self.chain = Chain(self.creator)
		else:
			self.chain = Chain(self.creator)

	def registerPeer(self, address):
		parsed_url = urlparse(peer.strip())
		self.peers.add(parsed_url.netloc)

	def getChain(self):
		fullChain = { "blockHeight": self.chain.blockHeight, "chain": self.chain.displayDict() }
		return json.dumps(fullChain)

	def resolveChain(self):
		maxHeights = {}

		for node in self.peers:
			response = requests.get("http://" + node + "/chain").json()
			maxHeights[node] = response["blockHeight"]

		# Replace chain
		response = requests.get("http://" + max(maxHeights) + "/chain").json()
		print(response["chain"])
		self.chain = chainFromResponse(response["chain"])