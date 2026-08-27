"""
QuantyCoin Genesis Block Generator & Vault Provisioner
Mines the official production Genesis Block using the exact Transaction & Block serialization models.
"""

import os
import sys
import struct
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crypto import (
    generate_mnemonic, mnemonic_to_seed, HDKey,
    hash256, sha256, hash160, compute_merkle_root
)
from crypto.bip32_44 import address_to_scriptpubkey
from core.transaction import Transaction, TxIn, TxOut
from core.block import Block, BlockHeader
from core.consensus import bits_to_target


def mine_genesis():
    print("Generating Creator 24-Word BIP39 Seed...")
    mnemonic = generate_mnemonic(256)
    seed = mnemonic_to_seed(mnemonic)
    master = HDKey.from_seed(seed)
    
    # Derivation Path m/44'/999'/0'/0/0
    creator_key = master.derive_path("m/44'/999'/0'/0/0")
    wif_key = creator_key.to_wif()
    hex_privkey = creator_key.key.hex()
    creator_pubkey = creator_key.get_public_key()
    creator_address = creator_key.get_address()
    
    timestamp_str = "2026: QuantyCoin - The High-Speed Quantum & AI Era Layer-1"
    timestamp_unix = 1771804800 # 2026-08-27 fixed epoch
    bits = 0x1e0fffff # Standard Genesis target
    target = bits_to_target(bits)
    
    # 1. Build Coinbase Transaction using Core Transaction Model
    script_sig = b'\x04\xff\xff\x00\x1d\x01\x04' + bytes([len(timestamp_str)]) + timestamp_str.encode('utf-8')
    script_pubkey = address_to_scriptpubkey(creator_address)
    
    cb_tx = Transaction(
        version=1,
        vin=[TxIn(prev_txid=b'\x00'*32, prev_vout=0xFFFFFFFF, script_sig=script_sig)],
        vout=[TxOut(value=50 * 100_000_000, script_pubkey=script_pubkey)],
        locktime=0
    )
    
    merkle_root = compute_merkle_root([cb_tx.txid])
    
    print(f"Coinbase TXID: {cb_tx.txid_hex}")
    print(f"Merkle Root:   {merkle_root[::-1].hex()}")
    print("Mining Genesis Block header matching target difficulty...")
    print(f"Target: {hex(target)}")
    
    n_version = 1
    prev_block = b'\x00' * 32
    
    nonce = 0
    start_time = time.time()
    while True:
        hdr = BlockHeader(
            version=n_version,
            prev_block=prev_block,
            merkle_root=merkle_root,
            timestamp=timestamp_unix,
            bits=bits,
            nonce=nonce
        )
        if hdr.verify_pow():
            genesis_hash_hex = hdr.hash_hex
            merkle_root_hex = merkle_root[::-1].hex()
            elapsed = time.time() - start_time
            print(f"\nGENESIS BLOCK MINED SUCCESSFULLY in {elapsed:.2f}s!")
            print(f"Genesis Hash: {genesis_hash_hex}")
            print(f"Merkle Root:  {merkle_root_hex}")
            print(f"Nonce:        {nonce}")
            print(f"Timestamp:    {timestamp_unix} (\"{timestamp_str}\")")
            print(f"Creator Addr: {creator_address}")
            break
            
        nonce += 1
        if nonce % 200000 == 0:
            print(f"Mining... Tested {nonce} nonces...")

    # 2. Write Desktop Secret Backup (Air-Gapped Vault)
    desktop_path = os.path.expanduser("~/Desktop")
    if os.name == 'nt' and not os.path.exists(desktop_path):
        user_profile = os.environ.get("USERPROFILE", "C:\\Users\\hcsme")
        desktop_path = os.path.join(user_profile, "Desktop")
        
    vault_file = os.path.join(desktop_path, "QUANTYCOIN_GENESIS_CREATOR_SECRETS_DO_NOT_SHARE.txt")
    
    vault_content = f"""======================================================================
QUANTYCOIN CORE — CREATOR MASTER GENESIS VAULT (CONFIDENTIAL)
GENERATED: 2026-08-27
======================================================================
[!] DIESE DATEI WURDE VOR DEM GIT-PUSH AUS DEM REPOSITORY ISOLIERT.
[!] NIEMALS TEILEN ODER AUF GITHUB HOCHLADEN!

24-WORD BIP39 MNEMONIC SEED:
{mnemonic}

DERIVATION PATH: m/44'/999'/0'/0/0
CREATOR MASTER PRIVATE KEY (WIF / HEX):
WIF: {wif_key}
HEX: {hex_privkey}

CREATOR PUBLIC ADDRESS:
{creator_address}

GENESIS BLOCK DATA:
- Timestamp: "{timestamp_str}"
- Genesis Hash: 0x{genesis_hash_hex}
- Merkle Root: 0x{merkle_root_hex}
- Nonce: {nonce}
======================================================================
"""
    with open(vault_file, 'w', encoding='utf-8') as f:
        f.write(vault_content)
    print(f"\n[VAULT SECURE] Desktop Vault written to:\n{vault_file}")
    
    # 3. Write Public Constants Only (core/genesis_constants.py)
    constants_py = f'''"""
QuantyCoin Public Genesis & Network Parameters
STRICT AIR-GAP COMPLIANCE: ZERO PRIVATE KEYS OR MNEMONICS STORED HERE
"""

# Protocol Magic Bytes: "QUAN"
MAGIC_BYTES = b"\\x51\\x55\\x41\\x4e" # 0x51 0x55 0x41 0x4E

# Default Network Ports
DEFAULT_P2P_PORT = 19888
DEFAULT_RPC_PORT = 19889
DEFAULT_STRATUM_PORT = 3333

# Genesis Block Constants
GENESIS_TIMESTAMP_STR = "{timestamp_str}"
GENESIS_TIMESTAMP = {timestamp_unix}
GENESIS_BITS = 0x{bits:08x}
GENESIS_NONCE = {nonce}
GENESIS_HASH = "{genesis_hash_hex}"
GENESIS_MERKLE_ROOT = "{merkle_root_hex}"
GENESIS_COINBASE_PAYOUT_ADDRESS = "{creator_address}"
GENESIS_BLOCK_REWARD = 50 # 50 QTY

# Consensus Parameters
TARGET_BLOCK_TIME = 60 # 60 seconds (1 minute)
DIFFICULTY_RETARGET_INTERVAL = 144 # 144 blocks (~2.4 hours)
SUBSIDY_HALVING_INTERVAL = 2100000 # 2,100,000 blocks (~4 years)
MAX_BLOCK_SIZE = 32 * 1024 * 1024 # 32 MB
'''
    with open('core/genesis_constants.py', 'w', encoding='utf-8') as f:
        f.write(constants_py)
    print("core/genesis_constants.py updated with public parameters.")


if __name__ == "__main__":
    mine_genesis()
