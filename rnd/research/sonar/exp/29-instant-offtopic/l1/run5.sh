#!/bin/bash
D=$(pwd)
for job in and:main:be-0cfd4a77 and:health3:be-0cfd4a77-health3 and:health5:be-0cfd4a77-health5 ios:main:be-0cfd4a77 ios:health3:be-0cfd4a77-health3 ios:health5:be-0cfd4a77-health5; do
  IFS=: read p a t <<< "$job"
  (cd <scratch> && BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs:<workspace>/shared-data/crypto be/node_modules/.bin/tsx be/adapter.ts --requests $D/$p-$a-h5.requests.jsonl --out $D/$p-$a-h5.traces.jsonl --gpu --timeout-ms 120000 > $D/$p-$a-h5.log 2>&1)
  echo "$p-$a rc $? $(tail -1 $D/$p-$a-h5.log | cut -c1-60)"
done
