#!/bin/bash
# ROUTING-R1 step A replay (MacBook, 0 generation, 0 judge): stub llama-server + the LITEPACKS adapter (LITEDECLINE_OFF=5) on the patched
# tree kiln-local/be-0cfd4a77-cut7-litepacks-routingr1, ROUTING_R1 = off | P | T | H. Detector :8094 must be up (never started here).
# Usage: bash replay.sh <job dir with req/{K1,K3}-{v01,cm,probes}.requests.jsonl + stub_server.py>
set -u
J=$1; B=<workspace>; MD=$B/shared-models/emergency-detector; SRV=$B/spikes/llama-b11010-cpu/bin/llama-server
T=$B/kiln-local/be-0cfd4a77-cut7-litepacks-routingr1
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down"; exit 1; }
cd $T || exit 1
echo "tree answer.ts=$(shasum -a 256 src/routing/answer.ts | cut -c1-16) adapter=$(shasum -a 256 be/adapter-litedecline.ts | cut -c1-16)"
PORT=18779; python3 -I $J/stub_server.py $PORT $B/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf & STUB=$!; trap 'kill $STUB 2>/dev/null' EXIT; sleep 1
export BOAR_EVAL_PACK_DIRS=$B/shared-data/packs/v3proto:$B/shared-data/packs/wave3:$B/shared-data/packs/wave2:$B/shared-data/packs/wave1:$B/shared-data/packs:$B/shared-data/crypto
export BOAR_SHARED_MODELS=$B/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
  BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5
for F in off P T H; do for SET in K1-v01 K1-cm K1-probes K3-v01 K3-cm K3-probes; do
  O=$J/out/$F-$SET; [ -s $O.traces.jsonl ] && [ "$(wc -l < $O.traces.jsonl)" = "$(wc -l < $J/req/$SET.requests.jsonl)" ] && continue
  rm -f $O.traces.jsonl; t0=$(date +%s)
  if [ $F = off ]; then unset ROUTING_R1; else export ROUTING_R1=$F; fi
  be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests $J/req/$SET.requests.jsonl --out $O.traces.jsonl \
    --backend server --server-bin $SRV --server-url http://127.0.0.1:$PORT --threads 4 --timeout-ms 600000 > $O.log 2>&1
  echo "$F $SET rc=$? rows=$(wc -l < $O.traces.jsonl | tr -d ' ') $(( $(date +%s) - t0 ))s"
done; done
echo DONE
