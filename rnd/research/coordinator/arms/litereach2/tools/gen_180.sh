#!/bin/bash
# LITEREACH2-180 generation (MacBook, one llama-server at a time via busy.sh): b20 = 1200/4/8 via run_gen.sh; per-pack gate_180.py run; checkpoint after pack 3. Resumable.
set -u; L=<workspace>/rnd/research/coordinator/arms/litereach2; BZ=$L/../headpass-st/tools/busy.sh; D=$L/runs/180
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
bash $L/../_lib/arm.sh $L/arm-180.conf crit_check || { echo "crit_check FAIL"; exit 7; }
k=0; T0=$(date +%s)
for p in $PACKS; do k=$((k+1)); r=$D/litereach2-b20-180-$p-s42
  if [ -s $r.traces.jsonl ] && [ "$(grep -c . $r.traces.jsonl)" = 20 ] && grep -q DONE $r.traces.status 2>/dev/null; then echo "skip $p"; else
    w=0; while "$BZ" > $D/.busy 2>&1; do [ $w = 0 ] && echo "wait-busy $p $(date +%T) $(head -1 $D/.busy)"; w=1; sleep 20; done
    rm -f $r.traces.jsonl; t=$(date +%s)
    $L/tools/run_gen.sh 1200 4 8 $r.requests.jsonl $r.traces.jsonl || { echo "FAIL gen $p (see $r.traces.status)"; exit 2; }
    echo "$(date +%T) done $p wall=$(( $(date +%s) - t ))s free=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}')GiB"
  fi
  python3 -I $L/tools/gate_180.py run $p || { echo "STOP gate $p"; exit 8; }
  if [ $k = 3 ]; then python3 -I $L/tools/gate_180.py checkpoint || { echo "KILL at checkpoint"; exit 8; }; fi
done
cat $D/litereach2-b20-180-*-s42.traces.jsonl > $D/b20-180.all.traces.jsonl
python3 -I $L/tools/gate_180.py all || { echo "GATE-180 FAIL"; exit 8; }
echo "ALLDONE gen wall=$(( $(date +%s) - T0 ))s"
