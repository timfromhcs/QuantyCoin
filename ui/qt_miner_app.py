"""
QuantyCoin Standalone Miner Native GUI (Qt6 / PySide6 v4.0)
Real-Time Dynamic Hashrate Graph, Multi-Threaded Parallel Workers, Solo Mining & Stratum Pool Server
"""

import sys
import os
import time
from typing import Optional, List, Dict, Any

from PySide6 import QtWidgets, QtCore, QtGui

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.qt_theme import CYBERPUNK_QSS
from ui.qt_traffic_graph import RealTimeGraphWidget
from miner.engine import MiningEngine
from miner.stratum import StratumServer


class MinerTelemetryWorker(QtCore.QThread):
    telemetry_signal = QtCore.Signal(dict)

    def __init__(self, miner_app):
        super().__init__()
        self.miner_app = miner_app
        self.running = True

    def run(self):
        while self.running:
            if self.miner_app.engine:
                data = self.miner_app.engine.get_telemetry()
            else:
                data = {
                    "is_mining": False,
                    "threads": 4,
                    "hashrate_hs": 0,
                    "hashrate_khs": 0.0,
                    "total_hashes": 0,
                    "blocks_mined": 0,
                    "history": []
                }
            self.telemetry_signal.emit(data)
            self.msleep(1000)

    def stop(self):
        self.running = False
        self.quit()
        self.wait(2000)


