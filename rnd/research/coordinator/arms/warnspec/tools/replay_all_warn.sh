#!/bin/bash
# WARNSPEC-PATCH replay driver: per set (probes v01 st): warn tree ON (WARN=1), warn tree OFF, pristine wt/pr1 (TREE=pr1). 0 LLM.
set -u
A=<workspace>/rnd/research/coordinator/arms/warnspec; R=$A/runs
for s in probes v01 st; do
  [ -f $R/warn-$s-on.traces.status ] && grep -q DONE $R/warn-$s-on.traces.status || WARN=1 $A/tools/run_warn_replay.sh $R/warn-replay-$s.pr1+warn.requests.jsonl $R/warn-$s-on.traces.jsonl || exit 1
  env -u WARN $A/tools/run_warn_replay.sh $R/warn-replay-$s.pr1+warn.requests.jsonl $R/warn-$s-off.traces.jsonl || exit 1
  env -u WARN TREE=pr1 $A/tools/run_warn_replay.sh $R/warn-replay-$s.pr1.requests.jsonl $R/warn-$s-pr1.traces.jsonl || exit 1
  echo "$(date '+%T') $s done"
done
echo replay-all-warn-done
