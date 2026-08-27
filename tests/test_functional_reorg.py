import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.test_framework import QuantyTestFramework


class ReorgTest(QuantyTestFramework):
    def __init__(self):
        super().__init__(num_nodes=2, base_p2p_port=21400, base_rpc_port=22400)

    def run_test(self):
        print("1. Mining 3 common base blocks on Node 0 and syncing...")
        self.generate(0, 3)
        self.sync_blocks()
        assert self.nodes[0].rpc.get_block_count() == 3
        assert self.nodes[1].rpc.get_block_count() == 3
        
        print("2. Disconnecting Node 1 to simulate a network split / partition...")
        # Disconnect Node 1
        self.nodes[1].daemon.p2p.stop()
        
        print("3. Mining Branch A on Node 0 (2 blocks -> Height 5)...")
        self.generate(0, 2)
        assert self.nodes[0].rpc.get_block_count() == 5
        
        print("4. Mining Branch B on Node 1 (4 blocks -> Height 7)...")
        self.generate(1, 4)
        assert self.nodes[1].rpc.get_block_count() == 7
        
        print("5. Reconnecting partition & resolving fork choice...")
        # Restart Node 1 P2P and connect to Node 0
        self.nodes[1].daemon.p2p.start()
        self.nodes[1].daemon.p2p.connect_to_peer("127.0.0.1", self.nodes[0].p2p_port)
        
        # Inject Branch B tip into Node 0
        tip_b_block = self.nodes[1].daemon.chainstate.get_block_by_height(7)
        for h in range(4, 8):
            b = self.nodes[1].daemon.chainstate.get_block_by_height(h)
            self.nodes[0].daemon.chainstate.process_block(b)
            
        print("6. Verifying that Node 0 reorganized to Branch B (Height 7)...")
        assert self.nodes[0].rpc.get_block_count() == 7
        assert self.nodes[0].rpc.get_info()["bestblockhash"] == self.nodes[1].rpc.get_info()["bestblockhash"]


if __name__ == "__main__":
    test = ReorgTest()
    ok = test.main()
    if not ok:
        exit(1)
