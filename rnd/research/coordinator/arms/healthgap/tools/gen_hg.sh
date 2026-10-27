#!/bin/bash
# HEALTHGAP generation driver (rule v1.1 §5d; MacBook, sequential, one llama-server at a time via run_hg.sh/busy.sh):
# the 15 gap items + 10 controls (mkreq_hg.py gen), seed 42, claim kit, persona succinct (adapter default), 4B; OFF then ON.
set -u
H=<workspace>/rnd/research/coordinator/arms/healthgap; R=$H/runs; t0=$(date +%s)
python3 -I $H/tools/mkreq_hg.py gen hg-gen-s42 cut7+healthgap $R/hg-gen-s42.requests.jsonl || exit 1
env -u HEALTHGAP DUMP=$R/hg-gen-off-s42.prompts.jsonl $H/tools/run_hg.sh $R/hg-gen-s42.requests.jsonl $R/hg-gen-off-s42.traces.jsonl || { echo "FAIL off"; exit 1; }
env HEALTHGAP=1 DUMP=$R/hg-gen-on-s42.prompts.jsonl $H/tools/run_hg.sh $R/hg-gen-s42.requests.jsonl $R/hg-gen-on-s42.traces.jsonl || { echo "FAIL on"; exit 1; }
echo "gen done wall $(( $(date +%s) - t0 )) s"
