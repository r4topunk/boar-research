#!/bin/bash
# DETECTOR-FT2 driver (mini, MPS): train each arm, HF-screen its 3 epoch checkpoints, drop the clearly failing ones (disk). 0 LLM.
cd <runner>/kiln/detector-ft; PY=.venv/bin/python; export HF_HUB_OFFLINE=1
for arm in "v3e-D150 data2/D150 1" "v3e-D300 data2/D300 1" "v3e-D600 data2/D600 1" "v3e-D300-pw3 data2/D300 3"; do
  set -- $arm; T=$1
  echo "== $T $(date +%T)"; $PY tools/ft_v3e.py $T $2 $3 > results/$T.log 2>&1; grep -E "AUC|best" results/$T.log
  $PY tools/hf2score.py $T.e1 $T.e2 $T.e3 && $PY tools/ft2_screen.py $T.e1 $T.e2 $T.e3
  for k in 1 2 3; do $PY -c "import json,sys;r=json.load(open('results/$T.e$k.screen.json'));sys.exit(0 if (r['pass_hf'] or (r['exact_lost']<=1 and r['sonar_ratio']>=.97)) else 1)" || rm -rf results/$T.e$k.model; done
  df -h ~ | tail -1
done
echo DONE $(date +%T)
