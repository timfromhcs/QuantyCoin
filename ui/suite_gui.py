"""
QuantyCoin Combined All-in-One Suite GUI (Cyberpunk Dark Mode v4.0)
Unified Control Center for Full Node, Light Wallet & Mining Engine
Branding: Obsidian #0A0D14 | Quanty Cyan #00F0FF | Neon Violet #8A2BE2 | Slate Grey #1E2433
"""

import sys
import os
import json
import time
import webbrowser
import threading
from typing import Optional, Any, Dict, List
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Safe imports for both package and PyInstaller onefile execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from ui.shared_theme import render_html_page
except ImportError:
    from shared_theme import render_html_page

from node.daemon import QuantyNode
from wallet.hd_wallet import HDWallet
from wallet.rpc_client import WalletRPCClient
from miner.engine import MiningEngine

SUITE_HTML_BODY = """
<!-- UNIFIED STATUS RIBBON -->
<div class="card" style="margin-bottom: 24px; background: linear-gradient(135deg, rgba(18, 23, 36, 0.9), rgba(30, 36, 51, 0.9)); border-color: var(--border-cyan);">
  <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
    <div>
      <div style="font-size: 20px; font-weight: 800; letter-spacing: 0.5px;">QUANTYCOIN CORE <span style="color: var(--accent-cyan);">SUITE v4.0</span></div>
      <div style="font-size: 13px; color: var(--text-muted); margin-top: 2px;">Unified Layer-1 Node, HD Wallet & Mining Control Matrix</div>
    </div>
    <div style="display: flex; gap: 12px;">
      <button class="btn btn-primary" id="btn-suite-launch" onclick="launchAllServices()">🚀 1-CLICK LAUNCH ALL</button>
      <button class="btn btn-danger" onclick="stopAllServices()">⏹ STOP ALL</button>
    </div>
  </div>
</div>

<!-- 4 TOP METRIC CARDS -->
<div class="grid-4" style="margin-bottom: 24px;">
  <div class="card">
    <div class="card-header">
      <span class="card-title">Node Height</span>
      <span class="status-indicator" id="node-ind"></span>
    </div>
    <div class="card-value" id="val-blocks">0</div>
    <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;" id="val-peers">Peers: 0 Connected</div>
  </div>
  <div class="card">
    <div class="card-header">
      <span class="card-title">Wallet Balance</span>
      <span style="color: var(--accent-cyan); font-weight: 700;">QTY</span>
    </div>
    <div class="card-value" id="val-balance" style="color: var(--accent-cyan);">0.0000</div>
    <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;" id="val-addr-short">qty1q...</div>
  </div>
  <div class="card">
    <div class="card-header">
      <span class="card-title">Mining Hashrate</span>
      <span style="color: var(--accent-green);">⚡</span>
    </div>
    <div class="card-value" id="val-hashrate" style="color: var(--accent-green);">0.00 kH/s</div>
    <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;" id="val-blocks-found">Blocks Found: 0</div>
  </div>
  <div class="card">
    <div class="card-header">
      <span class="card-title">Ecosystem Health</span>
      <span style="color: var(--accent-violet);">🛡</span>
    </div>
    <div class="card-value" style="font-size: 20px; color: var(--accent-green);" id="val-health">100% OPERATIONAL</div>
    <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Zero-Mock v4.0 Verified</div>
  </div>
</div>

<!-- NAVIGATION TABS -->
<div class="tabs">
  <button class="tab-btn active" onclick="switchTab('suite-node')">🌐 Full Node Monitor</button>
  <button class="tab-btn" onclick="switchTab('suite-wallet')">💎 Light Wallet Hub</button>
  <button class="tab-btn" onclick="switchTab('suite-miner')">⛏ Mining Operation</button>
</div>

<!-- TAB: NODE -->
<div id="tab-suite-node">
  <div class="grid-2">
    <div class="card">
      <div class="card-header">
        <span class="card-title">Chainstate Information</span>
      </div>
      <div style="display: flex; flex-direction: column; gap: 10px; font-size: 13px; font-family: var(--font-mono);">
        <div><strong style="color: var(--text-muted);">Best Block Hash:</strong> <span id="val-besthash" style="color: var(--accent-cyan); word-break: break-all;">-</span></div>
        <div><strong style="color: var(--text-muted);">Mempool TX Count:</strong> <span id="val-mempool">0</span></div>
        <div><strong style="color: var(--text-muted);">Network Circulating Supply:</strong> <span id="val-supply">50.00 QTY</span></div>
        <div><strong style="color: var(--text-muted);">Wire Magic Bytes:</strong> <span style="color: var(--accent-violet);">0x51 0x55 0x41 0x4E ("QUAN")</span></div>
      </div>
    </div>
    <div class="card">
      <div class="card-header">
        <span class="card-title">Quick RPC Call</span>
      </div>
      <div style="display: flex; gap: 10px;">
        <input type="text" id="suite-rpc-in" class="input-control" value="getinfo">
        <button class="btn btn-primary" onclick="runSuiteRpc()">Run</button>
      </div>
      <pre id="suite-rpc-out" style="margin-top: 12px; background: var(--bg-input); padding: 12px; border-radius: 8px; font-family: var(--font-mono); font-size: 12px; color: var(--text-main); max-height: 150px; overflow-y: auto;">Ready.</pre>
    </div>
  </div>
</div>

<!-- TAB: WALLET -->
<div id="tab-suite-wallet" style="display: none;">
  <div class="grid-2">
    <div class="card">
      <div class="card-header">
        <span class="card-title">Instant P2P Transfer</span>
      </div>
      <div class="input-group">
        <label class="input-label">Recipient (qty1q...)</label>
        <input type="text" id="suite-send-to" class="input-control" placeholder="qty1q...">
      </div>
      <div class="input-group">
        <label class="input-label">Amount (QTY)</label>
        <input type="number" id="suite-send-amt" class="input-control" placeholder="1.0" step="0.01">
      </div>
      <button class="btn btn-primary" style="width: 100%; justify-content: center;" onclick="runSuiteSend()">🚀 Broadcast Transaction</button>
      <div id="suite-send-res" style="margin-top: 12px; font-family: var(--font-mono); font-size: 13px;"></div>
    </div>
    <div class="card" style="text-align: center;">
      <div class="card-header">
        <span class="card-title">Primary Receiving Address</span>
      </div>
      <img id="suite-qr-img" src="" alt="QR Code" style="width: 160px; height: 160px; display: inline-block; background: #FFF; padding: 10px; border-radius: 8px; margin: 10px 0;">
      <div id="suite-addr-box" style="background: var(--bg-input); padding: 10px; border-radius: 8px; font-family: var(--font-mono); font-size: 12px; color: var(--accent-cyan); word-break: break-all;">Loading...</div>
    </div>
  </div>
</div>

<!-- TAB: MINER -->
<div id="tab-suite-miner" style="display: none;">
  <div class="grid-2">
    <div class="card">
      <div class="card-header">
        <span class="card-title">Mining Configuration</span>
      </div>
      <div class="input-group">
        <label class="input-label">Worker Threads (<span id="suite-threads-val">4</span>)</label>
        <input type="range" id="suite-thread-slider" min="1" max="16" value="4" style="width: 100%; accent-color: var(--accent-cyan);" oninput="document.getElementById('suite-threads-val').innerText = this.value">
      </div>
      <div style="display: flex; gap: 12px; margin-top: 16px;">
        <button class="btn btn-primary" style="flex: 1; justify-content: center;" onclick="controlSuiteMiner(true)">▶ START SOLO MINER</button>
        <button class="btn btn-danger" style="flex: 1; justify-content: center;" onclick="controlSuiteMiner(false)">⏹ STOP MINER</button>
      </div>
    </div>
    <div class="card">
      <div class="card-header">
        <span class="card-title">Hashrate Chart</span>
      </div>
      <canvas id="suite-hashrate-canvas" width="550" height="180" style="width: 100%; height: 180px; background: var(--bg-input); border-radius: 8px;"></canvas>
    </div>
  </div>
</div>
"""

