#!/bin/bash
# FACTBOOK-V2-CONFIRM: Opus judge.v1, both orders, seed 7, N 4; criterion f17179a5. 120 calls, cap 130.
set -u
A=<workspace>/rnd/research/coordinator/arms; O=$A/packshape/v2confirm; SJ=$A/deepthink/tools/shard_judge.sh; BE=<workspace>/boar-eval/bench/selftest/boar-factbook
for arm in BASE S42 S43; do
  case $arm in BASE) tr=$A/packproof/gen/on-k13/traces.jsonl;; S42) tr=$A/packshape/gen/on-k13s/traces.jsonl;; S43) tr=$A/packshape/gen/on-k13s43/traces.jsonl;; esac
  bash $SJ $tr $O/$arm.judgments.jsonl $BE $O/ids.txt fbv2-opus-$arm 4 opus > $O/$arm.log 2>&1
  echo "$(date +%T) $arm rc=$?" >> $O/status.txt
done; echo DONE >> $O/status.txt
