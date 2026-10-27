#!/bin/bash
# LITE7 runner = lite5/tools/run_lite5_gen.sh on tree kiln-local/be-0cfd4a77-cut7-lite7 (X2b tree + tools/lite7.patch), adapter be/adapter-lite7.ts
# (= adapter-lite5.ts + the LITE_STYLE line). Mode on: LITE_STYLE=1 (deps.liteStyle); off: unset (byte-identical prompts). Optional DUMP=<file> -> BOAR_PROMPT_DUMP.
# Guards: detector :8094 up (never stopped), busy.sh free, disk >= 4 GiB. Usage: run_lite7_gen.sh <requests.jsonl> <out traces.jsonl> <on|off>
set -u
REQ=$1; OUT=$2; MODE=$3; T=<workspace>/kiln-local/be-0cfd4a77-cut7-lite7; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
A=<workspace>/rnd/research/coordinator/arms/headpass-st; L7=<workspace>/rnd/research/coordinator/arms/lite7; SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server
echo "start $(date +%s) $(date '+%F %T') mode=$MODE" > "$S"
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 0fba26b8c55aa776 ] || { echo "FAIL patch sha" >> "$S"; exit 1; }
[ "$(cat ARM)" = cut7+lite7 ] || { echo "FAIL ARM" >> "$S"; exit 1; }
[ "$(cat HEADPASS_X2B_PATCH_SHA256)" = "$(shasum -a 256 $A/headpass-x2b.vs-cut7.patch | cut -d' ' -f1)" ] || { echo "FAIL x2b patch sha" >> "$S"; exit 1; }
[ "$(cut -c1-16 LITE7_PATCH_SHA256)" = 6ef9c0dbcde9591d ] && [ "$(cut -c1-16 $L7/tools/lite7.patch.sha256)" = 6ef9c0dbcde9591d ] || { echo "FAIL lite7 patch sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter-lite7.ts | cut -c1-16)" = 9da2d01a5535b429 ] || { echo "FAIL adapter-lite7 sha" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
"$A/tools/busy.sh" && { echo "FAIL a llama-server or adapter job is already running" >> "$S"; exit 1; }
pgrep -f "be/adapter-lite[0-9][.]ts" >/dev/null && { echo "FAIL an adapter-lite job is already running" >> "$S"; exit 1; }
FREE=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 4 ] || { echo "FAIL disk ${FREE} GiB < 4" >> "$S"; exit 1; }
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/v3proto:<workspace>/shared-data/packs/wave3:<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
export BOAR_SERVER_EXTRA_ARGS="--reasoning off"
unset LITE_STYLE BOAR_PROMPT_DUMP; case $MODE in on) export LITE_STYLE=1;; off) ;; *) echo "FAIL mode" >> "$S"; exit 1;; esac
[ -n "${DUMP:-}" ] && export BOAR_PROMPT_DUMP=$DUMP
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
echo "cmd adapter-lite7.ts --requests $REQ --out $OUT ${EXTRA[*]} extra=${BOAR_SERVER_EXTRA_ARGS} LITE_STYLE=${LITE_STYLE:-unset}" >> "$S"
be/node_modules/tsx/dist/cli.mjs be/adapter-lite7.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
