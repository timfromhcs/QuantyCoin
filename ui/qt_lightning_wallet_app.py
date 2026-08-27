"""
QuantyCoin Standalone Lightning / Light Wallet Client (Qt6 / PySide6 v4.0)
Remote-SPV Sync (No Local Node Requirement), Instant Startup, Lightning Fast Transfers & QR Codes
"""

import sys
import os
import io
from typing import Optional, List, Dict, Any

from PySide6 import QtWidgets, QtCore, QtGui
import qrcode

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.qt_theme import CYBERPUNK_QSS
from wallet.hd_wallet import HDWallet
from wallet.rpc_client import WalletRPCClient


class LightningSyncWorker(QtCore.QThread):
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
                self.sync_signal.emit({
                    "connected": True,
                    "address": addr,
                    "balance": bal.get("balance", 0.0),
                    "balance_sat": bal.get("balance_sat", 0),
                    "utxos": utxos
                })
            except Exception:
                addr = self.wallet.get_receiving_address(0)
                self.sync_signal.emit({
                    "connected": False,
                    "address": addr,
                    "balance": 0.0,
                    "balance_sat": 0,
                    "utxos": []
                })
            self.msleep(2500)

    def stop(self):
        self.running = False
        self.quit()
        self.wait(2000)


class QuantyLightningWalletWindow(QtWidgets.QMainWindow):
    def __init__(self, remote_rpc_port: int = 19889):
        super().__init__()
        self.setWindowTitle("QuantyCoin Lightning Light Wallet (Remote SPV v7.0 Production)")
        self.resize(980, 640)
        self.setStyleSheet(CYBERPUNK_QSS)

        # Set Window Icon
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'share', 'pixmaps', 'quantycoin.ico'))
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

        self.wallet = HDWallet()
        self.rpc_client = WalletRPCClient(rpc_port=remote_rpc_port)
        self.init_ui()

        # Remote Sync Worker
        self.sync_worker = LightningSyncWorker(self.wallet, self.rpc_client)
        self.sync_worker.sync_signal.connect(self.update_state)
        self.sync_worker.start()

    def init_ui(self):
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # HEADER RIBBON
        header = QtWidgets.QFrame()
        header.setObjectName("card-frame")
        h_layout = QtWidgets.QHBoxLayout(header)
        h_layout.setContentsMargins(12, 10, 12, 10)

        left = QtWidgets.QVBoxLayout()
        t1 = QtWidgets.QLabel("⚡ QUANTYCOIN LIGHTNING LIGHT WALLET")
        t1.setStyleSheet("font-size: 16px; font-weight: 800; color: #00F0FF;")
        t2 = QtWidgets.QLabel("Ultra-Lightweight SPV Client (Instant Payments, Zero Local Blockchain Storage)")
        t2.setStyleSheet("font-size: 11px; color: #94A3B8;")
        left.addWidget(t1)
        left.addWidget(t2)
        h_layout.addLayout(left)

        h_layout.addStretch()
        self.conn_pill = QtWidgets.QLabel("● REMOTE SPV SYNC")
        self.conn_pill.setStyleSheet("background: rgba(0, 240, 255, 0.15); color: #00F0FF; border: 1px solid rgba(0, 240, 255, 0.4); padding: 6px 14px; border-radius: 12px; font-weight: 700; font-family: 'JetBrains Mono'; font-size: 11px;")
        h_layout.addWidget(self.conn_pill)
        main_layout.addWidget(header)

        # TABBED NAVIGATION
        self.tabs = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tabs)

        # TAB 1: OVERVIEW & BALANCE
        tab_over = QtWidgets.QWidget()
        o_layout = QtWidgets.QVBoxLayout(tab_over)
        o_layout.setSpacing(14)

        metrics = QtWidgets.QHBoxLayout()
        self.card_bal = self._create_card("TOTAL BALANCE", "0.00000000 QTY", "0 Satoshis Available", "#00F0FF")
        self.card_status = self._create_card("NODE SYNC MODE", "Remote SPV Node", "Port 19889", "#00FF88")
        metrics.addWidget(self.card_bal)
        metrics.addWidget(self.card_status)
        o_layout.addLayout(metrics)

        # Quick Actions
        actions = QtWidgets.QHBoxLayout()
        btn_go_send = QtWidgets.QPushButton("🚀 Fast Send QTY")
        btn_go_send.setObjectName("btn-primary")
        btn_go_send.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        btn_go_recv = QtWidgets.QPushButton("📥 Request / Receive QTY")
        btn_go_recv.setObjectName("btn-violet")
        btn_go_recv.clicked.connect(lambda: self.tabs.setCurrentIndex(2))
        actions.addWidget(btn_go_send)
        actions.addWidget(btn_go_recv)
        o_layout.addLayout(actions)

        # Spendable UTXOs
        u_box = QtWidgets.QGroupBox("Live Spendable UTXOs")
        u_layout = QtWidgets.QVBoxLayout(u_box)
        self.utxo_table = QtWidgets.QTableWidget(0, 3)
        self.utxo_table.setHorizontalHeaderLabels(["TXID : VOUT", "Amount (QTY)", "Height"])
        self.utxo_table.horizontalHeader().setStretchLastSection(True)
        self.utxo_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        u_layout.addWidget(self.utxo_table)
        o_layout.addWidget(u_box)
        self.tabs.addTab(tab_over, "💎 Wallet Balance")

        # TAB 2: FAST SEND
        tab_send = QtWidgets.QWidget()
        s_layout = QtWidgets.QVBoxLayout(tab_send)
        s_card = QtWidgets.QFrame()
        s_card.setObjectName("card-frame")
        sc_layout = QtWidgets.QVBoxLayout(s_card)
        sc_layout.setSpacing(12)

        sc_layout.addWidget(QtWidgets.QLabel("Recipient Destination Address (qty1q...):"))
        self.send_addr_in = QtWidgets.QLineEdit()
        self.send_addr_in.setPlaceholderText("Enter QuantyCoin address...")
        sc_layout.addWidget(self.send_addr_in)

        amt_h = QtWidgets.QHBoxLayout()
        v1 = QtWidgets.QVBoxLayout()
        v1.addWidget(QtWidgets.QLabel("Amount (QTY):"))
        self.send_amt_spin = QtWidgets.QDoubleSpinBox()
        self.send_amt_spin.setRange(0.0001, 21000000.0)
        self.send_amt_spin.setDecimals(8)
        v1.addWidget(self.send_amt_spin)
        amt_h.addLayout(v1)

        v2 = QtWidgets.QVBoxLayout()
        v2.addWidget(QtWidgets.QLabel("Fee (QTY):"))
        self.send_fee_spin = QtWidgets.QDoubleSpinBox()
        self.send_fee_spin.setRange(0.00001, 0.5)
        self.send_fee_spin.setValue(0.0001)
        self.send_fee_spin.setDecimals(8)
        v2.addWidget(self.send_fee_spin)
        amt_h.addLayout(v2)
        sc_layout.addLayout(amt_h)

        btn_broadcast = QtWidgets.QPushButton("⚡ Broadcast Instant Transaction")
        btn_broadcast.setObjectName("btn-primary")
        btn_broadcast.setMinimumHeight(40)
        btn_broadcast.clicked.connect(self.execute_fast_send)
        sc_layout.addWidget(btn_broadcast)

        self.send_status = QtWidgets.QLabel("")
        self.send_status.setFont(QtGui.QFont("JetBrains Mono", 11))
        sc_layout.addWidget(self.send_status)

        s_layout.addWidget(s_card)
        s_layout.addStretch()
        self.tabs.addTab(tab_send, "🚀 Fast Send")

        # TAB 3: RECEIVE & QR
        tab_recv = QtWidgets.QWidget()
        r_layout = QtWidgets.QVBoxLayout(tab_recv)
        r_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        r_card = QtWidgets.QFrame()
        r_card.setObjectName("card-frame")
        r_card.setMaximumWidth(520)
        rc_layout = QtWidgets.QVBoxLayout(r_card)
        rc_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        rc_layout.setSpacing(12)

        rc_layout.addWidget(QtWidgets.QLabel("Receive QuantyCoin Instant Payment"))
        self.qr_label = QtWidgets.QLabel()
        self.qr_label.setFixedSize(200, 200)
        self.qr_label.setStyleSheet("background: #FFFFFF; border-radius: 10px; padding: 8px;")
        self.qr_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        rc_layout.addWidget(self.qr_label)

        self.recv_addr_txt = QtWidgets.QLineEdit()
        self.recv_addr_txt.setReadOnly(True)
        self.recv_addr_txt.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.recv_addr_txt.setFont(QtGui.QFont("JetBrains Mono", 11, QtGui.QFont.Weight.Bold))
        rc_layout.addWidget(self.recv_addr_txt)

        btn_copy = QtWidgets.QPushButton("📋 Copy Address")
        btn_copy.setObjectName("btn-primary")
        btn_copy.clicked.connect(self._copy_address)
        rc_layout.addWidget(btn_copy)
        r_layout.addWidget(r_card)
        self.tabs.addTab(tab_recv, "📥 Receive & QR")

        # TAB 4: BIP39 VAULT
        tab_vault = QtWidgets.QWidget()
        v_layout = QtWidgets.QVBoxLayout(tab_vault)
        v_card = QtWidgets.QFrame()
        v_card.setObjectName("card-frame")
        vc_layout = QtWidgets.QVBoxLayout(v_card)

        vc_layout.addWidget(QtWidgets.QLabel("BIP39 HD Key Management & Recovery"))
        self.mnemonic_box = QtWidgets.QPlainTextEdit()
        self.mnemonic_box.setReadOnly(True)
        self.mnemonic_box.setFont(QtGui.QFont("JetBrains Mono", 11))
        self.mnemonic_box.setPlainText(f"ACTIVE 24-WORD RECOVERY PHRASE:\n{self.wallet.mnemonic}\n\nDERIVATION PATH: m/44'/999'/0'/0/0")
        vc_layout.addWidget(self.mnemonic_box)

        btn_new_seed = QtWidgets.QPushButton("✨ Generate Fresh Wallet")
        btn_new_seed.setObjectName("btn-violet")
        btn_new_seed.clicked.connect(self.new_wallet)
        vc_layout.addWidget(btn_new_seed)
        v_layout.addWidget(v_card)
        self.tabs.addTab(tab_vault, "🔐 BIP39 Vault")

        self.statusBar().showMessage("Lightning Light Wallet v4.0 Active | Remote Sync: 127.0.0.1:19889")

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

    def update_state(self, data: dict):
        addr = data.get("address", "")
        self.recv_addr_txt.setText(addr)

        bal = data.get("balance", 0.0)
        bal_sat = data.get("balance_sat", 0)
        self.card_bal.value_label.setText(f"{bal:.8f} QTY")
        self.card_bal.sub_label.setText(f"{bal_sat:,} Satoshis Available")

        if data.get("connected"):
            self.conn_pill.setText("● REMOTE SPV CONNECTED")
            self.conn_pill.setStyleSheet("background: rgba(0, 255, 136, 0.15); color: #00FF88; border: 1px solid rgba(0, 255, 136, 0.4); padding: 6px 14px; border-radius: 12px; font-weight: 700; font-family: 'JetBrains Mono'; font-size: 11px;")
        else:
            self.conn_pill.setText("○ RECONNECTING SPV...")
            self.conn_pill.setStyleSheet("background: rgba(255, 0, 122, 0.15); color: #FF007A; border: 1px solid rgba(255, 0, 122, 0.4); padding: 6px 14px; border-radius: 12px; font-weight: 700; font-family: 'JetBrains Mono'; font-size: 11px;")

        utxos = data.get("utxos", [])
        self.utxo_table.setRowCount(len(utxos))
        for row, u in enumerate(utxos):
            txid = u.get("txid", "")
            vout = u.get("vout", 0)
            self.utxo_table.setItem(row, 0, QtWidgets.QTableWidgetItem(f"{txid[:16]}... : {vout}"))
            val_item = QtWidgets.QTableWidgetItem(f"+{u.get('value', 0.0):.4f} QTY")
            val_item.setForeground(QtGui.QColor("#00FF88"))
            self.utxo_table.setItem(row, 1, val_item)
            self.utxo_table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"#{u.get('height', 0)}"))

        if addr:
            self._render_qr(addr)

    def _render_qr(self, addr: str):
        try:
            qr = qrcode.QRCode(version=1, box_size=5, border=2)
            qr.add_data(addr)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            qimg = QtGui.QImage.fromData(buf.getvalue())
            self.qr_label.setPixmap(QtGui.QPixmap.fromImage(qimg).scaled(180, 180, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        except Exception as e:
            print(f"QR error: {e}")

    def _copy_address(self):
        addr = self.recv_addr_txt.text().strip()
        if addr:
            QtWidgets.QApplication.clipboard().setText(addr)
            QtWidgets.QMessageBox.information(self, "Copied", f"Address copied:\n{addr}")

    def execute_fast_send(self):
        to_addr = self.send_addr_in.text().strip()
        amt = self.send_amt_spin.value()
        fee = self.send_fee_spin.value()

        if not to_addr:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter destination address.")
            return

        amt_sat = int(amt * 100_000_000)
        fee_sat = int(fee * 100_000_000)
        sender_addr = self.wallet.get_receiving_address(0)

        self.send_status.setText("<span style='color: #00F0FF;'>Broadcasting instant transaction...</span>")
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
            self.send_status.setText(f"<span style='color: #00FF88;'>✓ TXID: {txid}</span>")
            QtWidgets.QMessageBox.information(self, "Payment Broadcasted", f"Instant payment sent!\nTXID: {txid}")
        except Exception as e:
            self.send_status.setText(f"<span style='color: #FF007A;'>✗ Error: {e}</span>")

    def new_wallet(self):
        self.wallet = HDWallet()
        self.mnemonic_box.setPlainText(f"ACTIVE 24-WORD RECOVERY PHRASE:\n{self.wallet.mnemonic}\n\nDERIVATION PATH: m/44'/999'/0'/0/0")
        if self.sync_worker:
            self.sync_worker.wallet = self.wallet

    def closeEvent(self, event: QtGui.QCloseEvent):
        if hasattr(self, 'sync_worker') and self.sync_worker:
            self.sync_worker.stop()
        event.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = QuantyLightningWalletWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
