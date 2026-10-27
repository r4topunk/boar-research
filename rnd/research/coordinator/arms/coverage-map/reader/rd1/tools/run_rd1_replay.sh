#!/bin/bash
# RD1 replay (0 LLM, MacBook): F1b configuration (MAIN 97, funnel-K3 traces, rs-RD1 clone = H4 + RD1, RS_MERGE=gidf, 13-pack kit, v3 cooking/money, packHeadPass a2 + packDense2 extra).
# usage: run_rd1_replay.sh <label> <0|1>   (1 = BOAR_READ_SEQ=1, 0 = unset)
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; D=$C/compose
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=$B/kiln-local/rs-RD1
L=$1; SW=$2; OUT=$C/reader/rd1/replays/main.$L.jsonl; t0=$(date +%s); cd $B
PK=$(python3 -I $D/tools/kits.py 10); PK=${PK//packs\/wave3\/qa-/packs\/v3proto\/qa-}
echo "$PK" | tr , '\n' > $OUT.packs
export RS_MERGE=gidf; unset BOAR_READ_SEQ; [ "$SW" = 1 ] && export BOAR_READ_SEQ=1
$TSX $TOOL --questions $R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $PK \
  --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json "{\"packHeadPass\":\"a2\",\"packDense2\":\"extra\"}" --out $OUT 2> $OUT.err
echo "$L rc=$? $(( $(date +%s) - t0 ))s $(tail -1 $OUT.err | cut -c1-160)"
