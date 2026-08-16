# QuantyCoin Release Notes & Changelog

## [1.0.0] - 2026-08-16

### Initial Release - QuantyCoin (QTY) Mainnet Launch

QuantyCoin is an autonomous, quantum-resistant cryptocurrency built with ML-DSA signatures, 32 MB block capacity, 1-minute block intervals, and ASIC-compatible SHA-256 Proof of Work.

### Key Features
- **Quantum Resistance**: ML-DSA post-quantum signature schemes and P2QRH address support (`qty` / `dqty` Bech32 HRPs).
- **Consensus Parameters**:
  - Max Block Size: 32 MB (`MAX_BLOCK_SERIALIZED_SIZE = 33,554,432 bytes`).
  - Target Block Time: 60 seconds (1 minute).
  - Difficulty Adjustment: LWMA/DGW difficulty retargeting active from height 1.
- **Mining**: SHA-256 PoW algorithm maintaining ASIC hardware compatibility.
- **P2P Networking & Fallbacks**:
  - Default UPnP / NAT-PMP port mapping enabled.
  - Native IPv6 network stack support.
  - Tor / I2P proxy integration.
  - Pre-configured seed nodes (`seed1.quantycoin.org`, `seed2.quantycoin.org`).
- **Genesis Block**: Remined genesis block with timestamp `"QuantyCoin genesis: quantum-safe launch baseline, 16/Aug/2026"`.
- **GUI & Tools**: Qt5 GUI wallet, `qtyd` full node, `qty-cli` RPC interface, `qty-tx`, `qty-wallet`, and `qty-util`.
- **CI/CD**: Fully automated multi-platform GitHub Actions release matrix for Linux, macOS, and Windows.
