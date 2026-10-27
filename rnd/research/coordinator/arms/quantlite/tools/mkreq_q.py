#!/usr/bin/env python3
"""QUANTLITE requests: LITE5's X2b ON st20 requests (lite5/runs/lite5-on-st20-<pack>-s42.requests.jsonl) with only
runId (and, for the Q8 arm, config.modelId) changed. Asserts every other byte of each request is equal.
Usage: mkreq_q.py <tag q8|q4mini> <out dir> [id,id,... for a subset (smoke)]"""
import json, sys, os, glob, copy
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, "..", "..")
tag, out = sys.argv[1], sys.argv[2]; sub = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
MID = {"q8": "qwen3-1.7b-q8_0", "q4mini": "qwen3-1.7b-q4km"}[tag]
n = 0; os.makedirs(out, exist_ok=True)
for f in sorted(glob.glob(os.path.join(A, "lite5/runs/lite5-on-st20-*-s42.requests.jsonl"))):
    pack = os.path.basename(f)[len("lite5-on-st20-"):-len("-s42.requests.jsonl")]
    run = f"quantlite-{tag}-{'smoke' if sub else 'st20'}-{pack}-s42"
    rows = []
    for l in open(f):
        r = json.loads(l)
        if sub is not None and r["item"]["id"] not in sub: continue
        assert r["config"]["modelId"] == "qwen3-1.7b-q4km" and r["seed"] == 42
        q = copy.deepcopy(r); q["runId"] = run; q["config"]["modelId"] = MID
        a, b = copy.deepcopy(r), copy.deepcopy(q)
        for x in (a, b): x["runId"] = ""; x["config"]["modelId"] = ""
        assert a == b
        rows.append(q)
    if rows:
        open(os.path.join(out, run + ".requests.jsonl"), "w").write("".join(json.dumps(x, separators=(",", ":")) + "\n" for x in rows)); n += len(rows)
print(f"{tag}: {n} requests -> {out}")
