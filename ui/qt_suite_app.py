"""
QuantyCoin Combined All-in-One Native Desktop Suite (Qt6 / PySide6 v4.0)
Unified Sovereign Wallet, Lightning SPV Wallet, Full Node Daemon & Mining Operations Center
"""

import sys
import os
from typing import Optional

from PySide6 import QtWidgets, QtCore, QtGui

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.qt_theme import CYBERPUNK_QSS
from ui.qt_node_app import QuantyNodeWindow
from ui.qt_wallet_full_app import QuantyFullWalletWindow
from ui.qt_lightning_wallet_app import QuantyLightningWalletWindow
from ui.qt_miner_app import QuantyMinerWindow
from node.daemon import QuantyNode
from wallet.hd_wallet import HDWallet
from miner.engine import MiningEngine


class QuantyMasterSuiteWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuantyCoin Master Suite (QTY2 / 2.0.0)")
        self.resize(1180, 760)
        self.setStyleSheet(CYBERPUNK_QSS)

        # Set Window Icon
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'share', 'pixmaps', 'quantycoin.ico'))
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

        # Shared Global Node Daemon
        self.global_node: Optional[QuantyNode] = None
        try:
            self.global_node = QuantyNode(p2p_port=19444, rpc_port=19445)
            self.global_node.start()
        except Exception as e:
            print(f"Master suite node notice: {e}")

        self.init_ui()

    def init_ui(self):
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        root_layout = QtWidgets.QHBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        # LEFT SIDEBAR
        sidebar = QtWidgets.QFrame()
        sidebar.setObjectName("card-frame")
        sidebar.setFixedWidth(220)
        sb_layout = QtWidgets.QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(10, 16, 10, 16)
        sb_layout.setSpacing(10)

        # Brand Header
        brand_box = QtWidgets.QHBoxLayout()
        logo_btn = QtWidgets.QLabel("Q")
        logo_btn.setFixedSize(36, 36)
        logo_btn.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        logo_btn.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00F0FF, stop:1 #8A2BE2); color: #000000; font-weight: 900; font-family: 'JetBrains Mono'; font-size: 20px; border-radius: 8px;")
        
        b_title = QtWidgets.QVBoxLayout()
        t1 = QtWidgets.QLabel("QUANTYCOIN")
        t1.setStyleSheet("font-weight: 800; font-size: 15px; color: #F1F5F9; letter-spacing: 0.5px;")
        t2 = QtWidgets.QLabel("SUITE v6.0")
        t2.setStyleSheet("font-weight: 700; font-size: 11px; color: #00F0FF; font-family: 'JetBrains Mono';")
        b_title.addWidget(t1)
        b_title.addWidget(t2)
        brand_box.addWidget(logo_btn)
        brand_box.addLayout(b_title)
        sb_layout.addLayout(brand_box)

        sb_layout.addSpacing(16)

        # Navigation Buttons
        self.btn_nav_wallet = QtWidgets.QPushButton("💎 Full Wallet (Node)")
        self.btn_nav_wallet.setCheckable(True)
        self.btn_nav_wallet.setChecked(True)
        self.btn_nav_wallet.clicked.connect(lambda: self.switch_view(0))

        self.btn_nav_lightning = QtWidgets.QPushButton("⚡ Lightning Wallet")
        self.btn_nav_lightning.setCheckable(True)
        self.btn_nav_lightning.clicked.connect(lambda: self.switch_view(1))

        self.btn_nav_node = QtWidgets.QPushButton("🌐 Full Node Daemon")
        self.btn_nav_node.setCheckable(True)
        self.btn_nav_node.clicked.connect(lambda: self.switch_view(2))

        self.btn_nav_miner = QtWidgets.QPushButton("⛏ Mining Operation")
        self.btn_nav_miner.setCheckable(True)
        self.btn_nav_miner.clicked.connect(lambda: self.switch_view(3))

        sb_layout.addWidget(self.btn_nav_wallet)
        sb_layout.addWidget(self.btn_nav_lightning)
        sb_layout.addWidget(self.btn_nav_node)
        sb_layout.addWidget(self.btn_nav_miner)

        sb_layout.addStretch()

        # Global Control Box
        ctrl_box = QtWidgets.QGroupBox("Global Control")
        c_layout = QtWidgets.QVBoxLayout(ctrl_box)
        c_layout.setSpacing(8)

        btn_launch_all = QtWidgets.QPushButton("🚀 1-Click Launch")
        btn_launch_all.setObjectName("btn-primary")
        btn_launch_all.clicked.connect(self.launch_all)
        c_layout.addWidget(btn_launch_all)

        btn_stop_all = QtWidgets.QPushButton("⏹ Stop All")
        btn_stop_all.setObjectName("btn-danger")
        btn_stop_all.clicked.connect(self.stop_all)
        c_layout.addWidget(btn_stop_all)

        sb_layout.addWidget(ctrl_box)
        root_layout.addWidget(sidebar)

        # MAIN CONTENT STACK
        self.stack = QtWidgets.QStackedWidget()
        root_layout.addWidget(self.stack, 1)

        # Instantiate the 4 Sub-Apps (without creating separate OS windows)
        self.app_wallet = QuantyFullWalletWindow(auto_start_daemon=False)
        self.app_lightning = QuantyLightningWalletWindow()
        self.app_node = QuantyNodeWindow(auto_start_daemon=False)
        self.app_miner = QuantyMinerWindow()

        self.stack.addWidget(self.app_wallet.centralWidget())
        self.stack.addWidget(self.app_lightning.centralWidget())
        self.stack.addWidget(self.app_node.centralWidget())
        self.stack.addWidget(self.app_miner.centralWidget())

        self.statusBar().showMessage("QuantyCoin Unified Cyberpunk Suite v6.0 Active | All Systems Synchronized")

    def switch_view(self, index: int):
        self.stack.setCurrentIndex(index)
        self.btn_nav_wallet.setChecked(index == 0)
        self.btn_nav_lightning.setChecked(index == 1)
        self.btn_nav_node.setChecked(index == 2)
        self.btn_nav_miner.setChecked(index == 3)

    def launch_all(self):
        if not self.global_node:
            self.global_node = QuantyNode(p2p_port=19444, rpc_port=19445)
            self.global_node.start()
        self.app_miner.start_mining()
        QtWidgets.QMessageBox.information(self, "Launched", "All QuantyCoin ecosystem services (Node, Wallets, Miner) are active!")

    def stop_all(self):
        self.app_miner.stop_mining()
        if self.global_node:
            self.global_node.stop()
        QtWidgets.QMessageBox.information(self, "Stopped", "All active services halted.")

    def closeEvent(self, event: QtGui.QCloseEvent):
        if hasattr(self, 'app_miner') and self.app_miner:
            self.app_miner.stop_mining()
            if hasattr(self.app_miner, 'telemetry_worker') and self.app_miner.telemetry_worker:
                self.app_miner.telemetry_worker.stop()
        if hasattr(self, 'app_wallet') and self.app_wallet and hasattr(self.app_wallet, 'sync_worker') and self.app_wallet.sync_worker:
            self.app_wallet.sync_worker.stop()
        if hasattr(self, 'app_lightning') and self.app_lightning and hasattr(self.app_lightning, 'sync_worker') and self.app_lightning.sync_worker:
            self.app_lightning.sync_worker.stop()
        if hasattr(self, 'app_node') and self.app_node and hasattr(self.app_node, 'worker') and self.app_node.worker:
            self.app_node.worker.stop()
        if hasattr(self, 'global_node') and self.global_node:
            self.global_node.stop()
        event.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = QuantyMasterSuiteWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
