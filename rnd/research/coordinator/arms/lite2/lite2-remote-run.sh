#!/bin/bash
# LITE2 mini-side runner = bonsai2-2b-remote-run.sh (b64a7a6d…) on the side dir be-repo-lite2/ (= be-repo-bonsai2/ + tools/adapter-lite2.patch: adapter.ts e37b5a89…).
# Arms: L  = Qwen3-1.7B Q4_K_M (unsloth @ d7f544ee) on the standard b11010 build-cpu, BOAR_SERVER_EXTRA_ARGS="--reasoning off";
#       T2 = Ternary-Bonsai-2-2B PTQ1_0 on PrismML's fork (prism-b10777-e3de715), "--device none --no-op-offload --reasoning off" (as BONSAI2-2B).
# BOAR_EVAL_PACK_DIRS adds the wave3/2/1 pack dirs in front of the default (packs, crypto) so the self-test requests' pack resolves; the claim kit resolves as before.
# RSS sampler: every 2 s, the llama-server (not :8094) RSS in KiB -> runs/<runId>/rss.txt (max + samples).
# Usage (on the mini, under nohup): lite2-remote-run.sh <runId> <L|T2> [noplaces]   (requests already at be-repo/runs/<runId>/requests.jsonl)
set -u
RUN=$1; ARMK=$2; PL=${3:-places}
T=<runner>/kiln/be-0cfd4a77-cut7; SD=be-repo-lite2; MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
STD=<runner>/spikes/llama-b11010/build-cpu/bin/llama-server; FORK=<runner>/spikes/llama-prism/bin/llama-server
case $ARMK in
  L) SRV=$STD; MODEL=<runner>/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf; MSHA=b139949c5bd74937; MID=qwen3-1.7b-q4km; export BOAR_SERVER_EXTRA_ARGS="--reasoning off";;
  T2) SRV=$FORK; MODEL=<runner>/shared-models/bonsai2/Ternary-Bonsai-2-2B-PTQ1_0.gguf; MSHA=36061ad406df8a49; MID=bonsai2-2b-ptq1_0; export BOAR_SERVER_EXTRA_ARGS="--device none --no-op-offload --reasoning off";;
  *) echo "bad arm $ARMK"; exit 1;;
esac
cd $T; R=be-repo/runs/$RUN; S=$R/STATUS
echo "start $(date +%s) $(date '+%F %T') arm $ARMK" > $S
[ "$(cat ARM)" = cut7 ] || { echo "FAIL ARM" >> $S; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 0fba26b8c55aa776 ] || { echo "FAIL patch sha" >> $S; exit 1; }
[ "$(shasum -a 256 $SD/adapter.ts | cut -c1-16)" = e37b5a8932fa1c88 ] || { echo "FAIL adapter sha" >> $S; exit 1; }
[ "$(shasum -a 256 $SD/server.ts | cut -c1-16)" = 4c347f0324f73545 ] || { echo "FAIL server sha" >> $S; exit 1; }
[ "$(shasum -a 256 $MODEL | cut -c1-16)" = $MSHA ] || { echo "FAIL model sha" >> $S; exit 1; }
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
export BOAR_EVAL_PACK_DIRS=<runner>/shared-data/packs/wave3:<runner>/shared-data/packs/wave2:<runner>/shared-data/packs/wave1:<runner>/shared-data/packs:<runner>/shared-data/crypto
export BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
echo "cmd BOAR_SERVER_EXTRA_ARGS=${BOAR_SERVER_EXTRA_ARGS:-} $SD/adapter.ts --requests $R/requests.jsonl --out $R/traces.jsonl ${EXTRA[*]}" >> $S
( while :; do p=$(pgrep -f "llama-server -m $MODEL" | head -1); [ -n "$p" ] && ps -o rss= -p $p >> $R/rss.txt; sleep 2; done ) & SAMP=$!
<runner>/bin/run-heavy Kiln $SD/node_modules/.bin/tsx $SD/adapter.ts --requests $R/requests.jsonl --out $R/traces.jsonl "${EXTRA[@]}" > $R/run.log 2>&1
rc=$?
kill $SAMP 2>/dev/null
[ -s $R/rss.txt ] && echo "rss_kib max $(sort -n $R/rss.txt | tail -1) median $(sort -n $R/rss.txt | awk '{a[NR]=$1} END{print a[int((NR+1)/2)]}') samples $(wc -l < $R/rss.txt | tr -d ' ')" >> $S
pgrep -fl "llama-server" | grep -v -- "--port 8094" >/dev/null && echo "WARN llama-server left running" >> $S
curl -sf http://127.0.0.1:8094/health >/dev/null && echo "detector still up" >> $S || echo "DETECTOR-LOST" >> $S
echo "end $(date +%s) rc=$rc" >> $S
if [ $rc -eq 0 ]; then echo DONE >> $S; else echo "FAIL rc=$rc" >> $S; exit $rc; fi
