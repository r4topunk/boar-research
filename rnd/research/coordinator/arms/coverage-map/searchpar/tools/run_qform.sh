#!/bin/bash
# SEARCHPAR QFORM 432 six-file replay (0 LLM, MacBook): the g2-fullkit v2-off recipe (six wave A-union packs, stock settings, gate search) on rs-R34.
# usage: run_qform.sh <label> [VAR=val ...]   (RS_MERGE=gidf is passed by the caller as VAR)
set -u
B=<workspace>; R=$B/rnd/research/coordinator/arms/retrieve-sweep; D=$B/rnd/research/coordinator/arms/coverage-map/searchpar
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
S=$B/shared-data
PK=$S/packs/wave2/boar-factbook.sqlite,$S/packs/wave1/boar-firstaid-en.sqlite,$S/packs/wave1/boar-medlineplus-en.sqlite,$S/crypto/boar-crypto.sqlite,$S/packs/boar-wikivoyage-en.sqlite,$S/packs/wave4/boar-visa-en.sqlite
LAB=$1; shift; OUT=$D/replays/qform.$LAB.jsonl; t0=$(date +%s); cd $B
env "$@" $B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx $R/tools/replay-sweep.ts --questions $R/../qform/items/qform.questions.jsonl \
  --tree $B/kiln-local/rs-R34 --packs $PK --gate search --cpu-embed --wide 12 --out $OUT 2> $OUT.err
echo "$LAB rc=$? $(( $(date +%s) - t0 ))s [$*] $(tail -1 $OUT.err | cut -c1-120)"
