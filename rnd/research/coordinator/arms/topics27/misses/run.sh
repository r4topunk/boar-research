#!/bin/bash
# VITAL-MISSES replay (0 LLM, MacBook). usage: run.sh <label> <tree-dir-name> <questions.jsonl> [ENV=VAL ...]
set -u
B=<workspace>; A=$B/rnd/research/coordinator/arms; D=$A/topics27
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$A/retrieve-sweep/tools/replay-sweep.ts
L=$1; TREE=$B/kiln-local/$2; Q=$3; shift 3; OUT=$D/replay/misses.$L.jsonl; t0=$(date +%s); cd $B
env "$@" $TSX $TOOL --questions $Q --tree $TREE --packs $B/shared-data/packs/wiki-vital5.sqlite --corpus essential \
  --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 --gate search \
  --forward-opts --settings-json '{"quickFirst":true,"alwaysComplete":false,"packHeadPass":"a2","packDense2":"append-budget","personalityId":"detailed"}' \
  --out $OUT 2> $OUT.err
echo "$L rc=$? $(( $(date +%s) - t0 ))s $(tail -1 $OUT.err | cut -c1-200)"
