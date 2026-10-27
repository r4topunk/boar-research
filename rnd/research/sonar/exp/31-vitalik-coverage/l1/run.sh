#!/bin/bash
# exp-31 probe run: 12 the post author-class probe questions, clean engine 0cfd4a77 (main), iPhone profile (1.5B), kit A and kit A + vital5.
D=$(cd "$(dirname "$0")" && pwd)
T=<scratch>
for k in a v5; do
  (cd $T && BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs:<workspace>/shared-data/crypto be/node_modules/.bin/tsx be/adapter.ts --requests $D/ios-$k.requests.jsonl --out $D/ios-$k.traces.jsonl --gpu --event-source-text --timeout-ms 120000 > $D/ios-$k.log 2>&1)
  echo "ios-$k rc $? $(tail -1 $D/ios-$k.log | cut -c1-200)"
done
