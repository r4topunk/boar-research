#!/bin/bash
# usage: guard.sh <tree> <outdir>  -> packread (per-item pack) + v0.1 (claim kit) replays
cd <workspace>
T=$1; D=$2; mkdir -p $D
R="<workspace>/boar-eval/adapters/desktop-node/node_modules/.bin/tsx <scratch>/tools/replay2.ts"
PR=boar-eval/bench/slices/packread-v1/questions.jsonl
: > $D/packread.jsonl
for p in boar-factbook boar-firstaid-en boar-medlineplus-en boar-simplewiki-en qa-bitcoin-se qa-ethereum-se qa-health-se qa-outdoors-se qa-travel-se; do
  ids=$(python3 -I -c "import json,sys; print(','.join(json.loads(l)['id'] for l in open('$PR') if json.loads(l)['id'].startswith('st-$p-')))")
  $R --questions $PR --ids $ids --tree $T --packs shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite,shared-data/packs/v3proto/$p.sqlite --tasks-from $PWD/rnd/research/coordinator/arms/packread/traces/packread-anchor-engine.traces.jsonl --out $D/pr-$p.jsonl 2>&1 | grep '^{' 
  cat $D/pr-$p.jsonl >> $D/packread.jsonl
done
$R --questions boar-eval/bench/v0.1/questions.public.jsonl --tree $T --packs shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite --tasks-from $PWD/rnd/research/coordinator/arms/pr1/runs/v01-pr1-s42.traces.jsonl --out $D/v01.jsonl 2>&1 | grep '^{'
