#!/bin/bash
# RAG-FUNNEL replay on the MacBook (0 generation, 0 judge): as factpresent_replay.sh (stub llama-server + the real LITEPACKS adapter,
# LITEDECLINE_OFF=5, RETFLOOR_VARIANT=base) on a clone of the FACTPRESENT replay tree plus apply_funnel.py (logging only: raw, dense, compressed ids).
# Sets: K0/K1/K3 x V01 + CM (MAIN 97). Detector :8094 must already be up (never started here).
# Usage: bash ragfunnel_replay.sh <job dir with req/<K>-V01|CM.requests.jsonl and stub_server.py> <retfloor-fp tree to clone>
set -u
J=$1; SRC=$2; B=<workspace>; MD=$B/shared-models/emergency-detector; SRV=$B/spikes/llama-b11010-cpu/bin/llama-server
TL=$(cd $(dirname $0) && pwd)
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down (not started here)"; exit 1; }
T=$J/be-0cfd4a77-cut7-litepacks-retfloor-funnel
if [ ! -d $T ]; then cp -c -R $SRC $T && rm -rf $T/be/.cache && python3 -I $TL/apply_funnel.py $T || { echo "FAIL tree"; exit 1; }; fi
cd $T || exit 1
echo "tree answer.ts=$(shasum -a 256 src/routing/answer.ts | cut -c1-16) adapter=$(shasum -a 256 be/adapter-litedecline.ts | cut -c1-16)"
PORT=18778; python3 -I $J/stub_server.py $PORT $B/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf & STUB=$!; trap 'kill $STUB 2>/dev/null' EXIT; sleep 1
export BOAR_EVAL_PACK_DIRS=$B/shared-data/packs/v3proto:$B/shared-data/packs/wave3:$B/shared-data/packs/wave2:$B/shared-data/packs/wave1:$B/shared-data/packs:$B/shared-data/crypto
export BOAR_SHARED_MODELS=$B/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
  BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5
mkdir -p $J/out
for SET in K0-V01 K0-CM K1-V01 K1-CM K3-V01 K3-CM; do
  O=$J/out/$SET; [ -s $O.traces.jsonl ] && [ "$(wc -l < $O.traces.jsonl)" = "$(wc -l < $J/req/$SET.requests.jsonl)" ] && continue
  rm -f $O.traces.jsonl $O.prompts.jsonl; t0=$(date +%s)
  RETFLOOR_VARIANT=base be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests $J/req/$SET.requests.jsonl --out $O.traces.jsonl \
    --backend server --server-bin $SRV --server-url http://127.0.0.1:$PORT --dump-prompts $O.prompts.jsonl --threads 4 --timeout-ms 600000 > $O.log 2>&1
  echo "$SET rc=$? rows=$(wc -l < $O.traces.jsonl | tr -d ' ') $(( $(date +%s) - t0 ))s"
done
echo DONE
