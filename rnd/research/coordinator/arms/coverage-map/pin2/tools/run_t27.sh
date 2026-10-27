#!/bin/bash
# PIN2 27-topic replay (0 LLM, MacBook): topics27/misses/run.sh recipe (wiki-vital5 + essential, SEFIX-124 env) on kiln-local/rs-PIN2. usage: run_t27.sh <label> [VAR=val ...]
set -u
B=<workspace>; A=$B/rnd/research/coordinator/arms; D=$A/coverage-map/pin2
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$A/retrieve-sweep/tools/replay-sweep.ts
L=$1; shift; TREE=$B/kiln-local/rs-PIN2; Q=$A/topics27/in/t27-detailed-s42.requests.jsonl; OUT=$D/replays/t27.$L.jsonl; t0=$(date +%s); cd $B
env RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1 "$@" $TSX $TOOL --questions $Q --tree $TREE --packs $B/shared-data/packs/wiki-vital5.sqlite --corpus essential \
  --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 --gate search \
  --forward-opts --settings-json '{"quickFirst":true,"alwaysComplete":false,"packHeadPass":"a2","packDense2":"append-budget","personalityId":"detailed"}' \
  --out $OUT 2> $OUT.err
echo "$L rc=$? $(( $(date +%s) - t0 ))s [$*] $(tail -1 $OUT.err | cut -c1-200)"
