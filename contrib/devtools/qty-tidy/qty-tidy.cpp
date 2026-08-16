// Copyright (c) 2023 QTY Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include "logprintf.h"

#include <clang-tidy/ClangTidyModule.h>
#include <clang-tidy/ClangTidyModuleRegistry.h>

class QTYModule final : public clang::tidy::ClangTidyModule
{
public:
    void addCheckFactories(clang::tidy::ClangTidyCheckFactories& CheckFactories) override
    {
        CheckFactories.registerCheck<qty::LogPrintfCheck>("qty-unterminated-logprintf");
    }
};

static clang::tidy::ClangTidyModuleRegistry::Add<QTYModule>
    X("qty-module", "Adds qty checks.");

volatile int QTYModuleAnchorSource = 0;
