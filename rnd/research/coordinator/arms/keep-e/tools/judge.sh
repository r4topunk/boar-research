#!/bin/bash
# KEEP-E judge (MacBook): Haiku 5.5-low judge.v1-low, N = 4 shards, both orders, deepthink/tools/shard_judge.sh, on the E answers of the 14 changed
# (no --preflight: the frozen criterion states the cap in its Judge block, not a ## Budget block; same as routing-r1/tools/judge.sh)
# MAIN rows (all differ from the LITEPACKS baseline text). Units: v01 (bench/v0.1), qa-cooking-se / qa-money-se (bench/selftest). Criterion cap 60 Haiku.
set -u
H=<workspace>/rnd/research/coordinator/arms/keep-e; SJ=$H/../deepthink/tools/shard_judge.sh; L=$H/../_lib; BE=<workspace>/boar-eval/bench
C=$H/KEEP-E-criterion.md; [ "$(shasum -a 256 $C | cut -d' ' -f1)" = "$(cut -d' ' -f1 $H/KEEP-E-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
TR=$H/traces/ke-E-MAIN14-s42.traces.jsonl
for u in v01 qa-cooking-se qa-money-se; do
  case $u in v01) B=$BE/v0.1; PS=v01; pre=vit-;; *) B=$BE/selftest/$u; PS=st-$u; pre=st-$u-;; esac
  X=ke-E-$u; I=$H/judgments/$X.ids; O=$H/judgments/$X.judgments.jsonl
  python3 -I -c "import json,sys;[print(json.loads(l)['itemId']) for l in open(sys.argv[1]) if json.loads(l)['itemId'].startswith(sys.argv[2])]" $TR $pre > $I
  n=$(wc -l < $I | tr -d ' '); [ "$n" = 0 ] && { rm -f $I; continue; }
  python3 -I $L/check_judgments.py $O $I > /dev/null 2>&1 && { echo "skip $X"; continue; }
  bash $SJ $TR $O $B $I keep-e-$u-haiku55-low 4 haiku || { echo "judge FAIL $X"; exit 1; }
  python3 -I $L/check_judgments.py $O $I $X || exit 1; echo "JUDGED $X ids=$n rows=$(wc -l < $O | tr -d ' ')"
done; echo ALLDONE
