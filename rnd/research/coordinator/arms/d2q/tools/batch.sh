#!/bin/bash
D=<workspace>/rnd/research/coordinator/arms/d2q
for a in ${ARMS:-off x1 x2}; do bash $D/tools/run.sh main $a; for g in on-k13 on-k13+qa-ethereum-se on-k13+qa-bitcoin-se; do bash $D/tools/run.sh st $a $g; done; done
echo ALLDONE
