#!/bin/bash
# OCCDECL stage 1: run_pool.sh for A/B x K0/K1 sequentially (two llama-servers per job), then fetch each OCC sidecar from the mini job dir.
set -u
A=<workspace>/rnd/research/coordinator/arms; O=$A/occdecl; NC=$A/null-cal
for job in "$@"; do V=${job%-*}; K=${job#*-}
  # a mini job already launched for this run (e.g. by an earlier chain): wait for it to end, run_pool then reuses it
  while <on the mini> "test -f <runner>/kiln/lp-screens/jobs/occdecl-$V-$K-screen2-$K-s42/STATUS && ! grep -qE '^(DONE|FAIL)' <runner>/kiln/lp-screens/jobs/occdecl-$V-$K-screen2-$K-s42/STATUS"; do sleep 60; done
  OUT_BASE=$O/arms SCREEN_JSON=$NC/pool/screen2-$K.json \
    bash $NC/tools/run_pool.sh occdecl-$V $K $NC/pool/screen2-$K.ids $O/occdecl-$V.patch || echo "RUN FAIL $job"
  scp -q MINI_HOST:<runner>/kiln/lp-screens/jobs/occdecl-$V-$K-screen2-$K-s42/traces.occ.jsonl $O/sidecar/occdecl-$V-$K-screen2-$K-s42.occ.jsonl || echo "sidecar fetch FAIL $job"
done
echo CHAIN-DONE
