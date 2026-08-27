import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.test_framework import QuantyTestFramework


class MiningTest(QuantyTestFramework):
    def __init__(self):
        super().__init__(num_nodes=2, base_p2p_port=21100, base_rpc_port=22100)

    def run_test(self):
        payout_addr = "qty1q98n2qhm5aasdree49jjp3kd34c6vas7ev0fz2g"
        
        print("1. Verifying initial Genesis state...")
        assert self.nodes[0].rpc.get_block_count() == 0
        assert self.nodes[1].rpc.get_block_count() == 0
        
        print("2. Mining 5 blocks on Node 0...")
        hashes = self.generate(0, 5, payout_addr)
        assert len(hashes) == 5
        assert self.nodes[0].rpc.get_block_count() == 5
        
        print("3. Synchronizing blocks across P2P wire to Node 1...")
        self.sync_blocks()
        assert self.nodes[1].rpc.get_block_count() == 5
        
        print("4. Verifying miner coinbase rewards & balance calculation...")
        bal = self.nodes[0].rpc.get_address_balance(payout_addr)
        # Genesis (50) + 5 Blocks (5 * 50) = 300 QTY
        assert bal["balance"] == 300.0
        assert bal["balance_sat"] == 30_000_000_000
        
        print("5. Querying mining telemetry & block templates...")
        mining_info = self.nodes[0].rpc._call("getmininginfo", [])
        assert mining_info["blocks"] == 5
        assert mining_info["chain"] == "main"
        
        tmpl = self.nodes[0].rpc.get_block_template()
        assert tmpl["height"] == 6
        assert tmpl["coinbasevalue"] == 50 * 100_000_000


if __name__ == "__main__":
    test = MiningTest()
    ok = test.main()
    if not ok:
        exit(1)
