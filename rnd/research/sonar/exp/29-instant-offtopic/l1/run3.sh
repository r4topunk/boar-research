#!/bin/bash
D=$(pwd)
for job in and:main:be-0cfd4a77 and:instguard3:be-0cfd4a77-instguard3 and:instguard4:be-0cfd4a77-instguard4 ios:main:be-0cfd4a77 ios:instguard3:be-0cfd4a77-instguard3 ios:instguard4:be-0cfd4a77-instguard4; do
  IFS=: read p a t <<< "$job"
  (cd <scratch> && BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs:<workspace>/shared-data/crypto be/node_modules/.bin/tsx be/adapter.ts --requests $D/$p-$a-fb.requests.jsonl --out $D/$p-$a-fb.traces.jsonl --gpu --timeout-ms 120000 > $D/$p-$a-fb.log 2>&1)
  echo "$p-$a-fb rc $? $(tail -1 $D/$p-$a-fb.log | cut -c1-80)"
done
