#!/bin/bash
# KEEP-E step B generation on the Mac mini (run there with bash): patched LITEPACKS tree <runner>/kiln/be-0cfd4a77-cut7-litepacks-keepe
# (answer.ts 9a52b8a1...), LITEDECLINE_OFF=5, Qwen3-1.7B Q4_K_M, --reasoning off, seed 42 (requests), K1 kit, the 14 changed MAIN rows.
# Runs E (KEEP_E=1) then base (KEEP_E unset; host-parity control vs the MacBook LITEPACKS baseline). The adapter starts its own llama-server
# on an OS-assigned port and stops it at exit. Detector :8094 used, never started/stopped. Disk guard >= 25 GiB.
# Usage: bash gen_mini.sh <job dir with req/ke-MAIN14-s42.requests.jsonl>
set -u
export PATH=/opt/homebrew/bin:$PATH
J=$1; B=$HOME/boar; T=$B/kiln/be-0cfd4a77-cut7-litepacks-keepe; MD=$B/shared-models/emergency-detector; SRV=$B/spikes/llama-b11010/build-cpu/bin/llama-server
cd $T || exit 1
[ "$(shasum -a 256 src/routing/answer.ts | cut -c1-16)" = 9a52b8a103fee6c9 ] || { echo "FAIL answer.ts sha"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector down"; exit 1; }
export BOAR_EVAL_PACK_DIRS=$B/shared-data/packs/v3proto:$B/shared-data/packs/wave3:$B/shared-data/packs/wave2:$B/shared-data/packs/wave1:$B/shared-data/packs:$B/shared-data/crypto
export BOAR_SHARED_MODELS=$B/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
  BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5
for V in E base; do
  FREE=$(df -k $HOME | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 25 ] || { echo "FAIL disk ${FREE} GiB < 25"; exit 1; }
  if [ $V = E ]; then export KEEP_E=1; else unset KEEP_E; fi; R=ke-$V-MAIN14-s42; t0=$(date +%s)
  be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests $J/req/ke-MAIN14-s42.requests.jsonl --out $J/out/$R.traces.jsonl --backend server --server-bin $SRV --threads 4 --timeout-ms 600000 > $J/out/$R.log 2>&1
  echo "$V rc=$? rows=$(wc -l < $J/out/$R.traces.jsonl | tr -d ' ') free=${FREE}GiB $(( $(date +%s) - t0 ))s"
done
echo ALLDONE
