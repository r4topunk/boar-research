#!/bin/bash
# HEALTHGAP-r2 0-LLM route replay (rule v1.2 §5c) = tools/run_hg_replay.sh with the r2 pins: tree kiln-local/be-0cfd4a77-cut7-healthgap
# (ARM cut7+healthgap-r2 = cut 7 + tools/healthgap-r2.patch), or with TREE=c7 the scratch plain cut 7 tree (src diff-checked vs
# kiln-local/be-0cfd4a77-cut7). be/replay-stub.ts (mk_replay_stub.py): no model, no llama-server started, so busy.sh is logged
# and not waited on (generation waits; tools/run_hg2.sh). Detector :8094 must be up (never restarted). HEALTHGAP=1 (ON) or unset.
# Usage: [TREE=c7] run_hg2_replay.sh <requests.jsonl> <out traces.jsonl>
set -u
H=<workspace>/rnd/research/coordinator/arms/healthgap; REQ=$1; OUT=$2; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
BUSY=<workspace>/rnd/research/coordinator/arms/headpass-st/tools/busy.sh
echo "start $(date +%s) $(date '+%F %T') tree=${TREE:-hg2} env HEALTHGAP=${HEALTHGAP:-} busy=$("$BUSY" 2>&1 | head -1 | cut -c1-80)" > "$S"
case "${HEALTHGAP:-}" in 1|"") ;; *) echo "FAIL HEALTHGAP=${HEALTHGAP}" >> "$S"; exit 1 ;; esac
if [ "${TREE:-hg2}" = c7 ]; then
  T=<scratch>
  diff -rq $T/src <workspace>/kiln-local/be-0cfd4a77-cut7/src > /dev/null || { echo "FAIL not cut 7" >> "$S"; exit 1; }
  [ "$(cat $T/ARM)" = cut7 ] && [ -z "${HEALTHGAP:-}" ] || { echo "FAIL c7 ARM/env" >> "$S"; exit 1; }
else
  T=<workspace>/kiln-local/be-0cfd4a77-cut7-healthgap
  [ "$(cat $T/ARM)" = cut7+healthgap-r2 ] || { echo "FAIL ARM" >> "$S"; exit 1; }
  [ "$(shasum -a 256 $T/src/routing/healthGap.ts | cut -c1-16)" = "$(cut -c1-16 $H/tools/pins-r2.healthGap.ts)" ] && [ "$(shasum -a 256 $T/src/routing/answer.ts | cut -c1-16)" = "$(cut -c1-16 $H/tools/pins-r2.answer.ts)" ] || { echo "FAIL patched-file pins" >> "$S"; exit 1; }
fi
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
grep -q 'process.env.HEALTHGAP' src/routing/*.ts && { echo "FAIL engine reads env" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
FREE=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 3 ] || { echo "FAIL disk ${FREE} GiB < 3" >> "$S"; exit 1; }
python3 -I $H/tools/mk_replay_stub.py "$T" >> "$S" || exit 1
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
be/node_modules/tsx/dist/cli.mjs be/replay-stub.ts --requests "$REQ" --out "$OUT" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
