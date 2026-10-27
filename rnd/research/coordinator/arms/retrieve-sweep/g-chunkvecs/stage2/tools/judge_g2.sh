#!/bin/bash
# judge CTL then ARM answers on an ids file with Haiku 5.5-low judge.v1, N 4 shards, both orders (arms/deepthink/tools/shard_judge.sh). Usage: judge_g2.sh <ids file> <out suffix ("" or -pass2)>
H=<workspace>/rnd/research/coordinator/arms/retrieve-sweep/g-chunkvecs/stage2; A=<workspace>/rnd/research/coordinator/arms
for W in ctl arm; do
  bash $A/deepthink/tools/shard_judge.sh $H/traces/g2-$W.traces.jsonl $H/judge/g2-$W$2.judgments.jsonl $H/bench/g2_216 $1 g2-$W-haiku55-low 4 haiku; echo "$W rc=$?"
done; echo JUDGED
