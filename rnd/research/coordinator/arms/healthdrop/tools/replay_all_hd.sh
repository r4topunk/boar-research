#!/bin/bash
# HEALTHDROP step 0: every set x {ON arm, OFF arm, BASE}. 0 LLM.
set -u
A=<workspace>/rnd/research/coordinator/arms/healthdrop; R=$A/runs; X=$A/tools/run_hd_replay.sh
SETS="st-qa-travel-se st-qa-ethereum-se st-qa-bitcoin-se st-qa-health-se st-qa-outdoors-se st-boar-firstaid-en st-boar-medlineplus-en st-boar-factbook st-boar-simplewiki-en v01 probes v01-hk probes-hk"
for s in ${1:-$SETS}; do
  HEALTHDROP=1 $X $R/hd-$s.arm.requests.jsonl $R/hd-$s-on.traces.jsonl || exit 1
  env -u HEALTHDROP $X $R/hd-$s.arm.requests.jsonl $R/hd-$s-off.traces.jsonl || exit 1
  env -u HEALTHDROP TREE=base $X $R/hd-$s.base.requests.jsonl $R/hd-$s-base.traces.jsonl || exit 1
  echo "$(date '+%T') $s done"
done
echo replay-all-hd-done
