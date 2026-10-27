#!/bin/bash
# LITETHINK sequential driver: args = <master.status> then triples "B req out"; runs run_lt_gen.sh one at a time; stops on first FAIL.
# Skips a run whose traces .status already ends in DONE.
M=$1; shift; LT=<workspace>/rnd/research/coordinator/arms/litethink
echo "seq start $(date '+%F %T')" > "$M"
while [ $# -ge 3 ]; do B=$1; RQ=$2; O=$3; shift 3; S=${O%.jsonl}.status
  if [ -f "$S" ] && tail -1 "$S" | grep -q DONE; then echo "skip $O" >> "$M"; continue; fi
  echo "$(date +%T) run B=$B $(basename $O)" >> "$M"
  bash $LT/tools/run_lt_gen.sh "$B" "$RQ" "$O"; rc=$?
  echo "$(date +%T) rc=$rc $(basename $O)" >> "$M"
  [ $rc = 0 ] || { echo "SEQ FAIL" >> "$M"; exit 1; }
done
echo "SEQ DONE $(date '+%F %T')" >> "$M"
