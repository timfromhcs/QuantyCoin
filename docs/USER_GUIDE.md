# QuantyCoin End-User Guide

Welcome to QuantyCoin (QTY). This guide walks you through setting up your wallet, receiving QTY, and sending transactions with full self-sovereignty.

---

## 1. What is QuantyCoin?

QuantyCoin is an open-source, decentralized cryptocurrency powered by SHA-256D Proof-of-Work. It provides:
- **60-Second Block Times**: Rapid transaction confirmation.
- **Fixed Hard Cap**: Exactly 21,000,000 QTY maximum supply.
- **Self-Sovereign Wallets**: You control your private keys and 24-word recovery seed.
- **Native Bech32 Addresses**: Human-readable addresses starting with `qty1q...`.

---

## 2. Setting Up Your Wallet

QuantyCoin includes a native Qt6 graphical wallet with an integrated background full node.

### Prerequisites
- Python 3.10+ installed on your computer.
- Install the required GUI dependencies:
  ```bash
  pip install PySide6 qrcode pillow
  ```

### Launching the Sovereign Full Wallet
```bash
python quanty_wallet_full_app.py
```

### Creating a New Wallet
1. On first launch, the wallet will generate a **24-word BIP39 mnemonic seed**.
2. **Write down your 24 words on physical paper.** Never store them in plain text on cloud services or share them with anyone.
3. Your wallet generates receiving addresses starting with `qty1q...`.

---

## 3. Receiving QuantyCoin

1. Click on the **Receive** tab in the wallet.
2. Your current receiving address (e.g. `qty1q...`) and an interactive QR code will be displayed.
3. Copy the address or scan the QR code from a sending application.
4. Once sent, your balance will update automatically when the transaction is confirmed in a mined block (~60 seconds).

---

## 4. Sending QuantyCoin

1. Click on the **Send** tab.
2. Enter the recipient's Bech32 address (`qty1q...`).
3. Enter the amount of QTY to send.
4. Set your transaction fee rate (standard is 0.0001 QTY).
5. Click **Send Coins**. The transaction is cryptographically signed using your private key and broadcast across the peer-to-peer network.

---

## 5. Wallet Backup & Recovery

- If your computer is lost or replaced, your funds can be restored completely using your 24-word seed.
- In the wallet, navigate to **Settings / Backup** to verify your seed phrase at any time.
