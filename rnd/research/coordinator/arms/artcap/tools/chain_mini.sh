#!/bin/bash
# ARTCAP mini chain: base identity (MAIN + ST) first, then MAIN cap4lead, ST capfact, ST cap4lead (MacBook: MAIN cap4, MAIN capfact, ST cap4).
D=<runner>/kiln/artcap/tools
$D/run_mini.sh main base; $D/run_mini.sh st base
$D/run_mini.sh main cap4lead RS_ARTCAP=cap4lead
$D/run_mini.sh st capfact RS_ARTCAP=capfact; $D/run_mini.sh st cap4lead RS_ARTCAP=cap4lead
echo MINI-CHAIN-DONE
