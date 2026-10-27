#!/bin/bash
# SEARCHPAR R1 QFORM 432 six-file replay (0 LLM, MacBook): the G2-FULLKIT v3-extra recipe (six A-union packs from v3proto, {"packHeadPass":"a2","packDense2":"extra"}) on rs-R1.
# usage: run_qform.sh <label> <off|cos|mix>
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms/retrieve-sweep; H=$B/rnd/research/coordinator/arms/coverage-map/searchpar/r1
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
V3=$B/shared-data/packs/v3proto
PK=$V3/boar-factbook.sqlite,$V3/boar-firstaid-en.sqlite,$V3/boar-medlineplus-en.sqlite,$V3/boar-crypto.sqlite,$V3/boar-wikivoyage-en.sqlite,$V3/boar-visa-en.sqlite
L=$1; M=$2; OUT=$H/replays/qform.$L.jsonl; t0=$(date +%s); cd $B
[ "$M" != off ] && export RS_RERANK=$M && export RS_RERANK_LOG=$OUT.rerank.log && rm -f $OUT.rerank.log
$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx $R/tools/replay-sweep.ts --questions $R/../qform/items/qform.questions.jsonl \
  --tree $B/kiln-local/rs-R1 --packs $PK --gate search --cpu-embed --wide 12 --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"extra"}' --out $OUT 2> $OUT.err
echo "$L rc=$? $(( $(date +%s) - t0 ))s $(tail -1 $OUT.err | cut -c1-160)"
