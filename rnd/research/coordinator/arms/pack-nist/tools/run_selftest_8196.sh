#!/bin/bash
# PACK-NIST self-test runner = arms/packs/tools/run_selftest.sh (cut 7 tree kiln-local/be-0cfd4a77-cut7, patch 0fba26b8, adapter 6298e5d3,
# ship profile, mmbert detector v3b on the MacBook :8094 used read-only) with ONE change: the 4B llama-server is started here on the
# track's own port 8196 with the adapter's exact spawn args and passed via --server-url (the adapter would otherwise pick a random port).
# + shared-data/packs/wave4 first in BOAR_EVAL_PACK_DIRS. Usage: run_selftest_8196.sh <requests.jsonl>... (traces next to each request file)
set -u
T=<workspace>/kiln-local/be-0cfd4a77-cut7; MD=<workspace>/shared-models/emergency-detector
SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server; M=<workspace>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf
PORT=8196; D=$(cd "$(dirname "$0")/../runs" && pwd); SL=$D/server-8196.log
cd "$T" || exit 1
[ "$(cut -c1-16 PATCH_SHA256)" = 0fba26b8c55aa776 ] || { echo "FAIL patch sha"; exit 1; }
[ "$(shasum -a 256 be/adapter.ts | cut -c1-16)" = 6298e5d3f49414fe ] || { echo "FAIL adapter sha"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down (not started here)"; exit 1; }
lsof -nP -iTCP:$PORT -sTCP:LISTEN >/dev/null && { echo "FAIL port $PORT busy"; exit 1; }
"$SRV" -m "$M" -t 4 -tb 4 -c 4096 -ngl 0 -np 1 --jinja --no-webui --cache-ram 0 --reasoning-format deepseek --host 127.0.0.1 --port $PORT > "$SL" 2>&1 &
SP=$!; trap 'kill $SP 2>/dev/null; wait $SP 2>/dev/null' EXIT
for i in $(seq 1 300); do curl -sf http://127.0.0.1:$PORT/health >/dev/null && break; sleep 1; done
export BOAR_EVAL_PACK_DIRS=${PACK_DIRS_PREFIX:+$PACK_DIRS_PREFIX:}<workspace>/shared-data/packs/wave4:<workspace>/shared-data/packs/wave3:<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
rc_all=0
for REQ in "$@"; do
  OUT=${REQ%.requests.jsonl}.traces.jsonl; S=${OUT%.jsonl}.status
  echo "start $(date +%s) $(date '+%F %T') server :$PORT" > "$S"
  be/node_modules/tsx/dist/cli.mjs be/adapter.ts --requests "$REQ" --out "$OUT" --backend server --server-bin "$SRV" --server-url http://127.0.0.1:$PORT --threads 4 --timeout-ms 600000 > "${OUT%.jsonl}.log" 2>&1; rc=$?
  echo "end $(date +%s) rc=$rc" >> "$S"; [ $rc = 0 ] && echo DONE >> "$S" || { echo "FAIL rc=$rc" >> "$S"; rc_all=$rc; }
done
exit $rc_all
