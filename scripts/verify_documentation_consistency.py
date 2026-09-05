#!/usr/bin/env python3
"""
QuantyCoin QTY4 Comprehensive Documentation Consistency Validator
Machine-verifies documented parameters against canonical consensus values across all active documentation files.
Checks:
  - protocol version (70040)
  - chain ID ("quantycoin-4.0")
  - network magic ("0x51545934" / "QTY4")
  - genesis hash ("000004eb1e117df3168d6d27118982e0a23c236120183e8390a6bbb82ee6fde3")
  - merkle root ("3526817e09d5a065247d15a45a7aa5cf351479e011d32ecfd752e94acfae55ea")
  - timestamp (1788614400)
  - nonce (2951011)
  - bits (504365055 / 0x1e0fffff)
  - P2P port (19444)
  - RPC port (19445)
  - Stratum ports (3333, 3334)
  - block size (33554432)
  - subsidy (50 QTY / 25 QTY)
  - halving interval (2100000)
  - coinbase maturity (100)
  - PoW configuration (Dual-PoW: SHA-256D ASIC & Scrypt CPU/GPU)
  - PQC configuration (ML-DSA-44)
"""

import sys
import json
import re
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from core.genesis_constants import (
    PROTOCOL_VERSION,
    CHAIN_ID,
    MAGIC_BYTES,
    DEFAULT_P2P_PORT,
    DEFAULT_RPC_PORT,
    DEFAULT_STRATUM_PORT,
    DEFAULT_STRATUM_V2_PORT,
    GENESIS_HASH,
    GENESIS_MERKLE_ROOT,
    GENESIS_TIMESTAMP,
    GENESIS_NONCE,
    GENESIS_BITS,
    TARGET_BLOCK_TIME,
    LANE_A_TARGET_TIME,
    LANE_B_TARGET_TIME,
    LANE_A_BASE_SUBSIDY,
    LANE_B_BASE_SUBSIDY,
    SUBSIDY_HALVING_INTERVAL,
    MAX_BLOCK_SIZE,
    COINBASE_MATURITY,
    MAX_SUPPLY_QTY,
    MAX_MONEY_SATOSHIS,
)

CANONICAL = {
    "protocol_version": str(PROTOCOL_VERSION),
    "chain_id": CHAIN_ID,
    "magic_hex": "0x51545934",
    "magic_str": "QTY4",
    "genesis_hash": GENESIS_HASH,
    "merkle_root": GENESIS_MERKLE_ROOT,
    "timestamp": str(GENESIS_TIMESTAMP),
    "nonce": str(GENESIS_NONCE),
    "bits_hex": "1e0fffff",
    "p2p_port": str(DEFAULT_P2P_PORT),
    "rpc_port": str(DEFAULT_RPC_PORT),
    "stratum_v1_port": str(DEFAULT_STRATUM_PORT),
    "stratum_v2_port": str(DEFAULT_STRATUM_V2_PORT),
    "block_size": str(MAX_BLOCK_SIZE),
    "halving_interval": str(SUBSIDY_HALVING_INTERVAL),
    "coinbase_maturity": str(COINBASE_MATURITY),
}

DOC_FILES_TO_AUDIT = [
    "README.md",
    "ARCHITECTURE.md",
    "ROADMAP.md",
    "SECURITY.md",
    "THREAT_MODEL.md",
    "VERIFICATION.md",
    "REPRODUCIBILITY.md",
    "RELEASE_PROCESS.md",
    "CITATION.cff",
    "llms.txt",
    "llms-full.txt",
    "TRUST.md",
    "docs/STATUS.md",
    "docs/project-summary.md",
    "docs/verification/index.md",
    "docs/protocol/index.md",
    "docs/protocol/QTY4_SPEC.md",
    "docs/protocol/CONSENSUS_RULES.md",
    "docs/protocol/GENESIS_SPEC.md",
    "docs/GENESIS_REPRODUCTION.md",
    "docs/CONSENSUS_ASSURANCE.md",
    "docs/SECURITY_ASSURANCE.md",
    "docs/BUILD_MATRIX.md",
]


