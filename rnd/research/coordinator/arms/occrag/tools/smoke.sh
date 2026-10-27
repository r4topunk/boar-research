#!/bin/bash
# OCCRAG smoke (not judged): generate <ids> on the mini with the OCCRAG patch through mini_gen.sh (same slot lock, base tree, env as run_arm.sh),
# copy back traces + the .occ.jsonl sidecar (raw trace, status, tokens). Usage: smoke.sh <K0|K1> <ids file> <patch> <run name>
set -eu
K=$1; IDS=$2; PF=$3; RUN=$4
A=<workspace>/rnd/research/coordinator/arms; H=$A/lp-screens; O=$A/occrag; M=MINI_HOST; MK=<runner>/kiln
B=$MK/be-0cfd4a77-cut7-litepacks; J=$MK/lp-screens/jobs/$RUN; CA=cut7-headpass-x2+litepacks+occrag
mkdir -p $O/smoke; REQ=$O/smoke/$RUN.requests.jsonl
python3 -I $H/tools/mkreq.py $K $IDS $RUN $CA $REQ
scp -q $H/tools/mini_gen.sh $M:$MK/lp-screens-mini_gen.sh
ssh -T -n $M "rm -rf $J; mkdir -p $J; cp -cR $B $J/tree; rm -rf $J/tree/be/.cache; echo $CA > $J/tree/ARM"
scp -q $REQ $M:$J/requests.jsonl; scp -q $PF $M:$J/candidate.patch
ssh -T -n $M "cd $J/tree && patch -p1 -s < ../candidate.patch && find . -name '*.orig' -delete && nohup bash $MK/lp-screens-mini_gen.sh $J > $J/nohup.log 2>&1 < /dev/null &"
while :; do sleep 20; s=$(ssh -T -n $M "tail -1 $J/STATUS"); case $s in DONE) break;; FAIL*) ssh -T -n $M "cat $J/STATUS; tail -30 $J/run.log"; exit 1;; esac; done
scp -q $M:$J/traces.jsonl $O/smoke/$RUN.traces.jsonl; scp -q $M:$J/traces.occ.jsonl $O/smoke/$RUN.occ.jsonl; scp -q $M:$J/STATUS $O/smoke/$RUN.status
ssh -T -n $M "rm -rf $J/tree"; echo "smoke $RUN done"
