#!/bin/sh
# Copyright (c) 2013-2019 The QTY Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

export LC_ALL=C
set -e
srcdir="$(dirname "$0")"
cd "$srcdir"
mkdir -p build-aux/m4
cp /usr/share/aclocal/pkg.m4 build-aux/m4/ 2>/dev/null || true

if [ -z "${LIBTOOLIZE}" ] && GLIBTOOLIZE="$(command -v glibtoolize)"; then
  LIBTOOLIZE="${GLIBTOOLIZE}"
  export LIBTOOLIZE
else
  LIBTOOLIZE="libtoolize"
fi
command -v autoreconf >/dev/null || \
  (echo "configuration failed, please install autoconf first" && exit 1)

${LIBTOOLIZE} --force --copy
mkdir -p build-aux/m4
cp /usr/share/aclocal/pkg.m4 build-aux/m4/ 2>/dev/null || true
autoreconf --install --force -I build-aux/m4 -I /usr/share/aclocal --warnings=all

if expr "'$(build-aux/config.guess --timestamp)" \< "'$(depends/config.guess --timestamp)" > /dev/null; then
  chmod ug+w build-aux/config.guess
  chmod ug+w src/secp256k1/build-aux/config.guess
  cp depends/config.guess build-aux
  cp depends/config.guess src/secp256k1/build-aux
fi
if expr "'$(build-aux/config.sub --timestamp)" \< "'$(depends/config.sub --timestamp)" > /dev/null; then
  chmod ug+w build-aux/config.sub
  chmod ug+w src/secp256k1/build-aux/config.sub
  cp depends/config.sub build-aux
  cp depends/config.sub src/secp256k1/build-aux
fi