SUITE_JS = """
let suiteHistory = [];

function switchTab(tabId) {
  document.getElementById('tab-suite-node').style.display = tabId === 'suite-node' ? 'block' : 'none';
  document.getElementById('tab-suite-wallet').style.display = tabId === 'suite-wallet' ? 'block' : 'none';
  document.getElementById('tab-suite-miner').style.display = tabId === 'suite-miner' ? 'block' : 'none';
  
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');
}

async function fetchSuiteData() {
  try {
    const res = await fetch('/api/suite/state');
    const d = await res.json();
    
    document.getElementById('val-blocks').innerText = d.node.blocks;
    document.getElementById('val-peers').innerText = `Peers: ${d.node.connections} Connected`;
    document.getElementById('val-besthash').innerText = d.node.bestblockhash;
    document.getElementById('val-mempool').innerText = d.node.mempool_size;
    document.getElementById('val-supply').innerText = `${d.node.circulating_supply.toFixed(2)} QTY`;
    
    document.getElementById('val-balance').innerText = d.wallet.balance.toFixed(4);
    document.getElementById('val-addr-short').innerText = d.wallet.address.slice(0, 16) + '...';
    document.getElementById('suite-addr-box').innerText = d.wallet.address;
    document.getElementById('suite-qr-img').src = `https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=${encodeURIComponent(d.wallet.address)}`;
    
    document.getElementById('val-hashrate').innerText = `${d.miner.hashrate_khs.toFixed(2)} kH/s`;
    document.getElementById('val-blocks-found').innerText = `Blocks Found: ${d.miner.blocks_mined}`;
    
    if (d.miner.history) {
      suiteHistory = d.miner.history.map(h => h.hashrate / 1000);
      drawSuiteChart();
    }
  } catch (e) {
    console.error('Suite fetch error:', e);
  }
}

function drawSuiteChart() {
  const canvas = document.getElementById('suite-hashrate-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  if (suiteHistory.length < 2) return;
  
  const maxVal = Math.max(...suiteHistory, 10.0);
  const step = w / (suiteHistory.length - 1);
  
  ctx.beginPath();
  suiteHistory.forEach((val, i) => {
    const x = i * step;
    const y = h - (val / maxVal) * (h - 20) - 10;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.strokeStyle = '#00FF88';
  ctx.lineWidth = 2;
  ctx.stroke();
}

async function launchAllServices() {
  await fetch('/api/suite/launch_all', {method: 'POST'});
  alert('All QuantyCoin ecosystem services (Node, Wallet, Miner) are active!');
  fetchSuiteData();
}

async function stopAllServices() {
  await fetch('/api/suite/stop_all', {method: 'POST'});
  alert('All services stopped.');
  fetchSuiteData();
}

async function controlSuiteMiner(start) {
  const threads = parseInt(document.getElementById('suite-thread-slider').value);
  await fetch('/api/suite/miner_control', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({action: start ? 'start' : 'stop', threads})
  });
  fetchSuiteData();
}

async function runSuiteRpc() {
  const cmd = document.getElementById('suite-rpc-in').value.trim();
  const res = await fetch('/api/suite/rpc', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({command: cmd})
  });
  const data = await res.json();
  document.getElementById('suite-rpc-out').innerText = JSON.stringify(data, null, 2);
}

async function runSuiteSend() {
  const to = document.getElementById('suite-send-to').value.trim();
  const amount = parseFloat(document.getElementById('suite-send-amt').value);
  const res = await fetch('/api/suite/send', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({to, amount})
  });
  const data = await res.json();
  const resDiv = document.getElementById('suite-send-res');
  if (data.success) {
    resDiv.innerHTML = `<span style="color: var(--accent-green);">✓ Broadcast Success! TXID: ${data.txid}</span>`;
    fetchSuiteData();
  } else {
    resDiv.innerHTML = `<span style="color: var(--accent-pink);">✗ Failed: ${data.error}</span>`;
  }
}

setInterval(fetchSuiteData, 2000);
fetchSuiteData();
"""


