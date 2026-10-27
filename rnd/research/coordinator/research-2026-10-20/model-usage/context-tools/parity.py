#!/usr/bin/env python3
"""Parity of the stub prompt capture vs the LITEPACKS traces: kept titles, context reason code, generated-or-not."""
import json, sys
D = "<workspace>/rnd/research/coordinator/research-2026-10-20/model-usage/context-tools/cap"
L = "<workspace>/rnd/research/coordinator/arms/litepacks/traces"
rd = lambda f: {r["itemId"]: r for r in map(json.loads, open(f))}
for X in ["lp-K0-v01-s42", "lp-K0-cm-s42", "lp-K1-v01-s42", "lp-K1-cm-s42", "lp-K1-st-s42", "lp-K3-st-s42"]:
    a, b = rd(f"{D}/{X}.traces.jsonl"), rd(f"{L}/{X}.traces.jsonl")
    pr = {}
    for l in open(f"{D}/{X}.prompts.jsonl"):
        p = json.loads(l); pr.setdefault(p["itemId"], []).append(p)
    same_kept = sum([k["title"] for k in a[i]["retrieval"]["kept"]] == [k["title"] for k in b[i]["retrieval"]["kept"]] for i in b)
    rc = lambda r: [c for c in r["route"]["reasonCodes"] if c.startswith(("context:", "headpass:")) or c in ("grounding:no-good-source",) or c.startswith("grounding:off-topic")]
    same_rc = sum(rc(a[i]) == rc(b[i]) for i in b)
    gen_b = {i for i in b if (b[i]["timing"].get("promptTokens") or 0) > 0}
    multi = sum(len(v) > 1 for v in pr.values())
    print(X, "n", len(b), "kept-identical", same_kept, "ctx/headpass/grounding codes identical", same_rc,
          "generated(orig)", len(gen_b), "prompts captured items", len(pr), "orig-gen-without-capture", len(gen_b - set(pr)), "capture-without-orig-gen", len(set(pr) - gen_b), "multi-gen items", multi)
