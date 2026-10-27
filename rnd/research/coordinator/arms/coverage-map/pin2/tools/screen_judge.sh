#!/bin/bash
# PIN2-SCREEN judge (MacBook, Haiku 5.5-low judge.v1, N 4, both orders, seed 7) on divergent items only (criterion PIN2-SCREEN 175076c0).
# Units: v01 + qa-cooking-se for both arms (vs bench refs); h2h = PIN2 t27 traces vs a local bench whose refs are the base t27 texts. Ledger judge/calls.log.
set -u
A=<workspace>/rnd/research/coordinator/arms; D=$A/coverage-map/pin2; J=$D/judge; L=$A/_lib; SJ=$A/deepthink/tools/shard_judge.sh; BE=<workspace>/boar-eval/bench
python3 -I $D/tools/screen_plan.py || exit 1
run() { local TR=$1 B=$2 I=$3 O=$4 SYS=$5; local m; m=$(wc -l < $I | tr -d ' '); [ "$m" = 0 ] && return 0
  if python3 -I $L/check_judgments.py $O $I > /dev/null 2>&1; then echo "judged already $O"; return 0; fi
  local t=$(date +%s); bash $SJ $TR $O $B $I $SYS 4 haiku > ${O%.jsonl}.judge.log 2>&1 || { echo "judge FAIL $O"; exit 1; }
  python3 -I $L/check_judgments.py $O $I || exit 1
  echo "$(date '+%F %T') $(basename $O) ids=$m calls=$((2*m)) wall=$(( $(date +%s) - t ))s" >> $J/calls.log; }
for arm in base pin2; do
  TR=$D/traces/pin2screen-$arm-main-s42.traces.jsonl
  run $TR $BE/v0.1 $J/v01.ids $J/$arm-v01.judgments.jsonl pin2screen-$arm-v01-haiku55-low
  run $TR $BE/selftest/qa-cooking-se $J/cooking.ids $J/$arm-cooking.judgments.jsonl pin2screen-$arm-cooking-haiku55-low
done
run $D/traces/pin2screen-pin2-t27-s42.traces.jsonl $J/h2h-bench $J/h2h.ids $J/h2h.judgments.jsonl pin2screen-h2h-pin2-vs-base-haiku55-low
echo JUDGED
