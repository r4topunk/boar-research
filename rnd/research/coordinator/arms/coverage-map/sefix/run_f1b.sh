#!/bin/bash
# SEFIX F1b replay (0 LLM, MacBook): MAIN 97, funnel-K3 traces, rs-H4 clone, RS_MERGE=gidf, N10 kit.
# usage: run_f1b.sh <label> <v2|v3> <append-budget|extra>   (v3 = cooking+money from v3proto with chunk_vecs)
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; D=$C/compose
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=${TREE:-$B/kiln-local/rs-H4}
L=$1; V=$2; M=$3; OUT=$C/sefix/replays/main.$L.jsonl; t0=$(date +%s); cd $B
PK=$(python3 -I $D/tools/kits.py 10)
if [ "$V" = v3 ]; then PK=${PK//packs\/wave3\/qa-/packs\/v3proto\/qa-}; fi
echo "$PK" | tr , '\n' > $OUT.packs
export RS_MERGE=gidf
$TSX $TOOL --questions $R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $PK \
  --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json "{\"packHeadPass\":\"a2\",\"packDense2\":\"$M\"}" --out $OUT 2> $OUT.err
echo "$L rc=$? $(( $(date +%s) - t0 ))s $(tail -1 $OUT.err | cut -c1-160)"
