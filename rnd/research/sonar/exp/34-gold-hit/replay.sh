#!/usr/bin/env bash
# replay.sh <tree> <name>: retrieval-only replay (stub LLM on :18500) of <scratch>>.requests.jsonl
set -e; T=$1; N=$2
cd $T && BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_EVAL_PACK_DIRS=<scratch> be/node_modules/.bin/tsx be/adapter.ts --requests <scratch> --out <scratch> --backend server --server-bin <scratch> --server-url http://127.0.0.1:18500 --event-source-text --threads 4 > <scratch> 2>&1
tail -1 <scratch> | cut -c1-80
