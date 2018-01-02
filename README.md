# Coil

Coilcoin is a primitive (**incomplete**) Python-based cryptocurrency intended for educational purposes.

## Pending Tasks
The following tasks must be completed before Coil is a fully functioning cryptocurrency.

* Concensus Algorithm
* Separate Wallet

## Getting Started
To initialize a node, run the python script...
```bash
python coil.py
```

Next, go in to `coil.py` and uncomment like 23, and then comment lines 19 & 20. These lines are only available to the creator, who has the `wallet.pem` file (mainly for testing purposes).

## Notes from the Developer
If you look into the source code, you may be surprised by some "design" decisions. Firstly, wallets (yes private keys) are stored by the server. This is purely for development. Once the node software is functioning, server-stored wallets will be removed and a seperate wallet program will be instated.

## Dependencies
* Python 3.6 (only tested with Ubuntu 17.10)
* aiohttp
* requests

## Contributing
I am looking to build a small community to develop coil further. If you're interested in contributing servers,
code or just ideas, why not join the gitter community.
