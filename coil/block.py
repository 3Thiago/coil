# block.py

import time
import json

from coil import chash
from coil import merkle
from coil import tx

class Block(object):
    def __init__(self, prevHash, nonce, txs, merkle):
        self.previousBlockHash = prevHash
        self.nonce = nonce
        self.transactions = txs
        self.merkleRoot = merkle
        self.timestamp = time.time()

    def hash(self):
        return chash.doubleHashEncodeJSON(self.__dict__)

    def json(self):
        newblock = self.__dict__
        newtransactions = []

        for t in newblock["transactions"]:
            if type(t).__name__ != "dict":
                newtransactions.append(t.__dict__)
            else:
                newtransactions.append(t)

        newblock["transactions"] = newtransactions
        return json.dumps(newblock)

    def verify(self):
        pass

class Genesis(Block):
    def __init__(self, creator):
        # ICO of 120 coins
        txs = [
            tx.Coinbase(creator, None, amount=12000)
        ]

        txs_dict = [ str(t.__dict__) for t in txs ]
        mr = merkle.generateMerkleRoot(txs_dict)

        super(Genesis, self).__init__(None, None, txs, mr)