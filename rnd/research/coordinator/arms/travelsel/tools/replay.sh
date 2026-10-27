#!/usr/bin/env bash
# replay.sh <tree> <requests.jsonl> <out.traces.jsonl> [port]: stub-LLM retrieval replay, kit A (crypto+wikivoyage) + V-exact places, no detector
set -e; B=<workspace>; T=$1; REQ=$2; OUT=$3; PORT=${4:-18500}
LL=<scratch>
K=$B/shared-data/poi/kit-vexact
cd $T && BOAR_SHARED_MODELS=$B/shared-models BOAR_EVAL_PACK_DIRS=$B/shared-data/packs:$B/shared-data/crypto be/node_modules/.bin/tsx be/adapter.ts --requests $REQ --out $OUT --backend server --server-bin $LL --server-url http://127.0.0.1:$PORT --event-source-text --threads 4 --places $K/world-places.sqlite,$K/t-N52E013.sqlite,$K/t-N38W010.sqlite,$K/t-N35E139.sqlite,$K/t-N35E140.sqlite > $OUT.log 2>&1
tail -1 $OUT.log | cut -c1-120
