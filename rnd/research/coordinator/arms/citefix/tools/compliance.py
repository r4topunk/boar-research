#!/usr/bin/env python3
"""CITEFIX: citation compliance before/after the normaliser (0 LLM). Usage: python3 -I compliance.py <traces.jsonl>...
raw_n   = rows whose model text held an engine-readable [n] (a [n] that CT-1 kept, or one it removed), attribution-added [n] excluded
raw_any = rows whose model text held [n] or a normaliser form (= raw_n after the fix)
shown_cited = rows with a [n] in the final text (before; includes attribution)"""
import json, re, sys
LIST = re.compile(r"(?<![\w\]])\[\d{1,2}(?:\s*[,;]\s*\d{1,2})+\]")
for p in sys.argv[1:]:
    n = rn = ra = sc = 0
    for l in open(p):
        d = json.loads(l); t = d["answer"]["text"] or ""; rc = d["route"]["reasonCodes"]; n += 1
        added = sum(len(x.split("-")) - 1 for x in rc if x.startswith("citations:added-"))
        removed = any(x.startswith("citations:removed-") for x in rc)
        has_n = len(re.findall(r"\[\d+\]", t)) > added or removed
        rn += has_n; ra += has_n or bool(LIST.search(t)); sc += bool(re.search(r"\[\d+\]", t))
    print(f"{p.split('/')[-1][:14]}\tn {n}\tmodel wrote [n]: {rn} -> {ra} after normaliser\tfinal text cited: {sc}")
