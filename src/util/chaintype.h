// Copyright (c) 2023 The QTY Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef QTY_UTIL_CHAINTYPE_H
#define QTY_UTIL_CHAINTYPE_H

#include <optional>
#include <string>

enum class ChainType {
    QTYMAIN,
    QTYTEST,
    QTYSIGNET,
    QTYREGTEST,
};

std::string ChainTypeToString(ChainType chain);

std::optional<ChainType> ChainTypeFromString(std::string_view chain);

#endif // QTY_UTIL_CHAINTYPE_H
