#!/bin/bash
# TK2FIX-L1 stage 5: Haiku 5.5-low N=4 shards, both orders, ON vs gold per pack (bench boar-eval/bench/selftest/<pack>), via deepthink/tools/shard_judge.sh.
# Preflight per run (PREFLIGHT_PROBE_IDS=0: guards only; criterion calls_cap Haiku 720), judge, check_judgments.py (fail closed). Requires l1/gate.json PASS.
set -u
L=<workspace>/rnd/research/coordinator/arms/tk2fix/l1; R=$L/runs; LIB=$L/../../_lib; B=<workspace>/boar-eval/bench/selftest; SJ=$L/../../deepthink/tools/shard_judge.sh
PACKS="boar-medlineplus-en boar-factbook boar-simplewiki-en qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en"
python3 -I -c "import json,sys;sys.exit(0 if json.load(open('$L/gate.json'))['verdict']=='PASS' else 8)" || { echo "gate not PASS: not judging"; exit 8; }
T0=$(date +%s)
for p in $PACKS; do X=tk2fix-l1-$p-s42; O=$R/$X.judgments.haiku55-low.jsonl
  python3 -I -c "import json,sys;[print(json.loads(l)['itemId']) for l in open(sys.argv[1])]" $R/$X.traces.jsonl > $R/$X.jids
  if python3 -I $LIB/check_judgments.py $O $R/$X.jids >/dev/null 2>&1; then echo "skip $X"; continue; fi
  SYS=selftest-$p-tk2fix-l1-haiku55-low
  PREFLIGHT_PROBE_IDS=0 PREFLIGHT_CRITERION=$L/../TK2FIX-L1-criterion.md PREFLIGHT_SET=selftest-180 PREFLIGHT_DECLARED_CALLS=40 \
    bash $SJ --preflight $R/$X.traces.jsonl $O $B/$p $R/$X.jids $SYS 4 haiku || { echo "PREFLIGHT FAIL $X"; exit 8; }
  t=$(date +%s); bash $SJ $R/$X.traces.jsonl $O $B/$p $R/$X.jids $SYS 4 haiku || { echo "judge FAIL $X"; exit 1; }
  python3 -I $LIB/check_judgments.py $O $R/$X.jids $X || exit 1
  echo "$(date +%T) JUDGED $X rows=$(wc -l < $O | tr -d ' ') wall=$(( $(date +%s) - t ))s"
done
echo "ALLDONE judge wall=$(( $(date +%s) - T0 ))s rows=$(cat $R/*.judgments.haiku55-low.jsonl | wc -l | tr -d ' ')"
