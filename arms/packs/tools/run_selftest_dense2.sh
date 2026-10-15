#!/bin/bash
# DENSECHUNK-ST2 stage 1 runner = run_selftest.sh on the cut-7 dense2 tree copy runner-local/be-0cfd4a77-cut7-dense2
# (cut 7 tree + arms/densechunk-st/packdense2-only.cut7.patch = the packDense2 code only, without the T-K2 source-code/attribution changes that packdense2.vs-dt512.patch also carries; adapter copy forwards the engine's
# retrieve opts {packDense2}). Pack dirs: shared-data/packs/v3proto FIRST (sidecar copies; kit sha256s = v3proto manifests).
# Usage: run_selftest_dense2.sh <requests.jsonl> <out traces.jsonl>
set -u
REQ=$1; OUT=$2; T=$BOAR_WS/runner-local/be-0cfd4a77-cut7-dense2; S=${OUT%.jsonl}.status; MD=$BOAR_WS/shared-models/emergency-detector
SRV=$BOAR_WS/spikes/llama-b11010-cpu/bin/llama-server
echo "start $(date +%s) $(date '+%F %T')" > "$S"
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 04a2a999828c8e46 ] || { echo "FAIL patch sha" >> "$S"; exit 1; }
[ "$(cut -c1-16 DENSE2_PATCH_SHA256)" = 40a259be9981a093 ] || { echo "FAIL dense2 patch sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter.ts | cut -c1-16)" = 4b7ef7d2b96843b9 ] || { echo "FAIL adapter sha" >> "$S"; exit 1; }
[ "$(cat ARM)" = cut7-dense2 ] || { echo "FAIL ARM" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
pgrep -fl "llama-server.*Qwen3-4B" >/dev/null && { echo "FAIL a 4B llama-server is already running" >> "$S"; exit 1; }
export BOAR_EVAL_PACK_DIRS=$BOAR_WS/shared-data/packs/v3proto:$BOAR_WS/shared-data/packs/wave2:$BOAR_WS/shared-data/packs/wave1:$BOAR_WS/shared-data/packs:$BOAR_WS/shared-data/crypto BOAR_SHARED_MODELS=$BOAR_WS/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
[ -n "${IDS:-}" ] && EXTRA+=(--ids "$IDS")
echo "cmd adapter.ts --requests $REQ --out $OUT ${EXTRA[*]}" >> "$S"
be/node_modules/tsx/dist/cli.mjs be/adapter.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
