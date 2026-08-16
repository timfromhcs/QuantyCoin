#!/usr/bin/env python3
# Copyright (c) 2024 The QTY Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test QTY regtest mining functionality and chain identity."""

from test_framework.test_framework import QTYTestFramework
from test_framework.util import (
    assert_equal,
    assert_raises_rpc_error,
)
from test_framework.wallet import MiniWallet, MiniWalletMode


class QTYRegtestMiningTest(QTYTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.chain = 'regtest'

    def run_test(self):
        self.test_qty_chain_identity()
        self.test_regtest_mining()
        self.test_generateblock_functionality()
        self.test_block_generation_with_transactions()

    def test_qty_chain_identity(self):
        """Test that QTY properly identifies as regtest chain."""
        self.log.info("Testing QTY chain identity detection...")
        
        # Check getblockchaininfo returns correct QTY chain
        blockchain_info = self.nodes[0].getblockchaininfo()
        assert_equal(blockchain_info['chain'], 'regtest')  # QTY regtest identifier
        
        # Check initial state
        assert_equal(blockchain_info['blocks'], 0)  # Genesis block
        assert_equal(blockchain_info['headers'], 0)
        
        self.log.info("✓ Chain identity correctly detected as regtest")

    def test_regtest_mining(self):
        """Test basic QTY regtest block generation."""
        self.log.info("Testing QTY regtest mining...")
        
        node = self.nodes[0]
        miniwallet = MiniWallet(node, mode=MiniWalletMode.RAW_P2PK)
        
        # Get initial state
        initial_height = node.getblockcount()
        
        # Generate a block
        # Use descriptor-based generation to avoid segwit/taproot and wallet deps
        desc = miniwallet.get_descriptor()
        block_hashes = self.generatetodescriptor(node, 1, desc)
        
        # Verify block was generated
        assert_equal(len(block_hashes), 1)
        assert_equal(node.getblockcount(), initial_height + 1)
        
        # Verify blockchain info updated
        blockchain_info = node.getblockchaininfo()
        assert_equal(blockchain_info['blocks'], initial_height + 1)
        assert_equal(blockchain_info['bestblockhash'], block_hashes[0])
        assert_equal(blockchain_info['chain'], 'regtest')  # Still QTY
        
        self.log.info("✓ QTY regtest mining successful")

    def test_generateblock_functionality(self):
        """Test generateblock RPC command for QTY."""
        self.log.info("Testing QTY generateblock RPC...")
        
        node = self.nodes[0]
        miniwallet = MiniWallet(node, mode=MiniWalletMode.RAW_P2PK)
        desc = miniwallet.get_descriptor()
        
        # Test generateblock with empty transaction list
        result = self.generateblock(node, output=desc, transactions=[])
        assert 'hash' in result
        assert len(result['hash']) == 64  # Valid block hash
        
        # Verify block exists and contains QTY-specific data
        block = node.getblock(result['hash'])
        assert_equal(len(block['tx']), 1)  # Only coinbase
        
        # Verify we're still on QTY chain
        chain_info = node.getblockchaininfo()
        assert_equal(chain_info['chain'], 'regtest')
        
        self.log.info("✓ QTY generateblock RPC working correctly")

    def test_block_generation_with_transactions(self):
        """Test generating QTY blocks with specific transactions."""
        self.log.info("Testing QTY block generation with transactions...")
        
        node = self.nodes[0]
        miniwallet = MiniWallet(node, mode=MiniWalletMode.RAW_P2PK)
        
        # Generate some QTY coins first
        self.generatetodescriptor(node, 100, miniwallet.get_descriptor())
        
        # Create a QTY transaction
        desc = miniwallet.get_descriptor()
        utxo = miniwallet.get_utxo()
        tx = miniwallet.create_self_transfer(utxo_to_spend=utxo)
        txid = node.sendrawtransaction(tx['hex'])
        
        # Generate QTY block with this transaction
        result = self.generateblock(node, output=desc, transactions=[txid])
        
        # Verify transaction is in the block
        block = node.getblock(result['hash'], 2)  # verbosity=2 for full tx details
        assert_equal(len(block['tx']), 2)  # Coinbase + our transaction
        assert_equal(block['tx'][1]['txid'], txid)
        
        # Verify still on QTY chain
        assert_equal(node.getblockchaininfo()['chain'], 'regtest')
        
        self.log.info("✓ QTY block generation with transactions successful")


if __name__ == '__main__':
    QTYRegtestMiningTest().main()
