#!/bin/bash
# MATHROUTE runner = arms/longsession/tools/run_ls.sh with the tree as a parameter.
#   arm A: kiln-local/be-0cfd4a77-cut7 (ARM cut7, untouched), no env.
#   arms B/C: kiln-local/be-0cfd4a77-cut7-mathroute (ARM cut7+mathroute = cut 7 + tools/mathroute-env.patch bbee9f4a…, env-gated, never committed)
#     B: MATHROUTE_NOCALC=1 MATHROUTE_RETRIEVE=off   C: MATHROUTE_NOCALC=1 MATHROUTE_RETRIEVE=on   (env passed by the caller)
# Same guards: busy.sh wait (never two servers), detector :8094 up, disk >= 8 GiB, patch/adapter sha checks.
# Usage: run_mr.sh <tree> <requests.jsonl> <out traces.jsonl>
set -u
T=$1; REQ=$2; OUT=$3; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server; BUSY=<workspace>/rnd/research/coordinator/arms/headpass-st/tools/busy.sh
echo "start $(date +%s) $(date '+%F %T') env NOCALC=${MATHROUTE_NOCALC:-} RETRIEVE=${MATHROUTE_RETRIEVE:-}" > "$S"
w=0; while "$BUSY" > /dev/null 2>&1; do [ $w -ge ${WAIT_MAX:-60} ] && { echo "FAIL busy for ${WAIT_MAX:-60} min" >> "$S"; exit 1; }; [ $w = 0 ] && echo "wait-busy $(date '+%T')" >> "$S"; w=$((w+1)); sleep 60; done
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-16 PATCH_SHA256)" = 0fba26b8c55aa776 ] || { echo "FAIL patch sha" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter.ts | cut -c1-16)" = 6298e5d3f49414fe ] || { echo "FAIL adapter sha" >> "$S"; exit 1; }
case "$(cat ARM)" in
  cut7) [ -z "${MATHROUTE_NOCALC:-}${MATHROUTE_RETRIEVE:-}" ] || { echo "FAIL env on the plain tree" >> "$S"; exit 1; } ;;
  cut7+mathroute) grep -q 'MATHROUTE_NOCALC' src/routing/answer.ts || { echo "FAIL mathroute patch missing" >> "$S"; exit 1; } ;;
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
