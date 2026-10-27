#!/bin/bash
# W78C: all arms, sequential (MacBook).
W=<workspace>/rnd/research/coordinator/arms/coverage-map/w78; cd $W
{ tools/run_w78c.sh B 0
  tools/run_w78c.sh Q4-64 32 RS_DENSE_Q=4 RS_DENSE_QN=64
  tools/run_w78c.sh Q4-128 32 RS_DENSE_Q=4 RS_DENSE_QN=128
  tools/run_w78c.sh Q2-128 32 RS_DENSE_Q=2 RS_DENSE_QN=128
  tools/run_w78c.sh IVF8 32 RS_DENSE_IVF=8
  tools/run_w78c.sh IVF32 32 RS_DENSE_IVF=32; } > replays-c/batchC.log 2>&1
