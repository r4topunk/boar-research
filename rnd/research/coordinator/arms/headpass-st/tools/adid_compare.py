#!/usr/bin/env python3
"""ADAPTER-IDENTITY compare (0 LLM): S traces (packs/selftest-runs/st-qa-health-se-cut7-s42) vs the two no-settings runs on the
cut7-headpass-x2 tree (adapters 8dd1faff and 6298e5d3), and the two runs against each other. Per field identical counts:
answer text (exact), retrieval.raw, retrieval.kept, timing.promptTokens, route.reasonCodes, route.tier; diff ids listed.
Writes aggregates/adapter-identity.json (+ same_answer.py output under 'same_answer')."""
import json, subprocess, sys
A = "<workspace>/rnd/research/coordinator/arms"; H = f"{A}/headpass-st"; D = f"{H}/gen-adapter-id"
F = {"S": f"{A}/packs/selftest-runs/st-qa-health-se-cut7-s42.traces.jsonl",
     "8dd1faff": f"{D}/st-qa-health-se-cut7-adid-8dd1faff-s42.traces.jsonl", "6298e5d3": f"{D}/st-qa-health-se-cut7-adid-6298e5d3-s42.traces.jsonl"}
tr = lambda p: {(t := json.loads(l))["itemId"]: t for l in open(p) if l.strip()}
T = {k: tr(v) for k, v in F.items()}
fields = {"answer": lambda t: (t.get("answer") or {}).get("text"), "raw": lambda t: (t.get("retrieval") or {}).get("raw"),
          "kept": lambda t: (t.get("retrieval") or {}).get("kept"), "promptTokens": lambda t: (t.get("timing") or {}).get("promptTokens"),
          "reasonCodes": lambda t: (t.get("route") or {}).get("reasonCodes"), "tier": lambda t: (t.get("route") or {}).get("tier"),
          "error": lambda t: t.get("error")}
out = {"files": F, "pairs": {}}
for a, b in (("S", "8dd1faff"), ("S", "6298e5d3"), ("6298e5d3", "8dd1faff")):
    ids = sorted(set(T[a]) & set(T[b])); r = {"n": len(ids)}
    for k, f in fields.items():
        diff = [i for i in ids if json.dumps(f(T[a][i]), sort_keys=True) != json.dumps(f(T[b][i]), sort_keys=True)]
        r[k] = {"identical": len(ids) - len(diff), "diff_ids": diff}
    sa = subprocess.run([sys.executable, "-I", f"{A}/seedgen/tools/same_answer.py", F[a], F[b], "--label", f"{a}-vs-{b}"], capture_output=True, text=True).stdout.splitlines()
    r["same_answer"] = json.loads(sa[0]) if sa else None
    out["pairs"][f"{a}_vs_{b}"] = r
    print(f"{a} vs {b}: n={len(ids)} " + " ".join(f"{k} {r[k]['identical']}" for k in fields))
json.dump(out, open(f"{H}/aggregates/adapter-identity.json", "w"), indent=1)
