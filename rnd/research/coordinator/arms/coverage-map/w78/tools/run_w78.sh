#!/bin/bash
# W78-BINARY MAIN 97 replay (0 LLM, MacBook): SEFIX-124 recipe (sefix/tools/run_main.sh F1F2F4) on kiln-local/rs-W78.
# usage: run_w78.sh <label> <binN|0> [first-N-items]
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; W=$C/w78
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=$B/kiln-local/rs-W78
LAB=$1; BIN=$2; N=${3:-}; OUT=$W/replays/main.$LAB.jsonl; t0=$(date +%s); cd $B
PK=$(python3 -I $C/compose/tools/kits.py 10)
Q=$R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl
if [ -n "$N" ]; then head -n $N $Q > $W/replays/q$N.jsonl; Q=$W/replays/q$N.jsonl; fi
rm -f $OUT.f1log
EXTRA=""; [ "$BIN" != 0 ] && EXTRA="RS_SE_LEAD_BIN=$BIN RS_SE_LEAD_BIN_DIR=$W/sidecars"
env RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1 RS_SE_LEAD_LOG=$OUT.f1log $EXTRA \
  $TSX $TOOL --questions $Q --tree $TREE --packs $PK \
  --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err
echo "$LAB rc=$? $(( $(date +%s) - t0 ))s $(tail -1 $OUT.err | cut -c1-200)"
