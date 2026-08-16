# QuantyCoin Release Notes & Changelog

## [2.3.0] - 2026-08-16 — Multi-Platform Cross-Build Fix & Android Wallet Addition

- **Fix Missing Includes in Miner**: Fixed `ParseHex` undeclared identifier error in `src/node/miner.cpp` by adding `#include <util/strencodings.h>`.
- **Android Wallet Support**: Added automated Android Light Client Wallet build pipeline job in `.github/workflows/build.yml` producing `quantycoin-android-wallet.zip`.
- **macOS Build Hardening**: Added explicit Qt5 environment paths (`export PATH` and `PKG_CONFIG_PATH`) for Homebrew `qt@5` on macOS runners.
- **Consensus & Features**: Maintained all consensus rules including 50/50 fee splitting, autonomous monthly treasury airdrops, standalone light client mode, block explorer, and one-click mining.

## [2.2.0] - 2026-08-16 — Multi-Platform CI/CD Hardening & Release Build Fix
- Fixed Automake Makefile stub dependencies and recursive script permissions.

## [2.0.1] - 2026-08-16 — Fix CI Build Permissions & Script Execution
- Add `chmod +x` step across build workflows.

## [2.0.0] - 2026-08-16 — Major Consensus & Feature Upgrade
- 50/50 Fee Split (Miner / Community Treasury).
- Autonomous Monthly Treasury Airdrops for wallets > 5 QTY & > 21 days age.
- Standalone Light Client Mode (Auto remote seed failover).
- Integrated Block Explorer & GUI Suite.

## [1.0.0] - 2026-08-16 — Initial Launch
- Quantum-Resistant ML-DSA-65 signatures & P2QRH addresses (`qty` / `dqty`).
- 32 MB Block capacity & 1-minute block intervals.
- SHA-256 ASIC-compatible Proof of Work.
