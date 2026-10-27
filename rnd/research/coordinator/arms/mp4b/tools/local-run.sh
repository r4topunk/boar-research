#!/bin/bash
# MP4B MacBook runner (criterion ../deepiter/DEEPITER-criterion.md, arm M): cut 7 engine tree (kiln-local/be-0cfd4a77-cut7 = 0cfd4a77 + cut7 patch 0fba26b8…, adapter boar-eval 4a22a4e 6298e5d3…)
# on the 4B with alwaysComplete=true and no deep model -> the engine's own multi-pass path. Mirrors the mini C run (deepvpara remote-run.sh, ARMK=C):
# --backend server --threads 4, ship profile, mmbert detector v3b on :8094 (the MacBook's detector; never stopped), noplaces (v0.2). Writes <out>.status DONE | FAIL rc=N.
# Usage: local-run.sh <requests.jsonl> <out traces.jsonl>
set -u
REQ=$1; OUT=$2; T=<workspace>/kiln-local/be-0cfd4a77-cut7; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server
echo "start $(date +%s) $(date '+%F %T')" > "$S"
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 0fba26b8c55aa776 ] || { echo "FAIL patch sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter.ts | cut -c1-16)" = 6298e5d3f49414fe ] || { echo "FAIL adapter sha" >> "$S"; exit 1; }
[ "$(cat ARM)" = cut7 ] || { echo "FAIL ARM" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
pgrep -fl "llama-server.*Qwen3-4B" >/dev/null && { echo "FAIL a 4B llama-server is already running" >> "$S"; exit 1; }
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
echo "cmd adapter.ts --requests $REQ --out $OUT ${EXTRA[*]}" >> "$S"
be/node_modules/tsx/dist/cli.mjs be/adapter.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
