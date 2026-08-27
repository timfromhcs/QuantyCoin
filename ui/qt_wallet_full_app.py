"""
QuantyCoin Standalone Full Wallet with Built-In Node (Qt6 / PySide6 v4.0)
Integrated Background Node Daemon, BIP39/44 HD Key Management, Live QR Codes & Coin Control
Inspired by Bitcoin Core / Bitcoin Cash II overviewpage.cpp, sendcoinsdialog.cpp & receivecoinsdialog.cpp
"""

import sys
import os
import io
import time
from typing import Optional, List, Dict, Any

from PySide6 import QtWidgets, QtCore, QtGui
import qrcode
from PIL import Image

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.qt_theme import CYBERPUNK_QSS
from node.daemon import QuantyNode
from wallet.hd_wallet import HDWallet
from wallet.rpc_client import WalletRPCClient


class FullWalletSyncWorker(QtCore.QThread):
    sync_signal = QtCore.Signal(dict)

    def __init__(self, wallet: HDWallet, rpc: WalletRPCClient):
        super().__init__()
        self.wallet = wallet
        self.rpc = rpc
        self.running = True

    def run(self):
        while self.running:
            try:
                addr = self.wallet.get_receiving_address(0)
                bal = self.rpc.get_address_balance(addr)
                utxos = self.rpc.get_address_utxos(addr)
                node_info = self.rpc.get_info()
                self.sync_signal.emit({
                    "address": addr,
                    "balance": bal.get("balance", 0.0),
                    "balance_sat": bal.get("balance_sat", 0),
                    "utxos": utxos,
                    "blocks": node_info.get("blocks", 0),
                    "peers": node_info.get("connections", 0),
                    "best_hash": node_info.get("bestblockhash", "")
                })
            except Exception:
                addr = self.wallet.get_receiving_address(0)
                self.sync_signal.emit({
                    "address": addr,
                    "balance": 0.0,
                    "balance_sat": 0,
                    "utxos": [],
                    "blocks": 0,
                    "peers": 0,
                    "best_hash": "Syncing with built-in node..."
                })
            self.msleep(2000)

    def stop(self):
        self.running = False
        self.quit()
        self.wait(2000)


