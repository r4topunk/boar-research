#!/bin/bash
# H4b: every replay sequential (0 LLM). TREE = rs-H4b. labels: g2 = gidf2, g1 = gidf (identity vs H4), off = unset (identity vs H4)
cd <workspace>/rnd/research/coordinator/arms/retrieve-sweep/h4-merge
export TREE=<workspace>/kiln-local/rs-H4b
r() { SET=$1; V=$2; if [ $V = off ]; then env -u RS_MERGE tools/run.sh $SET h4b-off; elif [ $V = g1 ]; then RS_MERGE=gidf tools/run.sh $SET h4b-g1; else RS_MERGE=gidf2 tools/run.sh $SET h4b-g2; fi; }
for SET in q6 K3 K3CM K3W qm; do for V in g2 g1 off; do r $SET $V; done; done
for SET in proof20 proof6; do for V in g2 off; do r $SET $V; done; done
c() { N=$1; V=$2; if [ $V = off ]; then env -u RS_MERGE tools/run_compose_h4b.sh $N h4b-stock; elif [ $V = g1 ]; then RS_MERGE=gidf tools/run_compose_h4b.sh $N h4b-g1; else RS_MERGE=gidf2 tools/run_compose_h4b.sh $N h4b-g2; fi; }
for V in g2 g1 off; do c 10 $V; done
for N in 0 2 4 6 8; do c $N g2; done
echo ALLDONE
