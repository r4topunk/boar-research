#!/bin/bash
cd <workspace>/rnd/research/coordinator/arms/coverage-map/searchpar/r5
while pgrep -f "tools/run_all.sh" >/dev/null; do sleep 5; done
IDS=$(cat identity.ids.q) tools/run_r5.sh qform h4 off <workspace>/kiln-local/rs-H4
IDS=$(cat identity.ids.l) tools/run_r5.sh longsession h4 off <workspace>/kiln-local/rs-H4
echo IDDONE
