"""
QuantyCoin 4.0 (QTY4) Public Genesis & Consensus Network Parameters
PROTOCOL FREEZE — DO NOT MODIFY CONSENSUS CONSTANTS DIRECTLY
AIR-GAP COMPLIANCE: ZERO SECRETS STORED IN REPOSITORY
"""

# Protocol Version & Chain Identifier
PROTOCOL_VERSION = 70040
CHAIN_ID = "quantycoin-4.0"

# Network Magic Bytes (4 bytes)
MAGIC_BYTES = b"\x51\x54\x59\x34"          # 0x51 0x54 0x59 0x34 ('QTY4')
TESTNET_MAGIC_BYTES = b"\x54\x51\x54\x34"  # 0x54 0x51 0x54 0x34 ('TQT4')
REGTEST_MAGIC_BYTES = b"\x52\x51\x54\x34"  # 0x52 0x51 0x54 0x34 ('RQT4')

# Default Network Ports
DEFAULT_P2P_PORT = 19444
DEFAULT_RPC_PORT = 19445
DEFAULT_STRATUM_PORT = 3333
DEFAULT_STRATUM_V2_PORT = 3334

DEFAULT_TESTNET_P2P_PORT = 29444
DEFAULT_TESTNET_RPC_PORT = 29445
DEFAULT_TESTNET_STRATUM_PORT = 13333
DEFAULT_TESTNET_STRATUM_V2_PORT = 13334

DEFAULT_REGTEST_P2P_PORT = 39444
DEFAULT_REGTEST_RPC_PORT = 39445
DEFAULT_REGTEST_STRATUM_PORT = 23333
DEFAULT_REGTEST_STRATUM_V2_PORT = 23334

# Genesis Block Constants
GENESIS_TIMESTAMP_STR = "2026-09-05: QuantyCoin 4.0 (QTY4) - Post-Quantum Dual-PoW Layer-1 Autonomous Blockchain Protocol"
GENESIS_TIMESTAMP = 1788614400
GENESIS_BITS = 0x1e0fffff
POW_LIMIT_BITS = 0x1e0fffff
GENESIS_NONCE = 2951011
GENESIS_HASH = "000004eb1e117df3168d6d27118982e0a23c236120183e8390a6bbb82ee6fde3"
GENESIS_MERKLE_ROOT = "3526817e09d5a065247d15a45a7aa5cf351479e011d32ecfd752e94acfae55ea"
GENESIS_COINBASE_PAYOUT_ADDRESS = "qty1qu9ztelcfra7uz8agw9qnfej6h8x9tqtxhuaqpf"
GENESIS_BLOCK_REWARD = 50  # 50 QTY
GENESIS_BLOCK_REWARD_SATOSHIS = 50 * 100_000_000  # 5,000,000,000 satoshis

# Consensus Parameters
TARGET_BLOCK_TIME = 60                       # 60 seconds combined nominal block time
LANE_A_TARGET_TIME = 120                     # 120 seconds target interval for Lane A
LANE_B_TARGET_TIME = 120                     # 120 seconds target interval for Lane B
LANE_A_BASE_SUBSIDY = 50 * 100_000_000       # 50 QTY (5,000,000,000 satoshis)
LANE_B_BASE_SUBSIDY = 25 * 100_000_000       # 25 QTY (2,500,000,000 satoshis)
THERMODYNAMIC_WEIGHT_A = 1                   # Work weight for Lane A (SHA-256D)
THERMODYNAMIC_WEIGHT_B = 2048                # Work weight for Lane B (Scrypt 1024)

DIFFICULTY_RETARGET_INTERVAL = 45            # 45 blocks per-lane LWMA-1 window
SUBSIDY_HALVING_INTERVAL = 2100000           # 2,100,000 blocks (~4 years)
MAX_SUPPLY_QTY = 21000000                    # 21,000,000 QTY
MAX_MONEY_SATOSHIS = 21000000 * 100_000_000  # 2,100,000,000,000,000 satoshis
MAX_BLOCK_SIZE = 32 * 1024 * 1024            # 32 MB
COINBASE_MATURITY = 100                      # 100 blocks
MTP_WINDOW = 11                              # 11 blocks Median-Time-Past window
FUTURE_TIME_LIMIT = 7200                     # 7200 seconds (2 hours) max forward drift
