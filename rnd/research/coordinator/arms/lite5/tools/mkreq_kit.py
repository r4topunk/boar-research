#!/usr/bin/env python3
"""LITE5 stage 6 (script-only; prints counts/hashes only): blind/bench-v02/runs-lite2/l-kit-v02-s42-slice.requests.jsonl -> runs-lite5/lite5-on-kit-v02-s42-slice.requests.jsonl
with runId rewritten, config.arm -> cut7-headpass-x2, settings += packHeadPass a2 + packDense2 append-budget; modelId stays qwen3-1.7b-q4km; claim kit unchanged (no sidecar)."""
import json, hashlib
B = "<private held-out dir>"; src = f"{B}/runs-lite2/l-kit-v02-s42-slice.requests.jsonl"; out = f"{B}/runs-lite5/lite5-on-kit-v02-s42-slice.requests.jsonl"
rows = [json.loads(l) for l in open(src) if l.strip()]
for r in rows:
    assert r["config"]["modelId"] == "qwen3-1.7b-q4km"
    r["runId"] = "lite5-on-kit-v02-s42-slice"; r["config"]["arm"] = "cut7-headpass-x2"; r["config"]["settings"] = {**r["config"]["settings"], "packHeadPass": "a2", "packDense2": "append-budget"}
open(out, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
print("rows", len(rows), "kit", [k["id"] for k in rows[0]["config"]["kit"]], "settings", rows[0]["config"]["settings"], "seed", rows[0]["seed"], "sha", hashlib.sha256(open(out, "rb").read()).hexdigest()[:16])
