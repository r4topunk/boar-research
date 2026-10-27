#!/bin/bash
# HEALTHGAP replay driver: probes ON, then v0.1 and self-tests OFF and ON (probes OFF ran first as the smoke).
set -u
H=<workspace>/rnd/research/coordinator/arms/healthgap; R=<workspace>/rnd/research/coordinator/arms/healthgap/runs
HEALTHGAP=1 $H/tools/run_hg_replay.sh $R/hg-replay-probes.requests.jsonl $R/hg-replay-probes-on.traces.jsonl || exit 1
for s in v01 st; do
  env -u HEALTHGAP $H/tools/run_hg_replay.sh $R/hg-replay-$s.requests.jsonl $R/hg-replay-$s-off.traces.jsonl || exit 1
  HEALTHGAP=1 $H/tools/run_hg_replay.sh $R/hg-replay-$s.requests.jsonl $R/hg-replay-$s-on.traces.jsonl || exit 1
done
echo replay-all-done
