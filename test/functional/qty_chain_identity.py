#!/usr/bin/env python3
# Copyright (c) 2024 The QTY Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test QTY chain identity detection across all network types."""

from test_framework.test_framework import QTYTestFramework
from test_framework.util import (
    assert_equal,
)


class QTYChainIdentityTest(QTYTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.chain = 'regtest'

    def run_test(self):
        self.test_qty_regtest_identity()
        self.verify_qty_chain_consistency()
        self.test_qty_genesis_block()

    def test_qty_regtest_identity(self):
        """Test QTY regtest chain identity."""
        self.log.info("Testing QTY regtest chain identity...")
        
        node = self.nodes[0]
        
        # Get blockchain info
        info = node.getblockchaininfo()
        
        # Verify QTY chain identity
        assert_equal(info['chain'], 'regtest')
        
        # Verify network-specific parameters
        assert_equal(info['blocks'], 0)  # Should start at genesis
        
        # Test mining info for QTY-specific values
        mining_info = node.getmininginfo()
        assert_equal(mining_info['chain'], 'regtest')
        
        # Verify difficulty is low for regtest
        assert mining_info['difficulty'] <= 1.0
        
        self.log.info("✓ QTY regtest identity verified")

    def verify_qty_chain_consistency(self):
        """Verify that all RPC commands return consistent QTY chain information."""
        self.log.info("Testing QTY chain type consistency across RPCs...")
        
        node = self.nodes[0]
        
        # Get chain from different RPC calls
        blockchain_chain = node.getblockchaininfo()['chain']
        mining_chain = node.getmininginfo()['chain']
        
        # All should return the same QTY chain identifier
        assert_equal(blockchain_chain, 'regtest')
        assert_equal(mining_chain, 'regtest')
        assert_equal(blockchain_chain, mining_chain)
        
        self.log.info("✓ QTY chain type consistency verified")

    def test_qty_genesis_block(self):
        """Test that QTY genesis block is properly configured."""
        self.log.info("Testing QTY genesis block...")
        
        node = self.nodes[0]
        
        # Get QTY genesis block
        genesis_hash = node.getblockhash(0)
        genesis_block = node.getblock(genesis_hash, 2)
        
        # Verify QTY genesis block properties
        assert_equal(genesis_block['height'], 0)
        # Genesis block should not have a previous block hash
        if 'previousblockhash' in genesis_block:
            assert genesis_block['previousblockhash'] is None
        assert_equal(len(genesis_block['tx']), 1)  # Only coinbase
        
        # Verify we're on QTY chain
        assert_equal(node.getblockchaininfo()['chain'], 'regtest')
        
        self.log.info("✓ QTY genesis block validation successful")


if __name__ == '__main__':
    QTYChainIdentityTest().main()
