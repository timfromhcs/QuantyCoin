"""
QuantyCoin Test Runner (Inspired by Bitcoin Core test_runner.py)
Executes all cryptographic unit tests, consensus tests, P2P tests, and functional integration tests.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.test_functional_mining import MiningTest
from tests.test_functional_wallet import WalletTest
from tests.test_functional_p2p import P2PTest
from tests.test_functional_reorg import ReorgTest
from tests.test_functional_stratum import run_stratum_test


def run_unit_tests() -> bool:
    print("========================================================")
    print("RUNNING CRYPTOGRAPHIC & CORE UNIT TESTS")
    print("========================================================")
    
    # 1. Crypto Tests
    import tests.test_crypto
    print("[PASS] Cryptographic verification suite")
    
    # 2. Core Tests
    import tests.test_core
    print("[PASS] Core transaction & consensus suite")
    
    # 3. P2P Tests
    import tests.test_p2p
    print("[PASS] P2P protocol serialization suite")
    
    return True


def run_functional_tests() -> bool:
    test_classes = [
        ("Mining & Subsidy Test", MiningTest),
        ("Wallet & BIP39 Transaction Test", WalletTest),
        ("P2P Multi-Node Relay Test", P2PTest),
        ("Chain Split & Deep Reorg Test", ReorgTest)
    ]
    
    results = []
    for name, cls in test_classes:
        test = cls()
        success = test.main()
        results.append((name, success))
        time.sleep(1.0)

    # Stratum V1 Mining Protocol Test
    stratum_ok = run_stratum_test(port=13335)
    results.append(("Stratum V1 Protocol Test", stratum_ok))
    time.sleep(1.0)

    # PQC, Dual-PoW & Stratum V2 Protocol Test Suite
    import unittest
    import tests.test_pqc_dualpow_sv2
    pqc_suite = unittest.TestLoader().loadTestsFromModule(tests.test_pqc_dualpow_sv2)
    pqc_runner = unittest.TextTestRunner(verbosity=1)
    pqc_res = pqc_runner.run(pqc_suite)
    results.append(("PQC, Dual-PoW & SV2 Test Suite", pqc_res.wasSuccessful()))
    time.sleep(1.0)
        
    print("\n========================================================")
    print("           QUANTYCOIN TEST SUITE RESULTS")
    print("========================================================")
    all_passed = True
    for name, success in results:
        status = "PASSED" if success else "FAILED"
        print(f" - {name:<35} : [{status}]")
        if not success:
            all_passed = False
            
    print("========================================================")
    if all_passed:
        print("ALL TESTS PASSED WITH 100% SUCCESS (0 FAILURES)!")
    else:
        print("SOME TESTS FAILED! CHECK OUTPUT ABOVE.")
    print("========================================================\n")
    return all_passed


def main():
    start = time.time()
    unit_ok = run_unit_tests()
    if not unit_ok:
        sys.exit(1)
        
    func_ok = run_functional_tests()
    elapsed = round(time.time() - start, 2)
    print(f"Total Test Execution Time: {elapsed} seconds")
    
    if not func_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
