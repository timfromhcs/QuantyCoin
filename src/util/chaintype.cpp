// Copyright (c) 2023 The QTY Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <util/chaintype.h>

#include <cassert>
#include <optional>
#include <string>

std::string ChainTypeToString(ChainType chain)
{
    switch (chain) {
    case ChainType::QTYMAIN:
        return "main";
    case ChainType::QTYTEST:
        return "test";
    case ChainType::QTYSIGNET:
        return "signet";
    case ChainType::QTYREGTEST:
        return "regtest";
    }
    assert(false);
}

std::optional<ChainType> ChainTypeFromString(std::string_view chain)
{
    if (chain == "main") {
        return ChainType::QTYMAIN;
    } else if (chain == "test") {
        return ChainType::QTYTEST;
    } else if (chain == "signet") {
        return ChainType::QTYSIGNET;
    } else if (chain == "regtest") {
        return ChainType::QTYREGTEST;
    } else {
        return std::nullopt;
    }
}