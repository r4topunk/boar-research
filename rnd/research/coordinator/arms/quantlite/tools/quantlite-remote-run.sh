#!/bin/bash
# QUANTLITE mini runner: one per-pack request file -> traces, on the X2b tree copied from the MacBook
# (<runner>/kiln/be-0cfd4a77-cut7-headpass-x2 = kiln-local tree minus be/.cache + be/node_modules; node_modules re-linked to the
# mini's same-version packages), adapter be/adapter-quantlite.ts (= adapter-lite5.ts + the qwen3-1.7b-q8_0 entries).
# Stock b11010, --reasoning off, -t 4, no places (as LITE5). One llama-server at a time; the :8094 detector is never stopped.
# Usage (mini, nohup): quantlite-remote-run.sh <requests.jsonl> <out traces.jsonl> <q8|q4>
set -u; export PATH=/opt/homebrew/bin:$PATH
REQ=$1; OUT=$2; Q=$3; S=${OUT%.jsonl}.status; T=<runner>/kiln/be-0cfd4a77-cut7-headpass-x2; MD=<runner>/shared-models/emergency-detector
SRV=<runner>/spikes/llama-b11010/build-cpu/bin/llama-server
case $Q in
  q8) MODEL=<runner>/shared-models/lite/Qwen3-1.7B-Q8_0.gguf; MSHA=0becaa825564295d; MID=qwen3-1.7b-q8_0;;
  q4) MODEL=<runner>/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf; MSHA=b139949c5bd74937; MID=qwen3-1.7b-q4km;;
  *) echo "bad model $Q"; exit 1;;
esac
echo "start $(date +%s) $(date '+%F %T') model $Q" > "$S"
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 0fba26b8c55aa776 ] || { echo "FAIL patch sha" >> "$S"; exit 1; }
[ "$(cat ARM)" = cut7-headpass-x2 ] || { echo "FAIL ARM" >> "$S"; exit 1; }
[ "$(cut -c1-16 HEADPASS_X2B_PATCH_SHA256)" = be413d7d5d9b3afd ] || { echo "FAIL x2b patch sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter-quantlite.ts | cut -c1-16)" = 89e31b5eec75e54c ] || { echo "FAIL adapter sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/server.ts | cut -c1-16)" = 4c347f0324f73545 ] || { echo "FAIL server sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 $MODEL | cut -c1-16)" = $MSHA ] || { echo "FAIL model sha" >> "$S"; exit 1; }
[ "$(grep -c "\"modelId\":\"$MID\"" $REQ)" = "$(wc -l < $REQ | tr -d ' ')" ] || { echo "FAIL requests modelId != $MID" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
if pgrep -fl "llama-server" | grep -v -- "--port 8094" >/dev/null; then echo "FAIL another llama-server is already running" >> "$S"; exit 1; fi
FREE=$(df -k ~ | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 25 ] || { echo "FAIL disk ${FREE} GiB < 25" >> "$S"; exit 1; }
echo "free_gib $FREE" >> "$S"
P=<runner>/shared-data
export BOAR_EVAL_PACK_DIRS=$P/packs/v3proto:$P/packs/wave3:$P/packs/wave2:$P/packs/wave1:$P/packs:$P/crypto BOAR_SHARED_MODELS=<runner>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
export BOAR_SERVER_EXTRA_ARGS="--reasoning off"
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
echo "cmd adapter-quantlite.ts --requests $REQ --out $OUT ${EXTRA[*]} extra=${BOAR_SERVER_EXTRA_ARGS}" >> "$S"
R=${OUT%.jsonl}.rss.txt; : > "$R"
( while :; do p=$(pgrep -f "llama-server -m $MODEL" | head -1); [ -n "$p" ] && ps -o rss= -p $p >> "$R"; sleep 2; done ) & SAMP=$!
<runner>/bin/run-heavy Kiln be/node_modules/tsx/dist/cli.mjs be/adapter-quantlite.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
kill $SAMP 2>/dev/null
[ -s "$R" ] && echo "rss_kib max $(sort -n "$R" | tail -1) median $(sort -n "$R" | awk '{a[NR]=$1} END{print a[int((NR+1)/2)]}') samples $(wc -l < "$R" | tr -d ' ')" >> "$S"
pgrep -fl "llama-server" | grep -v -- "--port 8094" >/dev/null && echo "WARN llama-server left running" >> "$S"
curl -sf http://127.0.0.1:8094/health >/dev/null && echo "detector still up" >> "$S" || echo "DETECTOR-LOST" >> "$S"
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
