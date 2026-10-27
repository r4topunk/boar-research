#!/bin/bash
# polls every 10 min (max 3.5 h) for the done status of M2/M4/M3 and runs each scorer once, in that order of readiness.
D=<workspace>/rnd/research/coordinator/arms/device-final; cd $D
done_() { grep -q '"state":"done"' out/df-$1.status.json 2>/dev/null; }
for n in $(seq 1 21); do
  for p in "m2-probes-s42 m2" "m4-uxmatrix-s42 m4" "m3-packproof-s42 m3"; do set -- $p
    [ -f judge/.scored-$2 ] && continue
    if done_ $1; then
      if [ $2 = m2 ]; then python3 -I tools/m2_probes.py && touch judge/.scored-m2; else tools/m34_label.sh $2 && touch judge/.scored-$2; fi
    fi
  done
  [ -f judge/.scored-m2 ] && [ -f judge/.scored-m3 ] && [ -f judge/.scored-m4 ] && { echo ALL-SCORED; exit 0; }
  echo "$(date +%T) poll $n: waiting"; sleep 600
done
echo TIMEOUT
