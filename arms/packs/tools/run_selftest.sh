#!/bin/bash
# T-K4c self-test runner = arms/mp4b/tools/local-run.sh (cut 7 tree runner-local/be-0cfd4a77-cut7 = 0cfd4a77 + cut7 patch 04a2a999, adapter 6298e5d3)
# + wave2 then wave1 pack dirs in BOAR_EVAL_PACK_DIRS ("install" = the adapter resolves kit ids to <id>.sqlite there, sha-checked, and symlinks them into the app dir corpus/).
# Settings come from the requests (claim: quickFirst, alwaysComplete=false).
# --backend server --threads 4, ship profile, mmbert detector v3b on :8094 (the MacBook's detector; never stopped), noplaces (v0.2). Writes <out>.status DONE | FAIL rc=N.
# Usage: run_selftest.sh <requests.jsonl> <out traces.jsonl>
set -u
REQ=$1; OUT=$2; T=$BOAR_WS/runner-local/be-0cfd4a77-cut7; S=${OUT%.jsonl}.status; MD=$BOAR_WS/shared-models/emergency-detector
SRV=$BOAR_WS/spikes/llama-b11010-cpu/bin/llama-server
echo "start $(date +%s) $(date '+%F %T')" > "$S"
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 04a2a999828c8e46 ] || { echo "FAIL patch sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter.ts | cut -c1-16)" = 6298e5d3f49414fe ] || { echo "FAIL adapter sha" >> "$S"; exit 1; }
[ "$(cat ARM)" = cut7 ] || { echo "FAIL ARM" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
pgrep -fl "llama-server.*Qwen3-4B" >/dev/null && { echo "FAIL a 4B llama-server is already running" >> "$S"; exit 1; }
export BOAR_EVAL_PACK_DIRS=$BOAR_WS/shared-data/packs/wave3:$BOAR_WS/shared-data/packs/wave2:$BOAR_WS/shared-data/packs/wave1:$BOAR_WS/shared-data/packs:$BOAR_WS/shared-data/crypto BOAR_SHARED_MODELS=$BOAR_WS/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
echo "cmd adapter.ts --requests $REQ --out $OUT ${EXTRA[*]}" >> "$S"
be/node_modules/tsx/dist/cli.mjs be/adapter.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
