#!/bin/bash
# DENSECHUNK-ST2 stage 1: ON generation for the 9 self-test packs, sequential (one 4B job on the MacBook). Resumable (DONE status skips).
G=<workspace>/rnd/research/coordinator/arms/densechunk-st/runs/gen; R=<workspace>/rnd/research/coordinator/arms/packs/tools/run_selftest_dense2.sh
for p in ${*:-qa-health-se qa-travel-se qa-ethereum-se qa-bitcoin-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en}; do
  n=st2-$p-cut7-s42; grep -q '^DONE' $G/$n.traces.status 2>/dev/null && continue
  rm -f $G/$n.traces.jsonl; echo "$(date '+%T') start $p"; $R $G/$n.requests.jsonl $G/$n.traces.jsonl; echo "$(date '+%T') $p rc=$? $(tail -1 $G/$n.traces.status)"
done; echo GEN-ALL-DONE
