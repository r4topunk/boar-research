#!/bin/bash
A=<workspace>/rnd/research/coordinator/arms; C=$A/ce-opus-check; BE=<workspace>/boar-eval/bench
for tag in ctl greedy; do ( for u in v01 qa-cooking-se qa-money-se; do
  case $u in v01) B=$BE/v0.1;; *) B=$BE/selftest/$u;; esac
  bash $A/deepthink/tools/shard_judge.sh $C/in/$tag-$u.traces.jsonl $C/out/$tag-$u.judgments.jsonl $B $C/in/$tag-$u.ids ceopus-$tag-$u 4 opus > $C/out/$tag-$u.log 2>&1
  echo "$tag $u rc=$?" >> $C/out/status.txt
done ) & done; wait; echo ALLDONE >> $C/out/status.txt
