#!/usr/bin/env python3

# Create a new wallet
# usage: ./new.py NAME

import sys
from pathlib import Path
from coil.wallet import Wallet, writeWallet

NAME = "default"

if len(sys.argv) > 1:
    NAME = sys.argv[1]

w = Wallet()

wallet_path = str(Path(str(Path.home()) + "/.config/coil/wallets/"))
wallet_file = Path(wallet_path + "/" + NAME + ".json")
if wallet_file.is_file():
    print("Wallet `" + NAME + "` already exists")
else:
    writeWallet(wallet_path + "/" + NAME + ".json", w)
    print("Successfully create wallet `" + NAME +".json`")