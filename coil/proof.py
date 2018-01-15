# proof.py

# The coil proof-of-work
# algorithm looks for four
# preceding 0's on the result
# double-sha256 of hash + nonce

from coil import chash

TARGET = 18

def proof(prevHash, nonce):
    result = chash.doubleHashEncode(str(prevHash) + str(nonce))

    max_count = 0
    for ch in result:
        count = result.count(ch)
        if count > max_count:
            max_count = count
    
    if max_count >= TARGET:
        return result

def validProof(prevHash, nonce):
    result = chash.doubleHashEncode(str(prevHash) + str(nonce))

    max_count = 0
    for ch in result:
        count = result.count(ch)
        if count > max_count:
            max_count = count
    
    return max_count >= TARGET