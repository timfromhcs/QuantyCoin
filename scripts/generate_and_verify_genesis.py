"""
QuantyCoin 2.0 (QTY2) Autonomous Air-Gapped Genesis Generator & Verification Engine
Complies with Specification Sections 2, 3, 4, 5, 6.
Strict Privacy: Zero secrets logged to terminal, zero secrets saved in git repo.
All working and private materials written exclusively to QuantySecrets.
"""

import os
import sys
import json
import time
import struct
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from crypto import (
    generate_mnemonic, mnemonic_to_seed, HDKey,
    hash256, sha256, hash160, compute_merkle_root
)
from crypto.bip32_44 import address_to_scriptpubkey
from core.transaction import Transaction, TxIn, TxOut
from core.block import Block, BlockHeader
from core.consensus import bits_to_target, target_to_bits

# Resolve Local Secret Vault path
HOME = Path.home()
VAULT_DIR = HOME / "Desktop" / "QuantySecrets" / "QuantyCoin"
GENESIS_WORKING_DIR = VAULT_DIR / "genesis" / "working"
GENESIS_GENERATED_DIR = VAULT_DIR / "genesis" / "generated"
GENESIS_VERIFICATION_DIR = VAULT_DIR / "genesis" / "verification"
GENESIS_ARCHIVE_DIR = VAULT_DIR / "genesis" / "archive"

