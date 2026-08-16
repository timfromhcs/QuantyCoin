# QuantyCoin Release Notes & Changelog

## [2.0.1] - 2026-08-16 — Fix CI Build Permissions & Script Execution

- **Fix Build Scripts Executable Bit**: Added `chmod +x` step across all GitHub Actions build workflows (`build.yml` & `build-and-address-tests.yml`) to resolve script execution permissions on runner checkout.
- **CI Matrix Fix**: Resolved process exit code 126 (`Permission denied`) on Linux and Windows cross-compiler workflows.
- **Consensus & Features**: Maintained all v2.0.0 features including 50/50 fee splitting, autonomous monthly treasury airdrops, standalone light client mode, block explorer, and one-click mining.

## [2.0.0] - 2026-08-16 — Major Consensus & Feature Upgrade
- 50/50 Fee Split (Miner / Community Treasury).
- Autonomous Monthly Treasury Airdrops for wallets > 5 QTY & > 21 days age.
- Standalone Light Client Mode (Auto remote seed failover).
- Integrated Block Explorer & GUI Suite.

## [1.0.0] - 2026-08-16 — Initial Launch
- Quantum-Resistant ML-DSA-65 signatures & P2QRH addresses (`qty` / `dqty`).
- 32 MB Block capacity & 1-minute block intervals.
- SHA-256 ASIC-compatible Proof of Work.
