#!/bin/bash
# U5 FOLLOWUP-PACKS replay (0 LLM, MacBook). usage: run_u5.sh <qform|longsession> <label> <BASE|ON> <carry 0|2> [drop-pack-name]   (IDS=a,b env limits ids; TREE env overrides)
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; R5=$C/searchpar/r5; D=$R/uxmatrix/u5
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx
SET=$1; L=$2; ARM=$3; CY=$4; DROP=${5:-}; TREE=${TREE:-$B/kiln-local/rs-U5}; IDS=${IDS:-}
OUT=$D/replays/$SET.$L.jsonl; t0=$(date +%s); cd $B
PK=$(python3 -I $C/compose/tools/kits.py 10)
if [ -n "$DROP" ]; then PK=$(echo "$PK" | tr ',' '\n' | grep -v "/$DROP.sqlite\$" | paste -sd, -); fi
unset RS_MERGE RS_SE_LEAD RS_SE_MAXDF RS_KEEP_NOPROPER RS_HEALTH_NOSOURCE_FALLBACK RS_STICKY
[ "$ARM" = ON ] && export RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1
[ "$CY" != 0 ] && export RS_STICKY=$CY
EXTRA=(); [ -n "$IDS" ] && EXTRA=(--ids $IDS)
echo "$PK" > $OUT.packs
$TSX $R5/tools/replay-sticky.ts --questions $R5/$SET.chain.jsonl --tree $TREE --packs $PK --gate search --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 0 \
  --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' ${EXTRA[@]+"${EXTRA[@]}"} --out $OUT 2> $OUT.err
echo "$SET $L rc=$? $(( $(date +%s) - t0 ))s packs=$(echo $PK | tr ',' '\n' | wc -l | tr -d ' ') $(tail -1 $OUT.err | cut -c1-160)"
