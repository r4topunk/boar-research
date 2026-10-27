#!/bin/bash
# Re-run one item (lan-exp-007) on a given tree with prompt dump: rerun_one.sh <tree dir> <requests> <out traces>
set -u
T=$1; REQ=$2; OUT=$3; MD=<workspace>/shared-models/emergency-detector; SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server
busy() { pgrep -fl llama-server | grep -v -- "--port 8094" | grep -q . || pgrep -f "be/adapter.ts" >/dev/null; }
w=0; while busy; do w=$((w+1)); [ $w -gt 60 ] && exit 2; sleep 60; done
cd "$T" || exit 1
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
be/node_modules/tsx/dist/cli.mjs be/adapter.ts --requests "$REQ" --out "$OUT" --backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000 --dump-prompts "${OUT%.traces.jsonl}.prompts.jsonl" > "${OUT%.jsonl}.log" 2>&1
