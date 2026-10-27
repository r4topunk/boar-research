#!/usr/bin/env python3
"""PR1 generation identity: compare pr1 traces against the cut 7 reference traces, per item.
Fields: answer text, route tier, kept titles, reason codes (all of them), task, outcome. Usage: compare_gen.py <ref> <pr1>"""
import json, sys
def load(p):
    d = {}
    for l in open(p):
        r = json.loads(l); d[r["itemId"]] = r
    return d
def ans(r):
    a = r.get("answer")
    return a.get("text") if isinstance(a, dict) else a
def view(r):
    rt = r.get("route", {}); ret = r.get("retrieval", {})
    return {"text": ans(r), "tier": rt.get("tier"), "task": rt.get("task"), "outcome": rt.get("outcome"),
            "kept": [k.get("title") for k in ret.get("kept", [])], "reasonCodes": rt.get("reasonCodes")}
ref, new = load(sys.argv[1]), load(sys.argv[2])
fields = ["text", "tier", "task", "outcome", "kept", "reasonCodes"]
same = {f: 0 for f in fields}; diff_ids = {}
for i, r in ref.items():
    if i not in new: diff_ids[i] = ["MISSING"]; continue
    a, b = view(r), view(new[i])
    bad = [f for f in fields if a[f] != b[f]]
    for f in fields: same[f] += a[f] == b[f]
    if bad: diff_ids[i] = bad
print(f"items ref {len(ref)} pr1 {len(new)}; extra in pr1: {sorted(set(new) - set(ref))}")
for f in fields: print(f"  {f}: identical {same[f]}/{len(ref)}")
print(f"  all fields identical: {len(ref) - len(diff_ids)}/{len(ref)}")
for i, bad in sorted(diff_ids.items()):
    print(f"DIFF {i}: {bad}")
    if bad != ["MISSING"]:
        a, b = view(ref[i]), view(new[i])
        for f in bad: print(f"   {f}\n     ref: {json.dumps(a[f], ensure_ascii=False)[:400]}\n     pr1: {json.dumps(b[f], ensure_ascii=False)[:400]}")
