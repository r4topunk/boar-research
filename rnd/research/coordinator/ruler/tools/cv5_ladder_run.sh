#!/bin/bash
# CV5-LADDER-OPUS Opus pass: judge.v1 (judge.mjs default opus), both orders, seed 7, N = 4 shards via arms/deepthink/tools/shard_judge.sh (model opus).
# One pass per in/<rung>.ids on that rung's existing traces (no generation). Checks the criterion sha and the call cap first. Status in out/status.txt.
set -u
R=<workspace>/rnd/research/coordinator; A=$R/arms; W=$R/ruler/cv5-ladder; BE=<workspace>/boar-eval/bench/v0.1
[ "$(shasum -a 256 $R/ruler/CV5-LADDER-OPUS-criterion.md | cut -d' ' -f1)" = "$(cut -d' ' -f1 $R/ruler/CV5-LADDER-OPUS-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
n=$(cat $W/in/*.ids | grep -c .); [ $((2*n)) -le 360 ] || { echo "planned calls $((2*n)) > cap 360"; exit 9; }
for f in $W/in/*.ids; do
  b=$(basename $f .ids); [ -s "$f" ] || continue
  TR=$(python3 -I -c "import json,sys; print(json.load(open('$W/in/set.json'))['rungs']['$b'])")
  bash $A/deepthink/tools/shard_judge.sh "$TR" $W/out/$b.judgments.jsonl $BE $f cv5ladder-$b 4 opus > $W/out/$b.log 2>&1
  echo "$(date +%T) $b rc=$?" >> $W/out/status.txt
done; echo ALLDONE >> $W/out/status.txt
