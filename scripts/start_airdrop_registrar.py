#!/usr/bin/env bash
import json
import sys
import os

AIRDROP_MIN_BALANCE = 5.0
AIRDROP_MIN_AGE_DAYS = 21
AIRDROP_INTERVAL_BLOCKS = 43200
TREASURY_ADDRESS = "qty1qspendenwallettreasury2026"

REGISTRY_FILE = "airdrop_registered_wallets.json"

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "r") as f:
            return json.load(f)
    return {"registered_wallets": {}}

def save_registry(data):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def register_wallet(address, balance, age_days):
    if balance <= AIRDROP_MIN_BALANCE:
        return False, f"Balance must be > {AIRDROP_MIN_BALANCE} QTY. Current balance: {balance} QTY."
    if age_days < AIRDROP_MIN_AGE_DAYS:
        return False, f"Wallet age must be >= {AIRDROP_MIN_AGE_DAYS} days. Current age: {age_days} days."
    
    reg = load_registry()
    reg["registered_wallets"][address] = {
        "balance": balance,
        "age_days": age_days,
        "status": "ELIGIBLE"
    }
    save_registry(reg)
    return True, f"Wallet {address} successfully registered for Monthly QTY Treasury Airdrops!"

def calculate_monthly_airdrop(treasury_balance):
    reg = load_registry()
    eligible = [addr for addr, info in reg["registered_wallets"].items() if info["status"] == "ELIGIBLE"]
    if not eligible:
        return {}
    share_per_user = treasury_balance / len(eligible)
    return {addr: share_per_user for addr in eligible}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "register":
        addr = sys.argv[2] if len(sys.argv) > 2 else "qty1qa8639f6b36aa83d174f6ff8f608084a9475678b1"
        bal = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
        age = int(sys.argv[4]) if len(sys.argv) > 4 else 30
        ok, msg = register_wallet(addr, bal, age)
        print(msg)
    else:
        print("QuantyCoin Airdrop Registrar Module Loaded.")
        print(f"Treasury Address: {TREASURY_ADDRESS}")
        print(f"Interval: {AIRDROP_INTERVAL_BLOCKS} blocks (~30 days)")
