#!/bin/bash
# SFT4B stage 0: writer retry round N for the articles in data/retry-{holdout,train}.txt (from filter_jev.py). Resumable.
cd "$(dirname "$0")/.." || exit 1
PY=${PY:-python3}; N=$1
cp data/retry-holdout.txt runs/retry-holdout-r$N.txt; cp data/retry-train.txt runs/retry-train-r$N.txt
$PY -I tools/write_examples.py holdout --round "$N" --ids-from runs/retry-holdout-r$N.txt && \
$PY -I tools/write_examples.py train --round "$N" --ids-from runs/retry-train-r$N.txt
echo "rc=$? $(date '+%F %T')"
