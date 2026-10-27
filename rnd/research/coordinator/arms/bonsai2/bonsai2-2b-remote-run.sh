#!/bin/bash
# BONSAI2-2B mini-side runner (copy of bonsai2-remote-run.sh, adapter = adapter-bonsai2-2b.patch e07db59f…; arm T2 = the 2B)
# BONSAI2 S1 mini-side runner = think4b-remote-run.sh on the cut 7 tree with the side dir be-repo-bonsai2/ (boar-eval HEAD e31a428 runner files
# + tools/adapter-bonsai2.patch a65e4c69…, next to the untouched be-repo/, sharing node_modules, vendor and runs/ by symlink; mini's own protocol.ts/gate.ts).
# Arms: T = Ternary-Bonsai-2-4B PTQ1_0 on PrismML's fork llama-server (prism-b10777-e3de715) with BOAR_SERVER_EXTRA_ARGS="--device none --no-op-offload --reasoning off";
#       C = Qwen3-4B-Instruct-2507 Q4_K_M on the standard b11010 build-cpu (no extra args). The model comes from the requests' config.modelId.
# Usage (on the mini, under nohup): bonsai2-remote-run.sh <runId> <T|C> [noplaces]   (requests already at be-repo/runs/<runId>/requests.jsonl)
# Writes be-repo/runs/<runId>/{traces.jsonl,run.log,STATUS}. Never stops the detector; restarts it only if down.
set -u
RUN=$1; ARMK=$2; PL=${3:-places}
T=<runner>/kiln/be-0cfd4a77-cut7; SD=be-repo-bonsai2; MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
STD=<runner>/spikes/llama-b11010/build-cpu/bin/llama-server; FORK=<runner>/spikes/llama-prism/bin/llama-server
case $ARMK in
  T) SRV=$FORK; MODEL=<runner>/shared-models/bonsai2/Ternary-Bonsai-2-4B-PTQ1_0.gguf; MSHA=56711263ec9a9ffe; MID=bonsai2-4b-ptq1_0; export BOAR_SERVER_EXTRA_ARGS="--device none --no-op-offload --reasoning off";;
  T2) SRV=$FORK; MODEL=<runner>/shared-models/bonsai2/Ternary-Bonsai-2-2B-PTQ1_0.gguf; MSHA=36061ad406df8a49; MID=bonsai2-2b-ptq1_0; export BOAR_SERVER_EXTRA_ARGS="--device none --no-op-offload --reasoning off";;
  C) SRV=$STD; MODEL=<runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf; MSHA=3605803b982cb64a; MID=qwen3-4b-instruct-2507-q4km; unset BOAR_SERVER_EXTRA_ARGS;;
  *) echo "bad arm $ARMK"; exit 1;;
esac
cd $T; R=be-repo/runs/$RUN; S=$R/STATUS
echo "start $(date +%s) $(date '+%F %T') arm $ARMK" > $S
[ "$(cat ARM)" = cut7 ] || { echo "FAIL ARM" >> $S; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 0fba26b8c55aa776 ] || { echo "FAIL patch sha" >> $S; exit 1; }
[ "$(shasum -a 256 $SD/adapter.ts | cut -c1-16)" = caa5b5ff10aa01cb ] || { echo "FAIL adapter sha" >> $S; exit 1; }
[ "$(shasum -a 256 $SD/server.ts | cut -c1-16)" = 4c347f0324f73545 ] || { echo "FAIL server sha" >> $S; exit 1; }
[ "$(shasum -a 256 $MODEL | cut -c1-16)" = $MSHA ] || { echo "FAIL model sha" >> $S; exit 1; }
# every request must ask for this arm's model (no silent mix)
[ "$(grep -c "\"modelId\":\"$MID\"" $R/requests.jsonl)" = "$(wc -l < $R/requests.jsonl | tr -d ' ')" ] || { echo "FAIL requests modelId != $MID" >> $S; exit 1; }
if ! curl -sf http://127.0.0.1:8094/health >/dev/null; then
  echo "detector down -> start" >> $S
  (cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null) || { echo "FAIL detector sums" >> $S; exit 1; }
  nohup $STD -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &
  for i in $(seq 1 60); do curl -sf http://127.0.0.1:8094/health >/dev/null && break; sleep 2; done
fi
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector" >> $S; exit 1; }
if pgrep -fl "llama-server" | grep -v -- "--port 8094" >/dev/null; then echo "FAIL another llama-server is already running" >> $S; exit 1; fi
df -g ~ | awk 'NR==2{print "free_gib " $4}' >> $S; sysctl -n vm.swapusage >> $S
EXTRA=(--backend server --server-bin $SRV --threads 4 --timeout-ms 600000)
[ "$PL" = noplaces ] || EXTRA=(--places $PLACES "${EXTRA[@]}")
export BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
echo "cmd BOAR_SERVER_EXTRA_ARGS=${BOAR_SERVER_EXTRA_ARGS:-} $SD/adapter.ts --requests $R/requests.jsonl --out $R/traces.jsonl ${EXTRA[*]}" >> $S
<runner>/bin/run-heavy Kiln $SD/node_modules/.bin/tsx $SD/adapter.ts --requests $R/requests.jsonl --out $R/traces.jsonl "${EXTRA[@]}" > $R/run.log 2>&1
rc=$?
pgrep -fl "llama-server" | grep -v -- "--port 8094" >/dev/null && echo "WARN llama-server left running" >> $S
curl -sf http://127.0.0.1:8094/health >/dev/null && echo "detector still up" >> $S || echo "DETECTOR-LOST" >> $S
echo "end $(date +%s) rc=$rc" >> $S
# FAIL CLOSED (2026-10-11): DONE only when the adapter exited 0; arm.sh wait/fetch stop on FAIL
if [ $rc -eq 0 ]; then echo DONE >> $S; else echo "FAIL rc=$rc" >> $S; exit $rc; fi
