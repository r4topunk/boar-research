#!/bin/bash
# LITEREACH2 generation chain (MacBook, one server at a time): <phase> = smoke | r20; cell b20 = 1200/4/8. Resumable.
set -u; L=<workspace>/rnd/research/coordinator/arms/litereach2; BZ=$L/../headpass-st/tools/busy.sh; ph=$1; D=$L/runs/$ph
for q in $D/*.requests.jsonl; do r=${q%.requests.jsonl}
  n=$(grep -c . $q); if [ -s $r.traces.jsonl ] && [ "$(grep -c . $r.traces.jsonl)" = $n ] && grep -q DONE $r.traces.status 2>/dev/null; then echo "skip $r"; continue; fi
  w=0; while "$BZ" > $D/.busy 2>&1; do [ $w = 0 ] && echo "wait-busy $(date +%T) $(head -1 $D/.busy)"; w=1; sleep 20; done
  rm -f $r.traces.jsonl; t=$(date +%s)
  $L/tools/run_gen.sh 1200 4 8 $q $r.traces.jsonl || { echo "FAIL gen $r"; exit 2; }
  echo "$(date +%T) done $(basename $r) wall=$(( $(date +%s) - t ))s free=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}')GiB"
done
cat $D/*.traces.jsonl > $L/runs/$ph.all.traces.jsonl; echo "CHAIN-DONE $ph $(date +%T)"
