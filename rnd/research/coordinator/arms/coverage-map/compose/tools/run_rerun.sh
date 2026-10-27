#!/bin/bash
# COMPOSE replay (0 LLM, MacBook): MAIN 97 questions, funnel K1 traces as --tasks-from, rs-H4 clone, K3 settings, exactly the h4-merge MAIN recipe.
# usage: run_compose.sh <N> <stock|gidf>   (RS_MERGE set only for gidf)
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; D=$C/compose
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=$B/kiln-local/rs-H4
N=$1; V=$2; OUT=$D/replays/rerun/main.N$N.$V.jsonl; t0=$(date +%s); cd $B
PK=$(python3 -I $D/tools/kits.py $N)
if [ "$V" = gidf ]; then export RS_MERGE=gidf; else unset RS_MERGE; fi
$TSX $TOOL --questions $R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $PK \
  --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err
echo "N=$N $V rc=$? $(( $(date +%s) - t0 ))s RS_MERGE=${RS_MERGE:-unset} $(tail -1 $OUT.err | cut -c1-160)"
