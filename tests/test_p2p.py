"""
QuantyCoin P2P Protocol & Framing Unit Tests
"""

import os
import sys
import struct

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from network.protocol import (
    create_message, parse_header, build_version_payload,
    parse_version_payload, build_inv_payload, parse_inv_payload,
    INV_TYPE_TX, INV_TYPE_BLOCK, HEADER_LENGTH
)
from core.genesis_constants import MAGIC_BYTES, PROTOCOL_VERSION


def test_wire_framing():
    payload = b"Hello QuantyCoin Wire"
    framed = create_message("testcmd", payload)
    
    assert len(framed) == HEADER_LENGTH + len(payload)
    magic, cmd, payload_len, checksum = parse_header(framed[:HEADER_LENGTH])
    
    assert magic == MAGIC_BYTES
    assert cmd == "testcmd"
    assert payload_len == len(payload)
    assert framed[HEADER_LENGTH:] == payload
    print("Wire Framing Test: PASS")


def test_version_payload():
    payload = build_version_payload(best_height=100, local_nonce=9999, user_agent="/QuantyTest:1.0/")
    info = parse_version_payload(payload)
    
    assert info["version"] == PROTOCOL_VERSION
    assert info["start_height"] == 100
    assert info["nonce"] == 9999
    assert info["user_agent"] == "/QuantyTest:1.0/"
    print("Version Handshake Payload Test: PASS")


def test_inv_payload():
    dummy_hash1 = b'\xaa' * 32
    dummy_hash2 = b'\xbb' * 32
    payload = build_inv_payload([(INV_TYPE_BLOCK, dummy_hash1), (INV_TYPE_TX, dummy_hash2)])
    items = parse_inv_payload(payload)
    
    assert len(items) == 2
    assert items[0] == (INV_TYPE_BLOCK, dummy_hash1)
    assert items[1] == (INV_TYPE_TX, dummy_hash2)
    print("Inventory Payload Serialization Test: PASS")


def run_all_p2p_tests():
    print("\n========================================================")
    print("RUNNING P2P PROTOCOL UNIT TEST SUITE")
    print("========================================================")
    test_wire_framing()
    test_version_payload()
    test_inv_payload()
    print("========================================================")
    print("ALL P2P PROTOCOL UNIT TESTS PASSED WITH 100% SUCCESS!")
    print("========================================================\n")


if __name__ == "__main__":
    run_all_p2p_tests()
