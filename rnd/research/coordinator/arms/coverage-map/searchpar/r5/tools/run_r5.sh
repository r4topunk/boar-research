#!/bin/bash
# SEARCHPAR R5 replay (0 LLM, MacBook): F1b configuration (13-pack N10 kit, cooking/money v3 files, RS_MERGE=gidf, packHeadPass a2 + packDense2 extra) on a clone.
# usage: run_r5.sh <qform|longsession> <label> <RS_STICKY value or "off"> [tree]   (tree default kiln-local/rs-R5; "off" leaves RS_STICKY unset)
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; D=$C/searchpar/r5
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx
SET=$1; L=$2; ST=$3; TREE=${4:-$B/kiln-local/rs-R5}; IDS=${IDS:-}
OUT=$D/replays/$SET.$L.jsonl; t0=$(date +%s); cd $B
PK=$(python3 -I $C/compose/tools/kits.py 10); PK=${PK//packs\/wave3\/qa-/packs\/v3proto\/qa-}
export RS_MERGE=gidf; unset RS_STICKY; [ "$ST" != off ] && export RS_STICKY=$ST
W=12; { [ $SET = longsession ] || [ "$ST" != off ]; } && W=0
EXTRA=(); [ -n "$IDS" ] && EXTRA=(--ids $IDS); [ -n "${CARRIER:-}" ] && EXTRA+=(--carrier-from $CARRIER)
$TSX $D/tools/replay-sticky.ts --questions $D/$SET.chain.jsonl --tree $TREE --packs $PK --gate search --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide $W \
  --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"extra"}' ${EXTRA[@]+"${EXTRA[@]}"} --out $OUT 2> $OUT.err
echo "$SET $L rc=$? $(( $(date +%s) - t0 ))s $(tail -1 $OUT.err | cut -c1-200)"
