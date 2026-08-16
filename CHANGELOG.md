# QuantyCoin Release Notes & Changelog

## [2.2.0] - 2026-08-16 — Multi-Platform CI/CD Hardening & Release Build Fix

- **CI Build Hardening**: Fixed Automake stub Makefile inclusion (`src/qt/Makefile`, `src/qt/test/Makefile`, `src/test/Makefile`) and unignored them in `.gitignore`.
- **Recursive Executable Bit Fix**: Fixed script execution permissions for `depends/`, `build-aux/`, `scripts/`, `configure`, and `autogen.sh` across Linux, macOS, and MinGW Windows runners.
- **Consensus & Features**: Maintained all v2.0.0 & v2.0.1 consensus features including 50/50 fee splitting, autonomous monthly treasury airdrops, standalone light client mode, block explorer, and one-click mining.

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
