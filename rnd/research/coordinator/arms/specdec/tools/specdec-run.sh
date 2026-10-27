#!/usr/bin/env bash
# SPECDEC step 2: replay matrix on the mini inside the heavy lock (one job). Config = name:mode:draft:nmax[:pmin].
# samp = engine sampler (T 0.7, top_k 40, top_p .95, min_p .05, seed 44); greedy = T 0 (G1 reads this one too).
# Usage (MacBook): tools/specdec-run.sh   -> results in <runner>/kiln/specdec/res on the mini, fetched to ../data/res by specdec-fetch.sh
set -uo pipefail
CFG="base1:samp:none:0 base2:samp:none:0 q06n4:samp:q06:4 q06n8:samp:q06:8 q15n4:samp:q15:4 q15n8:samp:q15:8 baseg:greedy:none:0 q06n4g:greedy:q06:4 q06n8g:greedy:q06:8 q15n4g:greedy:q15:4 q15n8g:greedy:q15:8 q06n4p75:samp:q06:4:0.75 q06n8p75:samp:q06:8:0.75 q06n4p75g:greedy:q06:4:0.75 q06n8p75g:greedy:q06:8:0.75"
echo "free before: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
scp -q $(dirname $0)/specdec_replay.py MINI_HOST:boar/kiln/specdec/
<on the mini> "cd <runner>/kiln/specdec && rm -rf res && HEAVY_CLASS=normal nohup <runner>/bin/run-heavy Kiln python3 specdec_replay.py prompts.jsonl res $CFG > run.log 2>&1 < /dev/null &" >/dev/null 2>&1
echo started
