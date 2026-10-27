#!/bin/bash
# JUDGE-V2: one more judge.v1 repeat (Haiku 5.5-low, judge.v1-low, N = 4 shards, both orders) on the cached mini K0 MAIN control answers (n 97, dev),
# same command path as arms/lp-screens/tools/run_arm.sh step 4 (deepthink/tools/shard_judge.sh), into arms/judge-v2/v1/rep<R>-<unit>.judgments.jsonl.
# Usage: run_v1.sh <repeat number, 2 or 3>. Calls are appended to runs/calls.ledger (shared cap with judge-v2.mjs, from the criterion).
set -u
R=$1; A=<workspace>/rnd/research/coordinator/arms; J=$A/judge-v2; C=$A/lp-screens/control; SJ=$A/deepthink/tools/shard_judge.sh
BE=<workspace>/boar-eval/bench; TR=$C/traces/lpctl-K0-main-s42.traces.jsonl; LED=$J/runs/calls.ledger; CAP=${CAP:-1200}
for u in v01 qa-cooking-se qa-money-se; do
  case $u in v01) B=$BE/v0.1;; *) B=$BE/selftest/$u;; esac
  I=$C/judgments/lpctl-K0-main-s42-$u.jids; O=$J/v1/rep$R-$u.judgments.jsonl; m=$(wc -l < $I | tr -d ' ')
  if python3 -I $A/_lib/check_judgments.py $O $I > /dev/null 2>&1; then echo "rep$R $u done"; continue; fi
  have=$(wc -l < $LED 2>/dev/null | tr -d ' '); have=${have:-0}
  [ $((have + 2*m)) -le $CAP ] || { echo "CAP: ledger $have + planned $((2*m)) > $CAP"; exit 6; }
  bash $SJ $TR $O $B $I jv2-v1rep$R-$u-haiku55-low 4 haiku > $J/runs/v1-rep$R-$u.log 2>&1 || { echo "judge FAIL rep$R $u"; exit 1; }
  python3 -I $A/_lib/check_judgments.py $O $I "v1rep$R-$u" || exit 1
  python3 -I -c "import json,sys;[print(json.dumps({'at':r.get('createdAt'),'tag':'v1:rep$R:$u:'+r['queryId']+':'+r['order'],'model':'claude-haiku-5-5','effort':'low','ok':r['ok']})) for r in map(json.loads,open(sys.argv[1]))]" $O >> $LED
  echo "rep$R $u ids=$m calls=$((2*m))"
done
