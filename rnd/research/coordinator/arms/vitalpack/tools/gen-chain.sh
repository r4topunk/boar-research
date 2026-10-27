#!/usr/bin/env bash
# Resumable pre-generation chain (0 judge calls): VITALADD slice -> DEEPCOVER slice -> VITALADD full v0.2 -> DEEPCOVER full v0.2, sequential on the mini.
# Per step: local traces present -> skip; remote STATUS present -> wait + fetch (never a second launch); else launch -> wait -> fetch. Stops at the first failure.
# Run from the repo root, detached: nohup bash <this> > arms/vitalpack/logs/gen-chain.log 2>&1 &   (idempotent: a later tick may re-run it)
set -u
A=rnd/research/coordinator/arms; export WAIT_EVERY=120 WAIT_HARD=20000; H=${MINI:-MINI_HOST}
step(){ conf=$1; req=$2; run=$3; out=$4; tree=$5
  if [ -s "$out/$run.traces.jsonl" ]; then echo "== $(date +%H:%M) $run already fetched, skip"; return 0; fi
  if ssh -T -n $H "test -e <runner>/kiln/be-0cfd4a77-$tree/be-repo/runs/$run/STATUS"; then echo "== $(date +%H:%M) $run already launched, waiting";
  else echo "== $(date +%H:%M) launch $run"; $A/_lib/arm.sh $A/$conf/arm.conf launch "$req" "$run" || { echo "LAUNCH FAILED $run"; exit 2; }; fi
  $A/_lib/arm.sh $A/$conf/arm.conf wait "$run" | tail -2; rc=${PIPESTATUS[0]}; [ $rc -eq 0 ] || { echo "WAIT rc=$rc $run"; exit 3; }
  $A/_lib/arm.sh $A/$conf/arm.conf fetch "$run" 2>&1 | grep -E '^\{|traces sha|FAIL|rror' ; echo "== $(date +%H:%M) done $run"; }
V=blind/bench-v02/runs-vitaladd; D=blind/bench-v02/runs-deepcover
step vitalpack $V/va-A-v02-s42-slice.requests.jsonl va-A-v02-s42-slice $V vitaladd
step deepcover $D/dc-C-v02-s42-slice.requests.jsonl dc-C-v02-s42-slice $D deepcover
step vitalpack $V/va-A-v02-s42.requests.jsonl va-A-v02-s42 $V vitaladd
step deepcover $D/dc-C-v02-s42.requests.jsonl dc-C-v02-s42 $D deepcover
echo "CHAIN DONE $(date +%H:%M)"
