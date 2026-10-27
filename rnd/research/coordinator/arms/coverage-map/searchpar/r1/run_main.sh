#!/bin/bash
# SEARCHPAR R1 DENSE-RERANK MAIN 97 replay (0 LLM, MacBook): the F1b base (13-pack N10 kit, cooking/money from v3proto, RS_MERGE=gidf,
# {"packHeadPass":"a2","packDense2":"extra"}) on the rs-R1 clone. usage: run_main.sh <label> <off|cos|mix> [first-N-items]
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; D=$C/compose; H=$C/searchpar/r1
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=$B/kiln-local/rs-R1
L=$1; M=$2; N=${3:-}; OUT=$H/replays/main.$L.jsonl; t0=$(date +%s); cd $B
PK=$(python3 -I $D/tools/kits.py 10); PK=${PK//packs\/wave3\/qa-/packs\/v3proto\/qa-}
echo "$PK" | tr , '\n' > $OUT.packs
export RS_MERGE=gidf
[ "$M" != off ] && export RS_RERANK=$M && export RS_RERANK_LOG=$OUT.rerank.log && rm -f $OUT.rerank.log
Q=$R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl
T=$C/replay/funnel-K3.traces.jsonl
if [ -n "$N" ]; then head -n $N $Q > $H/replays/q$N.jsonl; Q=$H/replays/q$N.jsonl; fi
$TSX $TOOL --questions $Q --tree $TREE --packs $PK \
  --tasks-from $T --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"extra"}' --out $OUT 2> $OUT.err
echo "$L rc=$? $(( $(date +%s) - t0 ))s $(tail -1 $OUT.err | cut -c1-160)"
