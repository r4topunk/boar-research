#!/bin/bash
# LITEREACH2 runner = lite5/tools/run_lite5_gen.sh with the tree kiln-local/be-0cfd4a77-cut7-litereach2 (APFS clone of cut7-headpass-x2 + litereach2-env.patch;
# ARM file kept "cut7-headpass-x2" so the requests stay the LITE5-180 ON rows with only runId changed) and the cell env BOAR_LR2_* exported.
# Usage: run_gen.sh <budget> <D> <cap> <requests.jsonl> <out traces.jsonl>
set -u
BT=$1; DD=$2; CP=$3; REQ=$4; OUT=$5; T=<workspace>/kiln-local/be-0cfd4a77-cut7-litereach2; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
L=<workspace>/rnd/research/coordinator/arms/litereach2; A=<workspace>/rnd/research/coordinator/arms/headpass-st; SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server
echo "start $(date +%s) $(date '+%F %T') env BOAR_LR2_BUDGET_TOKENS=$BT BOAR_LR2_DENSE_D=$DD BOAR_LR2_MAX_APPEND=$CP" > "$S"
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 0fba26b8c55aa776 ] || { echo "FAIL patch sha" >> "$S"; exit 1; }
[ "$(cat LITEREACH2_PATCH_SHA256)" = "$(shasum -a 256 $L/litereach2-env.patch | cut -d' ' -f1)" ] || { echo "FAIL litereach2 patch sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter-lite5.ts | cut -c1-16)" = 5785ffc48240f839 ] || { echo "FAIL adapter-lite5 sha" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
"$A/tools/busy.sh" && { echo "FAIL a llama-server or adapter job is already running" >> "$S"; exit 1; }
FREE=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 5 ] || { echo "FAIL disk ${FREE} GiB < 5" >> "$S"; exit 1; }
export BOAR_LR2_BUDGET_TOKENS=$BT BOAR_LR2_DENSE_D=$DD BOAR_LR2_MAX_APPEND=$CP
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/v3proto:<workspace>/shared-data/packs/wave3:<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
export BOAR_SERVER_EXTRA_ARGS="--reasoning off"
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
echo "cmd adapter-lite5.ts --requests $REQ --out $OUT ${EXTRA[*]} extra=${BOAR_SERVER_EXTRA_ARGS}" >> "$S"
be/node_modules/tsx/dist/cli.mjs be/adapter-lite5.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
