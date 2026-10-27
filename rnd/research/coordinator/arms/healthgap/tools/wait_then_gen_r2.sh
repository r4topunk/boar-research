#!/bin/bash
# Waits for the LITE5-180 driver (gen_180.sh / run_lite5_gen.sh) to exit and busy.sh to report free (avoids racing its
# server gaps between runs; its judge phase, claude -p only, is not waited on), then runs gen_hg2.sh (whose run_hg2.sh waits on busy.sh again before each run).
B=<workspace>/rnd/research/coordinator/arms/headpass-st/tools/busy.sh; w=0
while pgrep -f 'gen_180[.]sh|run_lite5_gen[.]sh' >/dev/null || "$B" >/dev/null 2>&1; do [ $w -ge 300 ] && { echo "FAIL waited 300 min"; exit 1; }; w=$((w+1)); sleep 60; done
echo "$(date '+%T') free after ${w} min"; sleep 20; "$B" >/dev/null 2>&1 && { echo "FAIL busy again"; exit 1; }
WAIT_MAX=120 <workspace>/rnd/research/coordinator/arms/healthgap/tools/gen_hg2.sh
