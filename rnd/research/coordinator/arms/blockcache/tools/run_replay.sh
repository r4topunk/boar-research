#!/bin/bash
# BLOCKCACHE replay driver (0 LLM): one replay-retrieval process per (order, cache size) on the instrumented scratch tree.
# usage: run_replay.sh <tree> <questions dir with S,R1,R2,R3,M .jsonl> <out dir> [orders] [sizes]   (size 0 = unbounded)
set -u
TREE=$1; QD=$2; OUT=$3; ORDERS=${4:-"S R1 R2 R3 M"}; SIZES=${5:-"16 64 256 0"}
B=<workspace>; P=$B/shared-data/packs/persona-a-union
PACKS=$P/boar-crypto.sqlite,$P/boar-wikivoyage-en.sqlite,$P/boar-visa-en.sqlite,$P/boar-medlineplus-en.sqlite,$P/boar-firstaid-en.sqlite,$P/boar-factbook.sqlite
mkdir -p $OUT
for o in $ORDERS; do for s in $SIZES; do
  L=$OUT/$o-$s.blocklog.jsonl; rm -f $L
  BOAR_BLOCK_CACHE=$s BOAR_BLOCKLOG=$L $B/boar-eval/adapters/desktop-node/tools/replay-retrieval.sh \
    --questions $QD/$o.jsonl --tree $TREE --packs $PACKS --gate rules --out $OUT/$o-$s.replay.jsonl 2> $OUT/$o-$s.stderr || { echo "FAIL $o $s"; exit 1; }
  echo "$o $s searches=$(grep -c '"search"' $L) misses=$(grep -c '"miss"' $L)"
done; done
