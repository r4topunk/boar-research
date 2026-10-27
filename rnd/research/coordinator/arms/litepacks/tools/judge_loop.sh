#!/bin/bash
# Re-run judge.sh over all arms every 2 min until generation is ALLDONE and a final pass completes. Usage: nohup judge_loop.sh > runs/logs/judge.log 2>&1 &
H=<workspace>/rnd/research/coordinator/arms/litepacks
while true; do
  g=0; grep -q '^ALLDONE' $H/runs/logs/gen.log && g=1
  grep -q '^FAIL' $H/runs/logs/gen.log && { echo "gen FAIL, stopping"; exit 2; }
  $H/tools/judge.sh K0 K1 K2 K3 K4 | grep -v '^not generated\|^K0 not generated\|^skip'; rc=${PIPESTATUS[0]}
  [ $rc != 0 ] && { echo "judge rc=$rc, stopping"; exit $rc; }
  [ $g = 1 ] && { echo "JUDGE LOOP DONE $(date +%T)"; exit 0; }
  sleep 120
done
