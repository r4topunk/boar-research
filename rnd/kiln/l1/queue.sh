#!/usr/bin/env bash
# Kiln mini queue (2026-10-03 13:10): health11 blind confirm (running) -> estask L1 remainder -> R3 meta-fresh1 -> b6e L1.
set -uo pipefail
L=<workspace>/rnd/kiln/l1; T=<scratch>
until grep -qE "H11-BLIND-RUNS-(DONE|STOPPED)" $T/bdecmckkv.output; do sleep 30; done
echo "== estask $(date +%H:%M)"; $L/estask-l1.sh
echo "== r3 $(date +%H:%M)"; $L/r3-meta-blind-runs.sh
echo "== b6e L1 $(date +%H:%M)"; $L/b6e-l1.sh
echo QUEUE-DONE
