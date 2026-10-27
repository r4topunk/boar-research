#!/bin/bash
# W78-PACKFMT (0 LLM, MacBook): MAIN 97 replay, W78C recipe (run_w78c.sh) on kiln-local/rs-W78 (+ W78-PACKFMT.patch).
# usage: run_w78pf.sh <label> <pf 0|1> <f1BinN|0> [ENV=VAL ...] ; pf=1 swaps simplewiki + travel for the kiln-local/w78pf-packs copies (lead_ivf tables).
# IDS=a,b -> --ids (cold start). OUTDIR overrides replays-pf.
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; W=$C/w78
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=$B/kiln-local/rs-W78
LAB=$1; PF=$2; FBIN=$3; shift 3; OD=${OUTDIR:-$W/replays-pf}; mkdir -p $OD; OUT=$OD/main.$LAB.jsonl; t0=$(date +%s); cd $B
PK=$(python3 -I $C/compose/tools/kits.py 10)
if [ "$PF" = 1 ]; then
  PK=${PK//$B\/shared-data\/packs\/v3proto\/boar-simplewiki-en.sqlite/$B/kiln-local/w78pf-packs/boar-simplewiki-en.sqlite}
  PK=${PK//$B\/shared-data\/packs\/v3proto\/qa-travel-se.sqlite/$B/kiln-local/w78pf-packs/qa-travel-se.sqlite}
fi
Q=$R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl
IDARG=(); [ -n "${IDS:-}" ] && IDARG=(--ids "$IDS")
rm -f $OUT.f1log $OUT.denselog
EXTRA="RS_SE_LEAD_BIN_DIR=$W/sidecars RS_DENSE_Q_DIR=$W/sidecars-c RS_DENSE_LOG=$OUT.denselog $*"
[ "$FBIN" != 0 ] && EXTRA="$EXTRA RS_SE_LEAD_BIN=$FBIN"
env RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1 RS_SE_LEAD_LOG=$OUT.f1log $EXTRA \
  $TSX $TOOL --questions $Q --tree $TREE --packs $PK ${IDARG[@]+"${IDARG[@]}"} \
  --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err
echo "$LAB rc=$? $(( $(date +%s) - t0 ))s $(tail -1 $OUT.err | cut -c1-200)"
