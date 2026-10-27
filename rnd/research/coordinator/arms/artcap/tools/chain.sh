#!/bin/bash
# ARTCAP stage 0 chain: identity first, then the three arms on both sets (sequential).
D=<workspace>/rnd/research/coordinator/arms/artcap/tools
$D/run.sh st base
$D/run.sh main cap4 RS_ARTCAP=cap4; $D/run.sh main capfact RS_ARTCAP=capfact; $D/run.sh main cap4lead RS_ARTCAP=cap4lead
$D/run.sh st cap4 RS_ARTCAP=cap4; $D/run.sh st capfact RS_ARTCAP=capfact; $D/run.sh st cap4lead RS_ARTCAP=cap4lead
echo CHAIN-DONE
