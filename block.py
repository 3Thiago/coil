# block.py

import time
import chash
import merkle
import tx

class Block(object):
    def __init__(self, prevHash, nonce, txs, merkle):
        self.previousBlockHash = prevHash
        self.nonce = nonce
        self.transactions = txs
        self.merkleRoot = merkle

    @property
    def time(self):
        return time.time()

    def hash(self):
        return chash.doubleHashEncodeJSON(self.__dict__)

    def verify(self):
        pass

class Genesis(Block):
    def __init__(self, creator):
        # ICO of 120 coins
        txs = [
            tx.Coinbase(creator, amount=120)
        ]

        txs_dict = [ str(t.__dict__) for t in txs ]
        mr = merkle.generateMerkleRoot(txs_dict)

        super(Genesis, self).__init__(None, None, txs, mr)