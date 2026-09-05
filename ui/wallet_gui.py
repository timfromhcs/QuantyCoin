"""
QuantyCoin Standalone Light Wallet GUI (Cyberpunk Dark Mode v4.0)
Remote-RPC Sync, BIP39 24-Word Recovery, QR Code Send/Receive & Multi-Account Manager
"""

import sys
import os
import json
import webbrowser
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

from wallet.hd_wallet import HDWallet
from wallet.rpc_client import WalletRPCClient

WALLET_HTML_BODY = """
<div class="tabs">
  <button class="tab-btn active" onclick="switchTab('overview')">💎 Balance & Overview</button>
  <button class="tab-btn" onclick="switchTab('send')">🚀 Send QTY</button>
  <button class="tab-btn" onclick="switchTab('receive')">📥 Receive & QR Code</button>
  <button class="tab-btn" onclick="switchTab('vault')">🔐 BIP39 Seed Vault</button>
</div>

<!-- TAB 1: OVERVIEW -->
<div id="tab-overview">
  <div class="grid-3" style="margin-bottom: 24px;">
    <div class="card">
      <div class="card-header">
        <span class="card-title">Available Balance</span>
        <span style="color: var(--accent-cyan); font-weight: 700;">QTY</span>
      </div>
      <div class="card-value" id="val-balance" style="color: var(--accent-cyan);">0.00000000</div>
      <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;" id="val-satoshis">0 Satoshis</div>
    </div>
    <div class="card">
      <div class="card-header">
        <span class="card-title">Primary Address</span>
        <button class="btn" style="padding: 2px 8px; font-size: 11px;" onclick="copyPrimaryAddress()">Copy</button>
      </div>
      <div id="val-primary-addr" style="font-family: var(--font-mono); font-size: 12px; color: var(--text-main); word-break: break-all;">Loading...</div>
      <div style="font-size: 12px; color: var(--text-muted); margin-top: 6px;">Derivation: m/44'/999'/0'/0/0</div>
    </div>
    <div class="card">
      <div class="card-header">
        <span class="card-title">Connected RPC Node</span>
        <span class="status-indicator"></span>
      </div>
      <div class="card-value" style="font-size: 20px;" id="val-node-status">127.0.0.1:19889</div>
      <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Remote SPV Sync Mode</div>
    </div>
  </div>

  <div class="card">
    <div class="card-header">
      <span class="card-title">Recent Wallet Activity & UTXOs</span>
      <button class="btn" onclick="fetchWalletData()">🔄 Refresh</button>
    </div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Outpoint (TXID : VOUT)</th>
            <th>Value (QTY)</th>
            <th>Block Height</th>
            <th>Type</th>
          </tr>
        </thead>
        <tbody id="utxo-table-body">
          <tr><td colspan="4" style="text-align: center; color: var(--text-muted);">No unspent outputs found for this address.</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<!-- TAB 2: SEND -->
<div id="tab-send" style="display: none;">
  <div class="card" style="max-width: 650px; margin: 0 auto;">
    <div class="card-header">
      <span class="card-title">Transfer QuantyCoin (Instant P2P Broadcast)</span>
    </div>
    <div class="input-group">
      <label class="input-label">Recipient Destination Address</label>
      <input type="text" id="send-to-addr" class="input-control" placeholder="qty1q... or quan1q...">
    </div>
    <div class="grid-2">
      <div class="input-group">
        <label class="input-label">Amount (QTY)</label>
        <input type="number" id="send-amount" class="input-control" placeholder="0.00" step="0.0001">
      </div>
      <div class="input-group">
        <label class="input-label">Network Fee (QTY)</label>
        <input type="number" id="send-fee" class="input-control" value="0.0001" step="0.0001">
      </div>
    </div>
    <button class="btn btn-primary" style="width: 100%; justify-content: center; margin-top: 10px;" onclick="executeSend()">🚀 Sign & Broadcast Transaction</button>
    <div id="send-status-msg" style="margin-top: 16px; font-family: var(--font-mono); font-size: 13px;"></div>
  </div>
</div>

<!-- TAB 3: RECEIVE & QR -->
<div id="tab-receive" style="display: none;">
  <div class="card" style="max-width: 550px; margin: 0 auto; text-align: center;">
    <div class="card-header">
      <span class="card-title">Your QuantyCoin Receiving Address</span>
    </div>
    <div style="background: #FFF; padding: 20px; display: inline-block; border-radius: 12px; margin: 16px 0;" id="qr-container">
      <img id="qr-img" src="" alt="QR Code" style="width: 200px; height: 200px; display: block;">
    </div>
    <div style="background: var(--bg-input); padding: 12px; border-radius: 8px; font-family: var(--font-mono); font-size: 13px; color: var(--accent-cyan); word-break: break-all; margin-bottom: 16px;" id="receive-addr-display">
      Loading...
    </div>
    <button class="btn btn-primary" onclick="copyPrimaryAddress()">📋 Copy Address to Clipboard</button>
  </div>
</div>

<!-- TAB 4: BIP39 VAULT -->
<div id="tab-vault" style="display: none;">
  <div class="grid-2">
    <div class="card">
      <div class="card-header">
        <span class="card-title">Generate New BIP39 Wallet</span>
      </div>
      <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px;">Create a brand new 24-word cryptographic seed phrase with master private keys.</p>
      <button class="btn btn-primary" onclick="generateNewSeed()">✨ Generate Fresh 24-Word Seed</button>
      <pre id="new-seed-display" style="margin-top: 16px; background: var(--bg-input); padding: 12px; border-radius: 8px; font-family: var(--font-mono); font-size: 13px; color: var(--accent-green); white-space: pre-wrap; display: none;"></pre>
    </div>

    <div class="card">
      <div class="card-header">
        <span class="card-title">Restore Existing Wallet</span>
      </div>
      <div class="input-group">
        <label class="input-label">Enter 24-Word Recovery Phrase</label>
        <textarea id="restore-seed-input" class="input-control" rows="3" placeholder="word1 word2 word3 ... word24"></textarea>
      </div>
      <button class="btn btn-violet" onclick="restoreFromSeed()">🔑 Restore Wallet</button>
    </div>
  </div>
</div>
"""

