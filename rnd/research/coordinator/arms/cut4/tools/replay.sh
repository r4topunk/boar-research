#!/usr/bin/env bash
# replay.sh <tree> <requests.jsonl> <out.traces.jsonl>: stub-LLM retrieval replay, kit A (crypto+wikivoyage), no detector, no places
set -e; B=<workspace>; T=$1; REQ=$2; OUT=$3
S=<scratch>
cd $T && BOAR_SHARED_MODELS=$B/shared-models BOAR_EVAL_PACK_DIRS=$B/shared-data/packs:$B/shared-data/crypto be/node_modules/.bin/tsx be/adapter.ts --requests $REQ --out $OUT --backend server --server-bin $S/llama.cpp/build/bin/llama-server --server-url http://127.0.0.1:18500 --event-source-text --threads 4 > $OUT.log 2>&1
tail -1 $OUT.log | cut -c1-120
