# coild.py
# Coil Daemon
# Primitive Cryptocurrency
# Written by Jesse Sibley
# MIT Licence (@chickencoder)

# API Overview
# /chain/<opt_block_no>         DONE
# /chain/last                   DONE
# /chain/lastHash               DONE
# /chain/resolve                DONE
# /join/<address:port>          DONE
# /resolve/peers                DONE
# /peers                        DONE
# /balance                      DONE
# /mempool                      DONE
# /tx                           DONE [X]
# /mine                         DONE
# /ping                         DONE

__version__ = "0.1.0"

from coil.wallet import readWallet, writeWallet, Wallet
from coil.tx import Transaction
from coil.node import Node

import sys
import binascii
from time import time
from pathlib import Path

from flask import Flask, Response, request, jsonify
app = Flask(__name__)

WALLET_FOLDER = str(Path.home()) + "/.config/coil/wallets/"
HOST = "0.0.0.0"

if len(sys.argv) > 1:
    PORT = int(sys.argv[1])
else:
    PORT = 1337

################################################
# creator = Wallet()
# writeWallet(WALLET_FOLDER + "master.json", creator)
################################################

creator = readWallet(WALLET_FOLDER + "master.json")
node = Node(creator.address, creator.publicKeyHex, HOST + ":" + str(PORT))

def respondPlain(txt):
    return Response(response=txt, content_type="application/json")

def respondMessage(txt):
    return jsonify(message=txt)

@app.route("/")
def index():
    return jsonify(time=time())

@app.route("/ping/")
def ping():
    return jsonify(time=time())

@app.route("/chain/")
@app.route("/chain/<index>/")
def chain(index=None):
    if index:
        try:
            return respondPlain(node.getBlock(int(index)))
        except Exception:
            return respondMessage("Invalid block index.")
    else:
        return respondPlain(node.getChain())

@app.route("/chain/last/")
def last():
    return respondPlain(node.getLastBlock())

@app.route("/chain/lastHash/")
def last_hash():
    return respondMessage(node.chain.lastBlock.hash())

@app.route("/resolve/chain/")
def resolve_chain():
    return respondPlain(node.resolveChain())

@app.route("/join/<address>/")
def join(address):
    # Make sure that address is not this
    # node's address
    if address != HOST + ":" + str(PORT):
        peers = node.registerPeer(address)
        return jsonify(peers=list(peers))
    else:
        return jsonify(peers=list(node.peers))

@app.route("/resolve/peers/")
def resolve_peers():
    # Request all peers,
    # choose largest list
    peers = node.resolvePeers()
    return jsonify(peers=list(peers))

@app.route("/peers/")
def peers():
    return jsonify(peers=list(node.peers))

@app.route("/balance/<address>/")
def balance(address):
    balance = 0
    for block in node.chain.chain:
        for tx in block.transactions:
            # This is annoying. Must fix
            if type(tx).__name__ != "dict":
                tx = tx.__dict__

            # If Coinbase
            if tx["address"] == address:
                for o in tx["outputs"]:
                    if o["address"] == address:
                        balance += o["amount"]

            elif tx["address"] != address:
                for o in tx["outputs"]:
                    if o["address"] == address:
                        balance += o["amount"]

            outputAddresses = [ a["address"] for a in tx["outputs"] ]
            if tx["address"] == address and not address in outputAddresses:
                balance -= sum([a["amount"] for a in tx["outputs"]])

    return jsonify(address=address, balance=balance)

@app.route("/mempool/")
def mempool():
    return jsonify(pool=node.getMemPool())

@app.route("/resolve/mempool/")
def resolve_mempool():
    mem = node.resolveMemPool()
    return jsonify(pool=mem)

@app.route("/tx", methods=["GET", "POST"])
def transaction():
    if request.method == "POST":
        # privatekey, inputs, outputs
        private = request.form.get("private")
        public = request.form.get("public")
        inputs = request.forms.get("inputs")
        outputs = request.forms.get("outputs")

        # Create Wallet object from POST
        if private and public and inputs and outputs:
            transactor = Wallet(privateKey=binascii.unhexlify(private), publicKey=binascii.unhexlify(public))
            tx = Transaction(wallet.address, inputs, outputs, wallet.publicKeyHex)
            tx.sign(transactor.sign(tx.hash()))

            # Submit transaction to node
            node.submitTransaction(tx)
            node.broadcast("/resolve/mempool/")

            return respondMessage("Transaction has been submitted")
        else:
            return respondMessage("Invalid POST data")

@app.route("/mine/", methods=["GET", "POST"])
def mine():
    try:
        address = request.form.get("minerAddress")
        minerPubKey = request.form.get("minerPubKey")
        previousBlockHash = request.form.get("previousBlockHash")
        nonce = request.form.get("nonce")
        transactionHashes = request.form.get("transactionHashes")

        success = node.submitBlock(address, minerPubKey, previousBlockHash, nonce, transactionHashes)
        node.broadcast("/resolve/chain/")
        return respondMessage("Successfully submitted block")

    except:
        return respondMessage("Failed to mine block")

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)