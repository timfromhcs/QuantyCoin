"""
QuantyCoin Standalone Full Node Native GUI (Qt6 / PySide6 v4.0)
Live P2P Telemetry, Interactive RPC Console, Network Graph & On-Chain Block Explorer
Inspired by Bitcoin Cash II / Bitcoin Core rpcconsole.cpp & peertablemodel.cpp
"""

import sys
import os
import json
from typing import Optional, List, Dict, Any

from PySide6 import QtWidgets, QtCore, QtGui

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.qt_theme import CYBERPUNK_QSS
from ui.qt_traffic_graph import RealTimeGraphWidget
from node.daemon import QuantyNode
from wallet.rpc_client import WalletRPCClient


class NodeRPCWorker(QtCore.QThread):
    telemetry_signal = QtCore.Signal(dict)

    def __init__(self, rpc_client: WalletRPCClient):
        super().__init__()
        self.rpc = rpc_client
        self.running = True

    def run(self):
        while self.running:
            try:
                info = self.rpc.get_info()
                try:
                    peers = self.rpc._call("getpeerinfo", [])
                    info["peers"] = peers
                except Exception:
                    info["peers"] = []
                self.telemetry_signal.emit(info)
            except Exception:
                self.telemetry_signal.emit({
                    "blocks": 0,
                    "connections": 0,
                    "bestblockhash": "Connecting to node...",
                    "mempool_size": 0,
                    "circulating_supply": 50.0,
                    "peers": []
                })
            self.msleep(1500)

    def stop(self):
        self.running = False
        self.quit()
        self.wait(2000)


