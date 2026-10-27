#!/usr/bin/env python3
"""COMBINED requests (0 LLM). python3 -I mk_req.py. = sefix/ans-req/sefixall-main-s{42,43}.requests.jsonl with runId combined-main-s{42,43} and arm label +combined; nothing else changes (kit pins, settings, seed)."""
A = "<workspace>/rnd/research/coordinator/arms"; SF = A + "/coverage-map/sefix"; CB = A + "/coverage-map/combined"
import json
for s in (42, 43):
    out = []
    for l in open(f"{SF}/ans-req/sefixall-main-s{s}.requests.jsonl"):
        r = json.loads(l); assert r["seed"] == s and r["config"]["arm"].endswith("+sefixall")
        r["runId"] = f"combined-main-s{s}"; r["config"]["arm"] = r["config"]["arm"][:-len("sefixall")] + "combined"; out.append(json.dumps(r, ensure_ascii=False))
    open(f"{CB}/req/combined-main-s{s}.requests.jsonl", "w").write("\n".join(out) + "\n"); print(s, len(out))
