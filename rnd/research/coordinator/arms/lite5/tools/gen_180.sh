#!/bin/bash
# LITE5-180 generation driver (MacBook, sequential, one llama-server at a time): per pack OFF then ON via run_lite5_gen.sh; per-run gate (gate180.py run);
# checkpoint after pack 3 (gate180.py checkpoint; KILL -> stop). Resumable (skips runs with 20 rows + DONE). Usage: nohup gen_180.sh > runs/180/gen_180.log 2>&1 &
set -u; H=<workspace>/rnd/research/coordinator/arms/lite5; R=$H/runs/180; BZ=$H/../headpass-st/tools/busy.sh
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
k=0; T0=$(date +%s)
for p in $PACKS; do k=$((k+1))
  for m in off on; do r=$R/lite5-180-$m-$p-s42
    if [ -s $r.traces.jsonl ] && [ "$(wc -l < $r.traces.jsonl | tr -d ' ')" = 20 ] && grep -q DONE $r.traces.status 2>/dev/null; then echo "skip $m $p"; else
      w=0; while "$BZ" > $R/.busy 2>&1; do [ $w = 0 ] && echo "wait-busy $m $p $(date +%T) $(head -1 $R/.busy)"; w=1; sleep 30; done
      rm -f $r.traces.jsonl; t=$(date +%s)
      $H/tools/run_lite5_gen.sh $r.requests.jsonl $r.traces.jsonl || { echo "FAIL gen $m $p (see $r.traces.status)"; exit 2; }
      echo "$(date +%T) done $m $p wall=$(( $(date +%s) - t ))s free=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}')GiB"
    fi
    python3 -I $H/tools/gate180.py run $m $p || { echo "STOP gate $m $p"; exit 8; }
  done
  if [ $k = 3 ]; then python3 -I $H/tools/gate180.py checkpoint || { echo "KILL at checkpoint"; exit 8; }; fi
done
echo "ALLDONE gen wall=$(( $(date +%s) - T0 ))s"
