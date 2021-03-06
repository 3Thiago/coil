# node.py
import requests
import json
import sys
import os

from urllib.parse import urlparse
from pathlib import Path
from time import time

from coil.tx import Transaction, Coinbase, createInput, createOutput
from coil.block import Block
from coil.chain import Chain
from coil.wallet import Wallet

CONFIG_FOLDER = str(Path.home()) + "/.config/coil"

def log(info):
    print("[Message] " + info)

def transactionFromDict(d):
    if d["inputs"] == []:
        # Coinbase Transaction
        o = d["outputs"][0]
        return Coinbase(o["address"], d["publicKey"], amount=o["amount"])
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
    response = response["chain"]
    blocks = [ blockFromDict(b) for b in response ]

    # Get Genesis Block
    genesis = blocks[0]

    # This could be prettier
    creator = genesis.transactions[0].outputs[0]["address"]
    try:
        pubkey = genesis.transactions[0]["pubkey"]
    except:
        pubkey = genesis.transactions[0].__dict__["publicKey"]

    return Chain(creator, pubkey, genesis=genesis, chain=blocks)

def chainFromPeers(peers):
    # Iterate through peers until a
    # valid chain is found
    peer_index = 0
    for peer in peers:
        url = "http://" + peer + "/chain/"

        try:
            response = requests.get(url)
            return chainFromResponse(response.json())

        except requests.exceptions.RequestException:
            print("Continue")

    log("Could not download blockchain from peers.")
    raise "Could not download blockchain from peers."

class Node(object):
    def __init__(self, creator, creatorPubKey, nodeLoc):
        print("Spinning up node...")
        self.chain = None
        self.creator = creator
        self.creatorPubKey = creatorPubKey
        self.mempool = []
        self.nodeLoc = nodeLoc        
        self.peers = self.readPeers()

        if self.readFromDisk():
            self.chain = self.readFromDisk()
        else:
            self.chain = Chain(self.creator, self.creatorPubKey)

        self.resolveChain()
        print("Node is live")

    def readPeers(self):
        lines = open(CONFIG_FOLDER + "/peers.txt", "r").readlines()
        lines = [ s.strip() for s in lines ]
        livePeers = set()

        for peer in lines:
            if peer != "http://" + self.nodeLoc:
                parsed_url = urlparse(peer)
                livePeers.add(parsed_url.netloc)

        return livePeers

    def writeToDisk(self):
        # Save chain to disk
        fullChain = { "chain": self.chain.displayDict() }
        jsonString = json.dumps(fullChain)

        f = open(CONFIG_FOLDER + "/blockchain/chain.json", "w")
        f.write(jsonString)
        f.close()

    def readFromDisk(self):
        f = open(CONFIG_FOLDER + "/blockchain/chain.json", "r")
        response = json.loads(f.read())
        return chainFromResponse(response)

        
    def ping(self, nodeloc):
        # Pinging a Wire node...
        # expects a plain text
        try:
            response = requests.get("http://" + nodeloc + "/ping/", timeout=5).json()
            if response["time"]:
                print("Successfull ping")
                return True
            else:
                return False

        except:
            # Remove peer from pool
            # & then broastcast
            return False

    def broadcast(self, route):
        # Send a GET request to all registered peers
        # PING all peers, if they're dead... update
        # self.peers
        if self.peers:
            for peer in self.peers.copy():
                if peer != self.nodeLoc:
                    if self.ping(peer):
                        try:
                            requests.get("http://" + peer + route, timeout=5)
                        except:
                            return False
                    else:
                        # Remove peer from pool
                        # & then broastcast
                        if peer in self.peers:
                            self.peers.remove(peer)
                            self.broadcast("/resolve/peers")

    def registerPeer(self, address):
        parsed_url = urlparse("http://" + address.strip())
        if parsed_url.netloc:
            self.peers.add(parsed_url.netloc)

        # This this peer is the first
        # peer this node knows about,
        # resolve the chain too
        if len(self.peers) == 1:
            self.resolveChain()

        # Tell nodes to add new peer
        self.broadcast("/join/" + address + "/")

        # Broadcast to all nodes
        self.broadcast("/resolve/peers/")

        return self.peers

    def resolvePeers(self):
        peersLists = {}

        # Read in peers from peers.txt
        # just incase they weren't live
        # on load
        self.peers = self.peers.union(self.readPeers())
        for peer in self.peers:
            if self.ping(peer):
                peerList = requests.get("http://" + peer + "/peers/", timeout=5).json()
                if peerList:
                    peersLists[peer] = peerList

        if peersLists != {}:
            self.peers = set(sorted(peersLists, key=lambda l: len(peersLists[l]), reverse=True))

        return self.peers

    def getChain(self):
        fullChain = { "blockHeight": self.chain.blockHeight, "chain": self.chain.displayDict() }
        return json.dumps(fullChain)

    def getBlock(self, index):
        block = self.chain.chain[index].json()
        return block

    def getLastBlock(self):
        return self.chain.lastBlock.json()

    def resolveChain(self):
        maxHeights = {}

        for peer in self.peers.copy():
            if self.ping(peer):
                response = requests.get("http://" + peer + "/chain/").json()
                maxHeights[peer] = response["blockHeight"]
            # else:
            #     # Remove peers & resolve
            #     self.peers.remove(peer)
            #     self.broadcast("/resolve/peers") 

        # Replace chain
        if maxHeights != {}:
            response = requests.get("http://" + max(maxHeights) + "/chain/").json()
            # Save changes to disk
            self.chain = chainFromResponse(response)
            
        self.writeToDisk()

        fullChain = { "blockHeight": self.chain.blockHeight, "chain": self.chain.displayDict() }
        return json.dumps(fullChain)

    def getMemPool(self):
        return [ tx.__dict__ for tx in self.mempool ]

    def getMemPoolHashes(self):
        return [ tx.hash() for tx in self.mempool ]

    def resolveMemPool(self):
        memPools = {}

        for peer in self.peers:
            if self.ping(peer):
                response = requests.get("http://" + peer + "/mempool").json()
                memPools[peer] = response["pools"]

        if memPools != {}:
            self.mempool = sorted(memPools, key=lambda l: len(memPools[l]), reverse=True)[0]

        return [ tx.__dict__ for tx in self.mempool ]

    def submitTransaction(self, tx):
        # Broadcast to all the new transaction
        self.mempool.append(tx)

    def submitBlock(self, address, minerPubKey, previousBlockHash, nonce, transactionHashes):
        # Broadcast to all the new block
        if self.chain.appendBlock(self.mempool, address, minerPubKey, previousBlockHash, nonce, transactionHashes):
            # Remove blocks from memPool
            self.mempool = [item for item in self.mempool if not item.hash() in transactionHashes]
            return True
        else:
            return False