#!/bin/bash
# KEEP-K1 replay on the MacBook (0 generation, 0 judge): stub llama-server + the real LITEPACKS adapter (LITEDECLINE_OFF=5) on a clone of
# the RAG-FUNNEL tree (litepacks + apply_retfloor.py + apply_funnel.py) plus apply_keep.py. Sets = arms/retfloor/req (MAIN 100 rows incl.
# MAIN 97 + 9 PM files = the 180 self-tests, each with its own pack). Detector :8094 must already be up (never started here).
# Usage: bash keep_replay.sh <job dir> <funnel tree> <port> <KEEP_VARIANT/RETFLOOR_VARIANT pairs, e.g. D4B/base base/V1orC ...>
set -u
J=$1; SRC=$2; PORT=$3; shift 3; B=<workspace>; MD=$B/shared-models/emergency-detector; SRV=$B/spikes/llama-b11010-cpu/bin/llama-server
TL=$(cd $(dirname $0) && pwd); RQ=$B/rnd/research/coordinator/arms/retfloor/req
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down (not started here)"; exit 1; }
T=$J/be-0cfd4a77-cut7-litepacks-keep
if [ ! -d $T ]; then mkdir -p $J; cp -c -R $SRC $T && rm -rf $T/be/.cache && python3 -I $TL/apply_keep.py $T || { echo "FAIL tree"; exit 1; }; fi
cd $T || exit 1
echo "tree answer.ts=$(shasum -a 256 src/routing/answer.ts | cut -c1-16)"
python3 -I $TL/stub_server.py $PORT $B/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf 2>/dev/null & STUB=$!; trap 'kill $STUB 2>/dev/null' EXIT; sleep 1
export BOAR_EVAL_PACK_DIRS=$B/shared-data/packs/v3proto:$B/shared-data/packs/wave3:$B/shared-data/packs/wave2:$B/shared-data/packs/wave1:$B/shared-data/packs:$B/shared-data/crypto
export BOAR_SHARED_MODELS=$B/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
  BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5
mkdir -p $J/out
for PAIR in "$@"; do KV=${PAIR%/*}; RF=${PAIR#*/}; for SET in $(cd $RQ && ls *.requests.jsonl | sed "s/.requests.jsonl//"); do
  O=$J/out/$KV+$RF-$SET; [ -s $O.traces.jsonl ] && [ "$(wc -l < $O.traces.jsonl)" = "$(wc -l < $RQ/$SET.requests.jsonl)" ] && continue
  rm -f $O.traces.jsonl $O.prompts.jsonl; t0=$(date +%s)
  KEEP_VARIANT=$KV RETFLOOR_VARIANT=$RF be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests $RQ/$SET.requests.jsonl --out $O.traces.jsonl \
    --backend server --server-bin $SRV --server-url http://127.0.0.1:$PORT --dump-prompts $O.prompts.jsonl --threads 4 --timeout-ms 600000 > $O.log 2>&1
  echo "$KV+$RF $SET rc=$? rows=$(wc -l < $O.traces.jsonl | tr -d ' ') $(( $(date +%s) - t0 ))s"
done; done
echo DONE