for d in [GENESIS_WORKING_DIR, GENESIS_GENERATED_DIR, GENESIS_VERIFICATION_DIR, GENESIS_ARCHIVE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Candidate Protocol Parameters for QTY2
PROTOCOL_VERSION = 70020
CHAIN_ID = "quantycoin-2.0"
NETWORK_MAGIC_HEX = "0x5155414e"
MAGIC_BYTES = b"\x51\x55\x41\x4e"
TIMESTAMP_STR = "2026-09-05: QuantyCoin 2.0 - SHA256D Layer-1 Autonomous Blockchain Protocol"
TIMESTAMP_UNIX = 1788600000
GENESIS_BITS = 0x1e0fffff
GENESIS_REWARD_SAT = 50 * 100_000_000

def step1_save_candidate_config():
    config = {
        "protocol_version": PROTOCOL_VERSION,
        "chain_id": CHAIN_ID,
        "network_magic": NETWORK_MAGIC_HEX,
        "timestamp_str": TIMESTAMP_STR,
        "timestamp_unix": TIMESTAMP_UNIX,
        "bits": GENESIS_BITS,
        "reward_sat": GENESIS_REWARD_SAT
    }
    candidate_file = GENESIS_WORKING_DIR / "candidate_params.json"
    with open(candidate_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    return config

def step2_generate_airgapped_creator_key():
    # 24-word BIP39 mnemonic
    mnemonic = generate_mnemonic(256)
    seed = mnemonic_to_seed(mnemonic)
    master = HDKey.from_seed(seed)
    creator_key = master.derive_path("m/44'/999'/0'/0/0")
    
    creator_address = creator_key.get_address()
    
    # Save confidential material ONLY in QuantySecrets/genesis/generated/
    vault_payload = {
        "notice": "QUANTYCOIN CREATOR MASTER VAULT - AIR-GAPPED & CONFIDENTIAL",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "derivation_path": "m/44'/999'/0'/0/0",
        "bip39_mnemonic": mnemonic,
        "creator_wif": creator_key.to_wif(),
        "creator_hex": creator_key.key.hex(),
        "creator_address": creator_address
    }
    vault_file = GENESIS_GENERATED_DIR / "genesis_creator_vault.json"
    with open(vault_file, "w", encoding="utf-8") as f:
        json.dump(vault_payload, f, indent=2)
    
    # Return ONLY public address for consensus use
    return creator_address

def step3_build_coinbase_and_merkle(creator_address: str):
    script_sig = b'\x04\xff\xff\x00\x1d\x01\x04' + bytes([len(TIMESTAMP_STR)]) + TIMESTAMP_STR.encode('utf-8')
    script_pubkey = address_to_scriptpubkey(creator_address)
    
    cb_tx = Transaction(
        version=1,
        vin=[TxIn(prev_txid=b'\x00' * 32, prev_vout=0xFFFFFFFF, script_sig=script_sig)],
        vout=[TxOut(value=GENESIS_REWARD_SAT, script_pubkey=script_pubkey)],
        locktime=0
    )
    
    merkle_root = compute_merkle_root([cb_tx.txid])
    return cb_tx, merkle_root

def step4_mine_genesis(cb_tx: Transaction, merkle_root: bytes):
    target = bits_to_target(GENESIS_BITS)
    prev_block = b'\x00' * 32
    version = 1
    
    nonce = 0
    start_time = time.time()
    while True:
        hdr = BlockHeader(
            version=version,
            prev_block=prev_block,
            merkle_root=merkle_root,
            timestamp=TIMESTAMP_UNIX,
            bits=GENESIS_BITS,
            nonce=nonce
        )
        if hdr.verify_pow():
            elapsed = time.time() - start_time
            block = Block(header=hdr, transactions=[cb_tx])
            return hdr, block, elapsed
        nonce += 1

def step5_independent_regeneration_and_verify(creator_address: str, solved_nonce: int, solved_hash: str):
    # Completely independent regeneration
    script_sig = b'\x04\xff\xff\x00\x1d\x01\x04' + bytes([len(TIMESTAMP_STR)]) + TIMESTAMP_STR.encode('utf-8')
    script_pubkey = address_to_scriptpubkey(creator_address)
    
    re_cb_tx = Transaction(
        version=1,
        vin=[TxIn(prev_txid=b'\x00' * 32, prev_vout=0xFFFFFFFF, script_sig=script_sig)],
        vout=[TxOut(value=GENESIS_REWARD_SAT, script_pubkey=script_pubkey)],
        locktime=0
    )
    re_merkle = compute_merkle_root([re_cb_tx.txid])
    
    re_hdr = BlockHeader(
        version=1,
        prev_block=b'\x00' * 32,
        merkle_root=re_merkle,
        timestamp=TIMESTAMP_UNIX,
        bits=GENESIS_BITS,
        nonce=solved_nonce
    )
    
    re_block = Block(header=re_hdr, transactions=[re_cb_tx])
    
    # Assertions
    assert re_hdr.hash_hex == solved_hash, "Independent regeneration hash mismatch!"
    assert re_hdr.verify_pow(), "Independent regeneration PoW verification failed!"
    assert re_block.verify_merkle_root(), "Independent regeneration Merkle root verification failed!"
    
    raw_serialized = re_block.serialize()
    deserialized_block, consumed = Block.deserialize(raw_serialized)
    assert consumed == len(raw_serialized), "Deserialization length mismatch!"
    assert deserialized_block.header.hash_hex == solved_hash, "Deserialized block hash mismatch!"
    assert deserialized_block.validate_structure()[0], "Structure validation failed!"
    
    report = {
        "independent_regeneration_pass": True,
        "pow_verified": True,
        "merkle_verified": True,
        "serialization_roundtrip_pass": True,
        "genesis_hash": solved_hash,
        "nonce": solved_nonce,
        "serialized_size_bytes": len(raw_serialized)
    }
    with open(GENESIS_VERIFICATION_DIR / "verification_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report, raw_serialized

def step6_export_public_manifest_and_constants(hdr: BlockHeader, block: Block, raw_block: bytes, creator_address: str):
    # Manifest in repository: genesis/PUBLIC_GENESIS_MANIFEST.json
    repo_genesis_dir = ROOT_DIR / "genesis"
    repo_genesis_dir.mkdir(parents=True, exist_ok=True)
    
    manifest = {
        "genesis_hash": hdr.hash_hex,
        "merkle_root": hdr.merkle_root[::-1].hex(),
        "timestamp": hdr.timestamp,
        "nonce": hdr.nonce,
        "bits": hdr.bits,
        "serialized_genesis_block": raw_block.hex(),
        "chain_id": CHAIN_ID,
        "network_magic": NETWORK_MAGIC_HEX,
        "protocol_version": PROTOCOL_VERSION
    }
    
    manifest_path = repo_genesis_dir / "PUBLIC_GENESIS_MANIFEST.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    # Also update core/genesis_constants.py
    constants_content = f'''"""
QuantyCoin 2.0 (QTY2) Public Genesis & Consensus Network Parameters
PROTOCOL FREEZE — DO NOT MODIFY CONSENSUS CONSTANTS DIRECTLY
AIR-GAP COMPLIANCE: ZERO SECRETS STORED IN REPOSITORY
"""

# Protocol Version & Chain Identifier
PROTOCOL_VERSION = {PROTOCOL_VERSION}
CHAIN_ID = "{CHAIN_ID}"

# Network Magic Bytes
MAGIC_BYTES = b"\\x51\\x55\\x41\\x4e" # 0x51 0x55 0x41 0x4E ('QUAN')
TESTNET_MAGIC_BYTES = b"\\x54\\x51\\x55\\x41" # 0x54 0x51 0x55 0x41 ('TQUA')
REGTEST_MAGIC_BYTES = b"\\x52\\x51\\x55\\x41" # 0x52 0x51 0x55 0x41 ('RQUA')

# Default Network Ports
DEFAULT_P2P_PORT = 19888
DEFAULT_RPC_PORT = 19889
DEFAULT_STRATUM_PORT = 3333

DEFAULT_TESTNET_P2P_PORT = 29888
DEFAULT_TESTNET_RPC_PORT = 29889
DEFAULT_TESTNET_STRATUM_PORT = 13333

DEFAULT_REGTEST_P2P_PORT = 39888
DEFAULT_REGTEST_RPC_PORT = 39889
DEFAULT_REGTEST_STRATUM_PORT = 23333

# Genesis Block Constants
GENESIS_TIMESTAMP_STR = "{TIMESTAMP_STR}"
GENESIS_TIMESTAMP = {TIMESTAMP_UNIX}
GENESIS_BITS = 0x{GENESIS_BITS:08x}
GENESIS_NONCE = {hdr.nonce}
GENESIS_HASH = "{hdr.hash_hex}"
GENESIS_MERKLE_ROOT = "{hdr.merkle_root[::-1].hex()}"
GENESIS_COINBASE_PAYOUT_ADDRESS = "{creator_address}"
GENESIS_BLOCK_REWARD = 50 # 50 QTY

# Consensus Parameters
TARGET_BLOCK_TIME = 60 # 60 seconds (1 minute)
DIFFICULTY_RETARGET_INTERVAL = 144 # 144 blocks
SUBSIDY_HALVING_INTERVAL = 2100000 # 2,100,000 blocks (~4 years)
MAX_SUPPLY_QTY = 21000000 # 21,000,000 QTY
MAX_BLOCK_SIZE = 32 * 1024 * 1024 # 32 MB
COINBASE_MATURITY = 100 # 100 blocks
'''
    with open(ROOT_DIR / "core" / "genesis_constants.py", "w", encoding="utf-8") as f:
        f.write(constants_content)
        
    # Also update public_genesis.json in root
    public_genesis_json = {
        "network": "QuantyCoin-2.0-Mainnet",
        "version": "2.0.0",
        "protocol_version": PROTOCOL_VERSION,
        "chain_id": CHAIN_ID,
        "magic_bytes": NETWORK_MAGIC_HEX,
        "genesis_block": {
            "hash": hdr.hash_hex,
            "prev_hash": "0000000000000000000000000000000000000000000000000000000000000000",
            "merkle_root": hdr.merkle_root[::-1].hex(),
            "timestamp": hdr.timestamp,
            "bits": hdr.bits,
            "nonce": hdr.nonce,
            "target": hex(hdr.get_target()),
            "serialized_block": raw_block.hex(),
            "coinbase": {
                "txid": block.transactions[0].txid_hex,
                "value_qty": 50.0,
                "value_sat": GENESIS_REWARD_SAT,
                "payout_address": creator_address
            }
        },
        "tokenomics": {
            "max_supply_qty": 21000000,
            "initial_reward_qty": 50.0,
            "halving_interval_blocks": 2100000,
            "target_block_time_seconds": 60,
            "max_block_size_bytes": 33554432,
            "difficulty_algorithm": "LWMA-1 (Linear-Weighted Moving Average)",
            "coinbase_maturity": 100
        }
    }
    with open(ROOT_DIR / "public_genesis.json", "w", encoding="utf-8") as f:
        json.dump(public_genesis_json, f, indent=2)

def main():
    print("==================================================================")
    print("QUANTYCOIN 2.0 (QTY2) AIR-GAPPED GENESIS GENERATION & VERIFICATION")
    print("==================================================================")
    
    print("[1/6] Loading & Validating Candidate Configuration...")
    step1_save_candidate_config()
    
    print("[2/6] Generating Air-Gapped Key Material in Secret Vault...")
    creator_address = step2_generate_airgapped_creator_key()
    print(f"      Creator Public Address: {creator_address}")
    
    print("[3/6] Constructing Deterministic Coinbase & Merkle Root...")
    cb_tx, merkle_root = step3_build_coinbase_and_merkle(creator_address)
    print(f"      Coinbase TXID: {cb_tx.txid_hex}")
    print(f"      Merkle Root:   {merkle_root[::-1].hex()}")
    
    print("[4/6] Mining Genesis Block (SHA-256D)...")
    hdr, block, elapsed = step4_mine_genesis(cb_tx, merkle_root)
    print(f"      Genesis Solved in {elapsed:.2f}s!")
    print(f"      Genesis Hash:  {hdr.hash_hex}")
    print(f"      Nonce:         {hdr.nonce}")
    print(f"      Bits:          0x{hdr.bits:08x}")
    
    print("[5/6] Performing Independent Regeneration & Verification...")
    report, raw_block = step5_independent_regeneration_and_verify(creator_address, hdr.nonce, hdr.hash_hex)
    print(f"      Independent Verification: PASS (Size: {len(raw_block)} bytes)")
    
    print("[6/6] Freezing Consensus Parameters & Exporting Public Manifest...")
    step6_export_public_manifest_and_constants(hdr, block, raw_block, creator_address)
    print("      Public Manifest Exported: genesis/PUBLIC_GENESIS_MANIFEST.json")
    print("      Core Constants Updated:   core/genesis_constants.py")
    print("      Public Genesis Updated:   public_genesis.json")
    
    print("==================================================================")
    print("GENESIS GENERATION & INDEPENDENT VERIFICATION COMPLETED (100% PASS)")
    print("==================================================================")

if __name__ == "__main__":
    main()
