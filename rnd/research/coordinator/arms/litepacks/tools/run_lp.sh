#!/bin/bash
# LITEPACKS generation (MacBook; the mini was unreachable at freeze). Tree kiln-local/be-0cfd4a77-cut7-litepacks (tools/mk_tree.sh),
# adapter be/adapter-litedecline.ts with LITEDECLINE_OFF=5 (OFF5 + the CMP30OFF warning line in answer.ts). Qwen3-1.7B, --reasoning off, seed 42 (requests).
# The adapter starts its own llama-server on an OS-assigned port and stops it at exit. Guards: detector :8094 up (never started/stopped here),
# no other llama-server/adapter job (busy.sh), disk >= 4 GiB. Resumable (skips runs with DONE and the expected row count).
# Usage: run_lp.sh <run name>...   (run name = lp-<K>-<set>-s42; requests in runs/req)
set -u
H=<workspace>/rnd/research/coordinator/arms/litepacks; T=<workspace>/kiln-local/be-0cfd4a77-cut7-litepacks
SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server; MD=<workspace>/shared-models/emergency-detector
BZ=$H/../headpass-st/tools/busy.sh
cd $T || exit 1
[ "$(cat ARM)" = cut7-headpass-x2+litepacks ] || { echo "FAIL ARM"; exit 1; }
[ "$(shasum -a 256 src/routing/answer.ts | cut -c1-16)" = 0d1ac07dd1d664be ] || { echo "FAIL answer.ts sha"; exit 1; }
[ "$(shasum -a 256 be/adapter-litedecline.ts | cut -c1-16)" = d53c14878ce4cbd3 ] || { echo "FAIL adapter sha"; exit 1; }
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/v3proto:<workspace>/shared-data/packs/wave3:<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto
export BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
export BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5
for X in "$@"; do
  REQ=$H/runs/req/$X.requests.jsonl; OUT=$H/traces/$X.traces.jsonl; S=$H/runs/logs/$X.status; L=$H/runs/logs/$X.log
  n=$(wc -l < $REQ | tr -d ' ')
  if grep -q '^DONE' $S 2>/dev/null && [ -s $OUT ] && [ "$(wc -l < $OUT | tr -d ' ')" = "$n" ]; then echo "skip $X"; continue; fi
  w=0; while $BZ > /dev/null 2>&1; do [ $w = 0 ] && echo "wait-busy $X $(date +%T)"; w=1; sleep 30; done
  curl -sf http://127.0.0.1:8094/health > /dev/null || { echo "FAIL detector :8094 down"; exit 1; }
  FREE=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 4 ] || { echo "FAIL disk ${FREE} GiB < 4"; exit 1; }
  rm -f $OUT; echo "start $(date +%s) $(date '+%F %T') LITEDECLINE_OFF=$LITEDECLINE_OFF free=${FREE}GiB" > $S
  be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests $REQ --out $OUT --backend server --server-bin $SRV --threads 4 --timeout-ms 600000 > $L 2>&1; rc=$?
  echo "end $(date +%s) rc=$rc" >> $S
  $BZ > /dev/null 2>&1 && echo "WARN llama-server left running" >> $S
  if [ $rc = 0 ]; then echo DONE >> $S; echo "$(date +%T) done $X rows=$(wc -l < $OUT | tr -d ' ')"; else echo "FAIL rc=$rc" >> $S; echo "FAIL $X"; exit $rc; fi
done
echo "ALLDONE $*"
