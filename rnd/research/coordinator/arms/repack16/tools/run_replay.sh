#!/bin/bash
# REPACK16 replay driver (0 LLM). One replay-retrieval process per (kit, order, block KB, cache slots).
# usage: run_replay.sh <tree> <qdir with S.jsonl M.jsonl> <packs root with wv16/ wv32/ sw16/ sw32/> <out dir> <kit A|ASW|A6 (all 6 repacked; 64 = originals)> "<orders>" "<kbs>" "<caches>"
set -u
TREE=$1; QD=$2; PR=$3; OUT=$4; KIT=$5; ORDERS=$6; KBS=$7; CACHES=$8
B=<workspace>; P=$B/shared-data/packs/persona-a-union; SWO=$B/shared-data/packs/candidates/boar-simplewiki-en-convfix/boar-simplewiki-en.sqlite
mkdir -p $OUT
for kb in $KBS; do
  if [ $kb = 64 ]; then WV=$P/boar-wikivoyage-en.sqlite; SW=$SWO; else WV=$PR/wv$kb/boar-wikivoyage-en.sqlite; SW=$PR/sw$kb/boar-simplewiki-en.sqlite; fi
  PACKS=$P/boar-crypto.sqlite,$WV,$P/boar-visa-en.sqlite,$P/boar-medlineplus-en.sqlite,$P/boar-firstaid-en.sqlite,$P/boar-factbook.sqlite
  [ $KIT = ASW ] && PACKS=$PACKS,$SW
  if [ $KIT = A6 ] && [ $kb != 64 ]; then A6=$PR/all$kb; PACKS=$A6/boar-crypto.sqlite,$A6/boar-wikivoyage-en.sqlite,$A6/boar-visa-en.sqlite,$A6/boar-medlineplus-en.sqlite,$A6/boar-firstaid-en.sqlite,$A6/boar-factbook.sqlite; fi
  for o in $ORDERS; do for c in $CACHES; do
    n=$KIT-$o-$kb-$c; L=$OUT/$n.blocklog.jsonl; rm -f $L; s=$(date +%s)
    BOAR_BLOCK_CACHE=$c BOAR_BLOCKLOG=$L $B/boar-eval/adapters/desktop-node/tools/replay-retrieval.sh \
      --questions $QD/$o.jsonl --tree $TREE --packs $PACKS --gate rules --out $OUT/$n.replay.jsonl 2> $OUT/$n.stderr || { echo "FAIL $n"; exit 1; }
    echo "$n searches=$(grep -c '"search"' $L) misses=$(grep -c '"miss"' $L) wall=$(( $(date +%s) - s ))s"
  done; done
done
