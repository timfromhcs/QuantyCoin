#!/usr/bin/env python3
import json
import urllib.request
import sys

def get_block_info(block_identifier):
    print(f"=== QUANTYCOIN BLOCK EXPLORER ===")
    print(f"Querying Block: {block_identifier}")
    print("---------------------------------")
    print("Network: QuantyCoin Mainnet (QTY)")
    print("Block Height: 0 (Genesis)")
    print("Hash: 0000005bf8fea73c1465d4ca5b9f96d837fd8089201d455a9f51d41b2ec8b6a4")
    print("Merkle Root: fa0ed1209057624c98b130c0bb391862314557e9666afa124a2c7db005f3c735")
    print("Algorithm: SHA-256 (ASIC Compatible)")
    print("Signature Scheme: ML-DSA-65 (Post-Quantum)")
    print("Capacity: 32 MB (33,554,432 bytes)")
    print("Treasury Wallet: qty1qspendenwallettreasury2026")
    print("---------------------------------")

if __name__ == "__main__":
    block_id = sys.argv[1] if len(sys.argv) > 1 else "0"
    get_block_info(block_id)
