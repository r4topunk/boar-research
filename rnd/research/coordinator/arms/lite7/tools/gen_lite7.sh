#!/bin/bash
# LITE7 generation driver (MacBook, sequential, one llama-server at a time): per pack ON via run_lite7_gen.sh; per-run gate (gate7.py run);
# checkpoint after pack 1 (gate7.py checkpoint; KILL -> stop); then gate7.py all. Resumable. Usage: nohup gen_lite7.sh > runs/180/gen_lite7.log 2>&1 &
set -u; H=<workspace>/rnd/research/coordinator/arms/lite7; R=$H/runs/180; BZ=$H/../headpass-st/tools/busy.sh
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
k=0; T0=$(date +%s); WB=0
for p in $PACKS; do k=$((k+1)); r=$R/lite7-180-on-$p-s42
  if [ -s $r.traces.jsonl ] && [ "$(wc -l < $r.traces.jsonl | tr -d ' ')" = 20 ] && grep -q DONE $r.traces.status 2>/dev/null; then echo "skip $p"; else
    w=0; while "$BZ" > $R/.busy 2>&1 || pgrep -f "be/adapter-lite[0-9][.]ts" > /dev/null; do [ $w = 0 ] && echo "wait-busy $p $(date +%T) $(head -1 $R/.busy)"; w=1; WB=$((WB+30)); sleep 30; done
    rm -f $r.traces.jsonl; t=$(date +%s)
    $H/tools/run_lite7_gen.sh $r.requests.jsonl $r.traces.jsonl on || { echo "FAIL gen $p (see $r.traces.status)"; exit 2; }
    echo "$(date +%T) done $p wall=$(( $(date +%s) - t ))s free=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}')GiB"
  fi
  python3 -I $H/tools/gate7.py run $p || { echo "STOP gate $p"; exit 8; }
  if [ $k = 1 ]; then python3 -I $H/tools/gate7.py checkpoint || { echo "KILL at checkpoint"; exit 8; }; fi
done
echo "ALLDONE gen wall=$(( $(date +%s) - T0 ))s busy-wait=${WB}s"
python3 -I $H/tools/gate7.py all; echo "GATE rc=$?"
