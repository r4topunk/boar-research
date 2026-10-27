#!/bin/bash
# LITEREADERS runner = oracle-st/tools/run_oracle.sh with adapter be/adapter-litereaders.ts (6298e5d3 + the LITE5 hunks + LFM2/Gemma entries;
# tools/adapter-litereaders.vs-6298e5d3.patch) on the copy tree kiln-local/be-0cfd4a77-cut7-oracle (be/adapter.ts left untouched).
# Oracle ON (BOAR_ORACLE_FILE = oracle-st/tools/oracle-add.json), prompt dump on, thinking OFF (BOAR_SERVER_EXTRA_ARGS="--reasoning off").
# 2 s RSS sampler of the non-detector llama-server -> <out>.rss. Guards: detector :8094 up, busy.sh free, disk >= 4 GiB.
# Usage: run_lr.sh <requests.jsonl> <out traces.jsonl>
set -u
REQ=$1; OUT=$2; T=<workspace>/kiln-local/be-0cfd4a77-cut7-oracle; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
AR=<workspace>/rnd/research/coordinator/arms; SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server
echo "start $(date +%s) $(date '+%F %T')" > "$S"
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 0fba26b8c55aa776 ] || { echo "FAIL patch sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter-litereaders.ts | cut -c1-16)" = 0fc76e138c758919 ] || { echo "FAIL adapter-litereaders sha" >> "$S"; exit 1; }
[ "$(cat ARM)" = cut7-oracle ] || { echo "FAIL ARM" >> "$S"; exit 1; }
[ "$(cat ORACLE_PATCH_SHA256)" = "$(shasum -a 256 $AR/oracle-st/oracle.vs-cut7.patch | cut -d' ' -f1)" ] || { echo "FAIL oracle patch sha" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
"$AR/headpass-st/tools/busy.sh" && { echo "FAIL a llama-server or adapter job is already running" >> "$S"; exit 1; }
FREE=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 4 ] || { echo "FAIL disk ${FREE} GiB < 4" >> "$S"; exit 1; }
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave3:<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
export BOAR_ORACLE_FILE=$AR/oracle-st/tools/oracle-add.json BOAR_PROMPT_DUMP=${OUT%.traces.jsonl}.prompts.jsonl BOAR_SERVER_EXTRA_ARGS="--reasoning off"
rm -f "${BOAR_PROMPT_DUMP}" "${OUT%.jsonl}.rss"
( while true; do for p in $(pgrep -x llama-server); do c=$(ps -o command= -p $p); case "$c" in *emergency-detector*) ;; *) echo "$(date +%s) $(ps -o rss= -p $p)" >> "${OUT%.jsonl}.rss";; esac; done; sleep 2; done ) & SP=$!
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
echo "cmd adapter-litereaders.ts --requests $REQ --out $OUT ${EXTRA[*]} extra=${BOAR_SERVER_EXTRA_ARGS} oracle=${BOAR_ORACLE_FILE}" >> "$S"
be/node_modules/tsx/dist/cli.mjs be/adapter-litereaders.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
kill $SP 2>/dev/null
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
