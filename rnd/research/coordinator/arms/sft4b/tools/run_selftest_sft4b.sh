#!/bin/bash
# SFT4B stage 2 self-test runner (NOT RUN YET; written 2026-10-13 stage 1) = arms/packs/tools/run_selftest.sh pointed at the side tree
# kiln-local/be-0cfd4a77-cut7-sft4b (to be created in stage 2: cp -a kiln-local/be-0cfd4a77-cut7, then `patch -p1 < arms/sft4b/tools/adapter-lora.patch`;
# patched be/adapter.ts sha256 45574c77cf4e748d…; ARM file = cut7-sft4b) with BOAR_SERVER_LORA = the GGUF LoRA under shared-models/ (sha checked).
# The LoRA is passed to every llama-server the adapter spawns: fast tier only (no --deep-model in stage 2).
# Usage: run_selftest_sft4b.sh <requests.jsonl> <out traces.jsonl>    (control C = the unpatched run_selftest.sh)
set -u
REQ=$1; OUT=$2; T=<workspace>/kiln-local/be-0cfd4a77-cut7-sft4b; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server
echo "start $(date +%s) $(date '+%F %T')" > "$S"
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 0fba26b8c55aa776 ] || { echo "FAIL patch sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter.ts | cut -c1-16)" = 45574c77cf4e748d ] || { echo "FAIL adapter sha" >> "$S"; exit 1; }
[ "$(cat ARM)" = cut7-sft4b ] || { echo "FAIL ARM" >> "$S"; exit 1; }
LORA=<workspace>/shared-models/qwen3-4b-instruct-2507-sft4b-lora-f16.gguf; LORA_SHA=${BOAR_LORA_SHA:?set BOAR_LORA_SHA = the STAGE1.md GGUF LoRA sha256}
[ "$(shasum -a 256 "$LORA" | cut -d" " -f1)" = "$LORA_SHA" ] || { echo "FAIL lora sha" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
pgrep -fl "llama-server.*Qwen3-4B" >/dev/null && { echo "FAIL a 4B llama-server is already running" >> "$S"; exit 1; }
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave3:<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal BOAR_SERVER_LORA=$LORA
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
echo "cmd adapter.ts --requests $REQ --out $OUT ${EXTRA[*]}" >> "$S"
be/node_modules/tsx/dist/cli.mjs be/adapter.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
