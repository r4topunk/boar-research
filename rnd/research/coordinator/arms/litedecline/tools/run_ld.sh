#!/bin/bash
# LITEDECLINE mini-side runner. Tree <runner>/kiln/be-0cfd4a77-cut7-litedecline (= be-0cfd4a77-cut7-headpass-x2 copy + tools/litedecline.patch),
# adapter be/adapter-litedecline.ts. Arm switch LITEDECLINE_OFF: on = unset, off = 3 (the criterion's three rules), off5 = 5 (report-only).
# Qwen3-1.7B Q4_K_M, b11010 CPU -t 4, --reasoning off, seed 42 (in requests). The adapter starts its own llama-server on a free OS port
# (never 8094; the :8094 detector is used, never started or stopped here). Guards: no other llama-server, disk >= 25 GiB.
# Usage (on the mini, nohup): run_ld.sh <on|off|off5> [set...]   sets default: v01 + 9 packs. Resumable (skips DONE runs).
set -u; export PATH=/opt/homebrew/bin:$PATH
ARMK=$1; shift; W=<runner>/kiln/litedecline; T=<runner>/kiln/be-0cfd4a77-cut7-litedecline; MD=<runner>/shared-models/emergency-detector
SRV=<runner>/spikes/llama-b11010/build-cpu/bin/llama-server; MODEL=<runner>/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf
SETS=${*:-"v01 st-qa-travel-se st-qa-ethereum-se st-qa-bitcoin-se st-qa-health-se st-qa-outdoors-se st-boar-firstaid-en st-boar-medlineplus-en st-boar-factbook st-boar-simplewiki-en"}
case $ARMK in on) unset LITEDECLINE_OFF;; off) export LITEDECLINE_OFF=3;; off5) export LITEDECLINE_OFF=5;; *) echo "bad arm"; exit 1;; esac
cd $T || exit 1
[ "$(cat ARM)" = cut7-headpass-x2+litedecline ] || { echo "FAIL ARM"; exit 1; }
[ "$(shasum -a 256 src/routing/answer.ts | cut -c1-16)" = 2cd3d656be0e7bf0 ] || { echo "FAIL answer.ts sha"; exit 1; }
[ "$(shasum -a 256 be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] || { echo "FAIL adapter sha"; exit 1; }
[ "$(shasum -a 256 $MODEL | cut -c1-16)" = b139949c5bd74937 ] || { echo "FAIL model sha"; exit 1; }
grep -q "process.env.LITEDECLINE" src/routing/*.ts && { echo "FAIL engine reads env"; exit 1; }
export BOAR_EVAL_PACK_DIRS=<runner>/shared-data/packs/v3proto:<runner>/shared-data/packs/wave3:<runner>/shared-data/packs/wave2:<runner>/shared-data/packs/wave1:<runner>/shared-data/packs:<runner>/shared-data/crypto
export BOAR_SHARED_MODELS=<runner>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
export BOAR_SERVER_EXTRA_ARGS="--reasoning off"
for s in $SETS; do
  R=$W/ld-$ARMK-$s-s42; S=$R.traces.status
  if grep -q '^DONE' $S 2>/dev/null; then echo "skip $s"; continue; fi
  while pgrep -fl llama-server | grep -v -- "--port 8094" > /dev/null; do echo "wait other llama-server $(date +%T)"; sleep 60; done
  FREE=$(df -g ~ | awk 'NR==2{print $4}'); [ "$FREE" -ge 25 ] || { echo "FAIL disk $FREE GiB < 25"; exit 1; }
  curl -sf http://127.0.0.1:8094/health > /dev/null || { echo "FAIL detector :8094 down"; exit 1; }
  rm -f $R.traces.jsonl; echo "start $(date +%s) $(date '+%F %T') arm=$ARMK LITEDECLINE_OFF=${LITEDECLINE_OFF:-unset} free=${FREE}GiB" > $S
  <runner>/bin/run-heavy Kiln be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests $R.requests.jsonl --out $R.traces.jsonl \
    --backend server --server-bin $SRV --threads 4 --timeout-ms 600000 > $R.traces.log 2>&1; rc=$?
  echo "end $(date +%s) rc=$rc" >> $S
  pgrep -fl llama-server | grep -v -- "--port 8094" > /dev/null && echo "WARN llama-server left running" >> $S
  if [ $rc = 0 ]; then echo DONE >> $S; echo "$(date +%T) done $s"; else echo "FAIL rc=$rc" >> $S; echo "FAIL $s"; exit $rc; fi
done
echo "ALLDONE $ARMK"
