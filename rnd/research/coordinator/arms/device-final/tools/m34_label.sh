#!/bin/bash
# DEVICE-FINAL M3/M4 labelling. usage: m34_label.sh m3|m4 [--dry-run]
# m3: packproof/tools/label.mjs on out/df-m3-packproof-s42.jsonl ; m4: uxmatrix/tools/label.mjs on out/df-m4-uxmatrix-s42.jsonl (Haiku 5.5-low via claude -p, unchanged).
# --dry-run: no LLM; rows from DRY_ROWS (default /tmp/fake-<k>.jsonl), fake labels, outputs under /tmp/dfdry/ ; writes nothing under judge/ aggregates/ CALLS.md.
set -eu
K=$1; DRY=${2:-}
D=<workspace>/rnd/research/coordinator/arms/device-final; C=$(dirname $D)
case $K in m3) ROWS=$D/out/df-m3-packproof-s42.jsonl; LAB=$C/packproof/tools/label.mjs;; m4) ROWS=$D/out/df-m4-uxmatrix-s42.jsonl; LAB=$C/uxmatrix/tools/label.mjs;; *) echo bad kind; exit 2;; esac
if [ "$DRY" = "--dry-run" ]; then W=/tmp/dfdry; mkdir -p $W; ROWS=${DRY_ROWS:-/tmp/fake-$K.jsonl}; OUT=$W/$K.json
else W=$D/judge; mkdir -p $W $D/aggregates; OUT=$D/aggregates/$K.json; fi
python3 -I $D/tools/m34_prep.py $K $ROWS $W/$K-units.json $W/$K-answers.json
if [ "$DRY" = "--dry-run" ]; then
  python3 -I $D/tools/m34_fakelabel.py $W/$K-units.json $W/$K-labels.jsonl; echo "DRY RUN: 0 Haiku calls (would label $(python3 -c "import json;print(len(json.load(open('$W/$K-units.json'))['units']))") units, A pass + borderline B/C rechecks)"
else
  node $LAB $W/$K-units.json $W/$K-labels.jsonl | tee -a $W/$K-label.log
  CALLS=$(python3 -c "import json;print(sum(json.loads(l).get('tries',1) for l in open('$W/$K-labels.jsonl') if l.strip()))")
  echo "| $(date +%m-%d\ %H:%M) | $K labels ($ROWS) | $CALLS | (cumulative: see sum of per-kind rows; cap 600 for M3+M4) |" >> $D/CALLS.md; echo "Haiku calls $K: $CALLS"
fi
python3 -I $D/tools/m34_agg.py $K $W/$K-answers.json $W/$K-labels.jsonl $OUT
