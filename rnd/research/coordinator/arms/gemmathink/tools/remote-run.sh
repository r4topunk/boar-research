#!/bin/bash
# GEMMATHINK (criterion 46e058d3…) mini-side runner = deepthink remote-run.sh on the gemmathink tree (same patch; be-repo adapter/server from boar-eval 80a16cc).
# committed adapter 7a0282ae, unchanged) under <runner>/bin/run-heavy, --backend server, detector v3b, ship profile.
# Usage (on the mini, under nohup): remote-run.sh <runId> <D|C> [noplaces]  (V-para: places kit-vexact as Run B; v0.2: noplaces as Run A)   (requests already at be-repo/runs/<runId>/requests.jsonl)
# Writes be-repo/runs/<runId>/{traces.jsonl,run.log,STATUS}. Never stops the detector; restarts it only if down.
set -u
RUN=$1; ARMK=$2; PL=${3:-places}
T=<runner>/kiln/be-0cfd4a77-gemmathink; MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
SRV=<runner>/spikes/llama-b11010/build-cpu/bin/llama-server
cd $T; R=be-repo/runs/$RUN; S=$R/STATUS
echo "start $(date +%s) $(date '+%F %T')" > $S
[ "$(cut -c1-16 PATCH_SHA256)" = 824e0b35fcdfe46b ] || { echo "FAIL patch sha" >> $S; exit 1; }
[ "$(shasum -a 256 be-repo/adapter.ts | cut -c1-16)" = ccf8cd1930a4b2f4 ] || { echo "FAIL adapter sha" >> $S; exit 1; }
grep -q "generate:deep-thinking" src/routing/depth.ts && grep -q "thinking: true, // DEEPTHINK" src/routing/depth.ts || { echo "FAIL deepthink patch not applied" >> $S; exit 1; }
[ "$(shasum -a 256 be-repo/server.ts | cut -c1-16)" = 0d069273381a5572 ] || { echo "FAIL server.ts sha" >> $S; exit 1; }
[ "$(cat DEEPTHINK_PATCH_SHA256)" = eb3f464b38782c7aabb950cb9c658102e92620f4e4a40dc54a5976eaa8d27ba6 ] || { echo "FAIL deepthink patch sha" >> $S; exit 1; }
if ! curl -sf http://127.0.0.1:8094/health >/dev/null; then
  echo "detector down -> start" >> $S
  (cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null) || { echo "FAIL detector sums" >> $S; exit 1; }
  nohup $SRV -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &
  for i in $(seq 1 60); do curl -sf http://127.0.0.1:8094/health >/dev/null && break; sleep 2; done
fi
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector" >> $S; exit 1; }
if pgrep -fl "llama-server.*(Qwen3.6-35B|gemma-4-26B)" >/dev/null; then echo "FAIL a MoE llama-server is already running" >> $S; exit 1; fi
df -g ~ | awk 'NR==2{print "free_gib " $4}' >> $S; sysctl -n vm.swapusage >> $S
# DEVIATION 1 (DEEPTHINK.md): adapter --timeout-ms default 120000 is a desktop-harness cap the app does not have (LlamaEngine: no per-generation
# timeout on planAnswer); with 1024 thinking tokens at ~9.5 tok/s it aborted both smoke items before any answer token. D never reached it (0/51, max 62 s).
EXTRA=(--backend server --server-bin $SRV --threads 4 --timeout-ms 600000)
[ "$PL" = noplaces ] || EXTRA=(--places $PLACES "${EXTRA[@]}")
[ "$ARMK" = D ] && EXTRA+=(--deep-model qwen3.6-35b-a3b-ud-q2kxl)
[ "$ARMK" = G ] && { EXTRA+=(--deep-model gemma-4-26b-a4b-ud-q2kxl); export BOAR_THINK_KWARG=1; }
export BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
echo "cmd adapter.ts --requests $R/requests.jsonl --out $R/traces.jsonl ${EXTRA[*]}" >> $S
<runner>/bin/run-heavy Kiln be-repo/node_modules/.bin/tsx be-repo/adapter.ts --requests $R/requests.jsonl --out $R/traces.jsonl "${EXTRA[@]}" > $R/run.log 2>&1
rc=$?
curl -sf http://127.0.0.1:8094/health >/dev/null && echo "detector still up" >> $S || echo "DETECTOR-LOST" >> $S
echo "end $(date +%s) rc=$rc" >> $S
# FAIL CLOSED (2026-10-11): DONE only when the adapter exited 0; arm.sh wait/fetch stop on FAIL
if [ $rc -eq 0 ]; then echo DONE >> $S; else echo "FAIL rc=$rc" >> $S; exit $rc; fi
