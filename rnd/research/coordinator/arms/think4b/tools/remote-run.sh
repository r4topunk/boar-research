#!/bin/bash
# THINK4B mini-side runner = deepvpara remote-run.sh with the fast model swapped for Qwen3-4B-Thinking-2507 (no deep model).
# Trees: Y = be-0cfd4a77-think4b (cut 6 + adapter 796add7, FAST_THINKING_BUDGET 256), Z = be-0cfd4a77-think4b512 (+ think4b512-on-cut6.patch 6a977a29…, budget 512).
# Usage (on the mini, under nohup): remote-run.sh <runId> <Y|Z> [noplaces]   (requests already at be-repo/runs/<runId>/requests.jsonl)
# Writes be-repo/runs/<runId>/{traces.jsonl,run.log,STATUS}. Never stops the detector; restarts it only if down.
set -u
RUN=$1; ARMK=$2; PL=${3:-places}
case $ARMK in Y) TREE=think4b;; Z) TREE=think4b512;; *) echo "bad arm $ARMK"; exit 1;; esac
T=<runner>/kiln/be-0cfd4a77-$TREE; MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
SRV=<runner>/spikes/llama-b11010/build-cpu/bin/llama-server
cd $T; R=be-repo/runs/$RUN; S=$R/STATUS
echo "start $(date +%s) $(date '+%F %T') tree $TREE" > $S
[ "$(cut -c1-16 PATCH_SHA256)" = 824e0b35fcdfe46b ] || { echo "FAIL patch sha" >> $S; exit 1; }
[ "$(shasum -a 256 be-repo/adapter.ts | cut -c1-16)" = 1860ef9b86c1242b ] || { echo "FAIL adapter sha" >> $S; exit 1; }
[ "$(shasum -a 256 be-repo/server.ts | cut -c1-16)" = 0d069273381a5572 ] || { echo "FAIL server sha" >> $S; exit 1; }
[ "$(cat ARM)" = $TREE ] || { echo "FAIL ARM" >> $S; exit 1; }
if [ $ARMK = Y ]; then grep -q "FAST_THINKING_BUDGET = 256;" src/routing/answer.ts || { echo "FAIL budget constant (Y)" >> $S; exit 1; }
else grep -q "FAST_THINKING_BUDGET = 512;" src/routing/answer.ts || { echo "FAIL budget constant (Z)" >> $S; exit 1; }
  [ "$(cat THINK4B512_PATCH_SHA256)" = 6a977a29132bca03603fef6031fcf5dd1b87b18670761eaa84b68a1682cc7866 ] || { echo "FAIL think4b512 patch sha" >> $S; exit 1; }; fi
[ "$(shasum -a 256 <runner>/shared-models/Qwen3-4B-Thinking-2507-Q4_K_M.gguf | cut -c1-16)" = ddd52e18200baab2 ] || { echo "FAIL model sha" >> $S; exit 1; }
if ! curl -sf http://127.0.0.1:8094/health >/dev/null; then
  echo "detector down -> start" >> $S
  (cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null) || { echo "FAIL detector sums" >> $S; exit 1; }
  nohup $SRV -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &
  for i in $(seq 1 60); do curl -sf http://127.0.0.1:8094/health >/dev/null && break; sleep 2; done
fi
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector" >> $S; exit 1; }
if pgrep -fl "llama-server.*Qwen3" | grep -v 8094 >/dev/null; then echo "FAIL another Qwen llama-server is already running" >> $S; exit 1; fi
df -g ~ | awk 'NR==2{print "free_gib " $4}' >> $S; sysctl -n vm.swapusage >> $S
# --timeout-ms 600000 as DT512 deviation 1 (the app has no per-generation timeout); C ran at the 120 s default with 0 timeouts, p90 10.7 s.
EXTRA=(--backend server --server-bin $SRV --threads 4 --timeout-ms 600000)
[ "$PL" = noplaces ] || EXTRA=(--places $PLACES "${EXTRA[@]}")
export BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
echo "cmd adapter.ts --requests $R/requests.jsonl --out $R/traces.jsonl ${EXTRA[*]}" >> $S
<runner>/bin/run-heavy Kiln be-repo/node_modules/.bin/tsx be-repo/adapter.ts --requests $R/requests.jsonl --out $R/traces.jsonl "${EXTRA[@]}" > $R/run.log 2>&1
rc=$?
curl -sf http://127.0.0.1:8094/health >/dev/null && echo "detector still up" >> $S || echo "DETECTOR-LOST" >> $S
echo "end $(date +%s) rc=$rc" >> $S
# FAIL CLOSED (2026-10-11): DONE only when the adapter exited 0; arm.sh wait/fetch stop on FAIL
if [ $rc -eq 0 ]; then echo DONE >> $S; else echo "FAIL rc=$rc" >> $S; exit $rc; fi
