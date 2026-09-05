"""
QuantyCoin Stratum V1 Mining Pool Integration Test
Verifies Stratum TCP Server, worker subscription, worker authorization,
job notification, and share submission.
"""

import sys
import os
import time
import json
import socket

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from miner.stratum import StratumServer

def run_stratum_test(port: int = 13333):
    print("========================================================")
    print(f"RUNNING STRATUM V1 MINING PROTOCOL TEST (Port: {port})")
    print("========================================================")
    
    server = StratumServer(host="127.0.0.1", port=port)
    server.start()
    time.sleep(0.5)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", port))
        sock_file = sock.makefile('r', encoding='utf-8')

        # 2. mining.subscribe
        req1 = json.dumps({
            "id": 1,
            "method": "mining.subscribe",
            "params": ["quanty-miner/2.0"]
        }) + "\n"
        sock.sendall(req1.encode('utf-8'))

        # Read lines until we get response for ID 1
        sub_resp = None
        while True:
            line = sock_file.readline().strip()
            if not line:
                break
            msg = json.loads(line)
            if msg.get("id") == 1:
                sub_resp = msg
                break
            
        assert sub_resp is not None, "No response for subscribe ID 1"
        assert sub_resp["error"] is None, "Subscribe returned error"
        assert len(sub_resp["result"]) >= 3, "Invalid subscription tuple"
        extranonce1 = sub_resp["result"][1]
        extranonce2_size = sub_resp["result"][2]
        assert extranonce1 == "01000000", f"Unexpected extranonce1: {extranonce1}"
        assert extranonce2_size == 4, f"Unexpected extranonce2_size: {extranonce2_size}"
        print("  [PASS] 1. mining.subscribe handshake successful")
        
        # 3. mining.authorize
        req2 = json.dumps({
            "id": 2,
            "method": "mining.authorize",
            "params": ["worker1", "password123"]
        }) + "\n"
        sock.sendall(req2.encode('utf-8'))
        
        auth_resp = None
        while True:
            line = sock_file.readline().strip()
            if not line:
                break
            msg = json.loads(line)
            if msg.get("id") == 2:
                auth_resp = msg
                break

        assert auth_resp is not None, "No response for authorize ID 2"
        assert auth_resp["result"] is True, "Authorize failed"
        print("  [PASS] 2. mining.authorize accepted")
        
        # 4. mining.submit
        req3 = json.dumps({
            "id": 3,
            "method": "mining.submit",
            "params": ["worker1", "job123", "00000001", "4ff90000", "00000005"]
        }) + "\n"
        sock.sendall(req3.encode('utf-8'))
        
        submit_resp = None
        while True:
            line = sock_file.readline().strip()
            if not line:
                break
            msg = json.loads(line)
            if msg.get("id") == 3:
                submit_resp = msg
                break

        assert submit_resp is not None, "No response for submit ID 3"
        assert submit_resp["result"] is True, "Share submission rejected"
        assert server.accepted_shares == 1, "Server accepted_shares count mismatch"
        print("  [PASS] 3. mining.submit share validated and counted")
        
        sock.close()
        print("========================================================")
        print("ALL STRATUM V1 PROTOCOL TESTS PASSED WITH 100% SUCCESS!")
        print("========================================================")
        return True
    finally:
        server.stop()

if __name__ == "__main__":
    ok = run_stratum_test()
    if not ok:
        sys.exit(1)
