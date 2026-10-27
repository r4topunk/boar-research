#!/bin/bash
# ROUTING-R1 step B generation on the Mac mini (run there): patched LITEPACKS tree <runner>/kiln/be-0cfd4a77-cut7-litepacks-routingr1
# (answer.ts 5faaef76...), LITEDECLINE_OFF=5, Qwen3-1.7B Q4_K_M, --reasoning off, seed 42 (requests), K1 kit. The adapter starts its own
# llama-server on an OS-assigned port and stops it at exit. Detector :8094 used, never started/stopped. Disk guard >= 25 GiB.
# Usage: gen_mini.sh <job dir with req/r1-<F>-K1-cm-s42.requests.jsonl> P T H
set -u
J=$1; shift; B=$HOME/boar; T=$B/kiln/be-0cfd4a77-cut7-litepacks-routingr1; MD=$B/shared-models/emergency-detector; SRV=$B/spikes/llama-b11010/build-cpu/bin/llama-server
cd $T || exit 1
[ "$(shasum -a 256 src/routing/answer.ts | cut -c1-16)" = 5faaef7601e42497 ] || { echo "FAIL answer.ts sha"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector down"; exit 1; }
export BOAR_EVAL_PACK_DIRS=$B/shared-data/packs/v3proto:$B/shared-data/packs/wave3:$B/shared-data/packs/wave2:$B/shared-data/packs/wave1:$B/shared-data/packs:$B/shared-data/crypto
export BOAR_SHARED_MODELS=$B/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
  BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5
for F in "$@"; do
  FREE=$(df -k $HOME | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 25 ] || { echo "FAIL disk ${FREE} GiB < 25"; exit 1; }
  R=r1-$F-K1-cm-s42; export ROUTING_R1=$F
  be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests $J/req/$R.requests.jsonl --out $J/out/$R.traces.jsonl --backend server --server-bin $SRV --threads 4 --timeout-ms 600000 > $J/out/$R.log 2>&1
  echo "$F rc=$? rows=$(wc -l < $J/out/$R.traces.jsonl | tr -d ' ') free=${FREE}GiB"
done
echo ALLDONE
