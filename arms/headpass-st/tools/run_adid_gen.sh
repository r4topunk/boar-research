#!/bin/bash
# ADAPTER-IDENTITY runner (copy of run_x2b_gen.sh: no v3proto in pack dirs, adapter sha from EXPECT_ADAPTER): tree runner-local/be-0cfd4a77-cut7-headpass-x2 (cut 7 + headpass-x2b.vs-cut7.patch, which includes the dump hook);
# adapter = 6298e5d3 + retrieve-opts forwarding (a77838f1, the cut7-stack adapter; adapter-forward-opts.patch): without it packDense2 never reaches retrieve(). The settings come from the requests (packHeadPass "a2" + packDense2 "append-budget"; mkreq_x2b.py).
# Env: BOAR_PROMPT_DUMP (jsonl). Guards: detector :8094 up (never stopped), no other llama-server than the detector, no adapter.ts job, disk >= 8 GiB.
# Usage: run_x2b_gen.sh <requests.jsonl> <out traces.jsonl>   Writes <out>.status DONE | FAIL ...
set -u
REQ=$1; OUT=$2; T=$BOAR_WS/runner-local/be-0cfd4a77-cut7-headpass-x2; S=${OUT%.jsonl}.status; MD=$BOAR_WS/shared-models/emergency-detector
A=$BOAR_WS/rnd/research/coordinator/arms/headpass-st; SRV=$BOAR_WS/spikes/llama-b11010-cpu/bin/llama-server
echo "start $(date +%s) $(date '+%F %T') dump=${BOAR_PROMPT_DUMP:-off}" > "$S"
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 04a2a999828c8e46 ] || { echo "FAIL patch sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter.ts | cut -c1-16)" = "${EXPECT_ADAPTER:?}" ] || { echo "FAIL adapter sha (expect the opts-forwarding adapter, adapter-forward-opts.patch)" >> "$S"; exit 1; }
[ "$(cat ARM)" = cut7-headpass-x2 ] || { echo "FAIL ARM" >> "$S"; exit 1; }
[ "$(cat HEADPASS_X2B_PATCH_SHA256)" = "$(shasum -a 256 $A/headpass-x2b.vs-cut7.patch | cut -d' ' -f1)" ] || { echo "FAIL x2b patch sha" >> "$S"; exit 1; }
# the item pack resolves to its sidecar copy (v3proto first in BOAR_EVAL_PACK_DIRS; the requests pin the copy's sha256)
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
"$A/tools/busy.sh" && { echo "FAIL a llama-server or adapter.ts job is already running" >> "$S"; exit 1; }
FREE=$(df -k $HOME | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 8 ] || { echo "FAIL disk ${FREE} GiB < 8" >> "$S"; exit 1; }
export BOAR_EVAL_PACK_DIRS=$BOAR_WS/shared-data/packs/wave3:$BOAR_WS/shared-data/packs/wave2:$BOAR_WS/shared-data/packs/wave1:$BOAR_WS/shared-data/packs:$BOAR_WS/shared-data/crypto BOAR_SHARED_MODELS=$BOAR_WS/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
echo "cmd adapter.ts --requests $REQ --out $OUT ${EXTRA[*]}" >> "$S"
be/node_modules/tsx/dist/cli.mjs be/adapter.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
