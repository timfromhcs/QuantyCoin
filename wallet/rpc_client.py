"""
QuantyCoin Wallet RPC Client
Connects to Local or Remote Node RPC with Fallback Discovery
Zero-Mock Implementation
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from core.genesis_constants import DEFAULT_RPC_PORT


class WalletRPCClient:
    """Communicates with QuantyCoin full node RPC."""
    def __init__(self, rpc_host: str = "127.0.0.1", rpc_port: int = DEFAULT_RPC_PORT, fallback_hosts: Optional[List[str]] = None):
        self.rpc_host = rpc_host
        self.rpc_port = rpc_port
        self.fallback_hosts = fallback_hosts or ["127.0.0.1", "seed1.quantycoin.org", "seed2.quantycoin.org"]

    def _call(self, method: str, params: list) -> Any:
        payload = json.dumps({
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }).encode('utf-8')
        
        hosts = [self.rpc_host]
        if self.rpc_host not in ("127.0.0.1", "localhost"):
            hosts += [h for h in self.fallback_hosts if h != self.rpc_host]
            
        last_error = None
        for host in hosts:
            url = f"http://{host}:{self.rpc_port}"
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            try:
                with urllib.request.urlopen(req, timeout=120) as response:
                    res_body = response.read().decode('utf-8')
                    res = json.loads(res_body)
                    if res.get("error"):
                        raise RuntimeError(res["error"]["message"])
                    return res["result"]
            except Exception as e:
                last_error = e
                continue
                
        raise ConnectionError(f"Failed to connect to RPC at {self.rpc_host}:{self.rpc_port}: {last_error}")

    def get_info(self) -> Dict[str, Any]:
        return self._call("getinfo", [])

    def get_block_count(self) -> int:
        return self._call("getblockcount", [])

    def get_address_balance(self, address: str) -> Dict[str, Any]:
        return self._call("getaddressbalance", [address])

    def get_address_utxos(self, address: str) -> List[Dict[str, Any]]:
        return self._call("getaddressutxos", [address])

    def send_raw_transaction(self, raw_tx_hex: str) -> str:
        return self._call("sendrawtransaction", [raw_tx_hex])

    def get_network_info(self) -> Dict[str, Any]:
        return self._call("getnetworkinfo", [])

    def get_block_template(self, pow_type: Optional[int] = None) -> Dict[str, Any]:
        params = [pow_type] if pow_type is not None else []
        return self._call("getblocktemplate", params)

    def submit_block(self, raw_block_hex: str) -> str:
        return self._call("submitblock", [raw_block_hex])

    def generate_to_address(self, num_blocks: int, address: str, pow_type: int = 0) -> List[str]:
        return self._call("generatetoaddress", [num_blocks, address, pow_type])

    def get_mining_lanes(self) -> Dict[str, Any]:
        return self._call("getmininglanes", [])

    def get_mining_targets(self) -> Dict[str, Any]:
        return self._call("getminingtargets", [])

    def get_chainwork(self) -> Dict[str, Any]:
        return self._call("getchainwork", [])

    def get_new_pq_address(self) -> Dict[str, Any]:
        return self._call("getnewpqaddress", [])

    def get_address_info(self, address: str) -> Dict[str, Any]:
        return self._call("getaddressinfo", [address])

    def get_stratum_info(self) -> Dict[str, Any]:
        return self._call("getstratuminfo", [])

    def help(self) -> Dict[str, str]:
        return self._call("help", [])
