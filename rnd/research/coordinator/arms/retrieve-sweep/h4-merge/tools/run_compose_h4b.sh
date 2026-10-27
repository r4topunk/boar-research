#!/bin/bash
# H4b COMPOSE replay (0 LLM, MacBook): same recipe as coverage-map/compose/tools/run_compose.sh, TREE = rs-H4b, output in h4-merge/replays.
# usage: run_compose_h4b.sh <N> <label> ; RS_MERGE from the caller's env (unset = stock)
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; D=$C/compose; H=$R/retrieve-sweep/h4-merge
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=$B/kiln-local/rs-H4b
N=$1; V=$2; OUT=$H/replays/compose.N$N.$V.jsonl; t0=$(date +%s); cd $B
PK=$(python3 -I $D/tools/kits.py $N)
$TSX $TOOL --questions $R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $PK \
  --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err
echo "compose N=$N $V rc=$? $(( $(date +%s) - t0 ))s RS_MERGE=${RS_MERGE:-unset} $(tail -1 $OUT.err | cut -c1-120)"
