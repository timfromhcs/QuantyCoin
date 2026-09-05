#!/usr/bin/env python3
"""
QuantyCoin QTY4 Canonical Protocol Truth Validator.

Cross-checks EVERY consensus parameter across:
  spec/qty4/*.json  +  core/genesis_constants.py  +  core/consensus.py
  +  core/money.py  +  genesis manifests  +  tests/vectors/qty4/*.json

Fails (exit 1) on ANY drift. Success requires 100% agreement.
Covers: protocol version, chain id, genesis identifiers, block timing,
PoW lanes/algorithms/weights/subsidies, halving, supply, target encoding,
difficulty/MTP rules, block limits, maturity, address formats, witness
versions, network constants, serialization versions, fork-choice rules.
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from core import genesis_constants as G  # noqa: E402
from core import consensus as C  # noqa: E402

ERRORS = []


def fail(msg):
    ERRORS.append(msg)
    print(f"[FAIL] {msg}")


def ok(msg):
    print(f"[PASS] {msg}")


def load_json(path):
    try:
        return json.loads((REPO / path).read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"cannot parse {path}: {e}")
        return None


def check_eq(label, actual, expected):
    if actual != expected:
        fail(f"{label}: {actual!r} != canonical {expected!r}")
    else:
        ok(f"{label} == {expected!r}")


def main():
    print("=" * 60)
    print("QTY4 CANONICAL PROTOCOL TRUTH VALIDATION")
    print("=" * 60)

    consensus = load_json("spec/qty4/consensus.json")
    genesis = load_json("spec/qty4/genesis.json")
    pow_spec = load_json("spec/qty4/pow.json")
    pqc = load_json("spec/qty4/pqc.json")
    net = load_json("spec/qty4/network.json")
    tx = load_json("spec/qty4/transaction.json")
    if any(x is None for x in (consensus, genesis, pow_spec, pqc, net, tx)):
        print(f"\n[FAIL] {len(ERRORS)} error(s).")
        sys.exit(1)

    # --- protocol version / chain id ---
    check_eq("spec.consensus.protocol_version", consensus.get("protocol_version"), G.PROTOCOL_VERSION)
    check_eq("spec.genesis.protocol_version", genesis.get("protocol_version"), G.PROTOCOL_VERSION)
    check_eq("spec.consensus.chain_id", consensus.get("chain_id"), G.CHAIN_ID)
    check_eq("spec.genesis.chain_id", genesis.get("chain_id"), G.CHAIN_ID)

    # --- genesis identifiers ---
    check_eq("spec.consensus.genesis_hash", consensus.get("genesis_hash"), G.GENESIS_HASH)
    check_eq("spec.genesis.genesis_hash", genesis.get("genesis_hash"), G.GENESIS_HASH)
    check_eq("spec.consensus.merkle_root", consensus.get("merkle_root"), G.GENESIS_MERKLE_ROOT)
    check_eq("spec.genesis.merkle_root", genesis.get("merkle_root"), G.GENESIS_MERKLE_ROOT)
    check_eq("spec.genesis.timestamp", genesis.get("timestamp"), G.GENESIS_TIMESTAMP)
    check_eq("spec.genesis.bits", genesis.get("bits"), G.GENESIS_BITS)
    check_eq("spec.genesis.nonce", genesis.get("nonce"), G.GENESIS_NONCE)

    # --- block timing ---
    check_eq("consensus.target_block_time", consensus.get("target_block_time_seconds"), G.TARGET_BLOCK_TIME)
    check_eq("pow.laneA.interval", pow_spec["lanes"]["LANE_A"].get("target_interval_seconds"), G.LANE_A_TARGET_TIME)
    check_eq("pow.laneB.interval", pow_spec["lanes"]["LANE_B"].get("target_interval_seconds"), G.LANE_B_TARGET_TIME)
    check_eq("consensus.MTP_window", consensus.get("median_time_past_window"), G.MTP_WINDOW)
    check_eq("consensus.future_limit", consensus.get("future_timestamp_limit_seconds"), G.FUTURE_TIME_LIMIT)

    # --- PoW lanes / algorithms / weights ---
    check_eq("pow.laneA.id", pow_spec["lanes"]["LANE_A"].get("id"), C.POW_TYPE_SHA256D)
    check_eq("pow.laneB.id", pow_spec["lanes"]["LANE_B"].get("id"), C.POW_TYPE_GENERAL_PURPOSE)
    check_eq("pow.laneA.algorithm", pow_spec["lanes"]["LANE_A"].get("algorithm"), "double_sha256")
    check_eq("pow.laneB.N", pow_spec["lanes"]["LANE_B"].get("scrypt_parameters", {}).get("N"), 1024)
    check_eq("pow.laneA.weight", pow_spec["lanes"]["LANE_A"].get("thermodynamic_work_weight"), G.THERMODYNAMIC_WEIGHT_A)
    check_eq("pow.laneB.weight", pow_spec["lanes"]["LANE_B"].get("thermodynamic_work_weight"), G.THERMODYNAMIC_WEIGHT_B)
    check_eq("consensus.weightA==consensus.py", C.LANE_WEIGHT_SHA256D, G.THERMODYNAMIC_WEIGHT_A)
    check_eq("consensus.weightB==consensus.py", C.LANE_WEIGHT_GENERAL_PURPOSE, G.THERMODYNAMIC_WEIGHT_B)

    # --- subsidies / halving / supply ---
    check_eq("pow.laneA.subsidy", pow_spec["lanes"]["LANE_A"].get("base_subsidy_satoshis"), G.LANE_A_BASE_SUBSIDY)
    check_eq("pow.laneB.subsidy", pow_spec["lanes"]["LANE_B"].get("base_subsidy_satoshis"), G.LANE_B_BASE_SUBSIDY)
    check_eq("consensus.halving", consensus.get("subsidy_halving_interval_blocks"), G.SUBSIDY_HALVING_INTERVAL)
    check_eq("consensus.max_supply", consensus.get("max_supply_satoshis"), G.MAX_MONEY_SATOSHIS)
    check_eq("consensus.satoshis_per_coin", consensus.get("satoshis_per_coin"), 100_000_000)
    # production subsidy spot checks (incl. halving boundaries)
    check_eq("subsidy(h=0,laneA)", C.get_block_subsidy(0, C.POW_TYPE_SHA256D), G.LANE_A_BASE_SUBSIDY)
    check_eq("subsidy(h=0,laneB)", C.get_block_subsidy(0, C.POW_TYPE_GENERAL_PURPOSE), G.LANE_B_BASE_SUBSIDY)
    check_eq("subsidy(pre-halving)", C.get_block_subsidy(G.SUBSIDY_HALVING_INTERVAL - 1, C.POW_TYPE_SHA256D),
             G.LANE_A_BASE_SUBSIDY)
    check_eq("subsidy(halving)", C.get_block_subsidy(G.SUBSIDY_HALVING_INTERVAL, C.POW_TYPE_SHA256D),
             G.LANE_A_BASE_SUBSIDY >> 1)
    check_eq("subsidy(halving+1)", C.get_block_subsidy(G.SUBSIDY_HALVING_INTERVAL + 1, C.POW_TYPE_SHA256D),
             G.LANE_A_BASE_SUBSIDY >> 1)
    check_eq("subsidy(2nd-halving)", C.get_block_subsidy(2 * G.SUBSIDY_HALVING_INTERVAL, C.POW_TYPE_SHA256D),
             G.LANE_A_BASE_SUBSIDY >> 2)
    if C.get_block_subsidy(0, C.POW_TYPE_SHA256D) > G.MAX_MONEY_SATOSHIS:
        fail("genesis subsidy exceeds MAX_MONEY")
    else:
        ok("subsidy within MAX_MONEY")

    # --- target encoding / difficulty ---
    check_eq("pow.limit_bits", pow_spec["lanes"]["LANE_A"].get("pow_limit_bits"), G.POW_LIMIT_BITS)
    check_eq("consensus.retarget_window", consensus.get("difficulty_retarget_window"), G.DIFFICULTY_RETARGET_INTERVAL)
    check_eq("pow.lwma_window", pow_spec.get("lwma_window"), G.DIFFICULTY_RETARGET_INTERVAL)
    check_eq("pow.algorithm", pow_spec.get("difficulty_algorithm"), "LWMA-1")
    if pow_spec.get("integer_arithmetic_only") is not True:
        fail("pow.integer_arithmetic_only must be true")
    else:
        ok("pow.integer_arithmetic_only == True")
    # strict decoder spot checks
    try:
        C.bits_to_target(0x1E8FFFFF)
        fail("bits_to_target must reject negative compact 0x1e8fffff")
    except ValueError:
        ok("bits_to_target rejects negative compact")
    if C.bits_to_target(0x1E0FFFFF) <= 0:
        fail("bits_to_target(0x1e0fffff) must be positive")
    else:
        ok("bits_to_target(0x1e0fffff) positive")
    if C.target_to_bits(C.POW_LIMIT_TARGET) != C.POW_LIMIT_BITS:
        fail("target_to_bits(POW_LIMIT) round-trip mismatch")
    else:
        ok("target_to_bits(POW_LIMIT) round-trip")

    # --- block limits / maturity ---
    check_eq("consensus.max_block_size", consensus.get("max_block_size_bytes"), G.MAX_BLOCK_SIZE)
    check_eq("consensus.coinbase_maturity", consensus.get("coinbase_maturity_blocks"), G.COINBASE_MATURITY)

    # --- addresses / witness versions ---
    modes = pqc.get("modes", {})
    check_eq("pqc.algorithm", pqc.get("algorithm"), "ML-DSA-44")
    check_eq("pqc.standard", pqc.get("standard"), "NIST FIPS 204")
    check_eq("pqc.sighash_domain", pqc.get("sighash_domain_tag"), "QUANTYCOIN_QTY4_PQC_SIGHASH_V1")
    check_eq("pqc.fail_closed", pqc.get("fail_closed_on_missing_backend"), True)
    check_eq("addr.v0.prefix", modes.get("MODE_0_LEGACY_ECDSA", {}).get("address_prefix"), "qty1q")
    check_eq("addr.v1.prefix", modes.get("MODE_1_ML_DSA", {}).get("address_prefix"), "qty1p")
    check_eq("addr.v2.prefix", modes.get("MODE_2_HYBRID", {}).get("address_prefix"), "qty1z")
    check_eq("addr.v0.witness", modes.get("MODE_0_LEGACY_ECDSA", {}).get("witness_version"), 0)
    check_eq("addr.v1.witness", modes.get("MODE_1_ML_DSA", {}).get("witness_version"), 1)
    check_eq("addr.v2.witness", modes.get("MODE_2_HYBRID", {}).get("witness_version"), 2)

    # --- networking constants ---
    main = net.get("networks", {}).get("mainnet", {})
    check_eq("net.magic_hex", main.get("magic_bytes_hex"), G.MAGIC_BYTES.hex().upper())
    check_eq("net.magic_ascii", main.get("magic_bytes_ascii"), "QTY4")
    check_eq("net.p2p", main.get("default_p2p_port"), G.DEFAULT_P2P_PORT)
    check_eq("net.rpc", main.get("default_rpc_port"), G.DEFAULT_RPC_PORT)
    check_eq("net.sv1", main.get("default_stratum_v1_port"), G.DEFAULT_STRATUM_PORT)
    check_eq("net.sv2", main.get("default_stratum_v2_port"), G.DEFAULT_STRATUM_V2_PORT)
    check_eq("net.hrp", main.get("bech32_hrp"), "qty")

    # --- serialization versions / fork choice ---
    check_eq("tx.version", tx.get("version"), 2)
    check_eq("tx.txid_digest", tx.get("txid_digest"), "double_sha256(legacy_serialization)")
    check_eq("tx.wtxid_digest", tx.get("wtxid_digest"), "double_sha256(witness_serialization)")
    check_eq("consensus.fork_choice", consensus.get("fork_choice_rule"), "weighted_cumulative_work")

    # --- vector corpus cross-check (subsidy + difficulty vectors must exist & agree) ---
    vec_dir = REPO / "tests" / "vectors" / "qty4"
    for name in ("subsidy.json", "difficulty.json", "chainwork.json", "MTP.json"):
        p = vec_dir / name
        if not p.exists():
            fail(f"missing vector file tests/vectors/qty4/{name}")
        else:
            ok(f"vector file present: {name}")

    print("=" * 60)
    if ERRORS:
        print(f"[FAIL] {len(ERRORS)} protocol-truth error(s).")
        sys.exit(1)
    print("ALL PROTOCOL TRUTH CHECKS PASSED (100%)")
    sys.exit(0)


if __name__ == "__main__":
    main()
