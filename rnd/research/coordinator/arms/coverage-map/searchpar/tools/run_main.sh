#!/bin/bash
# SEARCHPAR R3/R4 MAIN 97 replay (0 LLM, MacBook): the F1b recipe (13-pack kit, v3 cooking/money, RS_MERGE=gidf, packHeadPass a2 + packDense2 extra) on kiln-local/rs-R34.
# usage: run_main.sh <label> [VAR=val ...]   (arm switches via env; extra args --ids a,b via IDS=)
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; D=$C/searchpar
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=${TREE:-$B/kiln-local/rs-R34}
LAB=$1; shift; OUT=$D/replays/main.$LAB.jsonl; t0=$(date +%s); cd $B
PK=$(python3 -I $C/compose/tools/kits.py 10); PK=${PK//packs\/wave3\/qa-/packs\/v3proto\/qa-}
IDARG=(); [ -n "${IDS:-}" ] && IDARG=(--ids "$IDS")
env RS_MERGE=gidf "$@" $TSX $TOOL --questions $R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $PK ${IDARG[@]+"${IDARG[@]}"} \
  --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"extra"}' --out $OUT 2> $OUT.err
echo "$LAB rc=$? $(( $(date +%s) - t0 ))s [$*] $(tail -1 $OUT.err | cut -c1-160)"
