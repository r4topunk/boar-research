#!/bin/bash
# Step 3: build protocol traces from the mini generations and judge them (Haiku 5.5-low judge.v1-low, N 4, both orders). MacBook.
set -euo pipefail
A=<workspace>/rnd/research/coordinator/arms; ARM=$A/native-parity; SJ=$A/deepthink/tools/shard_judge.sh; BE=<workspace>/boar-eval/bench/v0.1
mkdir -p $ARM/traces $ARM/judgments $ARM/runs
scp -q MINI_HOST:boar/kiln/native-parity/s3-gen.jsonl $ARM/runs/s3-gen.jsonl
python3 -I - "$ARM" <<'PY'
import json, sys
arm_dir = sys.argv[1]; rows = [json.loads(l) for l in open(arm_dir + "/runs/s3-gen.jsonl")]
for arm in ["N-D", "N-S"]:
    with open(f"{arm_dir}/traces/native-{arm}-v01-s42.traces.jsonl", "w") as o:
        for r in rows:
            if r["arm"] != arm: continue
            o.write(json.dumps({"protocol": "1.0.0", "runId": f"native-parity-{arm}-s42", "itemId": r["id"],
                                "engine": {"commit": "5f8cc8f4", "arm": f"native-harness-{arm}"}, "answer": {"text": r["text"]},
                                "error": None if r["text"] else "empty answer"}) + "\n")
PY
for arm in N-D N-S; do
  TR=$ARM/traces/native-$arm-v01-s42.traces.jsonl; O=$ARM/judgments/native-$arm-v01-s42.judgments.jsonl; SYS=native-parity-$arm-v01-haiku55-low
  env PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=v01 PREFLIGHT_DECLARED_CALLS=102 PREFLIGHT_CRITERION=$ARM/NATIVE-PARITY-S3-criterion.md \
    bash $SJ --preflight $TR $O $BE $ARM/cv5-51.ids $SYS 4 haiku
  bash $SJ $TR $O $BE $ARM/cv5-51.ids $SYS 4 haiku > $ARM/runs/judge-$arm.log 2>&1
done
