#!/bin/bash
# LITEREACH2-180 stage 4: Haiku 5.5-low N=4 shards, both orders, B20 vs gold, per pack (bench boar-eval/bench/selftest/<pack>) via deepthink/tools/shard_judge.sh; 360 calls total.
# Requires aggregates/gate-180.json PASS. Preflight guards only (PREFLIGHT_PROBE_IDS=0). Fail-closed check_judgments.py.
set -u
L=<workspace>/rnd/research/coordinator/arms/litereach2; R=$L/runs/180; LB=$L/../_lib; B=<workspace>/boar-eval/bench/selftest; SJ=$L/../deepthink/tools/shard_judge.sh
python3 -I -c "import json,sys;sys.exit(0 if json.load(open('$L/aggregates/gate-180.json'))['verdict']=='PASS' else 8)" || { echo "gate-180 not PASS: not judging"; exit 8; }
for q in $R/*.requests.jsonl; do X=$(basename ${q%.requests.jsonl}); p=${X#litereach2-b20-180-}; p=${p%-s42}; O=$R/$X.judgments.haiku55-low.jsonl
  python3 -I -c "import json,sys;[print(json.loads(l)['itemId']) for l in open(sys.argv[1])]" $R/$X.traces.jsonl > $R/$X.jids
  if python3 -I $LB/check_judgments.py $O $R/$X.jids >/dev/null 2>&1; then echo "skip $X"; continue; fi
  n=$(grep -c . $R/$X.jids); SYS=selftest-$p-litereach2-b20-180-haiku55-low
  PREFLIGHT_PROBE_IDS=0 PREFLIGHT_CRITERION=$L/LITEREACH2-180-criterion.md PREFLIGHT_SET=selftest-180 PREFLIGHT_DECLARED_CALLS=$((2*n)) \
    bash $SJ --preflight $R/$X.traces.jsonl $O $B/$p $R/$X.jids $SYS 4 haiku || { echo "PREFLIGHT FAIL $X"; exit 8; }
  bash $SJ $R/$X.traces.jsonl $O $B/$p $R/$X.jids $SYS 4 haiku || { echo "judge FAIL $X"; exit 1; }
  python3 -I $LB/check_judgments.py $O $R/$X.jids $X || exit 1
  echo "$(date +%T) JUDGED $X rows=$(wc -l < $O | tr -d ' ')"
done
echo "ALLDONE rows=$(cat $R/*.judgments.haiku55-low.jsonl | wc -l | tr -d ' ')"
