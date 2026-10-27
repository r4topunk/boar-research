#!/bin/bash
# ORACLE-ST stage 1 driver (MacBook, sequential, one llama-server at a time): ORACLE-ADD then ORACLE-ONLY, 9 packs x 20.
# Resumable: skips runs whose traces have 20 rows and a DONE status. Per run: runs/<R>.{traces.jsonl,status,log,prompts.jsonl,ids}.
# Usage: nohup gen_chain.sh [cells...] > logs/gen_chain.log 2>&1 &
A=<workspace>/rnd/research/coordinator/arms/oracle-st; D=$A/runs
PACKS="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en"
CELLS=${*:-"oracleadd oracleonly"}
for c in $CELLS; do
  case $c in oracleadd) OF=$A/tools/oracle-add.json;; oracleonly) OF=$A/tools/oracle-only.json;; *) echo "bad cell $c"; exit 2;; esac
  for p in $PACKS; do R=st-$p-cut7-$c-s42
    if [ -s "$D/$R.traces.jsonl" ] && [ "$(wc -l < "$D/$R.traces.jsonl")" -eq 20 ] && grep -q DONE "$D/$R.traces.status" 2>/dev/null; then echo "skip $R"; continue; fi
    while true; do  # disk guard (>= 8 GiB free, as run_oracle.sh checks): wait for free space instead of stopping; free space moves with the system swap
      w=0; until [ "$(df -k <home> | tail -1 | awk '{print int($4/1048576)}')" -ge 8 ]; do [ $w = 0 ] && echo "wait-disk $R $(date '+%T')"; w=1; sleep 30; done
      rm -f "$D/$R.traces.jsonl" "$D/$R.prompts.jsonl"
      BOAR_ORACLE_FILE=$OF BOAR_PROMPT_DUMP=$D/$R.prompts.jsonl "$A/tools/run_oracle.sh" "$D/$R.requests.jsonl" "$D/$R.traces.jsonl"; rc=$?
      grep -q "FAIL disk" "$D/$R.traces.status" && { echo "retry-disk $R $(date '+%T')"; continue; }
      grep -qE "FAIL (a 4B llama-server|an adapter.ts job)" "$D/$R.traces.status" && { echo "retry-busy $R $(date '+%T')"; sleep 60; continue; }; break
    done
    echo "$R rc=$rc $(date '+%T') free=$(df -k <home> | tail -1 | awk '{print int($4/1048576)}')GiB"
    [ $rc = 0 ] || { echo "STOP on $R"; exit $rc; }
    python3 -I -c "import json,sys;[print(json.loads(l)['itemId']) for l in open(sys.argv[1])]" "$D/$R.traces.jsonl" > "$D/$R.ids"
  done
  echo "CELLDONE $c $(date '+%T')"
done; echo ALLDONE
