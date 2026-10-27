#!/bin/bash
# GEMMA-OPUS-MAIN Opus pass: judge.v1, both orders, seed 7, N = 4 via arms/deepthink/tools/shard_judge.sh (model opus); one pass per
# in/<arm>-<unit>.ids on that arm's existing MAIN 97 K0 traces (no generation). Seed-42 files first. Checks criterion sha and cap. Status in out/status.txt.
set -u
R=<workspace>/rnd/research/coordinator; A=$R/arms; W=$R/ruler/gemma-opus-main; BE=<workspace>/boar-eval/bench
[ "$(shasum -a 256 $R/ruler/GEMMA-OPUS-MAIN-criterion.md | cut -d' ' -f1)" = "$(cut -d' ' -f1 $R/ruler/GEMMA-OPUS-MAIN-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
n=$(cat $W/in/*.ids | grep -c .); [ $((2*n)) -le 400 ] || { echo "planned calls $((2*n)) > cap 400"; exit 9; }
for f in $(ls $W/in/ctl42-*.ids $W/in/gem42-*.ids $W/in/ctl43-*.ids $W/in/gem43-*.ids 2>/dev/null); do
  b=$(basename $f .ids); t=${b%%-*}; u=${b#*-}; [ -s "$f" ] || continue
  TR=$(python3 -I -c "import json; print(json.load(open('$W/in/set.json'))['traces']['$t'])")
  case $u in v01) B=$BE/v0.1;; *) B=$BE/selftest/$u;; esac
  bash $A/deepthink/tools/shard_judge.sh "$TR" $W/out/$b.judgments.jsonl $B $f gopus-$b 4 opus > $W/out/$b.log 2>&1
  echo "$(date +%T) $b rc=$?" >> $W/out/status.txt
done; echo ALLDONE >> $W/out/status.txt
