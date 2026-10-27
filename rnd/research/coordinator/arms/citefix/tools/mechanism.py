#!/usr/bin/env python3
"""CITEFIX: why each candidate answer is warned (0 LLM). Usage: python3 -I mechanism.py <traces.jsonl> <gate2.json>
Classes per warned answer: LIST (an [n, m] bracket list is its only citation form), CT1 (the model wrote [n] and CT-1 removed all of them),
NONE (no citation form at all). Also marks the gate role (false refusal / fixed by refusal)."""
import json, re, sys, collections
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
LIST = re.compile(r"\[\d+(?:\s*[,;–-]\s*\d+)+\]")
tr = [json.loads(l) for l in open(sys.argv[1])]; g = json.load(open(sys.argv[2]))
fr, br = set(g["false_ref"]), set(g["fixed_by_refusal"])
c = collections.Counter(); rows = []
for d in tr:
    t = d["answer"]["text"] or ""
    if not t.startswith(W): continue
    rc = " ".join(d["route"]["reasonCodes"])
    k = "LIST" if LIST.search(t) else "CT1" if "citations:removed" in rc and "all-citations-removed" in rc else "NONE"
    role = "false_ref" if d["itemId"] in fr else "fixed_by_refusal" if d["itemId"] in br else "-"
    c[(k, role)] += 1; rows.append((d["itemId"], k, role))
print(sys.argv[1].split("/")[-1], "warned", sum(c.values()), dict(sorted(c.items())))
for r in rows:
    if r[1] == "LIST": print("   LIST", r)
