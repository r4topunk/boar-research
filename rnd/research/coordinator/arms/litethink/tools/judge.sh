#!/bin/bash
# LITETHINK judge = lite5/tools/judge_180.sh pattern on the selftest20 rows: Haiku 5.5-low N=4 shards, both orders, think arm vs gold, per pack.
# Usage: judge.sh <256|512>  (requires gate.py PASS-or-reported and KILL=1 NO-KILL on that budget: aggregates/gate-t<B>.json verdict != KILL)
set -u; BU=$1
H=<workspace>/rnd/research/coordinator/arms/litethink; R=$H/runs; L=$H/../_lib; B=<workspace>/boar-eval/bench/selftest; SJ=$H/../deepthink/tools/shard_judge.sh
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
python3 -I -c "import json,sys;sys.exit(8 if json.load(open('$H/aggregates/gate-t$BU.json'))['kill']=='KILL' else 0)" || { echo "t$BU killed: not judging"; exit 8; }
T0=$(date +%s)
for p in $PACKS; do X=litethink-t$BU-st20-$p-s42; O=$R/$X.judgments.haiku55-low.jsonl
  python3 -I -c "import json,sys;[print(json.loads(l)['itemId']) for l in open(sys.argv[1])]" $R/$X.traces.jsonl > $R/$X.jids
  if python3 -I $L/check_judgments.py $O $R/$X.jids >/dev/null 2>&1; then echo "skip $X"; continue; fi
  N=$(( $(wc -l < $R/$X.jids) * 2 )); SYS=selftest-$p-litethink-t$BU-haiku55-low
  PREFLIGHT_PROBE_IDS=0 PREFLIGHT_CRITERION=$H/LITETHINK-criterion.md PREFLIGHT_SET=selftest-180 PREFLIGHT_DECLARED_CALLS=$N \
    bash $SJ --preflight $R/$X.traces.jsonl $O $B/$p $R/$X.jids $SYS 4 haiku || { echo "PREFLIGHT FAIL $X"; exit 8; }
  t=$(date +%s); bash $SJ $R/$X.traces.jsonl $O $B/$p $R/$X.jids $SYS 4 haiku || { echo "judge FAIL $X"; exit 1; }
  python3 -I $L/check_judgments.py $O $R/$X.jids $X || exit 1
  echo "$(date +%T) JUDGED $X rows=$(wc -l < $O | tr -d ' ') wall=$(( $(date +%s) - t ))s"
done
echo "ALLDONE t$BU judge wall=$(( $(date +%s) - T0 ))s"
