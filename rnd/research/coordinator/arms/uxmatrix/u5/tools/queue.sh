#!/bin/bash
T=<workspace>/rnd/research/coordinator/arms/uxmatrix/u5/tools
Q=<workspace>/rnd/research/coordinator/arms/coverage-map/searchpar/r5/qform.chain.jsonl
$T/run_u5.sh qform base BASE 0; $T/run_u5.sh qform on ON 0; $T/run_u5.sh qform on.c2 ON 2; $T/run_u5.sh qform base.c2 BASE 2; 
$T/run_u5.sh longsession on ON 0; TREE=<workspace>/kiln-local/rs-SEFIX $T/run_u5.sh longsession on.sefix ON 0
$T/run_u5.sh longsession on.c2 ON 2; $T/run_u5.sh longsession base BASE 0; $T/run_u5.sh longsession base.c2 BASE 2
for p in boar-crypto boar-factbook boar-firstaid-en boar-medlineplus-en boar-visa-en boar-wikivoyage-en; do
  ids=$(grep -o "\"id\": \"qf-$p-[0-9]*-F[08]\"" $Q | cut -d'"' -f4 | paste -sd, -)
  IDS=$ids $T/run_u5.sh qform off.$p ON 0 $p; IDS=$ids $T/run_u5.sh qform off.$p.c2 ON 2 $p
done; echo QB_DONE
