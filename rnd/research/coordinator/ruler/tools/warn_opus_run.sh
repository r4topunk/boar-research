#!/bin/bash
# HON-10 WARN-OPUS Opus judge pass: judge.v1 (judge.mjs default opus), both orders, seed 7, N = 4 shards via arms/deepthink/tools/shard_judge.sh (model opus).
# One pass per in/<arm>-<unit>.ids on the MacBook LITEPACKS traces (no generation). Checks the criterion sha and the call cap first. Status in out/status.txt.
set -u
R=<workspace>/rnd/research/coordinator; A=$R/arms; W=$R/ruler/warn-opus; LP=$A/litepacks/traces; BE=<workspace>/boar-eval/bench
[ "$(shasum -a 256 $R/ruler/WARN-OPUS-criterion.md | cut -d' ' -f1)" = "$(cut -d' ' -f1 $R/ruler/WARN-OPUS-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
n=$(cat $W/in/*.ids | grep -c .); [ $((2*n)) -le 220 ] || { echo "planned calls $((2*n)) > cap 220"; exit 9; }
for f in $W/in/*.ids; do
  b=$(basename $f .ids); arm=${b%%-*}; u=${b#*-}
  case $u in v01) TR=$LP/lp-$arm-v01-s42.traces.jsonl; B=$BE/v0.1;; qa-cooking-se|qa-money-se) TR=$LP/lp-$arm-cm-s42.traces.jsonl; B=$BE/selftest/$u;; *) TR=$LP/lp-$arm-st-s42.traces.jsonl; B=$BE/selftest/$u;; esac
  bash $A/deepthink/tools/shard_judge.sh $TR $W/out/$b.judgments.jsonl $B $f warnopus-$arm-$u 4 opus > $W/out/$b.log 2>&1
  echo "$(date +%T) $b rc=$?" >> $W/out/status.txt
done; echo ALLDONE >> $W/out/status.txt
