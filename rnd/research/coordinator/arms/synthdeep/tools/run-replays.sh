#!/usr/bin/env bash
# SYNTHDEEP replay gate: deep-tier retrieval replay on bench v0.1, cmpSplit off and on. Run from the repo root.
set -euo pipefail
A=rnd/research/coordinator/arms/synthdeep
export BOAR_REPLAY_CACHE=$PWD/rnd/research/coordinator/arms/deepcovfb/cache
C=(--deep --gate rules --tree wt/synthdeep --k 6 --pool 20 --questions boar-eval/bench/v0.1/questions.public.jsonl --packs shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite)
$A/tools/replay-split.sh "${C[@]}" --out $A/replay-off-v01.jsonl 2> $A/logs/replay-off.log
$A/tools/replay-split.sh "${C[@]}" --cmp-split --out $A/replay-on-v01.jsonl 2> $A/logs/replay-on.log
tail -1 $A/logs/replay-off.log; tail -1 $A/logs/replay-on.log
