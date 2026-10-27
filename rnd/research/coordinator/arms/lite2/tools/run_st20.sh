#!/bin/bash
# LITE2: run the 9 per-pack st20 runs of one arm sequentially (the adapter requires one config per requests file: each pack is its own kit), fetch, merge.
# Usage: run_st20.sh <L|T2>   -> runs/<a>-st20-s42.traces.jsonl (merged, ids order of the per-pack files) + per-pack traces/status
set -u; A=$1; a=$(echo $A | tr A-Z a-z); H=$(cd "$(dirname "$0")/.." && pwd); C=$H/arm-st-$A.conf; AS=$H/../_lib/arm.sh
PACKS="boar-factbook boar-firstaid-en boar-medlineplus-en boar-simplewiki-en qa-bitcoin-se qa-ethereum-se qa-health-se qa-outdoors-se qa-travel-se"
for p in $PACKS; do r=$a-st20-$p-s42
  [ -s $H/runs/$r.traces.jsonl ] && continue
  $AS $C launch $H/runs/$r.requests.jsonl $r || exit 2
  WAIT_EVERY=10 $AS $C wait $r | tail -1 || exit 3
  $AS $C fetch $r $H/runs/$r.traces.jsonl $H/runs/$r.requests.jsonl | grep -E '^valid|traces sha' || exit 4
done
cat $(for p in $PACKS; do echo $H/runs/$a-st20-$p-s42.traces.jsonl; done) > $H/runs/$a-st20-s42.traces.jsonl
echo "merged $(wc -l < $H/runs/$a-st20-s42.traces.jsonl) traces sha $(shasum -a 256 $H/runs/$a-st20-s42.traces.jsonl | cut -c1-16)"
