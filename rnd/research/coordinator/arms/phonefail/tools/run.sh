#!/bin/bash
# PHONEFAIL runner (copy of arms/longsession/tools/run_ls.sh on the pr1+warn tree kiln-local/be-cut7-warn, WARN unset; disk floor 5.2 GiB) = was: LONGSESSION runner = arms/seedgen/tools/run_probe.sh (cut 7 tree kiln-local/be-0cfd4a77-cut7 = 0cfd4a77 + cut7 patch 0fba26b8, adapter 6298e5d3),
# server backend, --threads 4, ship profile, mmbert detector v3b on :8094 (never stopped), claim kit boar-crypto + boar-wikivoyage-en (resolved from
# BOAR_EVAL_PACK_DIRS). Guard: before starting, waits (poll 60 s, up to 60 min) while busy.sh reports a llama-server other than the detector or an
# adapter.ts job: never two servers. DUMP=<prompts.jsonl> -> --dump-prompts. Writes <out>.status DONE | FAIL ...
# Usage: run_ls.sh <requests.jsonl> <out traces.jsonl>
set -u
REQ=$1; OUT=$2; T=<workspace>/kiln-local/be-cut7-warn; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server; BUSY=<workspace>/rnd/research/coordinator/arms/headpass-st/tools/busy.sh
echo "start $(date +%s) $(date '+%F %T')" > "$S"
w=0; while "$BUSY" > /dev/null 2>&1; do [ $w -ge ${WAIT_MAX:-60} ] && { echo "FAIL busy for ${WAIT_MAX:-60} min" >> "$S"; exit 1; }; [ $w = 0 ] && echo "wait-busy $(date '+%T')" >> "$S"; w=$((w+1)); sleep 60; done
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cut -c1-8 COMMIT)" = 8ac9eb7a ] || { echo "FAIL commit" >> "$S"; exit 1; }
[ "$(shasum -a 256 be/adapter.ts | cut -c1-16)" = 55adc5ff83d37d20 ] || { echo "FAIL adapter sha" >> "$S"; exit 1; }
[ "$(cat ARM)" = "pr1+warn" ] || { echo "FAIL ARM" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
FREE=$(df -k <home> | tail -1 | awk '{print int($4/1024)}'); [ "$FREE" -ge 5325 ] || { echo "FAIL disk ${FREE} MiB < 5325" >> "$S"; exit 1; }
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal; unset WARN NUMGUARD HEALTHGAP
EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
[ -n "${DUMP:-}" ] && EXTRA+=(--dump-prompts "$DUMP")
echo "cmd adapter.ts --requests $REQ --out $OUT ${EXTRA[*]}" >> "$S"
be/node_modules/tsx/dist/cli.mjs be/adapter.ts --requests "$REQ" --out "$OUT" "${EXTRA[@]}" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
