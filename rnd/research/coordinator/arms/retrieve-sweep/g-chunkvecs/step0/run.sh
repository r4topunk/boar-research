#!/bin/bash
# Step 0 (0 LLM, MacBook): MAIN 97 replay, K1 kit (crypto v2, wikivoyage v2, simplewiki v3proto), packDense2 true. $1 = out, $2 = settings json
B=<workspace>; R=$B/rnd/research/coordinator/arms/retrieve-sweep
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
cd $B
$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx $R/tools/replay-sweep.ts \
  --questions $R/../decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $B/kiln-local/be-0cfd4a77-cut7-litepacks \
  --packs $B/shared-data/crypto/boar-crypto.sqlite,$B/shared-data/packs/boar-wikivoyage-en.sqlite,$B/shared-data/packs/v3proto/boar-simplewiki-en.sqlite \
  --tasks-from $R/replay/funnel-K1.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json "$2" --out $1
