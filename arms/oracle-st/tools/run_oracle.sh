#!/bin/bash
# ORACLE-ST runner = arms/packs/tools/run_selftest.sh on the copy tree runner-local/be-0cfd4a77-cut7-oracle (cut 7 + oracle.vs-cut7.patch;
# adapter unchanged 6298e5d3). Env passed through: BOAR_ORACLE_FILE (oracle json; absent = off), BOAR_PROMPT_DUMP (jsonl), IDS (comma list).
# Guards: detector :8094 up (never stopped), no other 4B llama-server, no other adapter.ts job, free disk >= 8 GiB.
# Usage: run_oracle.sh <requests.jsonl> <out traces.jsonl>   Writes <out>.status DONE | FAIL ...
set -u
REQ=$1; OUT=$2; T=$BOAR_WS/runner-local/be-0cfd4a77-cut7-oracle; S=${OUT%.jsonl}.status; MD=$BOAR_WS/shared-models/emergency-detector
SRV=$BOAR_WS/spikes/llama-b11010-cpu/bin/llama-server
echo "start $(date +%s) $(date '+%F %T') oracle=${BOAR_ORACLE_FILE:-off} dump=${BOAR_PROMPT_DUMP:-off}" > "$S"
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 04a2a999828c8e46 ] || { echo "FAIL patch sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter.ts | cut -c1-16)" = 6298e5d3f49414fe ] || { echo "FAIL adapter sha" >> "$S"; exit 1; }
[ "$(cat ARM)" = cut7-oracle ] || { echo "FAIL ARM" >> "$S"; exit 1; }
[ "$(cat ORACLE_PATCH_SHA256)" = "$(shasum -a 256 $BOAR_WS/rnd/research/coordinator/arms/oracle-st/oracle.vs-cut7.patch | cut -d' ' -f1)" ] || { echo "FAIL oracle patch sha" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
pgrep -f "^[^ ]*llama-server .*Qwen3-4B" >/dev/null && { echo "FAIL a 4B llama-server is already running" >> "$S"; exit 1; }
pgrep -f "^[^ ]*node .*be/adapter[.]ts" >/dev/null && { echo "FAIL an adapter.ts job is already running" >> "$S"; exit 1; }
FREE=$(df -k $HOME | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 8 ] || { echo "FAIL disk ${FREE} GiB < 8" >> "$S"; exit 1; }
export BOAR_EVAL_PACK_DIRS=$BOAR_WS/shared-data/packs/wave3:$BOAR_WS/shared-data/packs/wave2:$BOAR_WS/shared-data/packs/wave1:$BOAR_WS/shared-data/packs:$BOAR_WS/shared-data/crypto BOAR_SHARED_MODELS=$BOAR_WS/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
[ -n "${IDS:-}" ] && EXTRA+=(--ids "$IDS")
echo "cmd adapter.ts --requests $REQ --out $OUT ${EXTRA[*]}" >> "$S"
be/node_modules/tsx/dist/cli.mjs be/adapter.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
