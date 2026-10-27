#!/bin/bash
# HEALTHGAP-r2 generation driver (rule v1.2 §5d; MacBook, sequential, one llama-server at a time via run_hg2.sh/busy.sh):
# gen = the 15 HEALTHGAP items + the follow-up forms p25 p26 p29 mt-es-para + the 10 frozen controls (claim kit), and genmlp =
# st-boar-medlineplus-en-003 with claim + boar-medlineplus-en; seed 42, persona succinct (adapter default), 4B; OFF then ON.
set -u
# Resumable: a run whose .status ends DONE is skipped (00:49 the ON run hit run_hg2.sh's disk guard, 4 GiB < 5, while swap was at 17 GiB).
H=<workspace>/rnd/research/coordinator/arms/healthgap; R=$H/runs/r2; t0=$(date +%s)
python3 -I $H/tools/mkreq_hg2.py gen hg2-gen-s42 cut7+healthgap-r2 $R/hg2-gen-s42.requests.jsonl || exit 1
python3 -I $H/tools/mkreq_hg2.py genmlp hg2-genmlp-s42 cut7+healthgap-r2 $R/hg2-genmlp-s42.requests.jsonl $H/runs/kit-claim+medlineplus.json || exit 1
for s in gen genmlp; do
  grep -qx DONE $R/hg2-$s-off-s42.traces.status 2>/dev/null || env -u HEALTHGAP $H/tools/run_hg2.sh $R/hg2-$s-s42.requests.jsonl $R/hg2-$s-off-s42.traces.jsonl || { echo "FAIL $s off"; exit 1; }
  grep -qx DONE $R/hg2-$s-on-s42.traces.status 2>/dev/null || env HEALTHGAP=1 $H/tools/run_hg2.sh $R/hg2-$s-s42.requests.jsonl $R/hg2-$s-on-s42.traces.jsonl || { echo "FAIL $s on"; exit 1; }
done
echo "gen done wall $(( $(date +%s) - t0 )) s"
