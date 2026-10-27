#!/bin/bash
# TK2FIX-L1 runner = packs/tools/run_selftest.sh with tree kiln-local/be-0cfd4a77-cut7-tk2fix (cut 7 + tk2fix.vs-cut7.patch 6cd09ca6…; be/ = cut 7's runner, adapter 6298e5d3).
# Same env as the reference with-pack runs. Guards: detector :8094 up (never stopped), busy.sh free, disk >= 5 GiB. Usage: run_gen.sh <requests.jsonl> <out traces.jsonl>
set -u
REQ=$1; OUT=$2; T=<workspace>/kiln-local/be-0cfd4a77-cut7-tk2fix; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server; BZ=<workspace>/rnd/research/coordinator/arms/headpass-st/tools/busy.sh
echo "start $(date +%s) $(date '+%F %T')" > "$S"
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 0fba26b8c55aa776 ] || { echo "FAIL patch sha" >> "$S"; exit 1; }
[ "$(cut -c1-16 TK2FIX_PATCH_SHA256)" = 6cd09ca64067bd82 ] || { echo "FAIL tk2fix patch sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter.ts | cut -c1-16)" = 6298e5d3f49414fe ] || { echo "FAIL adapter sha" >> "$S"; exit 1; }
[ "$(cat ARM)" = tk2fix-cut7 ] || { echo "FAIL ARM" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
"$BZ" && { echo "FAIL a llama-server or adapter job is already running" >> "$S"; exit 1; }
FREE=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 5 ] || { echo "FAIL disk ${FREE} GiB < 5" >> "$S"; exit 1; }
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave3:<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
echo "cmd adapter.ts --requests $REQ --out $OUT ${EXTRA[*]}" >> "$S"
be/node_modules/tsx/dist/cli.mjs be/adapter.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
