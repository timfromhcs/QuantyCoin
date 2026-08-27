import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.test_framework import QuantyTestFramework
from wallet.hd_wallet import HDWallet


class WalletTest(QuantyTestFramework):
    def __init__(self):
        super().__init__(num_nodes=2, base_p2p_port=21200, base_rpc_port=22200)

    def run_test(self):
        print("1. Creating test HD wallets...")
        wallet_a = HDWallet()
        wallet_b = HDWallet()
        
        addr_a = wallet_a.get_address(0)
        addr_b = wallet_b.get_address(0)
        print(f"   Wallet A: {addr_a}")
        print(f"   Wallet B: {addr_b}")
        
        print("2. Mining 3 blocks to fund Wallet A...")
        self.generate(0, 3, addr_a)
        self.sync_blocks()
        
        bal_a = self.nodes[0].rpc.get_address_balance(addr_a)
        assert bal_a["balance"] == 150.0 # 3 * 50 QTY
        
        print("3. Fetching spendable UTXOs for Wallet A...")
        utxos = self.nodes[0].rpc.get_address_utxos(addr_a)
        assert len(utxos) == 3
        
        print("4. Creating & signing 25 QTY transaction from Wallet A -> Wallet B...")
        raw_tx_hex, txid = wallet_a.create_and_sign_transaction(
            utxos=utxos,
            destination_address=addr_b,
            amount_sat=25 * 100_000_000,
            fee_sat=10_000
        )
        print(f"   Signed TXID: {txid}")
        
        print("5. Broadcasting transaction to Node 0 mempool...")
        res_txid = self.nodes[0].rpc.send_raw_transaction(raw_tx_hex)
        assert res_txid == txid
        
        print("6. Synchronizing mempools across P2P network...")
        self.sync_mempools()
        assert txid in self.nodes[1].rpc._call("getrawmempool", [])
        
        print("7. Mining 1 block to confirm transaction...")
        self.generate(0, 1)
        self.sync_blocks()
        
        print("8. Verifying final confirmed balances...")
        bal_b = self.nodes[1].rpc.get_address_balance(addr_b)
        assert bal_b["balance"] == 25.0
        
        bal_a_rec = self.nodes[0].rpc.get_address_balance(addr_a)
        bal_a_chg = self.nodes[0].rpc.get_address_balance(wallet_a.get_change_address(0))
        total_a_sat = bal_a_rec["balance_sat"] + bal_a_chg["balance_sat"]
        
        # 150 - 25 - 0.0001 (fee) = 124.9999 QTY
        assert total_a_sat == (150 * 100_000_000) - (25 * 100_000_000) - 10_000


if __name__ == "__main__":
    test = WalletTest()
    ok = test.main()
    if not ok:
        exit(1)
