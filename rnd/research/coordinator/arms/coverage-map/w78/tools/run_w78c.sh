#!/bin/bash
# W78C (0 LLM, MacBook): MAIN 97 replay, SEFIX-124 recipe (= W78B part A) on kiln-local/rs-W78 (+ W78B-DENSE + W78C-DENSE).
# usage: run_w78c.sh <label> <f1BinN|0> [ENV=VAL ...]   e.g. run_w78c.sh Q4-64 32 RS_DENSE_Q=4 RS_DENSE_QN=64 ; run_w78c.sh IVF8 32 RS_DENSE_IVF=8 ; run_w78c.sh B 0
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; W=$C/w78
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=$B/kiln-local/rs-W78
LAB=$1; FBIN=$2; shift 2; mkdir -p $W/replays-c; OUT=$W/replays-c/main.$LAB.jsonl; t0=$(date +%s); cd $B
PK=$(python3 -I $C/compose/tools/kits.py 10)
Q=$R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl
rm -f $OUT.f1log $OUT.denselog
EXTRA="RS_SE_LEAD_BIN_DIR=$W/sidecars RS_DENSE_Q_DIR=$W/sidecars-c RS_DENSE_LOG=$OUT.denselog $*"
[ "$FBIN" != 0 ] && EXTRA="$EXTRA RS_SE_LEAD_BIN=$FBIN"
env RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1 RS_SE_LEAD_LOG=$OUT.f1log $EXTRA \
  $TSX $TOOL --questions $Q --tree $TREE --packs $PK \
  --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err
echo "$LAB rc=$? $(( $(date +%s) - t0 ))s $(tail -1 $OUT.err | cut -c1-200)"
