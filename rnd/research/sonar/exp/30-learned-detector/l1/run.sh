#!/bin/bash
# health11 L1: detector = mmBERT-small v3b GGUF (q8_0 + q4_0 token table) via llama-server b11010 on :8094, JS head, frozen thr 0.2 (DETECTOR_THRESHOLD)
S=<scratch>; D=$(cd $(dirname $0); pwd); X=$(cd $D/..; pwd)
DET="BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://localhost:8094 BOAR_DETECTOR_HEAD=$X/results/mmbert-v3b.head.json"
for job in "$@"; do IFS=: read set p arm <<< "$job"
  tree=$S/be-0cfd4a77-$arm; envs=""; case "$arm" in health11|health13) envs="$DET";; esac
  (cd $tree && env $envs BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs:<workspace>/shared-data/crypto be/node_modules/.bin/tsx be/adapter.ts --requests $D/$set-$p-$arm.requests.jsonl --out $D/$set-$p-$arm.traces.jsonl --gpu --timeout-ms 120000 > $D/$set-$p-$arm.log 2>&1)
  echo "$set $p $arm rc $? $(date +%H:%M)"
done
