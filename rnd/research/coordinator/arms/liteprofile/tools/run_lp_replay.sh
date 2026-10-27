#!/bin/bash
# LITEPROFILE 0-LLM route replay (= warnspec/tools/run_warn_replay.sh for the liteprofile tree). TREE=lp: kiln-local/be-cut7-liteprofile
# (ARM pr1+liteprofile = wt/pr1 8ac9eb7a + tools/liteprofile.patch), every lite flag off (no WARN, no groupSources, no packHeadPass/
# packDense2 settings); TREE=pr1: the scratch pristine wt/pr1 tree (same adapter). be/replay-stub.ts = no model ("[STUB-MODEL]");
# no llama-server started; detector :8094 must be up (never restarted). HG=1 -> HEALTHGAP=1 (the PR-branch eval default), HG=0 -> unset.
# Usage: TREE=lp|pr1 HG=1|0 run_lp_replay.sh <requests.jsonl> <out traces.jsonl>
set -u
H=<workspace>/rnd/research/coordinator/arms/healthgap
REQ=$1; OUT=$2; S=${OUT%.jsonl}.status; MD=<workspace>/shared-models/emergency-detector
BUSY=<workspace>/rnd/research/coordinator/arms/headpass-st/tools/busy.sh
echo "start $(date +%s) $(date '+%F %T') tree=${TREE} HG=${HG} busy=$("$BUSY" 2>&1 | head -1 | cut -c1-80)" > "$S"
case "${TREE}" in
  pr1) T=<scratch>
       [ "$(cat $T/ARM)" = pr1 ] || { echo "FAIL pr1 ARM" >> "$S"; exit 1; }
       diff -rq $T/src <workspace>/wt/pr1/src > /dev/null || { echo "FAIL not wt/pr1 src" >> "$S"; exit 1; } ;;
  lp)  T=<workspace>/kiln-local/be-cut7-liteprofile
       [ "$(cat $T/ARM)" = pr1+liteprofile ] || { echo "FAIL ARM" >> "$S"; exit 1; }
       ( cd <workspace>/wt/pr1 && git diff --quiet ) || { echo "FAIL wt/pr1 dirty" >> "$S"; exit 1; } ;;
  *) echo "FAIL TREE" >> "$S"; exit 1 ;;
esac
cd "$T" || { echo "FAIL tree" >> "$S"; exit 1; }
grep -qE "process.env.(WARN|HEALTHGAP|SOURCEGROUP)" src/routing/*.ts src/rag/*.ts && { echo "FAIL engine reads env" >> "$S"; exit 1; }
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector :8094 down" >> "$S"; exit 1; }
python3 -I $H/tools/mk_replay_stub.py "$T" >> "$S" || exit 1
unset WARN SOURCEGROUP HEALTHGAP BOAR_PROMPT_DUMP
[ "$HG" = 1 ] && export HEALTHGAP=1
[ "${LPWARN:-0}" = 1 ] && export WARN=1  # ON smoke only (composition check vs the warn tree)
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
be/node_modules/tsx/dist/cli.mjs be/replay-stub.ts --requests "$REQ" --out "$OUT" > "${OUT%.jsonl}.log" 2>&1; rc=$?
echo "end $(date +%s) rc=$rc" >> "$S"; if [ $rc = 0 ]; then echo DONE >> "$S"; else echo "FAIL rc=$rc" >> "$S"; fi; exit $rc
