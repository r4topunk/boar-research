#!/bin/bash
# CV5-PER100-OPUS Opus pass: judge.v1, both orders, seed 7, N = 4 via arms/deepthink/tools/shard_judge.sh (model opus); one pass per in/<tier>-<unit>.ids
# on that tier's existing MAIN 97 K0 traces (no generation). Checks the criterion sha and the call cap first. Status in out/status.txt.
set -u
R=<workspace>/rnd/research/coordinator; A=$R/arms; W=$R/ruler/cv5-per100; BE=<workspace>/boar-eval/bench
[ "$(shasum -a 256 $R/ruler/CV5-PER100-OPUS-criterion.md | cut -d' ' -f1)" = "$(cut -d' ' -f1 $R/ruler/CV5-PER100-OPUS-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
n=$(cat $W/in/*.ids | grep -c .); [ $((2*n)) -le 310 ] || { echo "planned calls $((2*n)) > cap 310"; exit 9; }
for f in $W/in/*.ids; do
  b=$(basename $f .ids); t=${b%%-*}; u=${b#*-}; [ -s "$f" ] || continue
  TR=$(python3 -I -c "import json; print(json.load(open('$W/in/set.json'))['traces']['$t'])")
  case $u in v01) B=$BE/v0.1;; *) B=$BE/selftest/$u;; esac
  bash $A/deepthink/tools/shard_judge.sh "$TR" $W/out/$b.judgments.jsonl $B $f cv5p100-$b 4 opus > $W/out/$b.log 2>&1
  echo "$(date +%T) $b rc=$?" >> $W/out/status.txt
done; echo ALLDONE >> $W/out/status.txt