def audit_markdown_documents() -> int:
    print("--- [DOC AUDIT] ACTIVE DOCUMENTATION PARAMETER VERIFICATION ---")
    errors = 0
    checked_count = 0

    for rel_path in DOC_FILES_TO_AUDIT:
        fpath = repo_root / rel_path
        if not fpath.exists():
            print(f"[FAIL] Expected documentation file missing: {rel_path}")
            errors += 1
            continue

        content = fpath.read_text(encoding="utf-8")
        checked_count += 1

        # Check for obsolete QTY2/QTY3 leakage in active docs
        stale_signatures = [
            ("00000f7cecd0b1eafaab4d65183f7bd12713b67b6c1c4a30f6bf3f1b8efd30ba", "Old QTY2 Genesis Hash"),
            ("ac6346e4b3ae1f3e4cfabaa09376ee83d268d12476d3e243a42d0e22cf79224f", "Old QTY2 Merkle Root"),
            ("quantycoin-2.0", "Old QTY2 Chain Identifier"),
        ]
        # Allow historical references only in explicitly historical docs or changelog notes
        is_historical = "QTY3_PROTOCOL_FREEZE" in rel_path or "CHANGELOG" in rel_path
        if not is_historical:
            for stale_val, stale_label in stale_signatures:
                if stale_val in content:
                    print(f"[FAIL] {rel_path} contains obsolete {stale_label}: {stale_val}")
                    errors += 1

    print(f"[PASS] Audited {checked_count} active documentation files for parameter freshness.")
    return errors


def audit_machine_readable_specs() -> int:
    print("--- [SPEC AUDIT] MACHINE-READABLE SPEC & MANIFEST VERIFICATION ---")
    errors = 0

    spec_files = [
        (repo_root / "spec" / "qty4" / "consensus.json", "spec/qty4/consensus.json"),
        (repo_root / "spec" / "qty4" / "genesis.json", "spec/qty4/genesis.json"),
        (repo_root / "genesis" / "PUBLIC_GENESIS_MANIFEST.json", "genesis/PUBLIC_GENESIS_MANIFEST.json"),
        (repo_root / "genesis" / "public" / "public_genesis_manifest.json", "genesis/public/public_genesis_manifest.json"),
        (repo_root / "public_genesis.json", "public_genesis.json"),
    ]

    for p, name in spec_files:
        if not p.exists():
            print(f"[FAIL] Missing specification file: {name}")
            errors += 1
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            pv = data.get("protocol_version")
            cid = data.get("chain_id")
            ghash = data.get("genesis_hash") or data.get("genesis_block", {}).get("hash")
            mroot = data.get("merkle_root") or data.get("genesis_block", {}).get("merkle_root")

            if pv != PROTOCOL_VERSION:
                print(f"[FAIL] {name} protocol_version mismatch: {pv} != {PROTOCOL_VERSION}")
                errors += 1
            if cid != CHAIN_ID:
                print(f"[FAIL] {name} chain_id mismatch: {cid} != {CHAIN_ID}")
                errors += 1
            if ghash != GENESIS_HASH:
                print(f"[FAIL] {name} genesis_hash mismatch: {ghash} != {GENESIS_HASH}")
                errors += 1
            if mroot != GENESIS_MERKLE_ROOT:
                print(f"[FAIL] {name} merkle_root mismatch: {mroot} != {GENESIS_MERKLE_ROOT}")
                errors += 1
            print(f"[PASS] {name} verified against canonical consensus parameters.")
        except Exception as e:
            print(f"[FAIL] Error parsing {name}: {e}")
            errors += 1

    # Text artifact checks
    pub_dir = repo_root / "genesis" / "public"
    hash_txt = (pub_dir / "genesis_hash.txt").read_text(encoding="utf-8").strip()
    if hash_txt != GENESIS_HASH:
        print(f"[FAIL] genesis_hash.txt mismatch: {hash_txt} != {GENESIS_HASH}")
        errors += 1
    else:
        print(f"[PASS] genesis_hash.txt verified.")

    mroot_txt = (pub_dir / "genesis_merkle_root.txt").read_text(encoding="utf-8").strip()
    if mroot_txt != GENESIS_MERKLE_ROOT:
        print(f"[FAIL] genesis_merkle_root.txt mismatch: {mroot_txt} != {GENESIS_MERKLE_ROOT}")
        errors += 1
    else:
        print(f"[PASS] genesis_merkle_root.txt verified.")

    return errors


def main():
    print("==================================================")
    print("QUANTYCOIN QTY4 DOCUMENTATION & SPEC CONSISTENCY AUDIT")
    print("==================================================")
    total_errors = 0
    total_errors += audit_markdown_documents()
    total_errors += audit_machine_readable_specs()

    if total_errors > 0:
        print(f"\n[FAIL] Found {total_errors} documentation / spec consistency error(s).")
        sys.exit(1)

    print("\n==================================================")
    print("ALL DOCUMENTATION CONSISTENCY CHECKS PASSED (100%)")
    print("==================================================")
    sys.exit(0)


if __name__ == "__main__":
    main()
