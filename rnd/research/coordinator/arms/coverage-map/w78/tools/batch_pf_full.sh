#!/bin/bash
# W78-PACKFMT: the 3 full MAIN 97 arms (rerun after the bash 3.2 empty-array fix in run_w78pf.sh).
W=<workspace>/rnd/research/coordinator/arms/coverage-map/w78; cd $W
{ tools/run_w78pf.sh PF32 1 32 RS_DENSE_IVFP=32
  tools/run_w78pf.sh IVF32 0 32 RS_DENSE_IVF=32
  tools/run_w78pf.sh B 0 0; } > replays-pf/batchPF-full.log 2>&1
echo DONE >> replays-pf/batchPF-full.log
