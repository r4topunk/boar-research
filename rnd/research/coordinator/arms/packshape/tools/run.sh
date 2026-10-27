#!/bin/bash
# PACKSHAPE replay (0 LLM, MacBook; NOWIKI run.sh recipe). usage: run.sh <main|st> <BASE|SHAPED|FASHAPED>
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; D=$R/packshape
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=$B/kiln-local/rs-SEFIX
SET=$1; KIT=$2; t0=$(date +%s); cd $B; mkdir -p $D/replay
ENV="RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1"
PK=$(python3 -I $D/tools/kits.py $KIT)
case $SET in
 main) OUT=$D/replay/main.$KIT.jsonl
   env $ENV $TSX $TOOL --questions $R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $TREE --packs $PK \
     --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
     --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err ;;
 st) OUT=$D/replay/st.$KIT.on-k13.jsonl
   env $ENV $TSX $TOOL --questions $R/packproof/in/on-k13.requests.jsonl --tree $TREE --packs $PK \
     --tasks-from $R/packproof/gen/on-k13/traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
     --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $OUT 2> $OUT.err ;;
esac
echo "$SET $KIT rc=$? $(( $(date +%s) - t0 ))s $(tail -1 $OUT.err | cut -c1-200)"
