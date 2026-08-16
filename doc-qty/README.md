# QTY (QuantyCoin)

## Overview

QTY is a post-quantum POW cryptocurrency designed for the post-quantum era. It maintains Bitcoin's economic model and network architecture while implementing quantum-resistant cryptographic primitives and enhanced transaction capacity for large post-quantum signatures.

### Key Features

- **Post-Quantum Ready**: Integrated support for Dilithium, Falcon, and SPHINCS+ signature algorithms
- **Enhanced Capacity**: 8 MB max block weight (`MAX_BLOCK_WEIGHT`), 15 KB max script elements for Dilithium signatures
- **Bitcoin Compatibility**: Maintains Bitcoin's UTXO model, scripting system, and economic incentives
- **Quantum-Resistant Infrastructure**: Dilithium (ML-DSA) signing with hardened-only HD wallet derivation

### Roadmap Phases

- **Phase 1** (v0.1.0): Consensus parameter adjustments, weight normalization (`WITNESS_SCALE_FACTOR=16`)
- **Phase 2** (v1.1.0): Dilithium wallet + script primitives (hardened HD paths; no xpub/non-hardened derivation)
- **Phase 3** (current): Dilithium opcodes consensus-active from `nDilithiumHeight` (default height 1 on all networks)

### Dilithium HD limitations

Dilithium keys use **hardened-only** BIP32-style derivation (`m/44'/…'/account'/change'/index'`). Non-hardened / watch-only xpub address discovery is not supported without a Raccoon-G-style construction.

## Getting Started

### Build Instructions

```bash
# Clone the repository
git clone https://github.com/qty-ag/QTY-Core.git
cd QTY-Core

# Build dependencies (Ubuntu/Debian)
sudo apt-get install build-essential libtool autotools-dev automake pkg-config libssl-dev libevent-dev bsdmainutils

# Configure and build
./autogen.sh
./configure
make -j$(nproc)
```

### Running QTY

#### Regtest (Development)
```bash
./src/qtyd -regtest -daemon
./src/qty-cli -regtest getblockchaininfo
```

#### Testnet
```bash
./src/qtyd -testnet -daemon
./src/qty-cli -testnet getblockchaininfo
```

#### Mainnet
```bash
./src/qtyd -daemon
./src/qty-cli getblockchaininfo
```

### Network Information

| Network  | P2P   | RPC   | Onion  |
|----------|-------|-------|--------|
| Mainnet  | 9333  | 8332  | 8334   |
| Testnet  | 19333 | 18332 | 18334  |
| Signet   | 38333 | 38332 | 38334  |
| Regtest  | 19444 | 18443 | 18445  |

- **P2P**: Port for peer-to-peer node communication
- **RPC**: Port for JSON-RPC API access (qty-cli, applications)
- **Onion**: Target port for incoming Tor connections

## Contributing

QTY follows Bitcoin Core's development model with some adaptations for post-quantum development:

- Read [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines
- Follow the [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md)
- Review [Code Review Guidelines](reviews/CODE_REVIEW_GUIDELINES.md)
- Check [Testing Guide](testing/TESTING_GUIDE.md) for test requirements

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch from `master`
3. Make your changes with appropriate tests
4. Follow the PR template and submit for review
5. Address feedback and iterate through ACK process

## Documentation

- [Release Process](releases/RELEASE_PROCESS.md)
- [Security Policy](SECURITY.md)
- [Governance](GOVERNANCE.md)
- [Testing Guide](testing/TESTING_GUIDE.md)
- [Communication Policy](communication/COMMUNICATION.md)

## Support

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Design discussions and Q&A
- **Telegram**: Community announcements and general discussion

## License

QTY Core is released under the terms of the MIT license. See [COPYING](../COPYING) for more information.