WALLET_JS = """
let currentWallet = null;

function switchTab(tabId) {
  document.getElementById('tab-overview').style.display = tabId === 'overview' ? 'block' : 'none';
  document.getElementById('tab-send').style.display = tabId === 'send' ? 'block' : 'none';
  document.getElementById('tab-receive').style.display = tabId === 'receive' ? 'block' : 'none';
  document.getElementById('tab-vault').style.display = tabId === 'vault' ? 'block' : 'none';
  
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');
}

async function fetchWalletData() {
  try {
    const res = await fetch('/api/wallet/info');
    const data = await res.json();
    currentWallet = data;
    
    document.getElementById('val-balance').innerText = (data.balance || 0).toFixed(8);
    document.getElementById('val-satoshis').innerText = (data.balance_sat || 0).toLocaleString() + ' Satoshis';
    document.getElementById('val-primary-addr').innerText = data.address;
    document.getElementById('receive-addr-display').innerText = data.address;
    
    // QR Code
    document.getElementById('qr-img').src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(data.address)}`;
    
    const tbody = document.getElementById('utxo-table-body');
    if (data.utxos && data.utxos.length > 0) {
      tbody.innerHTML = data.utxos.map(u => `
        <tr>
          <td>${u.txid.slice(0, 16)}... : ${u.vout}</td>
          <td style="color: var(--accent-green); font-weight: 700;">+${u.value.toFixed(4)} QTY</td>
          <td>Block #${u.height}</td>
          <td><span class="brand-badge">${u.coinbase ? 'COINBASE REWARD' : 'STANDARD TX'}</span></td>
        </tr>
      `).join('');
    } else {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">No unspent outputs found for this address.</td></tr>`;
    }
  } catch (e) {
    console.error('Wallet fetch error:', e);
  }
}

function copyPrimaryAddress() {
  if (currentWallet && currentWallet.address) {
    navigator.clipboard.writeText(currentWallet.address);
    alert('Address copied to clipboard:\\n' + currentWallet.address);
  }
}

async function executeSend() {
  const to = document.getElementById('send-to-addr').value.trim();
  const amount = parseFloat(document.getElementById('send-amount').value);
  const fee = parseFloat(document.getElementById('send-fee').value);
  const statusDiv = document.getElementById('send-status-msg');
  
  if (!to || !amount || amount <= 0) {
    alert('Please enter a valid destination address and amount');
    return;
  }
  
  statusDiv.innerHTML = '<span style="color: var(--accent-cyan);">Signing & broadcasting transaction...</span>';
  
  try {
    const res = await fetch('/api/wallet/send', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({to, amount, fee})
    });
    const data = await res.json();
    if (data.success) {
      statusDiv.innerHTML = `<span style="color: var(--accent-green);">✓ Transaction Broadcast Success! TXID: ${data.txid}</span>`;
      fetchWalletData();
    } else {
      statusDiv.innerHTML = `<span style="color: var(--accent-pink);">✗ Transfer Failed: ${data.error}</span>`;
    }
  } catch (e) {
    statusDiv.innerHTML = `<span style="color: var(--accent-pink);">✗ RPC Error: ${e}</span>`;
  }
}

async function generateNewSeed() {
  try {
    const res = await fetch('/api/wallet/new_seed', {method: 'POST'});
    const data = await res.json();
    const display = document.getElementById('new-seed-display');
    display.style.display = 'block';
    display.innerText = `NEW 24-WORD RECOVERY SEED:\\n${data.mnemonic}\\n\\nPRIMARY ADDRESS: ${data.address}`;
    fetchWalletData();
  } catch (e) {
    alert('Error generating seed: ' + e);
  }
}

async function restoreFromSeed() {
  const mnemonic = document.getElementById('restore-seed-input').value.trim();
  if (!mnemonic) return;
  try {
    const res = await fetch('/api/wallet/restore', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({mnemonic})
    });
    const data = await res.json();
    if (data.success) {
      alert('Wallet successfully restored! Address: ' + data.address);
      fetchWalletData();
    } else {
      alert('Restore failed: ' + data.error);
    }
  } catch (e) {
    alert('Error: ' + e);
  }
}

setInterval(fetchWalletData, 3000);
fetchWalletData();
"""


