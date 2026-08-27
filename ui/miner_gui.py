"""
QuantyCoin Standalone Miner GUI (Cyberpunk Dark Mode v4.0)
Real-Time Hashrate Canvas Graph, Worker Telemetry, Solo & Stratum Pool Mining Controls
"""

import sys
import os
import json
import webbrowser
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

from miner.engine import MiningEngine
from miner.stratum import StratumServer

MINER_HTML_BODY = """
<div class="grid-4" style="margin-bottom: 24px;">
  <div class="card">
    <div class="card-header">
      <span class="card-title">Live Hashrate</span>
      <span style="color: var(--accent-cyan);">⚡</span>
    </div>
    <div class="card-value" id="val-hashrate" style="color: var(--accent-cyan);">0.00 kH/s</div>
    <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;" id="val-hashrate-hs">0 H/s</div>
  </div>
  <div class="card">
    <div class="card-header">
      <span class="card-title">Blocks Mined</span>
      <span style="color: var(--accent-green);">🏆</span>
    </div>
    <div class="card-value" id="val-blocks-mined" style="color: var(--accent-green);">0</div>
    <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Solo Rewards Solved</div>
  </div>
  <div class="card">
    <div class="card-header">
      <span class="card-title">Total Hashes</span>
      <span style="color: var(--accent-violet);">#</span>
    </div>
    <div class="card-value" id="val-total-hashes">0</div>
    <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Computed Nonces</div>
  </div>
  <div class="card">
    <div class="card-header">
      <span class="card-title">Mining Status</span>
      <span class="status-indicator" id="status-ind" style="background: #94A3B8; box-shadow: none;"></span>
    </div>
    <div class="card-value" id="val-status-text" style="font-size: 20px; color: var(--text-muted);">STANDBY</div>
    <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;" id="val-threads-count">Threads: 4</div>
  </div>
</div>

<div class="grid-2" style="margin-bottom: 24px;">
  <!-- CONTROL PANEL -->
  <div class="card">
    <div class="card-header">
      <span class="card-title">Miner Configuration & Control</span>
    </div>
    <div class="input-group">
      <label class="input-label">Coinbase Payout Address (qty1q...)</label>
      <input type="text" id="miner-payout-addr" class="input-control" value="qty1q98n2qhm5aasdree49jjp3kd34c6vas7ev0fz2g">
    </div>
    <div class="grid-2">
      <div class="input-group">
        <label class="input-label">CPU Worker Threads (<span id="thread-val">4</span>)</label>
        <input type="range" id="thread-slider" min="1" max="16" value="4" style="width: 100%; accent-color: var(--accent-cyan);" oninput="document.getElementById('thread-val').innerText = this.value">
      </div>
      <div class="input-group">
        <label class="input-label">Mining Protocol</label>
        <select id="mining-mode-select" class="input-control">
          <option value="solo">Solo Mining (Direct RPC)</option>
          <option value="stratum">Stratum Pool (Port 3333)</option>
        </select>
      </div>
    </div>
    <div style="display: flex; gap: 12px; margin-top: 10px;">
      <button class="btn btn-primary" id="btn-start-miner" style="flex: 1; justify-content: center;" onclick="toggleMining(true)">▶ START MINING</button>
      <button class="btn btn-danger" id="btn-stop-miner" style="flex: 1; justify-content: center;" onclick="toggleMining(false)">⏹ STOP MINING</button>
    </div>
  </div>

  <!-- REAL-TIME GRAPH -->
  <div class="card">
    <div class="card-header">
      <span class="card-title">Real-Time Hashrate Dynamics (kH/s)</span>
      <span class="brand-badge">LIVE 1s</span>
    </div>
    <canvas id="hashrate-canvas" width="550" height="200" style="width: 100%; height: 200px; background: var(--bg-input); border-radius: 8px;"></canvas>
  </div>
</div>
"""

