#!/bin/bash
# LITESAFETY runner: tree kiln-local/be-cut7-warn (ARM pr1+warn, pins warnspec/tools/pins.*), side adapter be/adapter-litesafety.ts
# (tools/mk_adapter.py, sha e0ea51a9...) or, with REPLAY=1, be/replay-stub-litesafety.ts (496fc340...; no model, no server).
# Env always NUMGUARD=1 HEALTHGAP=1 WARN=1 (LITE_* unset). The 1.7B (modelId qwen3-1.7b-q4km in the requests) gets
# BOAR_SERVER_EXTRA_ARGS="--reasoning off". Guards (generation): busy.sh wait (never two servers), detector :8094 up, disk >= 5 GiB (wait).
# Usage: [REPLAY=1] run_ls.sh <requests.jsonl> <out traces.jsonl>
set -u
T=<workspace>/kiln-local/be-cut7-warn; REQ=$1; OUT=$2; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
SRV=<workspace>/spikes/llama-b11010-cpu/bin/llama-server; A=<workspace>/rnd/research/coordinator/arms; BUSY=$A/headpass-st/tools/busy.sh; W=$A/warnspec
echo "start $(date +%s) $(date '+%F %T') replay=${REPLAY:-0}" > "$S"
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
[ "$(cat ARM)" = pr1+warn ] && [ "$(cat COMMIT)" = 8ac9eb7a0f79d9983a5712079379f595f3e4ad73 ] || { echo "FAIL ARM/COMMIT" >> "$S"; exit 1; }
[ "$(shasum -a 256 src/routing/warn.ts | cut -c1-16)" = "$(cut -c1-16 $W/tools/pins.warn.ts)" ] && [ "$(shasum -a 256 src/routing/answer.ts | cut -c1-16)" = "$(cut -c1-16 $W/tools/pins.answer.ts)" ] || { echo "FAIL patched-file pins" >> "$S"; exit 1; }
grep -q 'process.env.WARN\|process.env.HEALTHGAP\|process.env.NUMGUARD' src/routing/*.ts && { echo "FAIL engine reads env" >> "$S"; exit 1; }
if [ "${REPLAY:-0}" = 1 ]; then AD=be/replay-stub-litesafety.ts; PIN=496fc3402e18f446; else AD=be/adapter-litesafety.ts; PIN=e0ea51a998d04f11; fi
[ "$(shasum -a 256 $AD | cut -c1-16)" = $PIN ] || { echo "FAIL adapter pin $AD" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
if [ "${REPLAY:-0}" != 1 ]; then
  w=0; while "$BUSY" > /dev/null 2>&1; do [ $w -ge 60 ] && { echo "FAIL busy 60 min" >> "$S"; exit 1; }; [ $w = 0 ] && echo "wait-busy $(date '+%T')" >> "$S"; w=$((w+1)); sleep 60; done
  w=0; while :; do FREE=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 5 ] && break
    [ $w -ge 60 ] && { echo "FAIL disk ${FREE} GiB < 5 for 60 min" >> "$S"; exit 1; }; [ $w = 0 ] && echo "wait-disk ${FREE} GiB $(date '+%T')" >> "$S"; w=$((w+1)); sleep 60; done
  echo "disk ${FREE} GiB" >> "$S"
fi
export NUMGUARD=1 HEALTHGAP=1 WARN=1
unset BOAR_SERVER_EXTRA_ARGS; grep -q '"modelId":"qwen3-1.7b-q4km"' "$REQ" && export BOAR_SERVER_EXTRA_ARGS="--reasoning off"
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
EXTRA=(); [ "${REPLAY:-0}" != 1 ] && EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
echo "cmd $AD --requests $REQ --out $OUT ${EXTRA[*]+"${EXTRA[*]}"} extra=${BOAR_SERVER_EXTRA_ARGS:-}" >> "$S"
be/node_modules/tsx/dist/cli.mjs $AD --requests "$REQ" --out "$OUT" ${EXTRA[@]+"${EXTRA[@]}"} > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
