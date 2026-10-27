#!/bin/bash
# SEFIX MAIN 97 replay (0 LLM, MacBook): the COMPOSE N10 gidf recipe on kiln-local/rs-SEFIX. usage: run_main.sh <label> [VAR=val ...]   (switches via env; RS_MERGE=gidf always)
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; D=$C/sefix
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=${TREE:-$B/kiln-local/rs-SEFIX}
LAB=$1; shift; OUT=$D/replays/main.$LAB.jsonl; t0=$(date +%s); cd $B
PK=$(python3 -I $C/compose/tools/kits.py 10)
env RS_MERGE=gidf "$@" $TSX $TOOL --questions $R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $PK \
  --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err
echo "$LAB rc=$? $(( $(date +%s) - t0 ))s [$*] $(tail -1 $OUT.err | cut -c1-160)"
