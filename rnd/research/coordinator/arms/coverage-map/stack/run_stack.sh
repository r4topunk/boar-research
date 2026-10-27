#!/bin/bash
# STACK replay (0 LLM, MacBook): F1b base (13-pack N10 kit, cooking/money from v3proto, RS_MERGE=gidf, packHeadPass a2 + packDense2 extra) on kiln-local/rs-STACK
# (= rs-H4 + SEFIX-F1/F2/F4 + R1-RERANK). usage: run_stack.sh <label> <off|on> [first-N-items]
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; D=$C/compose; H=$C/stack
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=$B/kiln-local/rs-STACK
L=$1; M=$2; N=${3:-}; OUT=$H/replays/main.$L.jsonl; t0=$(date +%s); cd $B
PK=$(python3 -I $D/tools/kits.py 10); PK=${PK//packs\/wave3\/qa-/packs\/v3proto\/qa-}
echo "$PK" | tr , '\n' > $OUT.packs
export RS_MERGE=gidf
if [ "$M" = on ]; then export RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1 RS_RERANK=mix RS_RERANK_LOG=$OUT.rerank.log; rm -f $OUT.rerank.log; fi
Q=$R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl
T=$C/replay/funnel-K3.traces.jsonl
if [ -n "$N" ]; then head -n $N $Q > $H/replays/q$N.jsonl; Q=$H/replays/q$N.jsonl; fi
$TSX $TOOL --questions $Q --tree $TREE --packs $PK \
  --tasks-from $T --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"extra"}' --out $OUT 2> $OUT.err
echo "$L rc=$? $(( $(date +%s) - t0 ))s $(tail -1 $OUT.err | cut -c1-160)"
