#!/bin/sh
# Byte-identity of the boar-zstd native decoder vs fzstd on every block of every pack given (default: the g75 kit, the
# P-7b 16 KB rebuilds on the mini; wiki-vital5 is a format-1 pack with no blocks), plus the fallback cases. Writes identity.txt.
set -e
cd "$(dirname "$0")"
cc -O2 -I/opt/homebrew/include native_hashes.c ../tree/modules/boar-zstd/cpp/boar_zstd.c -lsqlite3 -o native_hashes
cc -O2 -I/opt/homebrew/include -L/opt/homebrew/lib fallback_cases.c ../tree/modules/boar-zstd/cpp/boar_zstd.c -lzstd -o fallback_cases
PACKS=${*:-"<workspace>/shared-data/crypto/boar-crypto.sqlite <workspace>/shared-data/packs/boar-wikivoyage-en.sqlite <volume>/boar/kiln/p7b/16/boar-crypto.sqlite <volume>/boar/kiln/p7b/16/boar-wikivoyage-en.sqlite"}
{
  echo "# boar-zstd vs fzstd 0.1.1, every block ($(date '+%Y-%m-%d %H:%M'))"
  for p in $PACKS; do
    ./native_hashes "$p" > native.tmp; node fzstd_hashes.mjs "$p" > fzstd.tmp
    n=$(wc -l < native.tmp | tr -d ' '); refused=$(awk '$2 == -1' native.tmp | wc -l | tr -d ' ')
    if cmp -s native.tmp fzstd.tmp; then v=IDENTICAL; else v="DIFFER ($(diff native.tmp fzstd.tmp | grep -c '^<') lines)"; fi
    echo "$p: $n blocks, native refused $refused, $v, pack sha256 $(shasum -a 256 "$p" | cut -c1-16)…"
  done
  ./fallback_cases
} | tee identity.txt
rm -f native.tmp fzstd.tmp
