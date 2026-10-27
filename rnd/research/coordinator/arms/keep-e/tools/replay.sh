#!/bin/bash
# KEEP-E step A replay (MacBook, 0 generation, 0 judge): stub llama-server + LITEPACKS adapter on kiln-local/be-0cfd4a77-cut7-litepacks-keepe,
# MAIN rows of arms/retfloor/req/MAIN.requests.jsonl, KEEP_E unset (base) vs 1. Detector :8094 must already be up (never started here).
# Usage: bash replay.sh <job dir> <port>
set -u
J=$1; PORT=$2; B=<workspace>; MD=$B/shared-models/emergency-detector; SRV=$B/spikes/llama-b11010-cpu/bin/llama-server
TL=$(cd $(dirname $0) && pwd); RQ=$B/rnd/research/coordinator/arms/retfloor/req/MAIN.requests.jsonl; T=$B/kiln-local/be-0cfd4a77-cut7-litepacks-keepe
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down (not started here)"; exit 1; }
cd $T || exit 1; echo "tree answer.ts=$(shasum -a 256 src/routing/answer.ts | cut -c1-16)"
python3 -I $TL/stub_server.py $PORT $B/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf 2>/dev/null & STUB=$!; trap 'kill $STUB 2>/dev/null' EXIT; sleep 1
export BOAR_EVAL_PACK_DIRS=$B/shared-data/packs/v3proto:$B/shared-data/packs/wave3:$B/shared-data/packs/wave2:$B/shared-data/packs/wave1:$B/shared-data/packs:$B/shared-data/crypto
export BOAR_SHARED_MODELS=$B/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
  BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5
mkdir -p $J
for V in base E; do O=$J/$V-MAIN; t0=$(date +%s); if [ $V = E ]; then export KEEP_E=1; else unset KEEP_E; fi
  be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests $RQ --out $O.traces.jsonl \
    --backend server --server-bin $SRV --server-url http://127.0.0.1:$PORT --dump-prompts $O.prompts.jsonl --threads 4 --timeout-ms 600000 > $O.log 2>&1
  echo "$V rc=$? rows=$(wc -l < $O.traces.jsonl | tr -d ' ') $(( $(date +%s) - t0 ))s"
done; echo DONE
