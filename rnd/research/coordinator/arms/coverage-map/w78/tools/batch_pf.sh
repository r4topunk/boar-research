#!/bin/bash
# W78-PACKFMT: full arms then 3 cold-start reps per arm (fresh process, one item), sequential (MacBook).
W=<workspace>/rnd/research/coordinator/arms/coverage-map/w78; cd $W; mkdir -p replays-pf/cold
{ tools/run_w78pf.sh PF32 1 32 RS_DENSE_IVFP=32
  tools/run_w78pf.sh IVF32 0 32 RS_DENSE_IVF=32
  tools/run_w78pf.sh B 0 0
  for r in 1 2 3; do
    OUTDIR=$W/replays-pf/cold IDS=vit-hum-001 tools/run_w78pf.sh PF32-r$r 1 32 RS_DENSE_IVFP=32
    OUTDIR=$W/replays-pf/cold IDS=vit-hum-001 tools/run_w78pf.sh IVF32-r$r 0 32 RS_DENSE_IVF=32
    OUTDIR=$W/replays-pf/cold IDS=vit-hum-001 tools/run_w78pf.sh B-r$r 0 0
  done; } > replays-pf/batchPF.log 2>&1
echo DONE >> replays-pf/batchPF.log
