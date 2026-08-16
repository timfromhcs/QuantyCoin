// Copyright (c) 2009-2010 Satoshi Nakamoto
// Copyright (c) 2009-2022 The QTY Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef QTY_CONSENSUS_CONSENSUS_H
#define QTY_CONSENSUS_CONSENSUS_H

#include <cstdlib>
#include <stdint.h>

/** The maximum allowed size for a serialized block, in bytes (only for buffer size limits) */
static const unsigned int MAX_BLOCK_SERIALIZED_SIZE = 32 * 1024 * 1024; // 32 MB // 8 MB
/** The maximum allowed weight for a block, in weight units */
static const unsigned int MAX_BLOCK_WEIGHT = 32 * 1024 * 1024; // 32 MB // 8 MW
/** The maximum allowed number of signature check operations in a block (network rule) */
static const int64_t MAX_BLOCK_SIGOPS_COST = 80000;
/** Coinbase transaction outputs can only be spent after this number of new blocks (network rule) */
static const int COINBASE_MATURITY = 100;

static const int WITNESS_SCALE_FACTOR = 16;

static const size_t MIN_TRANSACTION_WEIGHT = WITNESS_SCALE_FACTOR * 60; // 60 is the lower bound for the size of a valid serialized CTransaction
static const size_t MIN_SERIALIZABLE_TRANSACTION_WEIGHT = WITNESS_SCALE_FACTOR * 10; // 10 is the lower bound for the size of a serialized CTransaction

/** Flags for nSequence and nLockTime locks */
/** Interpret sequence numbers as relative lock-time constraints. */
static constexpr unsigned int LOCKTIME_VERIFY_SEQUENCE = (1 << 0);

/** QuantyCoin v2.0 Community Treasury & Monthly Airdrop Consensus Rules */
static const int64_t AIRDROP_INTERVAL_BLOCKS = 43200; // ~30 days at 60s block time
static const int64_t AIRDROP_MIN_AGE_BLOCKS = 30240;  // ~21 days (3 weeks)
static const int64_t AIRDROP_MIN_BALANCE_COIN = 5;    // Must hold > 5 QTY
static const char* const TREASURY_SPENDEN_ADDRESS = "qty1qspendenwallettreasury2026";

#endif // QTY_CONSENSUS_CONSENSUS_H