MINER_JS = """
let isMining = false;
let hashrateHistory = [];

async function toggleMining(start) {
  const address = document.getElementById('miner-payout-addr').value.trim();
  const threads = parseInt(document.getElementById('thread-slider').value);
  const mode = document.getElementById('mining-mode-select').value;
  
  if (start && !address) {
    alert('Please specify a payout address');
    return;
  }
  
  try {
    const res = await fetch('/api/miner/control', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({action: start ? 'start' : 'stop', address, threads, mode})
    });
    const data = await res.json();
    fetchMinerTelemetry();
  } catch (e) {
    alert('Miner control error: ' + e);
  }
}

async function fetchMinerTelemetry() {
  try {
    const res = await fetch('/api/miner/telemetry');
    const data = await res.json();
    isMining = data.is_mining;
    
    document.getElementById('val-hashrate').innerText = data.hashrate_khs.toFixed(2) + ' kH/s';
    document.getElementById('val-hashrate-hs').innerText = data.hashrate_hs.toLocaleString() + ' H/s';
    document.getElementById('val-blocks-mined').innerText = data.blocks_mined;
    document.getElementById('val-total-hashes').innerText = data.total_hashes.toLocaleString();
    document.getElementById('val-threads-count').innerText = `Threads: ${data.threads}`;
    
    const statusInd = document.getElementById('status-ind');
    const statusText = document.getElementById('val-status-text');
    
    if (data.is_mining) {
      statusInd.style.background = 'var(--accent-green)';
      statusInd.style.boxShadow = '0 0 10px var(--accent-green)';
      statusText.innerText = 'MINING ACTIVE';
      statusText.style.color = 'var(--accent-green)';
    } else {
      statusInd.style.background = '#94A3B8';
      statusInd.style.boxShadow = 'none';
      statusText.innerText = 'STANDBY';
      statusText.style.color = 'var(--text-muted)';
    }
    
    if (data.history) {
      hashrateHistory = data.history.map(h => h.hashrate / 1000);
      drawHashrateChart();
    }
  } catch (e) {
    console.error('Telemetry fetch error:', e);
  }
}

function drawHashrateChart() {
  const canvas = document.getElementById('hashrate-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  
  ctx.clearRect(0, 0, w, h);
  
  // Grid lines
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
  ctx.lineWidth = 1;
  for (let y = 0; y < h; y += 40) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }
  
  if (hashrateHistory.length < 2) return;
  
  const maxVal = Math.max(...hashrateHistory, 10.0);
  const step = w / (hashrateHistory.length - 1);
  
  // Gradient fill
  const grad = ctx.createLinearGradient(0, 0, 0, h);
  grad.addColorStop(0, 'rgba(0, 240, 255, 0.3)');
  grad.addColorStop(1, 'rgba(0, 240, 255, 0.0)');
  
  ctx.beginPath();
  ctx.moveTo(0, h);
  hashrateHistory.forEach((val, i) => {
    const x = i * step;
    const y = h - (val / maxVal) * (h - 20) - 10;
    ctx.lineTo(x, y);
  });
  ctx.lineTo(w, h);
  ctx.fillStyle = grad;
  ctx.fill();
  
  // Line stroke
  ctx.beginPath();
  hashrateHistory.forEach((val, i) => {
    const x = i * step;
    const y = h - (val / maxVal) * (h - 20) - 10;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.strokeStyle = '#00F0FF';
  ctx.lineWidth = 2;
  ctx.stroke();
}

setInterval(fetchMinerTelemetry, 1000);
fetchMinerTelemetry();
"""


class MinerGUIHandler(BaseHTTPRequestHandler):
    engine: Optional[MiningEngine] = None
    stratum: Optional[StratumServer] = None
    rpc_port: int = 19889

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/':
            html = render_html_page("Standalone Miner Suite", "MINER SUITE v4.0", MINER_HTML_BODY, MINER_JS)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        elif parsed.path == '/api/miner/telemetry':
            if self.engine:
                self._send_json(200, self.engine.get_telemetry())
            else:
                self._send_json(200, {
                    "is_mining": False,
                    "threads": 4,
                    "hashrate_hs": 0,
                    "hashrate_khs": 0,
                    "total_hashes": 0,
                    "blocks_mined": 0,
                    "history": []
                })
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/miner/control':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode('utf-8'))
            action = data.get("action")
            
            if action == 'start':
                addr = data.get("address")
                threads = int(data.get("threads", 4))
                mode = data.get("mode", "solo")
                
                if self.engine:
                    self.engine.stop()
                    
                MinerGUIHandler.engine = MiningEngine(payout_address=addr, rpc_port=self.rpc_port, threads=threads)
                MinerGUIHandler.engine.start()
                
                if mode == "stratum" and not MinerGUIHandler.stratum:
                    MinerGUIHandler.stratum = StratumServer()
                    MinerGUIHandler.stratum.start()
                    
                self._send_json(200, {"success": True, "status": "started"})
            elif action == 'stop':
                if MinerGUIHandler.engine:
                    MinerGUIHandler.engine.stop()
                if MinerGUIHandler.stratum:
                    MinerGUIHandler.stratum.stop()
                self._send_json(200, {"success": True, "status": "stopped"})

    def _send_json(self, status: int, data: Any):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        pass


def launch_miner_gui(gui_port: int = 8083, rpc_port: int = 19889):
    MinerGUIHandler.rpc_port = rpc_port
    server = HTTPServer(('127.0.0.1', gui_port), MinerGUIHandler)
    url = f"http://127.0.0.1:{gui_port}"
    print(f"\n========================================================")
    print(f"QUANTYCOIN STANDALONE MINER GUI RUNNING (v4.0)")
    print(f"Open in browser: {url}")
    print(f"========================================================\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    server.serve_forever()


if __name__ == "__main__":
    launch_miner_gui()
