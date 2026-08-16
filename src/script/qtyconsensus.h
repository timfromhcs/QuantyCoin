// Copyright (c) 2009-2010 Satoshi Nakamoto
// Copyright (c) 2009-2021 The QTY Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef QTY_SCRIPT_QTYCONSENSUS_H
#define QTY_SCRIPT_QTYCONSENSUS_H

#include <stdint.h>

#if defined(BUILD_QTY_INTERNAL) && defined(HAVE_CONFIG_H)
#include <config/qty-config.h>
  #if defined(_WIN32)
    #if defined(HAVE_DLLEXPORT_ATTRIBUTE)
      #define EXPORT_SYMBOL __declspec(dllexport)
    #else
      #define EXPORT_SYMBOL
    #endif
  #elif defined(HAVE_DEFAULT_VISIBILITY_ATTRIBUTE)
    #define EXPORT_SYMBOL __attribute__ ((visibility ("default")))
  #endif
#elif defined(MSC_VER) && !defined(STATIC_LIBQTYCONSENSUS)
  #define EXPORT_SYMBOL __declspec(dllimport)
#endif

#ifndef EXPORT_SYMBOL
  #define EXPORT_SYMBOL
#endif

#ifdef __cplusplus
extern "C" {
#endif

#define QTYCONSENSUS_API_VER 2

typedef enum qtyconsensus_error_t
{
    qtyconsensus_ERR_OK = 0,
    qtyconsensus_ERR_TX_INDEX,
    qtyconsensus_ERR_TX_SIZE_MISMATCH,
    qtyconsensus_ERR_TX_DESERIALIZE,
    qtyconsensus_ERR_AMOUNT_REQUIRED,
    qtyconsensus_ERR_INVALID_FLAGS,
    qtyconsensus_ERR_SPENT_OUTPUTS_REQUIRED,
    qtyconsensus_ERR_SPENT_OUTPUTS_MISMATCH
} qtyconsensus_error;

/** Script verification flags */
enum
{
    qtyconsensus_SCRIPT_FLAGS_VERIFY_NONE                = 0,
    qtyconsensus_SCRIPT_FLAGS_VERIFY_P2SH                = (1U << 0), // evaluate P2SH (BIP16) subscripts
    qtyconsensus_SCRIPT_FLAGS_VERIFY_DERSIG              = (1U << 2), // enforce strict DER (BIP66) compliance
    qtyconsensus_SCRIPT_FLAGS_VERIFY_NULLDUMMY           = (1U << 4), // enforce NULLDUMMY (BIP147)
    qtyconsensus_SCRIPT_FLAGS_VERIFY_CHECKLOCKTIMEVERIFY = (1U << 9), // enable CHECKLOCKTIMEVERIFY (BIP65)
    qtyconsensus_SCRIPT_FLAGS_VERIFY_CHECKSEQUENCEVERIFY = (1U << 10), // enable CHECKSEQUENCEVERIFY (BIP112)
    qtyconsensus_SCRIPT_FLAGS_VERIFY_WITNESS             = (1U << 11), // enable WITNESS (BIP141)
    qtyconsensus_SCRIPT_FLAGS_VERIFY_TAPROOT             = (1U << 17), // enable TAPROOT (BIPs 341 & 342)
    qtyconsensus_SCRIPT_FLAGS_VERIFY_DILITHIUM          = (1U << 21), // enable Dilithium signature validation
    qtyconsensus_SCRIPT_FLAGS_VERIFY_ALL                 = qtyconsensus_SCRIPT_FLAGS_VERIFY_P2SH | qtyconsensus_SCRIPT_FLAGS_VERIFY_DERSIG |
                                                               qtyconsensus_SCRIPT_FLAGS_VERIFY_NULLDUMMY | qtyconsensus_SCRIPT_FLAGS_VERIFY_CHECKLOCKTIMEVERIFY |
                                                               qtyconsensus_SCRIPT_FLAGS_VERIFY_CHECKSEQUENCEVERIFY | qtyconsensus_SCRIPT_FLAGS_VERIFY_WITNESS |
                                                               qtyconsensus_SCRIPT_FLAGS_VERIFY_TAPROOT | qtyconsensus_SCRIPT_FLAGS_VERIFY_DILITHIUM
};

typedef struct {
    const unsigned char *scriptPubKey;
    unsigned int scriptPubKeySize;
    int64_t value;
} UTXO;

/// Returns 1 if the input nIn of the serialized transaction pointed to by
/// txTo correctly spends the scriptPubKey pointed to by scriptPubKey under
/// the additional constraints specified by flags.
/// If not nullptr, err will contain an error/success code for the operation
EXPORT_SYMBOL int qtyconsensus_verify_script(const unsigned char *scriptPubKey, unsigned int scriptPubKeyLen,
                                                 const unsigned char *txTo        , unsigned int txToLen,
                                                 unsigned int nIn, unsigned int flags, qtyconsensus_error* err);

EXPORT_SYMBOL int qtyconsensus_verify_script_with_amount(const unsigned char *scriptPubKey, unsigned int scriptPubKeyLen, int64_t amount,
                                    const unsigned char *txTo        , unsigned int txToLen,
                                    unsigned int nIn, unsigned int flags, qtyconsensus_error* err);

EXPORT_SYMBOL int qtyconsensus_verify_script_with_spent_outputs(const unsigned char *scriptPubKey, unsigned int scriptPubKeyLen, int64_t amount,
                                    const unsigned char *txTo        , unsigned int txToLen,
                                    const UTXO *spentOutputs, unsigned int spentOutputsLen,
                                    unsigned int nIn, unsigned int flags, qtyconsensus_error* err);

EXPORT_SYMBOL unsigned int qtyconsensus_version();

#ifdef __cplusplus
} // extern "C"
#endif

#undef EXPORT_SYMBOL

#endif // QTY_SCRIPT_QTYCONSENSUS_H
