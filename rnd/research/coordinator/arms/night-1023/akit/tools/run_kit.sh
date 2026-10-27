#!/bin/bash
# KIT-V01 replay (0 LLM, MacBook): SEFIX-124 configuration (gidf + F1 + F2 + F4, F3 off) on rs-SEFIX, MAIN 97, funnel-K3 traces. usage: run_kit.sh <label> <extra packs comma list or ->
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; D=$R/night-1023/akit
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=$B/kiln-local/rs-SEFIX
LAB=$1; EXTRA=$2; OUT=$D/replays/main.$LAB.jsonl; t0=$(date +%s); cd $B
PK=$(python3 -I $C/compose/tools/kits.py 10)
[ "$EXTRA" != "-" ] && PK="$PK,$EXTRA"
env RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1 $TSX $TOOL --questions $R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $PK \
  --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err
echo "$LAB rc=$? $(( $(date +%s) - t0 ))s $(tail -1 $OUT.err | cut -c1-200)"
