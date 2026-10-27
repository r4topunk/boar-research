#!/bin/bash
# MIN3CITE-OPUS step B: judge.v1 Opus, both orders, seed 7, N = 4 via arms/deepthink/tools/shard_judge.sh (model opus); one pass per
# in/m3c-<unit>.ids on the MIN3CITE stage-2 traces (no generation). Checks criterion sha and cap 150. Status in out/status.txt.
set -u
R=<workspace>/rnd/research/coordinator; A=$R/arms; W=$R/ruler/min3cite-opus-main; BE=<workspace>/boar-eval/bench
[ "$(shasum -a 256 $R/ruler/MIN3CITE-OPUS-criterion.md | cut -d' ' -f1)" = "$(cut -d' ' -f1 $R/ruler/MIN3CITE-OPUS-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
n=$(cat $W/in/*.ids | grep -c .); [ $((2*n)) -le 150 ] || { echo "planned calls $((2*n)) > cap 150"; exit 9; }
TR=$A/min3cite/traces/min3cite-K0-main-s42.traces.jsonl
for f in $W/in/m3c-*.ids; do
  b=$(basename $f .ids); u=${b#m3c-}; [ -s "$f" ] || continue
  case $u in v01) B=$BE/v0.1;; *) B=$BE/selftest/$u;; esac
  bash $A/deepthink/tools/shard_judge.sh "$TR" $W/out/$b.judgments.jsonl $B $f m3copus-$b 4 opus > $W/out/$b.log 2>&1
  echo "$(date +%T) $b rc=$?" >> $W/out/status.txt
done; echo ALLDONE >> $W/out/status.txt
