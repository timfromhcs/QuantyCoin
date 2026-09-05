#!/usr/bin/env python3
"""
QuantyCoin Documentation & Source Consistency Checker
Verifies that documented consensus parameters match executable source constants in core/genesis_constants.py.
If documentation disagrees with executable constants, exits with 1 (blocking CI release).
"""

import sys
import json
import re
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from core.genesis_constants import (
    PROTOCOL_VERSION, CHAIN_ID, GENESIS_HASH, GENESIS_TIMESTAMP,
    GENESIS_NONCE, GENESIS_BITS, TARGET_BLOCK_TIME,
    SUBSIDY_HALVING_INTERVAL, MAX_BLOCK_SIZE,
    DEFAULT_P2P_PORT, DEFAULT_RPC_PORT, DEFAULT_STRATUM_PORT,
    DEFAULT_STRATUM_V2_PORT
)


def verify_readme(repo_root: Path) -> int:
    readme_path = repo_root / "README.md"
    if not readme_path.exists():
        print("[FAIL] README.md missing!")
        return 1
    content = readme_path.read_text(encoding="utf-8")
    errors = 0

    checks = [
        ("Protocol Version", str(PROTOCOL_VERSION)),
        ("Chain ID", CHAIN_ID),
        ("Genesis Hash", GENESIS_HASH),
        ("P2P Port", str(DEFAULT_P2P_PORT)),
        ("RPC Port", str(DEFAULT_RPC_PORT)),
        ("Stratum V2 Port", str(DEFAULT_STRATUM_V2_PORT)),
    ]

    for label, val in checks:
        if val not in content:
            print(f"[FAIL] README.md missing documented constant '{label}' ({val})")
            errors += 1
        else:
            print(f"[PASS] README.md verified for '{label}': {val}")
    return errors


def verify_specs(repo_root: Path) -> int:
    spec_consensus = repo_root / "spec" / "qty4" / "consensus.json"
    if not spec_consensus.exists():
        print("[FAIL] spec/qty4/consensus.json missing!")
        return 1
    data = json.loads(spec_consensus.read_text(encoding="utf-8"))
    errors = 0

    if data.get("protocol_version") != PROTOCOL_VERSION:
        print(f"[FAIL] consensus.json protocol_version mismatch: {data.get('protocol_version')} != {PROTOCOL_VERSION}")
        errors += 1

    if data.get("chain_id") != CHAIN_ID:
        print(f"[FAIL] consensus.json chain_id mismatch: {data.get('chain_id')} != {CHAIN_ID}")
        errors += 1

    if data.get("target_block_time_seconds") != TARGET_BLOCK_TIME:
        print(f"[FAIL] consensus.json target_block_time mismatch")
        errors += 1

    if data.get("max_block_size_bytes") != MAX_BLOCK_SIZE:
        print(f"[FAIL] consensus.json max_block_size mismatch")
        errors += 1

    return errors


def verify_public_genesis(repo_root: Path) -> int:
    gen_hash_file = repo_root / "genesis" / "public" / "genesis_hash.txt"
    if not gen_hash_file.exists():
        print("[FAIL] genesis/public/genesis_hash.txt missing!")
        return 1
    file_hash = gen_hash_file.read_text(encoding="utf-8").strip()
    if file_hash != GENESIS_HASH:
        print(f"[FAIL] Public genesis hash mismatch: {file_hash} != {GENESIS_HASH}")
        return 1
    print(f"[PASS] genesis/public/genesis_hash.txt matches executable constant: {file_hash}")
    return 0


def main():
    print("==================================================")
    print("QUANTYCOIN QTY4 DOCUMENTATION AUTO-CONSISTENCY CHECK")
    print("==================================================")
    total_errors = 0
    total_errors += verify_readme(repo_root)
    total_errors += verify_specs(repo_root)
    total_errors += verify_public_genesis(repo_root)

    if total_errors > 0:
        print(f"\n[FAIL] Found {total_errors} documentation consistency error(s).")
        sys.exit(1)

    print("\n==================================================")
    print("ALL DOCUMENTATION CONSISTENCY CHECKS PASSED (100%)")
    print("==================================================")
    sys.exit(0)


if __name__ == "__main__":
    main()