class WalletGUIHandler(BaseHTTPRequestHandler):
    wallet: HDWallet
    rpc_client: WalletRPCClient

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/':
            html = render_html_page("Light Wallet Client", "LIGHT WALLET v4.0", WALLET_HTML_BODY, WALLET_JS)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        elif parsed.path == '/api/wallet/info':
            addr = self.wallet.get_receiving_address(0)
            try:
                bal = self.rpc_client.get_address_balance(addr)
                utxos = self.rpc_client.get_address_utxos(addr)
                self._send_json(200, {
                    "address": addr,
                    "balance": bal.get("balance", 0.0),
                    "balance_sat": bal.get("balance_sat", 0),
                    "utxos": utxos
                })
            except Exception:
                self._send_json(200, {"address": addr, "balance": 0.0, "balance_sat": 0, "utxos": []})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8') if length > 0 else "{}"
        data = json.loads(body)
        
        if parsed.path == '/api/wallet/send':
            try:
                to_addr = data["to"]
                amt_sat = int(float(data["amount"]) * 100_000_000)
                fee_sat = int(float(data.get("fee", 0.0001)) * 100_000_000)
                sender_addr = self.wallet.get_receiving_address(0)
                utxos = self.rpc_client.get_address_utxos(sender_addr)
                
                tx = self.wallet.build_transaction(
                    destination_address=to_addr,
                    amount_sat=amt_sat,
                    available_utxos=utxos,
                    fee_sat=fee_sat
                )
                raw_hex = tx.serialize(include_witness=True).hex()
                txid = self.rpc_client.send_raw_transaction(raw_hex)
                self._send_json(200, {"success": True, "txid": txid})
            except Exception as e:
                self._send_json(200, {"success": False, "error": str(e)})
                
        elif parsed.path == '/api/wallet/new_seed':
            WalletGUIHandler.wallet = HDWallet()
            self._send_json(200, {
                "mnemonic": WalletGUIHandler.wallet.mnemonic,
                "address": WalletGUIHandler.wallet.get_receiving_address(0)
            })
            
        elif parsed.path == '/api/wallet/restore':
            try:
                WalletGUIHandler.wallet = HDWallet(mnemonic=data["mnemonic"])
                self._send_json(200, {"success": True, "address": WalletGUIHandler.wallet.get_receiving_address(0)})
            except Exception as e:
                self._send_json(200, {"success": False, "error": str(e)})

    def _send_json(self, status: int, data: Any):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        pass


def launch_wallet_gui(gui_port: int = 8082, rpc_port: int = 19889):
    WalletGUIHandler.wallet = HDWallet()
    WalletGUIHandler.rpc_client = WalletRPCClient(rpc_port=rpc_port)
    server = HTTPServer(('127.0.0.1', gui_port), WalletGUIHandler)
    url = f"http://127.0.0.1:{gui_port}"
    print(f"\n========================================================")
    print(f"QUANTYCOIN STANDALONE LIGHT WALLET GUI RUNNING (v4.0)")
    print(f"Open in browser: {url}")
    print(f"========================================================\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    server.serve_forever()


if __name__ == "__main__":
    launch_wallet_gui()
