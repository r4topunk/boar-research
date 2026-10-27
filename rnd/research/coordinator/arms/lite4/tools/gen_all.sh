#!/bin/bash
# LITE4: generate ON kit (l4-on-v02-s42-slice) then the 9 per-pack st20 runs, sequentially (one llama-server at a time); fetch + validate each; merge st20.
set -u; H=$(cd "$(dirname "$0")/.." && pwd); AS=$H/../_lib/arm.sh; B=<private held-out dir>
r=l4-on-v02-s42-slice
if [ ! -s $B/$r.traces.jsonl ]; then
  $AS $H/arm-L4.conf launch $B/$r.requests.jsonl $r || exit 2
  WAIT_EVERY=15 $AS $H/arm-L4.conf wait $r | tail -1 || exit 3
  $AS $H/arm-L4.conf fetch $r $B/$r.traces.jsonl $B/$r.requests.jsonl | grep -E '^valid|traces sha' || exit 4
fi
PACKS="boar-factbook boar-firstaid-en boar-medlineplus-en boar-simplewiki-en qa-bitcoin-se qa-ethereum-se qa-health-se qa-outdoors-se qa-travel-se"
C=$H/arm-st-L4.conf
for p in $PACKS; do r=l4-on-st20-$p-s42
  [ -s $H/runs/$r.traces.jsonl ] && continue
  $AS $C launch $H/runs/$r.requests.jsonl $r || exit 2
  WAIT_EVERY=10 $AS $C wait $r | tail -1 || exit 3
  $AS $C fetch $r $H/runs/$r.traces.jsonl $H/runs/$r.requests.jsonl | grep -E '^valid|traces sha' || exit 4
done
cat $(for p in $PACKS; do echo $H/runs/l4-on-st20-$p-s42.traces.jsonl; done) > $H/runs/l4-on-st20-s42.traces.jsonl
echo "merged $(wc -l < $H/runs/l4-on-st20-s42.traces.jsonl) traces sha $(shasum -a 256 $H/runs/l4-on-st20-s42.traces.jsonl | cut -c1-16)"
echo GEN-ALL-DONE
