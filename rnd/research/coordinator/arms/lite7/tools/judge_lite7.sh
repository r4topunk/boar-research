#!/bin/bash
# LITE7 stage 3: Haiku 5.5-low N=4 shards, both orders, ON vs gold on the random20 (seed 616) ids only, per pack (bench boar-eval/bench/selftest/<pack>),
# via deepthink/tools/shard_judge.sh; preflight guards per pack (PREFLIGHT_PROBE_IDS=0, calls_cap Haiku 40), check_judgments.py fail closed.
# Requires aggregates/gate7-v2.json PASS. Usage: nohup judge_lite7.sh > runs/180/judge_lite7.log 2>&1 &
set -u
H=<workspace>/rnd/research/coordinator/arms/lite7; R=$H/runs/180; L=$H/../_lib; B=<workspace>/boar-eval/bench/selftest; SJ=$H/../deepthink/tools/shard_judge.sh
python3 -I -c "import json,sys;sys.exit(0 if json.load(open('$H/aggregates/gate7-v2.json'))['verdict']=='PASS' else 8)" || { echo "gate7-v2 not PASS: not judging"; exit 8; }
T0=$(date +%s)
for p in qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do
  X=lite7-r20-on-$p-s42; O=$R/$X.judgments.haiku55-low.jsonl
  python3 -I -c "import json,sys;[print(i) for i in json.load(open('$H/../lite6/aggregates/lite6.json'))['random20_seed616'] if i.startswith('st-$p-')]" > $R/$X.jids
  n=$(wc -l < $R/$X.jids | tr -d ' '); [ "$n" = 0 ] && { echo "none $p"; continue; }
  grep -qx "$X.judgments.haiku55-low.jsonl" $R/.calls.ledger 2>/dev/null || echo "$X.judgments.haiku55-low.jsonl" >> $R/.calls.ledger
  if python3 -I $L/check_judgments.py $O $R/$X.jids >/dev/null 2>&1; then echo "skip $X"; continue; fi
  SYS=selftest-$p-lite7-r20-on-haiku55-low
  PREFLIGHT_PROBE_IDS=0 PREFLIGHT_CRITERION=$H/LITE7-criterion-v2.md PREFLIGHT_SET=selftest-180 PREFLIGHT_DECLARED_CALLS=$((2*n)) \
    bash $SJ --preflight $R/lite7-180-on-$p-s42.traces.jsonl $O $B/$p $R/$X.jids $SYS 4 haiku || { echo "PREFLIGHT FAIL $X"; exit 8; }
  t=$(date +%s); bash $SJ $R/lite7-180-on-$p-s42.traces.jsonl $O $B/$p $R/$X.jids $SYS 4 haiku || { echo "judge FAIL $X"; exit 1; }
  python3 -I $L/check_judgments.py $O $R/$X.jids $X || exit 1
  echo "$(date +%T) JUDGED $X rows=$(wc -l < $O | tr -d ' ') wall=$(( $(date +%s) - t ))s"
done
echo "ALLDONE judge wall=$(( $(date +%s) - T0 ))s rows=$(cat $R/lite7-r20-*.judgments.haiku55-low.jsonl | wc -l | tr -d ' ')"
