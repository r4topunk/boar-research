#!/bin/bash
# STACK runner (criterion sha 56ed7ccf…) = arms/crowdq/tools/run_all9.sh pointed at the stack tree; was: CROWDQ arm P runner = arms/packs/tools/run_selftest.sh pattern: cut 7 tree kiln-local/be-0cfd4a77-cut7,
# server backend, -t 4, ship profile, mmbert detector :8094 (never stopped), BOAR_EVAL_PACK_DIRS = wave2:wave1:packs:crypto (resolves the 9 ids + kit).
# Extra guards: no Qwen3-4B llama-server and no adapter.ts already running; free disk >= 8 GiB. Writes <out>.status DONE | FAIL ...
# Usage: run_all9.sh <requests.jsonl> <out traces.jsonl>   (the adapter resumes an existing partial out file)
set -u
REQ=$1; OUT=$2; T=<workspace>/kiln-local/be-0cfd4a77-cut7-stack; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server
echo "start $(date +%s) $(date '+%F %T')" > "$S"
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 0fba26b8c55aa776 ] || { echo "FAIL patch sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter.ts | cut -c1-16)" = 8dd1faff2b157d00 ] || { echo "FAIL adapter sha" >> "$S"; exit 1; }
[ "$(cat ARM)" = cut7-stack ] || { echo "FAIL ARM" >> "$S"; exit 1; }
[ "$(cat STACK_PATCH_SHA256 2>/dev/null)" = "$(shasum -a 256 <workspace>/rnd/research/coordinator/arms/stack/stack.vs-cut7.patch | cut -d" " -f1)" ] || { echo "FAIL stack patch sha" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
pgrep -fl "llama-server.*Qwen3-4B" >/dev/null && { echo "FAIL a 4B llama-server is already running" >> "$S"; exit 1; }
pgrep -fl "adapter.ts" >/dev/null && { echo "FAIL an adapter.ts job is already running" >> "$S"; exit 1; }
FREE=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 8 ] || { echo "FAIL disk ${FREE} GiB < 8" >> "$S"; exit 1; }
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
echo "cmd adapter.ts --requests $REQ --out $OUT ${EXTRA[*]}" >> "$S"
be/node_modules/tsx/dist/cli.mjs be/adapter.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
