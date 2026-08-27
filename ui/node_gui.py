"""
QuantyCoin Standalone Full Node GUI (Cyberpunk Dark Mode v4.0)
Live P2P Dashboard, Integrated Block Explorer & Interactive RPC Console
"""

import sys
import os
import json
import webbrowser
import threading
from typing import Optional, Any, Dict, List
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Safe imports for both package and PyInstaller onefile execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from ui.shared_theme import render_html_page
except ImportError:
    from shared_theme import render_html_page

from wallet.rpc_client import WalletRPCClient

NODE_HTML_BODY = """
<div class="tabs">
  <button class="tab-btn active" onclick="switchTab('dashboard')">🌐 P2P Dashboard</button>
  <button class="tab-btn" onclick="switchTab('explorer')">🔍 Block Explorer</button>
  <button class="tab-btn" onclick="switchTab('console')">⚡ RPC Console</button>
</div>

<!-- TAB 1: DASHBOARD -->
<div id="tab-dashboard">
  <div class="grid-4" style="margin-bottom: 24px;">
    <div class="card">
      <div class="card-header">
        <span class="card-title">Block Height</span>
        <span class="status-indicator"></span>
      </div>
      <div class="card-value" id="val-blocks">0</div>
      <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Synced Tip</div>
    </div>
    <div class="card">
      <div class="card-header">
        <span class="card-title">Connected Peers</span>
        <span style="color: var(--accent-cyan);">P2P</span>
      </div>
      <div class="card-value" id="val-peers">0</div>
      <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Active Links</div>
    </div>
    <div class="card">
      <div class="card-header">
        <span class="card-title">Mempool TXs</span>
        <span style="color: var(--accent-violet);">TX</span>
      </div>
      <div class="card-value" id="val-mempool">0</div>
      <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Unconfirmed Queue</div>
    </div>
    <div class="card">
      <div class="card-header">
        <span class="card-title">Circulation</span>
        <span style="color: var(--accent-green);">QTY</span>
      </div>
      <div class="card-value" id="val-supply">50.00</div>
      <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Total Mined</div>
    </div>
  </div>

  <div class="grid-2">
    <div class="card">
      <div class="card-header">
        <span class="card-title">Chainstate Information</span>
      </div>
      <div style="display: flex; flex-direction: column; gap: 10px; font-size: 13px; font-family: var(--font-mono);">
        <div><strong style="color: var(--text-muted);">Best Hash:</strong> <span id="val-besthash" style="color: var(--accent-cyan); word-break: break-all;">-</span></div>
        <div><strong style="color: var(--text-muted);">Protocol:</strong> <span>v70015 (QuantyWire)</span></div>
        <div><strong style="color: var(--text-muted);">Default P2P Port:</strong> <span>19888</span></div>
        <div><strong style="color: var(--text-muted);">Default RPC Port:</strong> <span>19889</span></div>
        <div><strong style="color: var(--text-muted);">Network:</strong> <span class="status-pill status-online">MAINNET v4.0 ACTIVE</span></div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <span class="card-title">Active P2P Peer Telemetry</span>
      </div>
      <div class="table-container" style="max-height: 200px; overflow-y: auto;">
        <table>
          <thead>
            <tr>
              <th>Address</th>
              <th>Type</th>
              <th>SubVer</th>
              <th>Latency</th>
            </tr>
          </thead>
          <tbody id="peer-table-body">
            <tr><td colspan="4" style="text-align: center; color: var(--text-muted);">Listening for inbound & outbound peers...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- TAB 2: BLOCK EXPLORER -->
<div id="tab-explorer" style="display: none;">
  <div class="card" style="margin-bottom: 20px;">
    <div class="card-header">
      <span class="card-title">QuantyCoin On-Chain Search</span>
    </div>
    <div style="display: flex; gap: 12px;">
      <input type="text" id="explorer-input" class="input-control" placeholder="Search by Block Height, Block Hash, Transaction ID (TXID) or Address (qty1q...)">
      <button class="btn btn-primary" onclick="searchExplorer()">Search</button>
    </div>
  </div>

  <div class="card" id="explorer-result-card" style="display: none;">
    <div class="card-header">
      <span class="card-title" id="explorer-result-title">Search Result</span>
    </div>
    <pre id="explorer-result-content" style="background: var(--bg-input); padding: 16px; border-radius: 8px; font-family: var(--font-mono); font-size: 13px; color: var(--accent-cyan); overflow-x: auto; max-height: 400px;"></pre>
  </div>
</div>

<!-- TAB 3: RPC CONSOLE -->
<div id="tab-console" style="display: none;">
  <div class="card">
    <div class="card-header">
      <span class="card-title">Interactive JSON-RPC Terminal</span>
    </div>
    <div style="display: flex; gap: 12px; margin-bottom: 16px;">
      <select id="rpc-quick-select" class="input-control" style="max-width: 220px;" onchange="fillRpcCommand(this.value)">
        <option value="">Quick Commands...</option>
        <option value="getinfo">getinfo</option>
        <option value="getblockchaininfo">getblockchaininfo</option>
        <option value="getblockcount">getblockcount</option>
        <option value="getmempoolinfo">getmempoolinfo</option>
        <option value="getpeerinfo">getpeerinfo</option>
        <option value="getmininginfo">getmininginfo</option>
      </select>
      <input type="text" id="rpc-command-input" class="input-control" placeholder="method [arg1] [arg2] (e.g. getblock 0)">
      <button class="btn btn-violet" onclick="executeRpcCommand()">Execute</button>
    </div>
    <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;">Response Terminal:</div>
    <pre id="rpc-terminal-output" style="background: var(--bg-input); padding: 16px; border-radius: 8px; font-family: var(--font-mono); font-size: 13px; color: var(--text-main); min-height: 250px; max-height: 450px; overflow-y: auto;">QuantyCoin JSON-RPC 2.0 Terminal Ready.
Type a command above and press Execute.</pre>
  </div>
</div>
"""

