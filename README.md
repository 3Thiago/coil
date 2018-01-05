# Coil

Coilcoin is a primitive (**incomplete**) Python-based cryptocurrency intended for educational purposes.

## Pending Tasks
The following tasks must be completed before Coil is a fully functioning cryptocurrency.

* Web Wallet is unfinished (history transactions not implemented)
* Coinbases are not verified

## Getting Started
To initialize a node, run the python script...
```bash
python coil.py
```

Next, go in to `coil.py` and uncomment like 23, and then comment lines 19 & 20. These lines are only available to the creator, who has the `wallet.pem` file (mainly for testing purposes).

## Proof of work
The proof of work algorithm used by Coil is called current. A valid proof is constructed from a nonce and previous hash. The resulting hash of these components must have 7 preceeding 0s and the hex equivalent of the hexdigest must be divisible by 7.

```python
def validProof(prevHash, nonce):
	result = doubleHashEncode(str(prevHash) + str(nonce))
	return result[:5] == "00000" and int(result, 16) % 5 == 0
```

## Notes from the Developer
If you look into the source code, you may be surprised by some "design" decisions. Firstly, wallets (yes private keys) are stored by the server. This is purely for development. Once the node software is functioning, server-stored wallets will be removed and a seperate wallet program will be instated.

## Dependencies
* Python 3.6 (only tested with Ubuntu 17.10)
* aiohttp
* requests

## Contributing
I am looking to build a small community to develop coil further. If you're interested in contributing servers,
code or just ideas, why not join the gitter community.
