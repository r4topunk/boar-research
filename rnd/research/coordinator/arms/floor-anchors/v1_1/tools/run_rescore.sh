#!/bin/bash
# JUDGE-V1_1 addendum 1: re-score the two FLOOR separability arms on the v0.1 57 under judge.v1_1 (W1). Same ledger; CAP 640.
set -u
H=<workspace>/rnd/research/coordinator/arms/floor-anchors; V=$H/v1_1; A=$(dirname $H); SJ=$A/deepthink/tools/shard_judge.sh
LIB=<workspace>/boar-eval/scorers/vendor/eval-lib-v1_1; B=<workspace>/boar-eval/bench/v0.1; LED=$V/runs/calls.ledger; CAP=640; I=$A/litepacks/data/v01-57.ids
for arm in onebee ctl17; do
  case $arm in onebee) TR=$H/traces/floor-anchors-K0-main-sub3e6183-s42.traces.jsonl;; ctl17) TR=$A/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl;; esac
  O=$V/judgments/W1-sep-$arm.judgments.jsonl
  if python3 -I $A/_lib/check_judgments.py $O $I > /dev/null 2>&1; then echo "done $arm"; continue; fi
  have=$(wc -l < $LED | tr -d ' '); [ $((have + 114)) -le $CAP ] || { echo "CAP: ledger $have + 114 > $CAP"; exit 6; }
  BOAR_EVAL_LIB=$LIB bash $SJ $TR $O $B $I fa11-W1-sep-$arm-haiku55-low 4 haiku > $V/runs/W1-sep-$arm.log 2>&1 || { echo "judge FAIL $arm"; exit 1; }
  python3 -I $A/_lib/check_judgments.py $O $I || exit 1
  printf '{"judgeVersion":"judge.v1_1-low","lib":"%s","judgeCoreSha256":"%s"}\n' $LIB $(shasum -a 256 $LIB/judge-core.mjs | cut -d' ' -f1) > ${O%.jsonl}.version
  python3 -I -c "import json,sys;[print(json.dumps({'at':r.get('createdAt'),'tag':'W1:sep-'+sys.argv[2]+':'+r['queryId']+':'+r['order'],'model':'claude-haiku-5-5','effort':'low','ok':r['ok']})) for r in map(json.loads,open(sys.argv[1]))]" $O $arm >> $LED
  echo "ok $arm ledger=$(wc -l < $LED | tr -d ' ')"
done
