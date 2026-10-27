#!/bin/bash
# LITE17 judge: Haiku 5.5-low (judge.v1-low), N = 4 shards, both orders, uncapped, via arms/deepthink/tools/shard_judge.sh (fail closed).
# Bench = boar-eval/bench/slices/chainwhen-v1 (the same 150 RELGATE ids; questions + refs copied verbatim from bench/selftest/<pack>).
# Usage: judge.sh B T Q S   (one pass per run, sequential)
A=<workspace>/rnd/research/coordinator/arms; H=$A/lite17; BENCH=<workspace>/boar-eval/bench/slices/chainwhen-v1
for a in "$@"; do
  R=lite17-$a
  "$A/deepthink/tools/shard_judge.sh" "$H/traces/$R.traces.jsonl" "$H/judgments/$R.judgments.jsonl" "$BENCH" "$H/traces/$R.ids" "$R" 4 haiku > "$H/judgments/$a.log" 2>&1
  echo "$R rc=$?" | tee -a "$H/judgments/$a.log"
done
