#!/bin/bash
# HEALTHGAP-r2 replay driver: per set (probes v01 st mlp r2): hg2 ON, hg2 OFF, plain cut 7 (TREE=c7). 0 LLM.
set -u
H=<workspace>/rnd/research/coordinator/arms/healthgap; R=$H/runs/r2
for s in probes v01 st mlp r2; do
  [ -f $R/hg2-replay-$s-on.traces.status ] && grep -q DONE $R/hg2-replay-$s-on.traces.status || HEALTHGAP=1 $H/tools/run_hg2_replay.sh $R/hg2-replay-$s.requests.jsonl $R/hg2-replay-$s-on.traces.jsonl || exit 1
  env -u HEALTHGAP $H/tools/run_hg2_replay.sh $R/hg2-replay-$s.requests.jsonl $R/hg2-replay-$s-off.traces.jsonl || exit 1
  env -u HEALTHGAP TREE=c7 $H/tools/run_hg2_replay.sh $R/c7-replay-$s.requests.jsonl $R/c7-replay-$s.traces.jsonl || exit 1
  echo "$(date '+%T') $s done"
done
echo replay-all-r2-done
