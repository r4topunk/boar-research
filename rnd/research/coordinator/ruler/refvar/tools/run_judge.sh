#!/bin/bash
# REFVAR judge passes (Haiku 5.5-low judge.v1-low, both orders, N=4). Usage: run_judge.sh <ref: v1|A|B>
set -u
D=<workspace>/rnd/research/coordinator; R=$D/ruler/refvar; SJ=$D/arms/deepthink/tools/shard_judge.sh; B=<workspace>/boar-eval/bench/v0.1
REF=$1
case $REF in v1) export JUDGE_CMD="node harness/judge.mjs";; A|B) export JUDGE_CMD="node harness/judge.mjs --refs $R/refs/draw$REF.jsonl";; *) exit 2;; esac
rc=0
for S in s17:$D/arms/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl s4b:$D/arms/gemma4-e2b/vs4b/traces/gemma4-e2b-vs4b-K0-main-s42.traces.jsonl; do
  n=${S%%:*}; t=${S#*:}
  bash $SJ "$t" "$R/judgments/refvar-$n-ref$REF.judgments.jsonl" "$B" "$R/refvar-20.ids" "refvar-$n-ref$REF-haiku55-low" 4 haiku || rc=$?
done
exit $rc
