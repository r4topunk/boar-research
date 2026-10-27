#!/bin/bash
# COVERAGE-MATRIX driver (MacBook, nohup). Phase 1: generate the 6 new cells on the mini (all launched; the mini slot lock runs 2 at a time), GEN_ONLY=1.
# Phase 2: judge cells one at a time in the frozen priority order (MATRIX-criterion.md §4); a cell over the cap is skipped as pending (rc 9), later cells
# still get their chance. Phase 3: report (0 LLM). Resumable: finished generation and judgments are skipped by run_cell.sh.
set -u
A=<workspace>/rnd/research/coordinator/arms; CM=$A/coverage-matrix; G=$A/gemma4-e2b; RC=$CM/tools/run_cell.sh; LG=$CM/logs
export OUT_BASE=$CM CRITERION=$CM/MATRIX-criterion.md
CELLS=("q17 KA $CM/cand80.ids $CM/kadirs.patch" "q17 KA $CM/main-97.ids $CM/kadirs.patch" "gemma KA $CM/cand80.ids $CM/gemma-ka.patch"
       "q4b K0 $CM/cand80.ids $G/vs4b-engsamp.patch" "q4b K3 $CM/cand80.ids $G/vs4b-engsamp.patch" "q4b KA $CM/cand80.ids $CM/q4b-ka.patch")
echo "$(date '+%F %T') phase 1 (generation)"
pids=()
for c in "${CELLS[@]}"; do set -- $c; n=$1-$2-$(basename $3 .ids); GEN_ONLY=1 bash $RC $1 $2 $3 $4 > $LG/gen-$n.log 2>&1 & pids+=($!); sleep 5; done
fail=0; for p in "${pids[@]}"; do wait $p || fail=$((fail+1)); done
echo "$(date '+%F %T') phase 1 done, failed cells: $fail"
echo "$(date '+%F %T') phase 2 (judging in priority order)"
for c in "${CELLS[@]}"; do set -- $c; n=$1-$2-$(basename $3 .ids)
  bash $RC $1 $2 $3 $4 > $LG/judge-$n.log 2>&1; rc=$?; echo "$(date '+%F %T') $n rc=$rc $(tail -1 $LG/judge-$n.log)"
done
python3 -I $CM/tools/matrix_report.py $CM/matrix-report.json > $LG/report.log 2>&1; echo "$(date '+%F %T') report rc=$? ALL DONE"
