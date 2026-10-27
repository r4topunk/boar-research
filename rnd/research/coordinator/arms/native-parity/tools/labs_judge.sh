#!/bin/bash
# RC1-LABS: build N-DL traces (tool answer where a lab fired, else the N-D text) and judge ONLY the changed ids with Haiku 5.5-low N 4 both orders. MacBook.
set -euo pipefail
A=<workspace>/rnd/research/coordinator/arms; ARM=$A/native-parity; SJ=$A/deepthink/tools/shard_judge.sh; BE=<workspace>/boar-eval/bench/v0.1
python3 -I - "$ARM" <<'PY'
import json, sys
d = sys.argv[1]; ids = open(d + "/cv5-51.ids").read().split()
nd = {r["id"]: r["text"] for r in map(json.loads, open(d + "/runs/s3-gen.jsonl")) if r["arm"] == "N-D"}
tl = {r["id"]: r for r in map(json.loads, open(d + "/runs/rc1-labs-tools.jsonl"))}
assert set(ids) <= set(tl), "missing tool rows"
assert all(tl[i]["kind"] in (None, "instant") for i in ids), "a Context tool result needs generation"
txt = {i: (tl[i]["text"] if tl[i]["lab"] else nd[i]) for i in ids}
ch = [i for i in ids if txt[i] != nd[i]]
open(d + "/runs/labs-changed.ids", "w").write("\n".join(ch) + "\n")
with open(d + "/traces/native-N-DL-v01-s42.traces.jsonl", "w") as o:
    for i in ids:
        o.write(json.dumps({"protocol": "1.0.0", "runId": "native-parity-N-DL-s42", "itemId": i, "engine": {"commit": "46be7377", "arm": "native-harness-N-DL"},
                            "answer": {"text": txt[i]}, "tool": tl[i]["tool"], "error": None if txt[i] else "empty answer"}) + "\n")
print("changed", len(ch))
PY
N=$(grep -c . $ARM/runs/labs-changed.ids)
TR=$ARM/traces/native-N-DL-v01-s42.traces.jsonl; O=$ARM/judgments/native-N-DL-v01-s42.judgments.jsonl; SYS=native-parity-N-DL-v01-haiku55-low
env PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=v01 PREFLIGHT_DECLARED_CALLS=$((2*N)) PREFLIGHT_CRITERION=$ARM/RC1-LABS-criterion.md \
  bash $SJ --preflight $TR $O $BE $ARM/runs/labs-changed.ids $SYS 4 haiku
bash $SJ $TR $O $BE $ARM/runs/labs-changed.ids $SYS 4 haiku > $ARM/runs/judge-N-DL.log 2>&1