class QuantyNodeWindow(QtWidgets.QMainWindow):
    def __init__(self, rpc_port: int = 19889, auto_start_daemon: bool = True):
        super().__init__()
        self.setWindowTitle("QuantyCoin Full Node (QTY2 / 2.0.0)")
        self.resize(1020, 680)
        self.setStyleSheet(CYBERPUNK_QSS)

        # Set Window Icon
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'share', 'pixmaps', 'quantycoin.ico'))
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

        self.daemon: Optional[QuantyNode] = None
        if auto_start_daemon:
            try:
                self.daemon = QuantyNode(p2p_port=19888, rpc_port=rpc_port)
                self.daemon.start()
            except Exception as e:
                print(f"Node startup warning: {e}")

        self.rpc_client = WalletRPCClient(rpc_port=rpc_port)
        self.init_ui()

        # Telemetry Worker Thread
        self.worker = NodeRPCWorker(self.rpc_client)
        self.worker.telemetry_signal.connect(self.update_telemetry)
        self.worker.start()

    def init_ui(self):
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # TOP RIBBON: 4 Key Metric Cards
        metrics_layout = QtWidgets.QHBoxLayout()
        metrics_layout.setSpacing(12)

        self.card_blocks = self._create_card("BLOCK HEIGHT", "0", "Synced Chain Tip", "#00F0FF")
        self.card_peers = self._create_card("ACTIVE PEERS", "0", "P2P Links", "#00FF88")
        self.card_mempool = self._create_card("MEMPOOL", "0 TXs", "Unconfirmed Queue", "#8A2BE2")
        self.card_supply = self._create_card("CIRCULATION", "50.00 QTY", "Total Mined Supply", "#FF007A")

        metrics_layout.addWidget(self.card_blocks)
        metrics_layout.addWidget(self.card_peers)
        metrics_layout.addWidget(self.card_mempool)
        metrics_layout.addWidget(self.card_supply)
        main_layout.addLayout(metrics_layout)

        # TABBED SECTIONS
        self.tabs = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tabs)

        # TAB 1: P2P Network Telemetry & Peers
        tab_p2p = QtWidgets.QWidget()
        p2p_layout = QtWidgets.QVBoxLayout(tab_p2p)
        p2p_layout.setSpacing(10)

        # Real-time traffic graph
        self.traffic_graph = RealTimeGraphWidget(self, title="Network Mempool Dynamics", unit="TXs", color="#00F0FF")
        p2p_layout.addWidget(self.traffic_graph)

        # Peer Table
        self.peer_table = QtWidgets.QTableWidget(0, 4)
        self.peer_table.setHorizontalHeaderLabels(["Peer Address", "Direction", "Protocol SubVer", "Ping Latency"])
        self.peer_table.horizontalHeader().setStretchLastSection(True)
        self.peer_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        p2p_layout.addWidget(self.peer_table)
        self.tabs.addTab(tab_p2p, "🌐 P2P Network & Peers")

        # TAB 2: On-Chain Block Explorer
        tab_explorer = QtWidgets.QWidget()
        exp_layout = QtWidgets.QVBoxLayout(tab_explorer)
        exp_layout.setSpacing(10)

        search_bar = QtWidgets.QHBoxLayout()
        self.search_in = QtWidgets.QLineEdit()
        self.search_in.setPlaceholderText("Search by Block Height, Block Hash (0000...), Transaction ID (TXID) or Address (qty1q...)")
        btn_search = QtWidgets.QPushButton("🔍 Search Chain")
        btn_search.setObjectName("btn-primary")
        btn_search.clicked.connect(self.execute_search)
        search_bar.addWidget(self.search_in)
        search_bar.addWidget(btn_search)
        exp_layout.addLayout(search_bar)

        self.explorer_view = QtWidgets.QTextEdit()
        self.explorer_view.setReadOnly(True)
        self.explorer_view.setFont(QtGui.QFont("JetBrains Mono", 11))
        self.explorer_view.setPlaceholderText("Search query results will be formatted here in real-time...")
        exp_layout.addWidget(self.explorer_view)
        self.tabs.addTab(tab_explorer, "🔍 Block Explorer")

        # TAB 3: Interactive RPC Terminal (rpcconsole.cpp)
        tab_rpc = QtWidgets.QWidget()
        rpc_layout = QtWidgets.QVBoxLayout(tab_rpc)
        rpc_layout.setSpacing(10)

        rpc_bar = QtWidgets.QHBoxLayout()
        self.rpc_combo = QtWidgets.QComboBox()
        self.rpc_combo.addItems(["Quick Commands...", "getinfo", "getblockchaininfo", "getblockcount", "getmempoolinfo", "getpeerinfo", "getmininginfo"])
        self.rpc_combo.currentTextChanged.connect(self._on_rpc_combo_changed)

        self.rpc_in = QtWidgets.QLineEdit()
        self.rpc_in.setPlaceholderText("Enter command [e.g. getblockcount or getblock 0] and press Enter...")
        self.rpc_in.returnPressed.connect(self.execute_rpc)

        btn_rpc_exec = QtWidgets.QPushButton("⚡ Execute")
        btn_rpc_exec.setObjectName("btn-violet")
        btn_rpc_exec.clicked.connect(self.execute_rpc)

        rpc_bar.addWidget(self.rpc_combo, 1)
        rpc_bar.addWidget(self.rpc_in, 3)
        rpc_bar.addWidget(btn_rpc_exec, 1)
        rpc_layout.addLayout(rpc_bar)

        self.rpc_terminal = QtWidgets.QPlainTextEdit()
        self.rpc_terminal.setReadOnly(True)
        self.rpc_terminal.setFont(QtGui.QFont("JetBrains Mono", 11))
        self.rpc_terminal.appendPlainText("========================================================================\nQUANTYCOIN JSON-RPC 2.0 INTERACTIVE TERMINAL READY (v4.0)\nType a command above and click Execute or press Enter.\n========================================================================\n")
        rpc_layout.addWidget(self.rpc_terminal)
        self.tabs.addTab(tab_rpc, "⚡ RPC Console")

        # STATUS BAR
        self.statusBar().showMessage("QuantyCoin Node Mainnet v4.0 Active | P2P: 19888 | RPC: 19889")

    def _create_card(self, title: str, value: str, sub: str, color: str) -> QtWidgets.QFrame:
        card = QtWidgets.QFrame()
        card.setObjectName("card-frame")
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        t_lbl = QtWidgets.QLabel(title)
        t_lbl.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 700;")
        v_lbl = QtWidgets.QLabel(value)
        v_lbl.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 800; font-family: 'JetBrains Mono';")
        s_lbl = QtWidgets.QLabel(sub)
        s_lbl.setStyleSheet("color: #64748B; font-size: 11px;")

        layout.addWidget(t_lbl)
        layout.addWidget(v_lbl)
        layout.addWidget(s_lbl)
        card.value_label = v_lbl
        return card

    def update_telemetry(self, data: dict):
        self.card_blocks.value_label.setText(str(data.get("blocks", 0)))
        self.card_peers.value_label.setText(str(data.get("connections", 0)))
        m_size = data.get("mempool_size", 0)
        self.card_mempool.value_label.setText(f"{m_size} TXs")
        self.traffic_graph.add_sample(float(m_size))

        supply = data.get("circulating_supply", 50.0)
        self.card_supply.value_label.setText(f"{supply:.2f} QTY")

        # Update peers table
        peers = data.get("peers", [])
        self.peer_table.setRowCount(len(peers))
        for row, p in enumerate(peers):
            self.peer_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(p.get("addr", ""))))
            self.peer_table.setItem(row, 1, QtWidgets.QTableWidgetItem("INBOUND" if p.get("inbound") else "OUTBOUND"))
            self.peer_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(p.get("subver", "QuantyWire"))))
            self.peer_table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{p.get('pingtime', 0)} ms"))

    def _on_rpc_combo_changed(self, text: str):
        if text and not text.startswith("Quick"):
            self.rpc_in.setText(text)

    def execute_rpc(self):
        raw = self.rpc_in.text().strip()
        if not raw:
            return
        parts = raw.split()
        method = parts[0]
        params = parts[1:]
        converted_params = []
        for p in params:
            if p.isdigit():
                converted_params.append(int(p))
            else:
                converted_params.append(p)

        self.rpc_terminal.appendPlainText(f"\n> {raw}")
        try:
            res = self.rpc_client._call(method, converted_params)
            self.rpc_terminal.appendPlainText(json.dumps(res, indent=2))
        except Exception as e:
            self.rpc_terminal.appendPlainText(f"[ERROR] {e}")

    def execute_search(self):
        query = self.search_in.text().strip()
        if not query:
            return
        try:
            if query.isdigit():
                hash_hex = self.rpc_client._call("getblockhash", [int(query)])
                res = self.rpc_client._call("getblock", [hash_hex])
            elif query.startswith("qty1") or query.startswith("quan1"):
                res = self.rpc_client.get_address_balance(query)
                res["spendable_utxos"] = self.rpc_client.get_address_utxos(query)
            elif len(query) == 64:
                try:
                    res = self.rpc_client._call("getblock", [query])
                except Exception:
                    res = self.rpc_client._call("getrawtransaction", [query])
            else:
                res = {"error": "Invalid search query. Enter block height, 64-char hash, or valid address."}
            self.explorer_view.setText(json.dumps(res, indent=2))
        except Exception as e:
            self.explorer_view.setText(f"Search Failed:\n{e}")

    def closeEvent(self, event: QtGui.QCloseEvent):
        if hasattr(self, 'worker') and self.worker:
            self.worker.stop()
        if hasattr(self, 'daemon') and self.daemon:
            self.daemon.stop()
        event.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = QuantyNodeWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
