#!/bin/bash
# SEFIX Opus read cooking/money: judge.v1 Opus via shard_judge.sh (model opus), both orders, seed 7, N 4; plan.json sha f41b63bb. 60 calls cap.
set -u
SF=<workspace>/rnd/research/coordinator/arms/coverage-map/sefix; A=<workspace>/rnd/research/coordinator/arms; BE=<workspace>/boar-eval/bench; SJ=$A/deepthink/tools/shard_judge.sh; O=$SF/opus-cm
TCTL=$A/litepacks/traces/mini/lp-K1-cm-s42.mini.traces.jsonl; TALL=$SF/ans-traces/sefixall-main-s42.traces.jsonl
for arm in CTL ALL; do for u in qa-cooking-se qa-money-se; do
  f=$O/ids.$arm.$u; [ -s $f ] || continue; tr=$TALL; [ $arm = CTL ] && tr=$TCTL
  bash $SJ $tr $O/$arm.$u.judgments.jsonl $BE/selftest/$u $f sefixcm-opus-$arm-$u 4 opus > $O/$arm.$u.log 2>&1
  echo "$(date +%T) $arm $u rc=$?" >> $O/status.txt
done; done; echo DONE >> $O/status.txt
