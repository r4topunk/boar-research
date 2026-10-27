#!/bin/bash
# LITEDECLINE judge (MacBook): Haiku 5.5-low judge.v1-low, N = 4 shards, both orders, uncapped, via deepthink/tools/shard_judge.sh (absolute paths).
# Preflight runs without --criterion: the frozen criterion says "uncapped" and has no ## Budget calls_cap line (Deviations).
# ON: every judged id (v01: data/v01-57.ids; st: the 20 ids per pack). OFF / OFF5: only ids whose answer text differs from ON (tools/changed_ids.py);
# identical answers reuse ON's rows in agg.py. Preflight per run (guards only, PREFLIGHT_PROBE_IDS=0), check_judgments.py after (fail closed).
# Usage: judge.sh <on|off|off5>
set -u
ARM=$1; H=<workspace>/rnd/research/coordinator/arms/litedecline; L=$H/../_lib; SJ=$H/../deepthink/tools/shard_judge.sh; BE=<workspace>/boar-eval/bench
SETS="v01 st-qa-travel-se st-qa-ethereum-se st-qa-bitcoin-se st-qa-health-se st-qa-outdoors-se st-boar-firstaid-en st-boar-medlineplus-en st-boar-factbook st-boar-simplewiki-en"
for s in $SETS; do X=ld-$ARM-$s-s42; TR=$H/traces/$X.traces.jsonl; O=$H/judgments/$X.judgments.jsonl; I=$H/judgments/$X.jids
  if [ $s = v01 ]; then B=$BE/v0.1; PS=v01; else B=$BE/selftest/${s#st-}; PS=selftest-180; fi
  if [ $ARM = on ]; then
    if [ $s = v01 ]; then cp $H/data/v01-57.ids $I; else python3 -I -c "import json,sys;[print(json.loads(l)['itemId']) for l in open(sys.argv[1])]" $TR > $I; fi
  else python3 -I $H/tools/changed_ids.py $H/traces/ld-on-$s-s42.traces.jsonl $TR $( [ $s = v01 ] && echo $H/data/v01-57.ids ) > $I; fi
  n=$(wc -l < $I | tr -d ' '); [ "$n" = 0 ] && { echo "none changed $X"; continue; }
  if python3 -I $L/check_judgments.py $O $I > /dev/null 2>&1; then echo "skip $X"; continue; fi
  SYS=litedecline-$ARM-$s-haiku55-low
  PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=$PS PREFLIGHT_DECLARED_CALLS=$((2*n)) \
    bash $SJ --preflight $TR $O $B $I $SYS 4 haiku || { echo "PREFLIGHT FAIL $X"; exit 8; }
  t=$(date +%s); bash $SJ $TR $O $B $I $SYS 4 haiku || { echo "judge FAIL $X"; exit 1; }
  python3 -I $L/check_judgments.py $O $I $X || exit 1
  echo "$(date +%T) JUDGED $X ids=$n rows=$(wc -l < $O | tr -d ' ') wall=$(( $(date +%s) - t ))s"
done
echo "ALLDONE judge $ARM"
