#!/bin/bash
# RETBENCH sweep queue: run configs one at a time (lane 1), skip those with an aggregate. usage: queue.sh configs/A-*.json ...
RB=<workspace>/rnd/research/coordinator/arms/retbench
for c in "$@"; do n=$(basename $c .json); [ -f $RB/aggregates/$n.json ] && { echo "skip $n"; continue; }
  LANE=1 $RB/tools/retbench.sh $c > $RB/replays/$n.log 2>&1; echo "DONE $n $(tail -1 $RB/replays/$n.log | cut -c1-300)"; done
echo QUEUE-END
