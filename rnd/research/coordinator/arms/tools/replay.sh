#!/usr/bin/env bash
# replay.sh <tree> <name>: retrieval-only replay with the stub LLM on :18500 (Sonar exp-34 method)
set -e; T=$1; N=$2; R=$(cd "$(dirname "$0")" && pwd)
cd $T && BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs:<workspace>/shared-data/crypto be/node_modules/.bin/tsx be/adapter.ts --requests $R/$N.requests.jsonl --out $R/$N.traces.jsonl --backend server --server-bin <scratch> --server-url http://127.0.0.1:18500 --event-source-text --threads 4 > $R/$N.log 2>&1
tail -1 $R/$N.log | cut -c1-100
