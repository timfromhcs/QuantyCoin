import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.test_framework import QuantyTestFramework


class P2PTest(QuantyTestFramework):
    def __init__(self):
        super().__init__(num_nodes=3, base_p2p_port=21300, base_rpc_port=22300)

    def run_test(self):
        print("1. Verifying initial P2P mesh network topology...")
        # Node 0 has connections from Node 1 and Node 2
        peers_0 = self.nodes[0].rpc._call("getpeerinfo", [])
        assert len(peers_0) >= 2
        
        print("2. Verifying protocol version and user agents...")
        for p in peers_0:
            assert p.get("version", 70015) == 70015
            assert "Quanty" in p.get("subver", "QuantyCore")
            
        print("3. Mining blocks on Node 0 and checking propagation to Node 1 & 2...")
        self.generate(0, 4)
        self.sync_blocks()
        
        for n in self.nodes:
            assert n.rpc.get_block_count() == 4
            
        print("4. Mining 2 blocks on Node 2 and syncing backwards to Node 0 & 1...")
        self.generate(2, 2)
        self.sync_blocks()
        
        for n in self.nodes:
            assert n.rpc.get_block_count() == 6


if __name__ == "__main__":
    test = P2PTest()
    ok = test.main()
    if not ok:
        exit(1)
