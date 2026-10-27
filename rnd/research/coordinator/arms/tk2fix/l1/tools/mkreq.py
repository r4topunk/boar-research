#!/usr/bin/env python3
"""TK2FIX-L1 requests (0 LLM). ON = packs/selftest-runs/st-<pack>-cut7-s42.requests.jsonl with only runId -> tk2fix-l1-<pack>-s42 and config.arm -> tk2fix-cut7.
Also the 5-item smoke (factbook 001, 002, 003, 004, 009) as tk2fix-l1-smoke-s42. Asserts everything else equal to the reference rows."""
import json, copy
A = "<workspace>/rnd/research/coordinator/arms"; O = f"{A}/tk2fix/l1/runs"
PACKS = ["boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en", "qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en"]
SMOKE = ["st-boar-factbook-001", "st-boar-factbook-002", "st-boar-factbook-003", "st-boar-factbook-004", "st-boar-factbook-009"]
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
w = lambda p, rows: open(p, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
def mk(r, run):
    a = copy.deepcopy(r); a["runId"] = run; a["config"]["arm"] = "tk2fix-cut7"
    b = copy.deepcopy(a); b["runId"] = r["runId"]; b["config"]["arm"] = r["config"]["arm"]; assert b == r
    assert r["config"]["modelId"] == "qwen3-4b-instruct-2507-q4km" and r["seed"] == 42 and r["config"]["settings"] == {"quickFirst": True, "alwaysComplete": False}, r["item"]["id"]
    return a
n = 0
for p in PACKS:
    rows = rd(f"{A}/packs/selftest-runs/st-{p}-cut7-s42.requests.jsonl"); assert len(rows) == 20
    on = [mk(r, f"tk2fix-l1-{p}-s42") for r in rows]; w(f"{O}/tk2fix-l1-{p}-s42.requests.jsonl", on); n += len(on)
    if p == "boar-factbook": w(f"{O}/tk2fix-l1-smoke-s42.requests.jsonl", [mk(r, "tk2fix-l1-smoke-s42") for r in rows if r["item"]["id"] in SMOKE])
print("rows", n, "smoke", len(rd(f"{O}/tk2fix-l1-smoke-s42.requests.jsonl")))
