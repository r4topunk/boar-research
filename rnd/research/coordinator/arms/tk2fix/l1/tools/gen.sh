#!/bin/bash
# TK2FIX-L1 generation driver (MacBook, sequential, one llama-server at a time): per pack run_gen.sh, per-run gate, checkpoint after pack 3 (KILL -> stop), then gate all.
# Resumable (skips runs with 20 rows + DONE). Usage: nohup gen.sh > runs/gen.log 2>&1 &
set -u; L=<workspace>/rnd/research/coordinator/arms/tk2fix/l1; R=$L/runs; BZ=$L/../../headpass-st/tools/busy.sh
PACKS="boar-medlineplus-en boar-factbook boar-simplewiki-en qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en"
k=0; T0=$(date +%s)
for p in $PACKS; do k=$((k+1)); r=$R/tk2fix-l1-$p-s42
  if [ -s $r.traces.jsonl ] && [ "$(wc -l < $r.traces.jsonl | tr -d ' ')" = 20 ] && grep -q DONE $r.traces.status 2>/dev/null; then echo "skip $p"; else
    w=0; while "$BZ" > $R/.busy 2>&1; do [ $w = 0 ] && echo "wait-busy $p $(date +%T) $(head -1 $R/.busy)"; w=1; sleep 30; done
    rm -f $r.traces.jsonl; t=$(date +%s)
    $L/tools/run_gen.sh $r.requests.jsonl $r.traces.jsonl || { echo "FAIL gen $p (see $r.traces.status)"; exit 2; }
    echo "$(date +%T) done $p wall=$(( $(date +%s) - t ))s free=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}')GiB"
  fi
  python3 -I $L/tools/gate.py run $p || { echo "STOP gate $p"; exit 8; }
  if [ $k = 3 ]; then python3 -I $L/tools/gate.py checkpoint || { echo "KILL at checkpoint"; exit 8; }; fi
done
python3 -I $L/tools/gate.py all || { echo "STOP gate all"; exit 8; }
echo "ALLDONE gen wall=$(( $(date +%s) - T0 ))s"
