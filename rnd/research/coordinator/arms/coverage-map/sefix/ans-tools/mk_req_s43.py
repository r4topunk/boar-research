#!/usr/bin/env python3
"""SEFIX-ALL seed-43 replicate requests (0 LLM). python3 -I mk_req_s43.py
ALL arm = ans-req/sefixall-main-s42.requests.jsonl with seed 43 + runId sefixall-main-s43; control = lp-screens/control/runs/req/lpctl-K1-main-s42.requests.jsonl (K1 kit, stock) with seed 43 + runId lpctl-K1-main-s43. Nothing else changes."""
import json
A = "<workspace>/rnd/research/coordinator/arms"; SF = A + "/coverage-map/sefix"
for src, dst, run in ((SF + "/ans-req/sefixall-main-s42.requests.jsonl", SF + "/ans-req/sefixall-main-s43.requests.jsonl", "sefixall-main-s43"),
                      (A + "/lp-screens/control/runs/req/lpctl-K1-main-s42.requests.jsonl", SF + "/ans-req/ctlk1-main-s43.requests.jsonl", "ctlk1-main-s43")):
    out = []
    for l in open(src):
        r = json.loads(l); assert r["seed"] == 42; r["seed"] = 43; r["runId"] = run; out.append(json.dumps(r, ensure_ascii=False))
    open(dst, "w").write("\n".join(out) + "\n"); print(dst, len(out))