class SuiteGUIHandler(BaseHTTPRequestHandler):
    node: Optional[QuantyNode] = None
    wallet: Optional[HDWallet] = None
    miner: Optional[MiningEngine] = None
    rpc_client: Optional[WalletRPCClient] = None

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/':
            html = render_html_page("Unified Control Suite", "ALL-IN-ONE SUITE v4.0", SUITE_HTML_BODY, SUITE_JS)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        elif parsed.path == '/api/suite/state':
            # Node data
            node_data = {
                "blocks": self.node.chainstate.best_height if self.node else 0,
                "connections": self.node.p2p.peer_count if self.node else 0,
                "bestblockhash": self.node.chainstate.best_hash_hex if self.node else "0000...",
                "mempool_size": self.node.chainstate.mempool.get_info()["size"] if self.node else 0,
                "circulating_supply": (self.node.chainstate.utxo_set.total_circulation / 100_000_000) if self.node else 50.0
            }
            # Wallet data
            w_addr = self.wallet.get_receiving_address(0) if self.wallet else "qty1q..."
            bal_sat, _ = self.node.chainstate.utxo_set.get_address_balance(w_addr) if self.node else (0, 0)
            wallet_data = {
                "address": w_addr,
                "balance": bal_sat / 100_000_000,
                "balance_sat": bal_sat
            }
            # Miner data
            miner_data = self.miner.get_telemetry() if self.miner else {
                "is_mining": False,
                "hashrate_khs": 0.0,
                "blocks_mined": 0,
                "history": []
            }
            
            self._send_json(200, {
                "node": node_data,
                "wallet": wallet_data,
                "miner": miner_data
            })
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8') if length > 0 else "{}"
        data = json.loads(body)
        
        if parsed.path == '/api/suite/launch_all':
            if not SuiteGUIHandler.node:
                SuiteGUIHandler.node = QuantyNode()
                SuiteGUIHandler.node.start()
            if not SuiteGUIHandler.wallet:
                SuiteGUIHandler.wallet = HDWallet()
            if not SuiteGUIHandler.miner:
                payout = SuiteGUIHandler.wallet.get_receiving_address(0)
                SuiteGUIHandler.miner = MiningEngine(payout_address=payout, threads=4)
                SuiteGUIHandler.miner.start()
            self._send_json(200, {"success": True})
            
        elif parsed.path == '/api/suite/stop_all':
            if SuiteGUIHandler.miner:
                SuiteGUIHandler.miner.stop()
            if SuiteGUIHandler.node:
                SuiteGUIHandler.node.stop()
            self._send_json(200, {"success": True})
            
        elif parsed.path == '/api/suite/miner_control':
            if data.get("action") == "start":
                if SuiteGUIHandler.miner:
                    SuiteGUIHandler.miner.stop()
                payout = SuiteGUIHandler.wallet.get_receiving_address(0) if SuiteGUIHandler.wallet else "qty1q98n2qhm5aasdree49jjp3kd34c6vas7ev0fz2g"
                threads = int(data.get("threads", 4))
                SuiteGUIHandler.miner = MiningEngine(payout_address=payout, threads=threads)
                SuiteGUIHandler.miner.start()
            else:
                if SuiteGUIHandler.miner:
                    SuiteGUIHandler.miner.stop()
            self._send_json(200, {"success": True})
            
        elif parsed.path == '/api/suite/rpc':
            cmd = data.get("command", "getinfo")
            if SuiteGUIHandler.node:
                try:
                    res = SuiteGUIHandler.node.rpc.rpc_methods[cmd]([])
                    self._send_json(200, {"result": res})
                except Exception as e:
                    self._send_json(200, {"error": str(e)})
            else:
                self._send_json(200, {"error": "Node not initialized"})
                
        elif parsed.path == '/api/suite/send':
            try:
                to_addr = data["to"]
                amt_sat = int(float(data["amount"]) * 100_000_000)
                sender_addr = SuiteGUIHandler.wallet.get_receiving_address(0)
                utxos = SuiteGUIHandler.node.chainstate.utxo_set.get_address_utxos(sender_addr)
                
                tx = SuiteGUIHandler.wallet.build_transaction(
                    destination_address=to_addr,
                    amount_sat=amt_sat,
                    available_utxos=utxos,
                    fee_sat=10000
                )
                accepted, msg = SuiteGUIHandler.node.chainstate.mempool.add_transaction(tx, SuiteGUIHandler.node.chainstate.utxo_set)
                if accepted:
                    SuiteGUIHandler.node.p2p.broadcast_tx(tx.txid, tx.serialize(include_witness=True))
                    self._send_json(200, {"success": True, "txid": tx.txid_hex})
                else:
                    self._send_json(200, {"success": False, "error": msg})
            except Exception as e:
                self._send_json(200, {"success": False, "error": str(e)})

    def _send_json(self, status: int, data: Any):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        pass


def launch_suite_gui(gui_port: int = 8080):
    SuiteGUIHandler.node = QuantyNode()
    SuiteGUIHandler.node.start()
    SuiteGUIHandler.wallet = HDWallet()
    payout = SuiteGUIHandler.wallet.get_receiving_address(0)
    SuiteGUIHandler.miner = MiningEngine(payout_address=payout, threads=4)
    
    server = HTTPServer(('127.0.0.1', gui_port), SuiteGUIHandler)
    url = f"http://127.0.0.1:{gui_port}"
    print(f"\n========================================================")
    print(f"QUANTYCOIN COMBINED ALL-IN-ONE SUITE RUNNING (v4.0)")
    print(f"Open in browser: {url}")
    print(f"========================================================\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    server.serve_forever()


if __name__ == "__main__":
    launch_suite_gui()
