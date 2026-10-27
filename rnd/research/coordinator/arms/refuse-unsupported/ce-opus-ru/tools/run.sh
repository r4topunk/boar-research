#!/bin/bash
# CE-OPUS-RU Opus judge pass: judge.v1 (judge.mjs default opus), both orders, seed 7, N = 4 shards via deepthink/tools/shard_judge.sh (model opus).
# One pass per unit on the MacBook LITEPACKS K3 traces (no generation). Checks the criterion sha first. Status in out/status.txt.
set -u
A=<workspace>/rnd/research/coordinator/arms; H=$A/refuse-unsupported; C=$H/ce-opus-ru; LP=$A/litepacks/traces; BE=<workspace>/boar-eval/bench
[ "$(shasum -a 256 $H/CE-OPUS-RU-criterion.md | cut -d' ' -f1)" = "$(cut -d' ' -f1 $H/CE-OPUS-RU-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
for u in v01 qa-money-se boar-factbook boar-medlineplus-en boar-simplewiki-en; do
  case $u in v01) TR=$LP/lp-K3-v01-s42.traces.jsonl; B=$BE/v0.1;; qa-*) TR=$LP/lp-K3-cm-s42.traces.jsonl; B=$BE/selftest/$u;; *) TR=$LP/lp-K3-st-s42.traces.jsonl; B=$BE/selftest/$u;; esac
  bash $A/deepthink/tools/shard_judge.sh $TR $C/out/$u.judgments.jsonl $B $C/in/$u.ids ceopusru-K3-$u 4 opus > $C/out/$u.log 2>&1
  echo "$(date +%T) $u rc=$?" >> $C/out/status.txt
done; echo ALLDONE >> $C/out/status.txt
