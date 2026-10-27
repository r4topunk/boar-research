#!/bin/bash
# PRECISION-GATE 0-LLM replay on the MacBook (= compose/tools/run_compose.sh N=10 gidf, TREE=kiln-local/rs-GATE; env switches from the caller).
# usage: run_replay.sh <label>     (RS_MERGE=gidf always; RS_SCORE_GATE / DG_ARM from the caller's env)
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; D=$C/compose; G=$C/gate
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=${TREE:-$B/kiln-local/rs-GATE}
LAB=$1; OUT=$G/replays/$LAB.jsonl; t0=$(date +%s); cd $B
PK=$(python3 -I $D/tools/kits.py 10); export RS_MERGE=gidf
$TSX $TOOL --questions $R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $PK \
  --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err
echo "$LAB rc=$? $(( $(date +%s) - t0 ))s RS_SCORE_GATE=${RS_SCORE_GATE:-unset} DG_ARM=${DG_ARM:-unset} $(tail -1 $OUT.err | cut -c1-160)"
