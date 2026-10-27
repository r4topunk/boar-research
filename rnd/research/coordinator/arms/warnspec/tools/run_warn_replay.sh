#!/bin/bash
# WARNSPEC-PATCH 0-LLM route replay = healthgap/tools/run_hg2_replay.sh for the warn tree: tree kiln-local/be-cut7-warn (ARM pr1+warn =
# wt/pr1 8ac9eb7a + tools/warn.patch) or, with TREE=pr1, the scratch pristine wt/pr1 tree (same adapter). be/replay-stub.ts (no model,
# answers "[STUB-MODEL]"); no llama-server started (busy.sh is logged). Detector :8094 must be up (never restarted). HEALTHGAP=1 always;
# WARN=1 (ON) or unset (OFF). Usage: [TREE=pr1] [WARN=1] run_warn_replay.sh <requests.jsonl> <out traces.jsonl>
set -u
A=<workspace>/rnd/research/coordinator/arms/warnspec; H=<workspace>/rnd/research/coordinator/arms/healthgap
REQ=$1; OUT=$2; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
BUSY=<workspace>/rnd/research/coordinator/arms/headpass-st/tools/busy.sh
echo "start $(date +%s) $(date '+%F %T') tree=${TREE:-warn} WARN=${WARN:-} busy=$("$BUSY" 2>&1 | head -1 | cut -c1-80)" > "$S"
case "${WARN:-}" in 1|"") ;; *) echo "FAIL WARN=${WARN}" >> "$S"; exit 1 ;; esac
if [ "${TREE:-warn}" = pr1 ]; then
  T=<scratch>
  [ "$(cat $T/ARM)" = pr1 ] && [ -z "${WARN:-}" ] || { echo "FAIL pr1 ARM/env" >> "$S"; exit 1; }
  diff -rq $T/src <workspace>/wt/pr1/src > /dev/null || { echo "FAIL not wt/pr1 src" >> "$S"; exit 1; }
else
  T=<workspace>/kiln-local/be-cut7-warn
  [ "$(cat $T/ARM)" = pr1+warn ] || { echo "FAIL ARM" >> "$S"; exit 1; }
  [ "$(shasum -a 256 $T/src/routing/warn.ts | cut -c1-16)" = "$(cut -c1-16 $A/tools/pins.warn.ts)" ] && [ "$(shasum -a 256 $T/src/routing/answer.ts | cut -c1-16)" = "$(cut -c1-16 $A/tools/pins.answer.ts)" ] || { echo "FAIL patched-file pins" >> "$S"; exit 1; }
fi
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
grep -q 'process.env.WARN\|process.env.HEALTHGAP' src/routing/*.ts && { echo "FAIL engine reads env" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
FREE=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}'); [ "$FREE" -ge 3 ] || { echo "FAIL disk ${FREE} GiB < 3" >> "$S"; exit 1; }
python3 -I $H/tools/mk_replay_stub.py "$T" >> "$S" || exit 1
export HEALTHGAP=1 BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
be/node_modules/tsx/dist/cli.mjs be/replay-stub.ts --requests "$REQ" --out "$OUT" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
