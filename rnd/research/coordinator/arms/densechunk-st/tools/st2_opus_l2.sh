#!/bin/bash
# DENSECHUNK-ST2 Opus L2: judge.v1 Opus (deepthink shard_judge.sh, N=4, both orders) on the SAME traces as L1, OFF and ON, 9 packs (720 calls).
# OFF -> arms/packs/selftest-runs/st-<p>-cut7-s42.judgments.opus.jsonl ; ON -> densechunk-st/runs/judge/st2-<p>-cut7-s42.judgments.opus.jsonl
# Resumable: a judged file with 40 rows and an empty .missing is skipped; judge.mjs resumes ok rows. One job at a time (4 concurrent Opus calls).
set -u
H=<workspace>/rnd/research/coordinator/arms; OD=$H/packs/selftest-runs; J=$H/densechunk-st/runs/judge; SJ=$H/deepthink/tools/shard_judge.sh
done_ok() { [ "$(wc -l < "$1" 2>/dev/null || echo 0)" -ge 40 ] && [ ! -s "${1%.jsonl}.missing" ]; }
for p in ${*:-qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en}; do
  B=<workspace>/boar-eval/bench/selftest/$p; IDS=$J/st2-$p-cut7-s42.ids
  o=$OD/st-$p-cut7-s42.judgments.opus.jsonl
  done_ok $o || { bash $SJ $OD/st-$p-cut7-s42.traces.jsonl $o $B $IDS selftest-$p-cut7-opus 4 opus; echo "$(date +%T) OFF $p rc=$?"; }
  n=$J/st2-$p-cut7-s42.judgments.opus.jsonl
  done_ok $n || { bash $SJ $J/st2-$p-cut7-s42.traces.jsonl $n $B $IDS selftest-$p-cut7-dense2-opus 4 opus; echo "$(date +%T) ON $p rc=$?"; }
done; echo OPUS-L2-DONE $(date '+%F %T')
