#!/usr/bin/env python3
"""SEFIX-124 (F1+F2+F4, F3 off) answer-screen requests (0 LLM). python3 -I mk_req_124.py
Source = ans-req/sefixall-main-s4{2,3}.requests.jsonl (same kit, same items); only runId and config.arm change. Seeds 42 / 43 as the ALL runs."""
import json
A = "<workspace>/rnd/research/coordinator/arms"; SF = A + "/coverage-map/sefix"
for s in (42, 43):
    out = []
    for l in open(f"{SF}/ans-req/sefixall-main-s{s}.requests.jsonl"):
        r = json.loads(l); assert r["seed"] == s and r["config"]["arm"].endswith("+sefixall")
        r["runId"] = f"sefix124-main-s{s}"; r["config"]["arm"] = r["config"]["arm"][:-len("sefixall")] + "sefix124"; out.append(json.dumps(r, ensure_ascii=False))
    open(f"{SF}/ans-req/sefix124-main-s{s}.requests.jsonl", "w").write("\n".join(out) + "\n"); print(s, len(out))
