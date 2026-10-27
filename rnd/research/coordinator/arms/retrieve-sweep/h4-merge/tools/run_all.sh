#!/bin/bash
# H4-MERGE: every replay, sequential (wall times comparable). 0 LLM. Controls first in each block.
cd <workspace>/rnd/research/coordinator/arms/retrieve-sweep/h4-merge
for SET in qm q6 K3 K3CM K3W; do
  for V in off rrf gidf; do
    if [ $V = off ]; then env -u RS_MERGE tools/run.sh $SET $V; else RS_MERGE=$V tools/run.sh $SET $V; fi
  done
done
echo ALLDONE
