#!/bin/bash
# LITEREADERS stage 2: Haiku 5.5-low N=4 shards, both orders, each reader vs gold, per pack run (deepthink/tools/shard_judge.sh, as lite5/tools/judge_180.sh).
# Requires aggregates/gate-r20.json PASS. Skips outputs already checked ok. Usage: nohup judge.sh > runs/judge.log 2>&1 &
set -u
H=<workspace>/rnd/research/coordinator/arms/litereaders; R=$H/runs; L=$H/../_lib; B=<workspace>/boar-eval/bench/selftest; SJ=$H/../deepthink/tools/shard_judge.sh
python3 -I -c "import json,sys;sys.exit(0 if json.load(open('$H/aggregates/gate-r20.json'))['verdict']=='PASS' else 8)" || { echo "gate-r20 not PASS: not judging"; exit 8; }
T0=$(date +%s)
for X in $(grep -- "-r20-" $R/RUNS); do p=$(echo $X | sed -E 's/^lr-[a-z0-9]+-r20-(.*)-s42$/\1/'); k=$(echo $X | cut -d- -f2); O=$R/$X.judgments.haiku55-low.jsonl
  python3 -I -c "import json,sys;[print(json.loads(l)['itemId']) for l in open(sys.argv[1])]" $R/$X.traces.jsonl > $R/$X.jids
  if python3 -I $L/check_judgments.py $O $R/$X.jids >/dev/null 2>&1; then echo "skip $X"; continue; fi
  n=$(wc -l < $R/$X.jids | tr -d ' '); SYS=selftest-$p-litereaders-$k-haiku55-low
  PREFLIGHT_PROBE_IDS=0 PREFLIGHT_CRITERION=$H/LITEREADERS-criterion.md PREFLIGHT_SET=selftest-180 PREFLIGHT_DECLARED_CALLS=$((2*n)) \
    bash $SJ --preflight $R/$X.traces.jsonl $O $B/$p $R/$X.jids $SYS 4 haiku || { echo "PREFLIGHT FAIL $X"; exit 8; }
  t=$(date +%s); bash $SJ $R/$X.traces.jsonl $O $B/$p $R/$X.jids $SYS 4 haiku || { echo "judge FAIL $X"; exit 1; }
  python3 -I $L/check_judgments.py $O $R/$X.jids $X || exit 1
  echo "$(date +%T) JUDGED $X rows=$(wc -l < $O | tr -d ' ') wall=$(( $(date +%s) - t ))s"
done
echo "ALLDONE judge wall=$(( $(date +%s) - T0 ))s rows=$(cat $R/*.judgments.haiku55-low.jsonl | wc -l | tr -d ' ')"
