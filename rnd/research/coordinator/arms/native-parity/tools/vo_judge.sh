#!/bin/bash
# VITAL-ONOFF: fetch the mini N-DV generations, build traces, judge ONLY the divergent ids (text != N-D) with Haiku 5.5-low N 4 both orders. MacBook.
set -euo pipefail
A=<workspace>/rnd/research/coordinator/arms; ARM=$A/native-parity; SJ=$A/deepthink/tools/shard_judge.sh; BE=<workspace>/boar-eval/bench/v0.1
scp -q MINI_HOST:boar/kiln/native-parity/vo-gen.jsonl $ARM/runs/vo-gen.jsonl
python3 -I - "$ARM" <<'PY'
import json, sys
d = sys.argv[1]; ids = open(d + "/cv5-51.ids").read().split()
nd = {r["id"]: r["text"] for r in map(json.loads, open(d + "/runs/s3-gen.jsonl")) if r["arm"] == "N-D"}
dv = {r["id"]: r["text"] for r in map(json.loads, open(d + "/runs/vo-gen.jsonl")) if r["arm"] == "N-DV"}
assert set(ids) <= set(dv), "missing N-DV generations"
div = [i for i in ids if dv[i] != nd[i]]
open(d + "/runs/vo-divergent.ids", "w").write("\n".join(div) + "\n")
with open(d + "/traces/native-N-DV-v01-s42.traces.jsonl", "w") as o:
    for i in ids:
        o.write(json.dumps({"protocol": "1.0.0", "runId": "native-parity-N-DV-s42", "itemId": i, "engine": {"commit": "5f8cc8f4", "arm": "native-harness-N-DV"},
                            "answer": {"text": dv[i]}, "error": None if dv[i] else "empty answer"}) + "\n")
print("divergent", len(div))
PY
N=$(grep -c . $ARM/runs/vo-divergent.ids)
TR=$ARM/traces/native-N-DV-v01-s42.traces.jsonl; O=$ARM/judgments/native-N-DV-v01-s42.judgments.jsonl; SYS=native-parity-N-DV-v01-haiku55-low
env PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=v01 PREFLIGHT_DECLARED_CALLS=$((2*N)) PREFLIGHT_CRITERION=$ARM/VITAL-ONOFF-criterion.md \
  bash $SJ --preflight $TR $O $BE $ARM/runs/vo-divergent.ids $SYS 4 haiku
bash $SJ $TR $O $BE $ARM/runs/vo-divergent.ids $SYS 4 haiku > $ARM/runs/judge-N-DV.log 2>&1
