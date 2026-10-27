#!/usr/bin/env bash
# DEEPCOV-FB step 0: baseline (curated kit) and pack-as-peer deep-tier replays on bench v0.1. Run from the repo root.
set -euo pipefail
A=rnd/research/coordinator/arms/deepcovfb
export BOAR_REPLAY_CACHE=$PWD/$A/cache
C=(--deep --gate rules --tree wt/cut7 --questions boar-eval/bench/v0.1/questions.public.jsonl --k 6 --pool 20)
$A/tools/replay-deep.sh "${C[@]}" --out $A/replay-base.jsonl 2> $A/logs/replay-base.log
$A/tools/replay-deep.sh "${C[@]}" --packs shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite,shared-data/packs/boar-wiki-en-top100k.sqlite --out $A/replay-peer.jsonl 2> $A/logs/replay-peer.log
tail -1 $A/logs/replay-base.log; tail -1 $A/logs/replay-peer.log
