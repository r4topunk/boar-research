#!/bin/bash
# HEALTHGAP-r2 generation runner (= tools/run_hg.sh with the r2 pins: ARM cut7+healthgap-r2, pins-r2.*): tree kiln-local/be-0cfd4a77-cut7-healthgap
# (ARM cut7+healthgap = cut 7 + tools/healthgap.patch; be/adapter.ts = cut 7's + tools/healthgap-adapter.patch: HEALTHGAP=1 ->
# deps.healthgap = true; the engine reads no env). HEALTHGAP=1 (ON) or unset (OFF control) from the caller.
# Guards: busy.sh wait (never two servers), detector :8094 up, patched-file + adapter pins, disk >= 5 GiB.
# Usage: run_hg.sh <requests.jsonl> <out traces.jsonl>
set -u
T=<workspace>/kiln-local/be-0cfd4a77-cut7-healthgap; REQ=$1; OUT=$2; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server; BUSY=<workspace>/rnd/research/coordinator/arms/headpass-st/tools/busy.sh
H=<workspace>/rnd/research/coordinator/arms/healthgap
echo "start $(date +%s) $(date '+%F %T') env HEALTHGAP=${HEALTHGAP:-}" > "$S"
w=0; while "$BUSY" > /dev/null 2>&1; do [ $w -ge ${WAIT_MAX:-60} ] && { echo "FAIL busy for ${WAIT_MAX:-60} min" >> "$S"; exit 1; }; [ $w = 0 ] && echo "wait-busy $(date '+%T')" >> "$S"; w=$((w+1)); sleep 60; done
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 0fba26b8c55aa776 ] || { echo "FAIL patch sha" >> "$S"; exit 1; }
[ "$(cat ARM)" = cut7+healthgap-r2 ] || { echo "FAIL ARM" >> "$S"; exit 1; }
grep -q 'process.env.HEALTHGAP === "1" ? { healthgap: true }' be/adapter.ts && ! grep -q 'process.env.HEALTHGAP' src/routing/*.ts || { echo "FAIL adapter switch / engine env" >> "$S"; exit 1; }
[ "$(shasum -a 256 src/routing/healthGap.ts | cut -c1-16)" = "$(cut -c1-16 $H/tools/pins-r2.healthGap.ts)" ] && [ "$(shasum -a 256 src/routing/answer.ts | cut -c1-16)" = "$(cut -c1-16 $H/tools/pins-r2.answer.ts)" ] || { echo "FAIL patched-file pins" >> "$S"; exit 1; }
case "${HEALTHGAP:-}" in 1|"") ;; *) echo "FAIL HEALTHGAP=${HEALTHGAP}" >> "$S"; exit 1 ;; esac
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
FREE=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 5 ] || { echo "FAIL disk ${FREE} GiB < 5" >> "$S"; exit 1; }
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
[ -n "${DUMP:-}" ] && EXTRA+=(--dump-prompts "$DUMP")
echo "cmd adapter.ts --requests $REQ --out $OUT ${EXTRA[*]}" >> "$S"
be/node_modules/tsx/dist/cli.mjs be/adapter.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
