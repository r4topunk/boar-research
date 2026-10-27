#!/bin/bash
# W78B part B (0 LLM, MacBook): the 216 QFORM items (factbook / firstaid / medlineplus), 3 v3proto packs, packDense2 true|extra, tree kiln-local/rs-W78.
# usage: run_w78b_q.sh <label> <true|extra> <denseBinN|0>
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; W=$C/w78
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
TSX=$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx; TOOL=$R/retrieve-sweep/tools/replay-sweep.ts; TREE=$B/kiln-local/rs-W78
LAB=$1; MODE=$2; DBIN=$3; OUT=$W/replays-b/qform.$LAB.jsonl; t0=$(date +%s); cd $B
V3=$B/shared-data/packs/v3proto
PK=$V3/boar-factbook.sqlite,$V3/boar-firstaid-en.sqlite,$V3/boar-medlineplus-en.sqlite
rm -f $OUT.denselog
EXTRA="RS_SE_LEAD_BIN_DIR=$W/sidecars RS_DENSE_LOG=$OUT.denselog"; [ "$DBIN" != 0 ] && EXTRA="$EXTRA RS_DENSE_BIN=$DBIN"
[ "$MODE" = true ] && SET='{"quickFirst":true,"alwaysComplete":false,"packDense2":true}' || SET='{"quickFirst":true,"alwaysComplete":false,"packDense2":"extra"}'
env $EXTRA $TSX $TOOL --questions $R/retrieve-sweep/g-chunkvecs/q3.jsonl --tree $TREE --packs $PK --cpu-embed --wide 12 \
  --forward-opts --settings-json "$SET" --out $OUT 2> $OUT.err
echo "$LAB rc=$? $(( $(date +%s) - t0 ))s $(tail -1 $OUT.err | cut -c1-200)"
