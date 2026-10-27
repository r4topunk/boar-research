#!/bin/bash
D=$(pwd)
for job in and:main:be-0cfd4a77 and:instguard:be-0cfd4a77-instguard and:instguard2:be-0cfd4a77-instguard2 ios:main:be-0cfd4a77 ios:instguard:be-0cfd4a77-instguard ios:instguard2:be-0cfd4a77-instguard2; do
  IFS=: read p a t <<< "$job"
  (cd <scratch> && BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs:<workspace>/shared-data/crypto be/node_modules/.bin/tsx be/adapter.ts --requests $D/$p-$a-rep.requests.jsonl --out $D/$p-$a-rep.traces.jsonl --gpu --timeout-ms 120000 > $D/$p-$a-rep.log 2>&1)
  echo "$p-$a-rep rc $? $(tail -1 $D/$p-$a-rep.log | cut -c1-120)"
done
