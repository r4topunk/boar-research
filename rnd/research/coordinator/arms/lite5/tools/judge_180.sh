#!/bin/bash
# LITE5-180 stage 4: Haiku 5.5-low N=4 shards, both orders, ON and OFF vs gold, per pack (bench boar-eval/bench/selftest/<pack>), via deepthink/tools/shard_judge.sh.
# Preflight per run (PREFLIGHT_PROBE_IDS=0: guards only, 0 probe calls; criterion calls_cap Haiku 720), then judge, then check_judgments.py (fail closed).
# Requires gate180.py all PASS (aggregates/gate-180.json). Skips outputs already checked ok. Usage: nohup judge_180.sh > runs/180/judge_180.log 2>&1 &
set -u
H=<workspace>/rnd/research/coordinator/arms/lite5; R=$H/runs/180; L=$H/../_lib; B=<workspace>/boar-eval/bench/selftest; SJ=$H/../deepthink/tools/shard_judge.sh
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
python3 -I -c "import json,sys;sys.exit(0 if json.load(open('$H/aggregates/gate-180.json'))['verdict']=='PASS' else 8)" || { echo "gate-180 not PASS: not judging"; exit 8; }
T0=$(date +%s)
for m in off on; do for p in $PACKS; do X=lite5-180-$m-$p-s42; O=$R/$X.judgments.haiku55-low.jsonl
  python3 -I -c "import json,sys;[print(json.loads(l)['itemId']) for l in open(sys.argv[1])]" $R/$X.traces.jsonl > $R/$X.jids
  if python3 -I $L/check_judgments.py $O $R/$X.jids >/dev/null 2>&1; then echo "skip $X"; continue; fi
  SYS=selftest-$p-lite5-180-$m-haiku55-low
  PREFLIGHT_PROBE_IDS=0 PREFLIGHT_CRITERION=$H/LITE5-180-criterion.md PREFLIGHT_SET=selftest-180 PREFLIGHT_DECLARED_CALLS=40 \
    bash $SJ --preflight $R/$X.traces.jsonl $O $B/$p $R/$X.jids $SYS 4 haiku || { echo "PREFLIGHT FAIL $X"; exit 8; }
  t=$(date +%s); bash $SJ $R/$X.traces.jsonl $O $B/$p $R/$X.jids $SYS 4 haiku || { echo "judge FAIL $X"; exit 1; }
  python3 -I $L/check_judgments.py $O $R/$X.jids $X || exit 1
  echo "$(date +%T) JUDGED $X rows=$(wc -l < $O | tr -d ' ') wall=$(( $(date +%s) - t ))s"
done; done
echo "ALLDONE judge wall=$(( $(date +%s) - T0 ))s rows=$(cat $R/*.judgments.haiku55-low.jsonl | wc -l | tr -d ' ')"
