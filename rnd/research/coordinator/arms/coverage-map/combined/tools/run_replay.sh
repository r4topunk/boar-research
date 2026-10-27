#!/bin/bash
# COMBINED MAIN 97 replay (0 LLM, MacBook) = sefix/tools/run_main.sh (SEFIX-ALL recipe: kits.py 10, packHeadPass a2, packDense2 append-budget, funnel-K3 tasks) on kiln-local/rs-COMBINED (H4 + SEFIX-ALL + RD1).
# usage: run_replay.sh <label> <0|1>   (1 = BOAR_READ_SEQ=1, 0 = unset = switch-off identity run); the four SEFIX switches are always on; RS_MERGE=gidf.
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; D=$C/combined
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=$B/kiln-local/rs-COMBINED
LAB=$1; SW=$2; OUT=$D/replays/main.$LAB.jsonl; t0=$(date +%s); cd $B
PK=$(python3 -I $C/compose/tools/kits.py 10)
unset BOAR_READ_SEQ; [ "$SW" = 1 ] && export BOAR_READ_SEQ=1
env RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_HEALTH_NOSOURCE_FALLBACK=1 RS_KEEP_NOPROPER=1 $TSX $TOOL --questions $R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $PK \
  --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err
echo "$LAB rc=$? $(( $(date +%s) - t0 ))s sw=$SW $(tail -1 $OUT.err | cut -c1-160)"
