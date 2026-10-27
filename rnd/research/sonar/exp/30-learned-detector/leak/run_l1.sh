#!/bin/bash
S=<scratch>; D=$(cd $(dirname $0); pwd)
for job in and:h9:health9 and:h10:health10 ios:h9:health9 ios:h10:health10; do IFS=: read p a t <<< "$job"
 (cd $S/be-0cfd4a77-$t && BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs:<workspace>/shared-data/crypto be/node_modules/.bin/tsx be/adapter.ts --requests $D/$1-$p.requests.jsonl --out $D/$1-$p-$a.traces.jsonl --gpu --timeout-ms 120000 > $D/$1-$p-$a.log 2>&1); echo "$p $a rc $?"
done
