#!/bin/bash
# HEADPASS-ST stage 1 driver (MacBook, sequential, ONE llama-server at a time): 9 x 20 ON self-tests, then v0.1+simplewiki OFF and ON.
# Before each run: wait (poll every 60 s) until busy.sh reports no llama-server other than the detector and no adapter.ts job (never kills
# anything); disk >= 8 GiB. Resumable: skips runs with the expected rows and DONE. Per run: gen/<R>.{traces.jsonl,status,log,prompts.jsonl,ids}.
# Usage: nohup gen_chain.sh > logs/gen_chain.log 2>&1 &
A=$BOAR_WS/rnd/research/coordinator/arms/headpass-st; D=$A/gen
RUNS=""; for p in qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do RUNS="$RUNS st-$p-cut7-headpass-s42:20"; done
RUNS="$RUNS v01sw-cut7-headpass-off-s42:60 v01sw-cut7-headpass-on-s42:60"
for x in $RUNS; do R=${x%%:*}; n=${x#*:}
  if [ -s "$D/$R.traces.jsonl" ] && [ "$(wc -l < "$D/$R.traces.jsonl")" -eq $n ] && grep -q DONE "$D/$R.traces.status" 2>/dev/null; then echo "skip $R"; continue; fi
  tries=0
  while true; do
    w=0; while "$A/tools/busy.sh" > "$D/.busy" 2>&1; do [ $w = 0 ] && echo "wait-busy $R $(date '+%T') $(head -1 $D/.busy)"; w=1; sleep 60; done
    w=0; until [ "$(df -k $HOME | tail -1 | awk '{print int($4/1048576)}')" -ge 8 ]; do [ $w = 0 ] && echo "wait-disk $R $(date '+%T')"; w=1; sleep 60; done
    rm -f "$D/$R.traces.jsonl" "$D/$R.prompts.jsonl"
    BOAR_PROMPT_DUMP=$D/$R.prompts.jsonl "$A/tools/run_hp_gen.sh" "$D/$R.requests.jsonl" "$D/$R.traces.jsonl"; rc=$?
    grep -q "FAIL disk" "$D/$R.traces.status" && { echo "retry-disk $R $(date '+%T')"; continue; }
    grep -q "FAIL a llama-server" "$D/$R.traces.status" && { echo "retry-busy $R $(date '+%T')"; sleep 60; continue; }; break
  done
  echo "$R rc=$rc $(date '+%T') rows=$(wc -l < "$D/$R.traces.jsonl" 2>/dev/null | tr -d ' ') free=$(df -k $HOME | tail -1 | awk '{print int($4/1048576)}')GiB"
  [ $rc = 0 ] || { echo "STOP on $R"; exit $rc; }
  python3 -I -c "import json,sys;[print(json.loads(l)['itemId']) for l in open(sys.argv[1])]" "$D/$R.traces.jsonl" > "$D/$R.ids"
done; echo ALLDONE
