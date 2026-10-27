#!/bin/bash
# Resume of gen_hg2.sh after the disk guard: wait (≤ 120 min) for ≥ 5 GiB free and busy.sh free, then rerun the resumable driver.
B=<workspace>/rnd/research/coordinator/arms/headpass-st/tools/busy.sh; w=0
while [ "$(df -k <home> | tail -1 | awk '{print int($4/1048576)}')" -lt 5 ] || "$B" >/dev/null 2>&1 || pgrep -f 'gen_180[.]sh|run_lite5_gen[.]sh' >/dev/null; do [ $w -ge 120 ] && { echo "FAIL disk/busy wait 120 min"; exit 1; }; w=$((w+1)); sleep 60; done
echo "$(date '+%T') resume after ${w} min, free $(df -h <home> | tail -1 | awk '{print $4}')"
WAIT_MAX=120 <workspace>/rnd/research/coordinator/arms/healthgap/tools/gen_hg2.sh
