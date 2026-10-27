#!/usr/bin/env bash
# SPECDEC G1 tie analysis: non-speculative greedy replay with top-2 logprobs, to check that the greedy diffs of the speculative runs
# start at near-ties (batch-vs-single-token numerics). Queued in the heavy lock behind everything else.
scp -q $(dirname $0)/specdec_replay.py MINI_HOST:boar/kiln/specdec/
<on the mini> "bash -c 'cd <runner>/kiln/specdec && HEAVY_CLASS=normal nohup <runner>/bin/run-heavy Kiln python3 specdec_replay.py prompts.jsonl res_lp baselp:greedylp:none:0 > run_lp.log 2>&1 < /dev/null &'" >/dev/null 2>&1
echo queued
