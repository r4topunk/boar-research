#!/bin/bash
D=$(pwd)
for job in and:main:be-0cfd4a77 and:instguard:be-0cfd4a77-instguard ios:main:be-0cfd4a77 ios:instguard:be-0cfd4a77-instguard; do
  IFS=: read p a t <<< "$job"
  (cd <scratch> && BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs:<workspace>/shared-data/crypto be/node_modules/.bin/tsx be/adapter.ts --requests $D/$p-$a.requests.jsonl --out $D/$p-$a.traces.jsonl --gpu --timeout-ms 120000 > $D/$p-$a.log 2>&1)
  echo "$p-$a rc $? $(tail -1 $D/$p-$a.log | cut -c1-200)"
done
