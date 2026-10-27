#!/bin/bash
# LITETHINK runner = lite5/tools/run_lite5_gen.sh with thinking ON: BOAR_SERVER_EXTRA_ARGS="--reasoning-budget <B>" (no "--reasoning off"; the Qwen3 template
# thinks by default; the engine fast path sends thinking_budget_tokens = FAST_THINKING_BUDGET per request). B=256: tree kiln-local/be-0cfd4a77-cut7-headpass-x2
# (stock FAST_THINKING_BUDGET 256). B=512: tree ...-x2-t512 = APFS clone + litethink512-on-x2.patch (answer.ts 256 -> 512, also raises max_tokens by 256).
# Usage: run_lt_gen.sh <256|512> <requests.jsonl> <out traces.jsonl>
set -u
B=$1; REQ=$2; OUT=$3; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
A=<workspace>/rnd/research/coordinator/arms/headpass-st; SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server; LT=<workspace>/rnd/research/coordinator/arms/litethink
T=<workspace>/kiln-local/be-0cfd4a77-cut7-headpass-x2; [ "$B" = 512 ] && T=$T-t512
echo "start $(date +%s) $(date '+%F %T') budget=$B tree=$T" > "$S"
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 0fba26b8c55aa776 ] || { echo "FAIL patch sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter-lite5.ts | cut -c1-16)" = 5785ffc48240f839 ] || { echo "FAIL adapter-lite5 sha" >> "$S"; exit 1; }
[ "$(cat ARM)" = cut7-headpass-x2 ] || { echo "FAIL ARM" >> "$S"; exit 1; }
[ "$(cat HEADPASS_X2B_PATCH_SHA256)" = "$(shasum -a 256 $A/headpass-x2b.vs-cut7.patch | cut -d' ' -f1)" ] || { echo "FAIL x2b patch sha" >> "$S"; exit 1; }
grep -q "^export const FAST_THINKING_BUDGET = $B;\$" src/routing/answer.ts || { echo "FAIL FAST_THINKING_BUDGET != $B" >> "$S"; exit 1; }
if [ "$B" = 512 ]; then [ "$(cat LITETHINK512_PATCH_SHA256)" = "$(shasum -a 256 $LT/litethink512-on-x2.patch | cut -d' ' -f1)" ] || { echo "FAIL t512 patch sha" >> "$S"; exit 1; }; fi
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
"$A/tools/busy.sh" && { echo "FAIL a llama-server or adapter job is already running" >> "$S"; exit 1; }
pgrep -f "be/adapter-lite5[.]ts" >/dev/null && { echo "FAIL adapter-lite5 job running" >> "$S"; exit 1; }
FREE=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 5 ] || { echo "FAIL disk ${FREE} GiB < 5" >> "$S"; exit 1; }
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/v3proto:<workspace>/shared-data/packs/wave3:<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
export BOAR_SERVER_EXTRA_ARGS="--reasoning-budget $B"
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
echo "cmd adapter-lite5.ts --requests $REQ --out $OUT ${EXTRA[*]} extra=${BOAR_SERVER_EXTRA_ARGS}" >> "$S"
be/node_modules/tsx/dist/cli.mjs be/adapter-lite5.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