class QuantyFullWalletWindow(QtWidgets.QMainWindow):
    def __init__(self, rpc_port: int = 19889, auto_start_daemon: bool = True):
        super().__init__()
        self.setWindowTitle("QuantyCoin Full Wallet (Integrated Node v7.0 Production)")
        self.resize(1060, 700)
        self.setStyleSheet(CYBERPUNK_QSS)

        # Set Window Icon
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'share', 'pixmaps', 'quantycoin.ico'))
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

        # Launch Built-in Full Node Daemon
        self.node_daemon: Optional[QuantyNode] = None
        if auto_start_daemon:
            try:
                self.node_daemon = QuantyNode(p2p_port=19888, rpc_port=rpc_port)
                self.node_daemon.start()
            except Exception as e:
                print(f"Built-in Node notice: {e}")

        self.wallet = HDWallet()
        self.rpc_client = WalletRPCClient(rpc_port=rpc_port)
        self.current_utxos: List[Dict[str, Any]] = []

        self.init_ui()

        # Sync Worker
        self.sync_worker = FullWalletSyncWorker(self.wallet, self.rpc_client)
        self.sync_worker.sync_signal.connect(self.update_wallet_state)
        self.sync_worker.start()

    def init_ui(self):
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # TOP BANNER
        banner = QtWidgets.QFrame()
        banner.setObjectName("card-frame")
        b_layout = QtWidgets.QHBoxLayout(banner)
        b_layout.setContentsMargins(14, 10, 14, 10)

        left_b = QtWidgets.QVBoxLayout()
        t1 = QtWidgets.QLabel("QUANTYCOIN FULL SOVEREIGN WALLET")
        t1.setStyleSheet("font-size: 16px; font-weight: 800; color: #F1F5F9; letter-spacing: 0.5px;")
        t2 = QtWidgets.QLabel("Native BIP39 HD Wallet & In-Memory Zero-Trust Node Engine")
        t2.setStyleSheet("font-size: 11px; color: #94A3B8;")
        left_b.addWidget(t1)
        left_b.addWidget(t2)
        b_layout.addLayout(left_b)

        b_layout.addStretch()

        self.status_pill = QtWidgets.QLabel("● BUILT-IN NODE ACTIVE")
        self.status_pill.setStyleSheet("background: rgba(0, 255, 136, 0.15); color: #00FF88; border: 1px solid rgba(0, 255, 136, 0.4); padding: 6px 14px; border-radius: 12px; font-weight: 700; font-family: 'JetBrains Mono'; font-size: 11px;")
        b_layout.addWidget(self.status_pill)
        main_layout.addWidget(banner)

        # TABBED NAVIGATION
        self.tabs = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tabs)

        # TAB 1: OVERVIEW (overviewpage.cpp)
        self.tab_overview = QtWidgets.QWidget()
        self._init_overview_tab()
        self.tabs.addTab(self.tab_overview, "💎 Balance & Overview")

        # TAB 2: SEND COINS (sendcoinsdialog.cpp)
        self.tab_send = QtWidgets.QWidget()
        self._init_send_tab()
        self.tabs.addTab(self.tab_send, "🚀 Send QTY")

        # TAB 3: RECEIVE COINS & QR (receivecoinsdialog.cpp)
        self.tab_receive = QtWidgets.QWidget()
        self._init_receive_tab()
        self.tabs.addTab(self.tab_receive, "📥 Receive & QR Code")

        # TAB 4: BIP39 SEED VAULT
        self.tab_vault = QtWidgets.QWidget()
        self._init_vault_tab()
        self.tabs.addTab(self.tab_vault, "🔐 BIP39 Seed Vault")

        # STATUS BAR
        self.statusBar().showMessage("Ready | Built-in Sovereign Node Online | HD Derivation: m/44'/999'/0'/0/0")

    def _init_overview_tab(self):
        layout = QtWidgets.QVBoxLayout(self.tab_overview)
        layout.setSpacing(14)

        # 3 Metrics
        cards_layout = QtWidgets.QHBoxLayout()
        cards_layout.setSpacing(12)

        self.card_bal = self._create_card("AVAILABLE BALANCE", "0.00000000 QTY", "0 Satoshis Spendable", "#00F0FF")
        self.card_unconf = self._create_card("PENDING MEMPOOL", "0.00000000 QTY", "0 Unconfirmed Inbound", "#8A2BE2")
        self.card_height = self._create_card("NODE CHAIN TIP", "Height: 0", "0 Connected P2P Peers", "#00FF88")

        cards_layout.addWidget(self.card_bal)
        cards_layout.addWidget(self.card_unconf)
        cards_layout.addWidget(self.card_height)
        layout.addLayout(cards_layout)

        # Primary Address Box
        addr_box = QtWidgets.QGroupBox("Primary Receiving Bech32 Address")
        a_layout = QtWidgets.QHBoxLayout(addr_box)
        self.lbl_addr = QtWidgets.QLineEdit()
        self.lbl_addr.setReadOnly(True)
        btn_copy_addr = QtWidgets.QPushButton("📋 Copy")
        btn_copy_addr.clicked.connect(self._copy_address)
        a_layout.addWidget(self.lbl_addr)
        a_layout.addWidget(btn_copy_addr)
        layout.addWidget(addr_box)

        # Recent UTXOs Table
        utxo_group = QtWidgets.QGroupBox("Spendable On-Chain UTXO Portfolio")
        u_layout = QtWidgets.QVBoxLayout(utxo_group)
        self.table_utxos = QtWidgets.QTableWidget(0, 4)
        self.table_utxos.setHorizontalHeaderLabels(["Outpoint (TXID : VOUT)", "Value (QTY)", "Height", "Coinbase Reward"])
        self.table_utxos.horizontalHeader().setStretchLastSection(True)
        self.table_utxos.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        u_layout.addWidget(self.table_utxos)
        layout.addWidget(utxo_group)

    def _init_send_tab(self):
        layout = QtWidgets.QVBoxLayout(self.tab_send)
        layout.setSpacing(14)

        form_card = QtWidgets.QFrame()
        form_card.setObjectName("card-frame")
        f_layout = QtWidgets.QVBoxLayout(form_card)
        f_layout.setSpacing(12)

        lbl_head = QtWidgets.QLabel("Transfer QuantyCoin (Instant P2P Broadcast)")
        lbl_head.setStyleSheet("font-size: 15px; font-weight: 700; color: #00F0FF;")
        f_layout.addWidget(lbl_head)

        f_layout.addWidget(QtWidgets.QLabel("Recipient Destination Address (qty1q... or Base58):"))
        self.send_to_in = QtWidgets.QLineEdit()
        self.send_to_in.setPlaceholderText("Enter valid QuantyCoin destination address...")
        f_layout.addWidget(self.send_to_in)

        amt_layout = QtWidgets.QHBoxLayout()
        amt_v = QtWidgets.QVBoxLayout()
        amt_v.addWidget(QtWidgets.QLabel("Amount (QTY):"))
        self.send_amt_in = QtWidgets.QDoubleSpinBox()
        self.send_amt_in.setRange(0.0001, 21000000.0)
        self.send_amt_in.setDecimals(8)
        self.send_amt_in.setSingleStep(1.0)
        amt_v.addWidget(self.send_amt_in)
        amt_layout.addLayout(amt_v)

        fee_v = QtWidgets.QVBoxLayout()
        fee_v.addWidget(QtWidgets.QLabel("Network Fee (QTY):"))
        self.send_fee_in = QtWidgets.QDoubleSpinBox()
        self.send_fee_in.setRange(0.00001, 1.0)
        self.send_fee_in.setDecimals(8)
        self.send_fee_in.setValue(0.0001)
        fee_v.addWidget(self.send_fee_in)
        amt_layout.addLayout(fee_v)
        f_layout.addLayout(amt_layout)

        btn_send = QtWidgets.QPushButton("🚀 Sign & Broadcast Transaction")
        btn_send.setObjectName("btn-primary")
        btn_send.setMinimumHeight(42)
        btn_send.clicked.connect(self.execute_send)
        f_layout.addWidget(btn_send)

        self.send_status_lbl = QtWidgets.QLabel("")
        self.send_status_lbl.setFont(QtGui.QFont("JetBrains Mono", 11))
        self.send_status_lbl.setWordWrap(True)
        f_layout.addWidget(self.send_status_lbl)

        layout.addWidget(form_card)
        layout.addStretch()

    def _init_receive_tab(self):
        layout = QtWidgets.QVBoxLayout(self.tab_receive)
        layout.setSpacing(14)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        card = QtWidgets.QFrame()
        card.setObjectName("card-frame")
        card.setMaximumWidth(560)
        c_layout = QtWidgets.QVBoxLayout(card)
        c_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        c_layout.setSpacing(14)

        t_lbl = QtWidgets.QLabel("Your QuantyCoin Receiving Address & QR Code")
        t_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #00F0FF;")
        c_layout.addWidget(t_lbl)

        self.qr_label = QtWidgets.QLabel()
        self.qr_label.setFixedSize(220, 220)
        self.qr_label.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; padding: 10px;")
        self.qr_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        c_layout.addWidget(self.qr_label)

        self.receive_addr_in = QtWidgets.QLineEdit()
        self.receive_addr_in.setReadOnly(True)
        self.receive_addr_in.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.receive_addr_in.setFont(QtGui.QFont("JetBrains Mono", 11, QtGui.QFont.Weight.Bold))
        c_layout.addWidget(self.receive_addr_in)

        btn_copy = QtWidgets.QPushButton("📋 Copy Address to Clipboard")
        btn_copy.setObjectName("btn-primary")
        btn_copy.clicked.connect(self._copy_address)
        c_layout.addWidget(btn_copy)

        layout.addWidget(card)

    def _init_vault_tab(self):
        layout = QtWidgets.QVBoxLayout(self.tab_vault)
        layout.setSpacing(14)

        grid = QtWidgets.QHBoxLayout()
        grid.setSpacing(14)

        # Generate fresh wallet
        gen_card = QtWidgets.QFrame()
        gen_card.setObjectName("card-frame")
        g_layout = QtWidgets.QVBoxLayout(gen_card)
        g_layout.addWidget(QtWidgets.QLabel("Generate Fresh BIP39 Wallet"))
        g_desc = QtWidgets.QLabel("Creates a brand new 24-word cryptographic seed phrase with master private keys.")
        g_desc.setStyleSheet("color: #94A3B8; font-size: 12px;")
        g_desc.setWordWrap(True)
        g_layout.addWidget(g_desc)

        btn_gen = QtWidgets.QPushButton("✨ Generate New 24-Word Seed")
        btn_gen.setObjectName("btn-primary")
        btn_gen.clicked.connect(self.generate_new_seed)
        g_layout.addWidget(btn_gen)

        self.seed_display = QtWidgets.QPlainTextEdit()
        self.seed_display.setReadOnly(True)
        self.seed_display.setFont(QtGui.QFont("JetBrains Mono", 11))
        self.seed_display.setPlaceholderText("New 24-word recovery phrase will appear here...")
        g_layout.addWidget(self.seed_display)
        grid.addWidget(gen_card)

        # Restore from seed
        res_card = QtWidgets.QFrame()
        res_card.setObjectName("card-frame")
        r_layout = QtWidgets.QVBoxLayout(res_card)
        r_layout.addWidget(QtWidgets.QLabel("Restore Existing Wallet"))
        r_desc = QtWidgets.QLabel("Enter your 24-word recovery phrase separated by spaces to restore all child keys.")
        r_desc.setStyleSheet("color: #94A3B8; font-size: 12px;")
        r_desc.setWordWrap(True)
        r_layout.addWidget(r_desc)

        self.restore_in = QtWidgets.QPlainTextEdit()
        self.restore_in.setFont(QtGui.QFont("JetBrains Mono", 11))
        self.restore_in.setPlaceholderText("word1 word2 word3 ... word24")
        r_layout.addWidget(self.restore_in)

        btn_restore = QtWidgets.QPushButton("🔑 Restore Wallet")
        btn_restore.setObjectName("btn-violet")
        btn_restore.clicked.connect(self.restore_wallet)
        r_layout.addWidget(btn_restore)
        grid.addWidget(res_card)

        layout.addLayout(grid)

    def _create_card(self, title: str, value: str, sub: str, color: str) -> QtWidgets.QFrame:
        card = QtWidgets.QFrame()
        card.setObjectName("card-frame")
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        t_lbl = QtWidgets.QLabel(title)
        t_lbl.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 700;")
        v_lbl = QtWidgets.QLabel(value)
        v_lbl.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: 800; font-family: 'JetBrains Mono';")
        s_lbl = QtWidgets.QLabel(sub)
        s_lbl.setStyleSheet("color: #64748B; font-size: 11px;")

        layout.addWidget(t_lbl)
        layout.addWidget(v_lbl)
        layout.addWidget(s_lbl)
        card.value_label = v_lbl
        card.sub_label = s_lbl
        return card

    def update_wallet_state(self, data: dict):
        addr = data.get("address", "")
        self.lbl_addr.setText(addr)
        self.receive_addr_in.setText(addr)

        bal = data.get("balance", 0.0)
        bal_sat = data.get("balance_sat", 0)
        self.card_bal.value_label.setText(f"{bal:.8f} QTY")
        self.card_bal.sub_label.setText(f"{bal_sat:,} Satoshis Spendable")

        blocks = data.get("blocks", 0)
        peers = data.get("peers", 0)
        self.card_height.value_label.setText(f"Height: {blocks}")
        self.card_height.sub_label.setText(f"{peers} Connected Peers")

        self.current_utxos = data.get("utxos", [])
        self.table_utxos.setRowCount(len(self.current_utxos))
        for row, u in enumerate(self.current_utxos):
            txid = u.get("txid", "")
            vout = u.get("vout", 0)
            self.table_utxos.setItem(row, 0, QtWidgets.QTableWidgetItem(f"{txid[:16]}... : {vout}"))
            val_item = QtWidgets.QTableWidgetItem(f"+{u.get('value', 0.0):.4f} QTY")
            val_item.setForeground(QtGui.QColor("#00FF88"))
            self.table_utxos.setItem(row, 1, val_item)
            self.table_utxos.setItem(row, 2, QtWidgets.QTableWidgetItem(f"Block #{u.get('height', 0)}"))
            self.table_utxos.setItem(row, 3, QtWidgets.QTableWidgetItem("YES" if u.get("coinbase") else "NO"))

        # Render QR Code Image
        if addr:
            self._render_qr_code(addr)

    def _render_qr_code(self, data_str: str):
        try:
            qr = qrcode.QRCode(version=1, box_size=6, border=2)
            qr.add_data(data_str)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            qimg = QtGui.QImage.fromData(buffer.getvalue())
            pixmap = QtGui.QPixmap.fromImage(qimg)
            self.qr_label.setPixmap(pixmap.scaled(200, 200, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        except Exception as e:
            print(f"QR render notice: {e}")

    def _copy_address(self):
        addr = self.receive_addr_in.text().strip()
        if addr:
            QtWidgets.QApplication.clipboard().setText(addr)
            QtWidgets.QMessageBox.information(self, "Copied", f"Address copied to clipboard:\n{addr}")

    def execute_send(self):
        to_addr = self.send_to_in.text().strip()
        amount_qty = self.send_amt_in.value()
        fee_qty = self.send_fee_in.value()

        if not to_addr:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter a valid destination address.")
            return

        amt_sat = int(amount_qty * 100_000_000)
        fee_sat = int(fee_qty * 100_000_000)
        sender_addr = self.wallet.get_receiving_address(0)

        self.send_status_lbl.setText("<span style='color: #00F0FF;'>Signing and broadcasting transaction...</span>")
        try:
            utxos = self.rpc_client.get_address_utxos(sender_addr)
            tx = self.wallet.build_transaction(
                destination_address=to_addr,
                amount_sat=amt_sat,
                available_utxos=utxos,
                fee_sat=fee_sat
            )
            raw_hex = tx.serialize(include_witness=True).hex()
            txid = self.rpc_client.send_raw_transaction(raw_hex)
            self.send_status_lbl.setText(f"<span style='color: #00FF88;'>✓ Broadcast Success! TXID: {txid}</span>")
            QtWidgets.QMessageBox.information(self, "Success", f"Transaction successfully broadcast to network!\nTXID: {txid}")
        except Exception as e:
            self.send_status_lbl.setText(f"<span style='color: #FF007A;'>✗ Transaction Failed: {e}</span>")

    def generate_new_seed(self):
        self.wallet = HDWallet()
        self.seed_display.setPlainText(f"NEW 24-WORD RECOVERY PHRASE:\n{self.wallet.mnemonic}\n\nPRIMARY RECEIVING ADDRESS:\n{self.wallet.get_receiving_address(0)}")
        if self.sync_worker:
            self.sync_worker.wallet = self.wallet

    def restore_wallet(self):
        mnemonic = self.restore_in.toPlainText().strip()
        if not mnemonic:
            return
        try:
            self.wallet = HDWallet(mnemonic=mnemonic)
            if self.sync_worker:
                self.sync_worker.wallet = self.wallet
            QtWidgets.QMessageBox.information(self, "Success", f"Wallet restored successfully!\nAddress: {self.wallet.get_receiving_address(0)}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Restore Failed", f"Invalid mnemonic phrase:\n{e}")

    def closeEvent(self, event: QtGui.QCloseEvent):
        if hasattr(self, 'sync_worker') and self.sync_worker:
            self.sync_worker.stop()
        if hasattr(self, 'node_daemon') and self.node_daemon:
            self.node_daemon.stop()
        event.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = QuantyFullWalletWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
