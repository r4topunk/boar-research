#!/bin/bash
# ROUTING-R1 judge (MacBook): Haiku 5.5-low judge.v1-low, N = 4 shards, both orders, deepthink/tools/shard_judge.sh; cap 60 calls (criterion).
set -u
H=<workspace>/rnd/research/coordinator/arms/routing-r1; SJ=$H/../deepthink/tools/shard_judge.sh; L=$H/../_lib; BE=<workspace>/boar-eval/bench
[ "$(shasum -a 256 $H/ROUTING-criterion.md | cut -d' ' -f1)" = "$(cut -d' ' -f1 $H/ROUTING-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
for F in H P T; do for P in qa-cooking-se qa-money-se; do
  TR=$H/traces/r1-$F-K1-cm-s42.traces.jsonl; X=r1-$F-$P; I=$H/judgments/$X.ids; O=$H/judgments/$X.judgments.jsonl
  python3 -I -c "import json,sys;[print(json.loads(l)['itemId']) for l in open(sys.argv[1]) if json.loads(l)['itemId'].startswith('st-'+sys.argv[2]+'-')]" $TR $P > $I
  n=$(wc -l < $I | tr -d ' '); [ "$n" = 0 ] && { rm -f $I; continue; }
  python3 -I $L/check_judgments.py $O $I > /dev/null 2>&1 && { echo "skip $X"; continue; }
  bash $SJ $TR $O $BE/selftest/$P $I routing-r1-$F-$P-haiku55-low 4 haiku || { echo "judge FAIL $X"; exit 1; }
  python3 -I $L/check_judgments.py $O $I $X || exit 1; echo "JUDGED $X ids=$n"
done; done; echo ALLDONE
