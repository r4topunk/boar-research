#!/bin/bash
# SFT4B stage 0: writer round 1 for hold-out then train (resumable: cached batches are skipped). nohup'd by the caller.
cd "$(dirname "$0")/.." || exit 1
PY=${PY:-python3}
$PY -I tools/write_examples.py holdout --round 1 && $PY -I tools/write_examples.py train --round 1
echo "rc=$? $(date '+%F %T')"
