// Copyright (c) 2022 The QTY Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef QTY_KERNEL_VALIDATION_CACHE_SIZES_H
#define QTY_KERNEL_VALIDATION_CACHE_SIZES_H

#include <script/sigcache.h>

#include <cstddef>
#include <limits>

namespace kernel {
struct ValidationCacheSizes {
    size_t signature_cache_bytes{DEFAULT_MAX_SIG_CACHE_BYTES / 2};
    size_t script_execution_cache_bytes{DEFAULT_MAX_SIG_CACHE_BYTES / 2};
};
}

#endif // QTY_KERNEL_VALIDATION_CACHE_SIZES_H
