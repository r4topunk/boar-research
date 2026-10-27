#!/bin/bash
# LITE5: run the 9 per-pack files of one mode (on|off) sequentially on the MacBook, merge in selftest20 pack order.
set -u; M=$1; H=<workspace>/rnd/research/coordinator/arms/lite5
PACKS="boar-factbook boar-firstaid-en boar-medlineplus-en boar-simplewiki-en qa-bitcoin-se qa-ethereum-se qa-health-se qa-outdoors-se qa-travel-se"
for p in $PACKS; do r=$H/runs/lite5-$M-st20-$p-s42
  [ -s $r.traces.jsonl ] && grep -q DONE $r.traces.status 2>/dev/null && continue
  $H/tools/run_lite5_gen.sh $r.requests.jsonl $r.traces.jsonl || { echo "FAIL $p"; exit 2; }
done
cat $(for p in $PACKS; do echo $H/runs/lite5-$M-st20-$p-s42.traces.jsonl; done) > $H/runs/lite5-$M-st20-s42.traces.jsonl
echo "merged $(wc -l < $H/runs/lite5-$M-st20-s42.traces.jsonl) sha $(shasum -a 256 $H/runs/lite5-$M-st20-s42.traces.jsonl | cut -c1-16)"
