#!/bin/bash
# REVEAL-CENSUS Opus pass: judge.v1, both orders, seed 7, N = 4 via arms/deepthink/tools/shard_judge.sh (model opus); one pass per in/ST-<unit>.ids
# on the null-cal control K0 st180 traces (no generation). Checks the criterion sha and the call cap first. Status in out/status.txt.
set -u
R=<workspace>/rnd/research/coordinator; A=$R/arms; W=$R/ruler/reveal-census; BE=<workspace>/boar-eval/bench
TR=$A/null-cal/control/traces/poolctl-K0-st180-s42.traces.jsonl
[ "$(shasum -a 256 $R/ruler/REVEAL-CENSUS-criterion.md | cut -d' ' -f1)" = "$(cut -d' ' -f1 $R/ruler/REVEAL-CENSUS-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
n=$(cat $W/in/*.ids | grep -c .); [ $((2*n)) -le 192 ] || { echo "planned calls $((2*n)) > cap 192"; exit 9; }
for f in $W/in/*.ids; do
  b=$(basename $f .ids); p=${b%%-*}; u=${b#*-}; [ -s "$f" ] || continue
  [ "$p" = ST ] || { echo "unexpected pop $p"; exit 9; }
  bash $A/deepthink/tools/shard_judge.sh $TR $W/out/$b.judgments.jsonl $BE/selftest/$u $f revealcensus-$u 4 opus > $W/out/$b.log 2>&1
  echo "$(date +%T) $b rc=$?" >> $W/out/status.txt
done; echo ALLDONE >> $W/out/status.txt
