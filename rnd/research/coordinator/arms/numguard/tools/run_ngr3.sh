#!/bin/bash
# NUMGUARD-r3 runner = run_ngf.sh with the r3 pins: tree kiln-local/be-0cfd4a77-cut7-numguard-r2 reused (ARM cut7+numguard-r3 = cut 7 + tools/numguard-r3.patch 00062063;
# be/adapter.ts = + tools/numguard-r3-adapter.patch: NUMGUARD=1 -> deps.numguard = true; the engine reads no env). NUMGUARD=1 required, NUMGUARD_NORETRIEVE refused.
#   tree: the numguard copy (ARM cut7+numguard); NUMGUARD=1 (ON) or unset (OFF control) passed by the caller; the plain cut 7 tree (ARM cut7) refuses NUMGUARD.
#   patched files pinned: src/routing/numguard.ts a149716f1650c4b9…, src/routing/answer.ts 0452ce613e5350ef… (= tools/numguard.patch applied to cut 7).
# Same guards as run_mr.sh: busy.sh wait (never two servers), detector :8094 up, disk >= 8 GiB, patch/adapter sha checks.
# Usage: run_ng.sh <tree> <requests.jsonl> <out traces.jsonl>
set -u
T=$1; REQ=$2; OUT=$3; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server; BUSY=<workspace>/rnd/research/coordinator/arms/headpass-st/tools/busy.sh
echo "start $(date +%s) $(date '+%F %T') env NUMGUARD=${NUMGUARD:-} NUMGUARD_NORETRIEVE=${NUMGUARD_NORETRIEVE:-}" > "$S"
w=0; while "$BUSY" > /dev/null 2>&1; do [ $w -ge ${WAIT_MAX:-60} ] && { echo "FAIL busy for ${WAIT_MAX:-60} min" >> "$S"; exit 1; }; [ $w = 0 ] && echo "wait-busy $(date '+%T')" >> "$S"; w=$((w+1)); sleep 60; done
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 0fba26b8c55aa776 ] || { echo "FAIL patch sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter.ts | cut -c1-16)" = 035b811c3ae6589a ] || { echo "FAIL adapter sha" >> "$S"; exit 1; }
case "$(cat ARM)" in
  cut7) [ -z "${NUMGUARD:-}" ] || { echo "FAIL env on the plain tree" >> "$S"; exit 1; } ;;
  cut7+numguard-r3) [ "${NUMGUARD:-}" = 1 ] && [ -z "${NUMGUARD_NORETRIEVE:-}" ] && ! grep -q 'process.env.NUMGUARD' src/routing/answer.ts && grep -q 'process.env.NUMGUARD === "1" ? { numguard: true }' be/adapter.ts && [ "$(shasum -a 256 src/routing/numguard.ts | cut -c1-16)" = 12116c45defb1286 ] && [ "$(shasum -a 256 src/routing/answer.ts | cut -c1-16)" = d3216dabd91f1049 ] || { echo "FAIL numguard-r3 patch or env" >> "$S"; exit 1; } ;;
  *) echo "FAIL ARM" >> "$S"; exit 1 ;;
esac
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
FREE=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 8 ] || { echo "FAIL disk ${FREE} GiB < 8" >> "$S"; exit 1; }
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
[ -n "${DUMP:-}" ] && EXTRA+=(--dump-prompts "$DUMP")
echo "cmd adapter.ts --requests $REQ --out $OUT ${EXTRA[*]}" >> "$S"
be/node_modules/tsx/dist/cli.mjs be/adapter.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
