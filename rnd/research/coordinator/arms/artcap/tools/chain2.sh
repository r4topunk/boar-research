#!/bin/bash
# MacBook part after the coordinator's mini split (16:2x): wait for main capfact, then ST cap4. Mini runs base identity, main cap4lead, ST capfact, ST cap4lead.
D=<workspace>/rnd/research/coordinator/arms/artcap/tools
while pgrep -f "artcap/tools/run.sh main capfact" >/dev/null; do sleep 5; done
echo "main capfact finished (MacBook)"
$D/run.sh st cap4 RS_ARTCAP=cap4
echo CHAIN2-DONE
