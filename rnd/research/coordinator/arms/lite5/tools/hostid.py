#!/usr/bin/env python3
"""LITE5 0-judge host identity: MacBook OFF (X2b tree, settings unset, sidecar pack copy) vs LITE2's mini l-st20 traces (same 1.7B, seed 42).
Fields: answer text, kept (title, section), promptTokens, reasonCodes, tier, error. Writes aggregates/hostid.json."""
import json, sys
A = "<workspace>/rnd/research/coordinator/arms"
ld = lambda f: {(t := json.loads(l))["itemId"]: t for l in open(f) if l.strip()}
M = ld(f"{A}/lite5/runs/lite5-off-st20-s42.traces.jsonl"); L = ld(f"{A}/lite2/runs/l-st20-s42.traces.jsonl")
F = {"answer": lambda t: (t.get("answer") or {}).get("text"), "kept": lambda t: [(s.get("title"), s.get("section")) for s in (t.get("retrieval") or {}).get("kept") or []],
     "promptTokens": lambda t: (t.get("timing") or {}).get("promptTokens"), "reasonCodes": lambda t: t["route"]["reasonCodes"], "tier": lambda t: t["route"].get("tier"), "error": lambda t: t.get("error")}
assert set(M) == set(L) and len(M) == 20
out = {k: sum(f(M[i]) == f(L[i]) for i in M) for k, f in F.items()}
out["answer_diff_ids"] = sorted(i for i in M if F["answer"](M[i]) != F["answer"](L[i]))
out["errors_mac"] = sum(bool(M[i].get("error")) for i in M); out["n"] = 20
json.dump(out, open(f"{A}/lite5/aggregates/hostid.json", "w"), indent=1); print(json.dumps(out))
