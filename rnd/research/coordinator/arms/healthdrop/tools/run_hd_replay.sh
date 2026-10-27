#!/bin/bash
# HEALTHDROP step-0 0-LLM route replay (= warnspec/tools/run_warn_replay.sh for the healthdrop tree). TREE=arm (default,
# kiln-local/be-cut7-healthdrop, ARM pr1+warn+healthdrop) or TREE=base (kiln-local/be-cut7-warn, ARM pr1+warn). be/replay-stub.ts
# (no model); no llama-server started. Detector :8094 must be up (never restarted). HEALTHGAP=1 always; WARN unset; HEALTHDROP=1 (ON) or unset.
# Usage: [TREE=base] [HEALTHDROP=1] run_hd_replay.sh <requests.jsonl> <out traces.jsonl>
set -u
H=<workspace>/rnd/research/coordinator/arms/healthgap
REQ=$1; OUT=$2; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
echo "start $(date +%s) $(date '+%F %T') tree=${TREE:-arm} HEALTHDROP=${HEALTHDROP:-}" > "$S"
case "${HEALTHDROP:-}" in 1|"") ;; *) echo "FAIL HEALTHDROP=${HEALTHDROP}" >> "$S"; exit 1 ;; esac
if [ "${TREE:-arm}" = base ]; then
  T=<workspace>/kiln-local/be-cut7-warn; [ "$(cat $T/ARM)" = pr1+warn ] && [ -z "${HEALTHDROP:-}" ] || { echo "FAIL base ARM/env" >> "$S"; exit 1; }
else
  T=<workspace>/kiln-local/be-cut7-healthdrop; [ "$(cat $T/ARM)" = pr1+warn+healthdrop ] || { echo "FAIL ARM" >> "$S"; exit 1; }
fi
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
grep -q 'process.env.HEALTHDROP\|process.env.WARN\|process.env.HEALTHGAP' src/routing/*.ts && { echo "FAIL engine reads env" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
FREE=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 3 ] || { echo "FAIL disk ${FREE} GiB < 3" >> "$S"; exit 1; }
[ -f be/replay-stub.ts ] && [ be/replay-stub.ts -nt be/adapter.ts ] || python3 -I $H/tools/mk_replay_stub.py "$T" >> "$S" || exit 1
export HEALTHGAP=1 BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
unset WARN
be/node_modules/tsx/dist/cli.mjs be/replay-stub.ts --requests "$REQ" --out "$OUT" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