class QuantyMinerWindow(QtWidgets.QMainWindow):
    def __init__(self, rpc_port: int = 19889):
        super().__init__()
        self.setWindowTitle("QuantyCoin Multi-Threaded Miner (v7.0 Production)")
        self.resize(1000, 660)
        self.setStyleSheet(CYBERPUNK_QSS)

        # Set Window Icon
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'share', 'pixmaps', 'quantycoin.ico'))
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

        self.rpc_port = rpc_port
        self.engine: Optional[MiningEngine] = None
        self.stratum: Optional[StratumServer] = None

        self.init_ui()

        # Telemetry Worker Thread
        self.telemetry_worker = MinerTelemetryWorker(self)
        self.telemetry_worker.telemetry_signal.connect(self.update_telemetry)
        self.telemetry_worker.start()

    def init_ui(self):
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # TOP 4 METRIC CARDS
        metrics_layout = QtWidgets.QHBoxLayout()
        metrics_layout.setSpacing(12)

        self.card_hashrate = self._create_card("LIVE HASHRATE", "0.00 kH/s", "0 H/s", "#00F0FF")
        self.card_blocks = self._create_card("BLOCKS MINED", "0", "Solo Solutions Found", "#00FF88")
        self.card_hashes = self._create_card("COMPUTED NONCES", "0", "Total Hashes", "#8A2BE2")
        self.card_status = self._create_card("MINER STATE", "STANDBY", "Worker Threads: 4", "#FF007A")

        metrics_layout.addWidget(self.card_hashrate)
        metrics_layout.addWidget(self.card_blocks)
        metrics_layout.addWidget(self.card_hashes)
        metrics_layout.addWidget(self.card_status)
        main_layout.addLayout(metrics_layout)

        # REAL-TIME DYNAMIC GRAPH
        self.graph = RealTimeGraphWidget(self, title="Real-Time Hashrate Dynamics", unit="kH/s", color="#00F0FF")
        main_layout.addWidget(self.graph)

        # CONTROL PANEL CARD
        control_card = QtWidgets.QFrame()
        control_card.setObjectName("card-frame")
        c_layout = QtWidgets.QVBoxLayout(control_card)
        c_layout.setSpacing(12)

        lbl_head = QtWidgets.QLabel("Mining Engine Configuration & Hardware Controls")
        lbl_head.setStyleSheet("font-size: 14px; font-weight: 700; color: #00F0FF;")
        c_layout.addWidget(lbl_head)

        c_layout.addWidget(QtWidgets.QLabel("Coinbase Payout Address (qty1q...):"))
        self.payout_in = QtWidgets.QLineEdit("qty1q98n2qhm5aasdree49jjp3kd34c6vas7ev0fz2g")
        c_layout.addWidget(self.payout_in)

        mid_layout = QtWidgets.QHBoxLayout()
        # Thread Slider
        th_box = QtWidgets.QVBoxLayout()
        self.lbl_threads = QtWidgets.QLabel("Worker Threads: 4")
        self.slider_threads = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider_threads.setRange(1, 32)
        self.slider_threads.setValue(4)
        self.slider_threads.valueChanged.connect(self._on_thread_slider_changed)
        th_box.addWidget(self.lbl_threads)
        th_box.addWidget(self.slider_threads)
        mid_layout.addLayout(th_box, 2)

        # Protocol Mode
        mode_box = QtWidgets.QVBoxLayout()
        mode_box.addWidget(QtWidgets.QLabel("Mining Protocol:"))
        self.mode_combo = QtWidgets.QComboBox()
        self.mode_combo.addItems(["Solo Mining (Direct RPC)", "Stratum Pool Mode (Port 3333)"])
        mode_box.addWidget(self.mode_combo)
        mid_layout.addLayout(mode_box, 2)
        c_layout.addLayout(mid_layout)

        # Action Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_start = QtWidgets.QPushButton("▶ START MINING")
        self.btn_start.setObjectName("btn-primary")
        self.btn_start.setMinimumHeight(42)
        self.btn_start.clicked.connect(self.start_mining)

        self.btn_stop = QtWidgets.QPushButton("⏹ STOP MINING")
        self.btn_stop.setObjectName("btn-danger")
        self.btn_stop.setMinimumHeight(42)
        self.btn_stop.clicked.connect(self.stop_mining)

        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        c_layout.addLayout(btn_layout)

        main_layout.addWidget(control_card)

        # HARDWARE TELEMETRY CONSOLE
        self.console = QtWidgets.QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(110)
        self.console.setFont(QtGui.QFont("JetBrains Mono", 10))
        self.console.appendPlainText("QuantyCoin Mining Engine Initialized. Configure threads and payout address above.")
        main_layout.addWidget(self.console)

        self.statusBar().showMessage("Solo / Stratum Miner v4.0 Active | Algorithm: SHA-256 (ASIC / Multi-Threaded)")

    def _create_card(self, title: str, val: str, sub: str, color: str) -> QtWidgets.QFrame:
        card = QtWidgets.QFrame()
        card.setObjectName("card-frame")
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        t_lbl = QtWidgets.QLabel(title)
        t_lbl.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 700;")
        v_lbl = QtWidgets.QLabel(val)
        v_lbl.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 800; font-family: 'JetBrains Mono';")
        s_lbl = QtWidgets.QLabel(sub)
        s_lbl.setStyleSheet("color: #64748B; font-size: 11px;")

        layout.addWidget(t_lbl)
        layout.addWidget(v_lbl)
        layout.addWidget(s_lbl)
        card.value_label = v_lbl
        card.sub_label = s_lbl
        return card

    def _on_thread_slider_changed(self, val: int):
        self.lbl_threads.setText(f"Worker Threads: {val}")

    def update_telemetry(self, data: dict):
        khs = data.get("hashrate_khs", 0.0)
        hs = data.get("hashrate_hs", 0)
        self.card_hashrate.value_label.setText(f"{khs:.2f} kH/s")
        self.card_hashrate.sub_label.setText(f"{hs:,} H/s")

        self.graph.add_sample(khs)

        blocks = data.get("blocks_mined", 0)
        self.card_blocks.value_label.setText(str(blocks))

        hashes = data.get("total_hashes", 0)
        self.card_hashes.value_label.setText(f"{hashes:,}")

        is_m = data.get("is_mining", False)
        th = data.get("threads", 4)
        if is_m:
            self.card_status.value_label.setText("MINING ACTIVE")
            self.card_status.value_label.setStyleSheet("color: #00FF88; font-size: 18px; font-weight: 800; font-family: 'JetBrains Mono';")
            self.card_status.sub_label.setText(f"{th} Active Workers")
        else:
            self.card_status.value_label.setText("STANDBY")
            self.card_status.value_label.setStyleSheet("color: #94A3B8; font-size: 18px; font-weight: 800; font-family: 'JetBrains Mono';")
            self.card_status.sub_label.setText(f"{th} Standby Workers")

    def start_mining(self):
        payout = self.payout_in.text().strip()
        threads = self.slider_threads.value()
        mode = "stratum" if "Stratum" in self.mode_combo.currentText() else "solo"

        if not payout:
            QtWidgets.QMessageBox.warning(self, "Payout Error", "Please provide a valid Coinbase payout address.")
            return

        if self.engine:
            self.engine.stop()

        self.engine = MiningEngine(payout_address=payout, rpc_port=self.rpc_port, threads=threads)
        self.engine.start()

        if mode == "stratum" and not self.stratum:
            self.stratum = StratumServer(port=3333, rpc_port=self.rpc_port)
            self.stratum.start()
            self.console.appendPlainText(f"[{time.strftime('%H:%M:%S')}] Stratum V1/V2 pool server listening on port 3333.")

        self.console.appendPlainText(f"[{time.strftime('%H:%M:%S')}] Started {threads} parallel worker threads for address: {payout}")

    def stop_mining(self):
        if self.engine:
            self.engine.stop()
        if self.stratum:
            self.stratum.stop()
        self.console.appendPlainText(f"[{time.strftime('%H:%M:%S')}] Mining workers halted.")

    def closeEvent(self, event: QtGui.QCloseEvent):
        if hasattr(self, 'telemetry_worker') and self.telemetry_worker:
            self.telemetry_worker.stop()
        self.stop_mining()
        event.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = QuantyMinerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
