#!/bin/bash
# stage 0 chain (sequential: shared replay cache db)
Q=<workspace>/rnd/research/coordinator/arms/qrewrite; O=$Q/items/oracle.json
while pgrep -f "replay-qrw.ts" > /dev/null; do sleep 5; done
$Q/tools/run.sh main base
$Q/tools/run.sh main S0 QRW_MAP=$O QRW_MODE=replace
$Q/tools/run.sh st S0 QRW_MAP=$O QRW_MODE=replace
$Q/tools/run.sh main S0Q QRW_MAP=$O QRW_MODE=concat
$Q/tools/run.sh st S0Q QRW_MAP=$O QRW_MODE=concat
$Q/tools/run.sh main S0W QRW_MAP=$O QRW_MODE=whole
$Q/tools/run.sh st S0W QRW_MAP=$O QRW_MODE=whole
echo CHAIN0 DONE