NODE_JS = """
function switchTab(tabId) {
  document.getElementById('tab-dashboard').style.display = tabId === 'dashboard' ? 'block' : 'none';
  document.getElementById('tab-explorer').style.display = tabId === 'explorer' ? 'block' : 'none';
  document.getElementById('tab-console').style.display = tabId === 'console' ? 'block' : 'none';
  
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');
}

async function fetchNodeData() {
  try {
    const res = await fetch('/api/node_status');
    const data = await res.json();
    
    document.getElementById('val-blocks').innerText = data.blocks;
    document.getElementById('val-peers').innerText = data.connections;
    document.getElementById('val-mempool').innerText = data.mempool_size;
    document.getElementById('val-supply').innerText = (data.circulating_supply || 50).toFixed(2) + ' QTY';
    document.getElementById('val-besthash').innerText = data.bestblockhash;
    
    const peerTbody = document.getElementById('peer-table-body');
    if (data.peers && data.peers.length > 0) {
      peerTbody.innerHTML = data.peers.map(p => `
        <tr>
          <td>${p.addr}</td>
          <td><span class="brand-badge">${p.inbound ? 'INBOUND' : 'OUTBOUND'}</span></td>
          <td>${p.subver || 'QuantyWire'}</td>
          <td style="color: var(--accent-cyan);">${p.pingtime} ms</td>
        </tr>
      `).join('');
    }
  } catch (e) {
    console.error('Fetch error:', e);
  }
}

async function searchExplorer() {
  const query = document.getElementById('explorer-input').value.trim();
  if (!query) return;
  
  try {
    const res = await fetch(`/api/explorer?q=${encodeURIComponent(query)}`);
    const data = await res.json();
    document.getElementById('explorer-result-card').style.display = 'block';
    document.getElementById('explorer-result-content').innerText = JSON.stringify(data, null, 2);
  } catch (e) {
    alert('Search error: ' + e);
  }
}

function fillRpcCommand(cmd) {
  if (cmd) {
    document.getElementById('rpc-command-input').value = cmd;
  }
}

async function executeRpcCommand() {
  const raw = document.getElementById('rpc-command-input').value.trim();
  if (!raw) return;
  const parts = raw.split(' ');
  const method = parts[0];
  const params = parts.slice(1).map(p => {
    if (!isNaN(p)) return Number(p);
    return p;
  });
  
  try {
    const res = await fetch('/api/rpc_exec', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({method, params})
    });
    const data = await res.json();
    document.getElementById('rpc-terminal-output').innerText = JSON.stringify(data, null, 2);
  } catch (e) {
    document.getElementById('rpc-terminal-output').innerText = 'RPC Error: ' + e;
  }
}

setInterval(fetchNodeData, 2000);
fetchNodeData();
"""


class NodeGUIHandler(BaseHTTPRequestHandler):
    rpc_client: WalletRPCClient

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/':
            html = render_html_page("Full Node & Block Explorer", "NODE SUITE v4.0", NODE_HTML_BODY, NODE_JS)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        elif parsed.path == '/api/node_status':
            try:
                info = self.rpc_client.get_info()
                peers = self.rpc_client._call("getpeerinfo", [])
                info["peers"] = peers
                self._send_json(200, info)
            except Exception:
                self._send_json(200, {"blocks": 0, "connections": 0, "mempool_size": 0, "bestblockhash": "Connecting to node...", "circulating_supply": 50, "peers": []})
        elif parsed.path == '/api/explorer':
            q = parse_qs(parsed.query).get('q', [''])[0]
            try:
                if q.isdigit():
                    res = self.rpc_client._call("getblock", [self.rpc_client._call("getblockhash", [int(q)])])
                elif q.startswith("qty1") or q.startswith("quan1"):
                    res = self.rpc_client.get_address_balance(q)
                    res["utxos"] = self.rpc_client.get_address_utxos(q)
                elif len(q) == 64:
                    try:
                        res = self.rpc_client._call("getblock", [q])
                    except Exception:
                        res = self.rpc_client._call("getrawtransaction", [q])
                else:
                    res = {"error": "Invalid search query"}
                self._send_json(200, res)
            except Exception as e:
                self._send_json(500, {"error": str(e)})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/rpc_exec':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode('utf-8'))
            try:
                result = self.rpc_client._call(data["method"], data.get("params", []))
                self._send_json(200, {"result": result})
            except Exception as e:
                self._send_json(200, {"error": str(e)})

    def _send_json(self, status: int, data: Any):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        pass


def launch_node_gui(gui_port: int = 8081, rpc_port: int = 19889):
    NodeGUIHandler.rpc_client = WalletRPCClient(rpc_port=rpc_port)
    server = HTTPServer(('127.0.0.1', gui_port), NodeGUIHandler)
    url = f"http://127.0.0.1:{gui_port}"
    print(f"\n========================================================")
    print(f"QUANTYCOIN STANDALONE FULL NODE GUI RUNNING (v4.0)")
    print(f"Open in browser: {url}")
    print(f"========================================================\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    server.serve_forever()


if __name__ == "__main__":
    launch_node_gui()
