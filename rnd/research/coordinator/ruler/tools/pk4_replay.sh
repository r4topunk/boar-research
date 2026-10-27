#!/bin/bash
# PK-4 PACK-PRUNE replay on the MacBook (0 generation, 0 judge): the RAG-FUNNEL tree (FACTPRESENT retfloor-fp tree + apply_funnel.py,
# logging only) on the A-union (KA) requests of arms/coverage-matrix/req, stub llama-server. boar-visa-en resolves from wave4, appended LAST to
# BOAR_EVAL_PACK_DIRS (= the effect of arms/coverage-matrix/kadirs.patch, whose ${HOME}/boar path does not exist on the MacBook).
# Detector :8094 must already be up (never started here). Runs every req/<SET>.requests.jsonl not yet complete in out/.
# Usage: bash pk4_replay.sh <job dir with req/ and stub_server.py> <funnel tree to clone (be-0cfd4a77-cut7-litepacks-retfloor-funnel)>
set -u
J=$1; SRC=$2; B=<workspace>; MD=$B/shared-models/emergency-detector; SRV=$B/spikes/llama-b11010-cpu/bin/llama-server
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down (not started here)"; exit 1; }
T=$J/be-funnel-pk4
if [ ! -d $T ]; then cp -c -R $SRC $T && rm -rf $T/be/.cache || { echo "FAIL tree"; exit 1; }; fi
cd $T || exit 1
echo "tree answer.ts=$(shasum -a 256 src/routing/answer.ts | cut -c1-16) adapter=$(shasum -a 256 be/adapter-litedecline.ts | cut -c1-16)"
PORT=18779; python3 -I $J/stub_server.py $PORT $B/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf & STUB=$!; trap 'kill $STUB 2>/dev/null' EXIT; sleep 1
export BOAR_EVAL_PACK_DIRS=$B/shared-data/packs/v3proto:$B/shared-data/packs/wave3:$B/shared-data/packs/wave2:$B/shared-data/packs/wave1:$B/shared-data/packs:$B/shared-data/crypto:$B/shared-data/packs/wave4
export BOAR_SHARED_MODELS=$B/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
  BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5
mkdir -p $J/out
for SET in $(cd $J/req && ls *.requests.jsonl | sed "s/.requests.jsonl//"); do
  O=$J/out/$SET; [ -s $O.traces.jsonl ] && [ "$(wc -l < $O.traces.jsonl)" = "$(wc -l < $J/req/$SET.requests.jsonl)" ] && continue
  rm -f $O.traces.jsonl $O.prompts.jsonl; t0=$(date +%s)
  RETFLOOR_VARIANT=base be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests $J/req/$SET.requests.jsonl --out $O.traces.jsonl \
    --backend server --server-bin $SRV --server-url http://127.0.0.1:$PORT --dump-prompts $O.prompts.jsonl --threads 4 --timeout-ms 600000 > $O.log 2>&1
  echo "$SET rc=$? rows=$(wc -l < $O.traces.jsonl | tr -d ' ') $(( $(date +%s) - t0 ))s"
done
echo DONE
