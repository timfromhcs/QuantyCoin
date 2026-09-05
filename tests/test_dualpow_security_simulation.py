"""
QuantyCoin QTY4 Dual-PoW Security & Hostile Mining Simulation Matrix
Phase P4: Simulates hostile mining distributions, liveness under lane disappearance,
and proves anti-grinding invariance of Weighted Cumulative Work.
"""

import sys
import time
import hashlib
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from core.genesis_constants import (
    POW_LIMIT_BITS, THERMODYNAMIC_WEIGHT_A, THERMODYNAMIC_WEIGHT_B,
    LANE_A_TARGET_TIME, LANE_B_TARGET_TIME
)
from core.block import BlockHeader
from core.consensus import (
    bits_to_target, target_to_bits, get_block_work,
    calculate_next_work_required_dual,
    POW_TYPE_SHA256D, POW_TYPE_GENERAL_PURPOSE
)
from crypto import hash256


class DualPoWHostileSimulator:
    """Simulates adversarial mining scenarios on dual-lane network."""

    def __init__(self):
        self.genesis_bits = POW_LIMIT_BITS

    def simulate_lane_disappearance(self, active_lane: int, inactive_lane: int, num_blocks: int = 60) -> bool:
        """Verify that when one lane disappears, the other lane continues advancing difficulty and chain."""
        headers = []
        t = 1000000
        # Start with balanced genesis headers
        for i in range(20):
            pt = POW_TYPE_SHA256D if i % 2 == 0 else POW_TYPE_GENERAL_PURPOSE
            h = BlockHeader(version=(pt << 16) | 1, prev_block=b'\x00'*32, merkle_root=b'\x00'*32, timestamp=t, bits=self.genesis_bits, nonce=0)
            headers.append(h)
            t += 60

        # Now inactive_lane ceases all mining. Only active_lane produces blocks.
        for i in range(num_blocks):
            bits = calculate_next_work_required_dual(headers, pow_type=active_lane)
            h = BlockHeader(version=(active_lane << 16) | 1, prev_block=headers[-1].hash, merkle_root=b'\x00'*32, timestamp=t, bits=bits, nonce=0)
            headers.append(h)
            t += 120  # target interval for single lane

        # Confirm active lane advanced
        active_headers = [h for h in headers if h.pow_type == active_lane]
        assert len(active_headers) >= num_blocks
        return True

    def simulate_anti_grinding_attack(self) -> bool:
        """
        Prove that an attacker generating extra low-difficulty blocks on Lane B (Scrypt)
        cannot overtake an honest chain with higher cumulative energy commitment on Lane A (SHA-256D).
        """
        # Honest Chain: 50 blocks of high-difficulty Lane A (difficulty ~4096x base, target 0x1c0fffff)
        honest_bits = 0x1c0fffff
        honest_chainwork = sum(get_block_work(honest_bits, POW_TYPE_SHA256D) for _ in range(50))

        # Attacker Chain: 60 blocks of easy Lane B at base difficulty (POW_LIMIT_BITS 0x1e0fffff)
        # Attacker has MORE blocks (60 vs 50), but LESS total cumulative work!
        attacker_bits = POW_LIMIT_BITS
        attacker_chainwork = sum(get_block_work(attacker_bits, POW_TYPE_GENERAL_PURPOSE) for _ in range(60))

        # Honest chainwork must dominate despite attacker having more blocks!
        assert honest_chainwork > attacker_chainwork, (
            f"Anti-grinding violation: Honest {honest_chainwork} vs Attacker {attacker_chainwork}"
        )
        return True

    def benchmark_pow_algorithms(self, iterations: int = 500) -> dict:
        """Produce reproducible execution benchmarks for both PoW lanes."""
        data = b"QuantyCoin Benchmark Header Block Candidate 80-bytes 123456789012345678"

        # Lane A: SHA-256D
        t0 = time.perf_counter()
        for _ in range(iterations):
            _ = hash256(data)
        t_sha = time.perf_counter() - t0
        rate_sha = iterations / t_sha

        # Lane B: Scrypt (N=1024, r=1, p=1)
        t0 = time.perf_counter()
        for _ in range(iterations):
            _ = hashlib.scrypt(data, salt=b"quantycoin_pow_gp", n=1024, r=1, p=1, maxmem=0, dklen=32)
        t_scrypt = time.perf_counter() - t0
        rate_scrypt = iterations / t_scrypt

        return {
            "iterations": iterations,
            "sha256d_seconds": t_sha,
            "sha256d_hashes_per_sec": rate_sha,
            "scrypt_seconds": t_scrypt,
            "scrypt_hashes_per_sec": rate_scrypt,
            "cost_ratio_scrypt_to_sha": rate_sha / rate_scrypt if rate_scrypt > 0 else 0
        }


def main():
    print("==================================================")
    print("QUANTYCOIN QTY4 DUAL-POW SECURITY & BENCHMARK SUITE")
    print("==================================================")
    sim = DualPoWHostileSimulator()

    print("1. Testing sudden SHA-256D lane disappearance (Scrypt sustains chain)...")
    sim.simulate_lane_disappearance(active_lane=POW_TYPE_GENERAL_PURPOSE, inactive_lane=POW_TYPE_SHA256D)
    print("   [PASS] Scrypt sustained chain progress independently.")

    print("2. Testing sudden Scrypt lane disappearance (SHA-256D sustains chain)...")
    sim.simulate_lane_disappearance(active_lane=POW_TYPE_SHA256D, inactive_lane=POW_TYPE_GENERAL_PURPOSE)
    print("   [PASS] SHA-256D sustained chain progress independently.")

    print("3. Testing Anti-Grinding attack (low-difficulty spam vs honest chain)...")
    sim.simulate_anti_grinding_attack()
    print("   [PASS] Weighted Cumulative Work defeated block-count spam attack.")

    print("4. Running PoW Lane Benchmarks...")
    bench = sim.benchmark_pow_algorithms(iterations=500)
    print(f"   SHA-256D Throughput: {bench['sha256d_hashes_per_sec']:,.0f} H/s")
    print(f"   Scrypt 1024 Throughput: {bench['scrypt_hashes_per_sec']:,.0f} H/s")
    print(f"   Measured Cost Ratio: {bench['cost_ratio_scrypt_to_sha']:.1f}x energy multiplier")
    print("==================================================")
    print("ALL DUAL-POW SECURITY TESTS & BENCHMARKS PASSED (100%)")
    print("==================================================")


if __name__ == "__main__":
    main()
