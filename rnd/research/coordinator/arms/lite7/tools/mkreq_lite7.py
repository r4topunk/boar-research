#!/usr/bin/env python3
"""LITE7 requests (0 LLM). Run: python3 -I mkreq_lite7.py
ON (180) = lite5/runs/180/lite5-180-on-<pack>-s42.requests.jsonl (1.7B + X2b) with only config.arm -> cut7+lite7 and runId -> lite7-180-on-<pack>-s42
(the style switch is the runner env LITE_STYLE=1, not a request field). Smoke: 5 items (medlineplus 001-004, health-se 001), ON and OFF
(OFF = same rows, run without LITE_STYLE: byte-identity anchor vs the LITE5-180 ON traces). Asserts every other field equals the LITE5-180 ON row."""
import json, copy
A = "<workspace>/rnd/research/coordinator/arms"; O = f"{A}/lite7/runs"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
SMOKE = {"boar-medlineplus-en": ["st-boar-medlineplus-en-001", "st-boar-medlineplus-en-002", "st-boar-medlineplus-en-003", "st-boar-medlineplus-en-004"], "qa-health-se": ["st-qa-health-se-001"]}
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
w = lambda p, rows: open(p, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
def conv(r, run):
    a = copy.deepcopy(r); a["config"]["arm"] = "cut7+lite7"; a["runId"] = run
    b = copy.deepcopy(a); b["config"]["arm"] = r["config"]["arm"]; b["runId"] = r["runId"]; assert b == r
    assert r["config"]["modelId"] == "qwen3-1.7b-q4km" and r["seed"] == 42 and r["config"]["arm"] == "cut7-headpass-x2"
    assert r["config"]["settings"] == {"quickFirst": True, "alwaysComplete": False, "packHeadPass": "a2", "packDense2": "append-budget"}
    return a
n = 0
for p in PACKS:
    src = rd(f"{A}/lite5/runs/180/lite5-180-on-{p}-s42.requests.jsonl"); assert len(src) == 20, p
    w(f"{O}/180/lite7-180-on-{p}-s42.requests.jsonl", [conv(r, f"lite7-180-on-{p}-s42") for r in src]); n += 20
    if p in SMOKE:
        for m in ("on", "off"):
            rows = [conv(r, f"lite7-smoke-{m}-{p}-s42") for r in src if r["item"]["id"] in SMOKE[p]]; assert len(rows) == len(SMOKE[p])
            w(f"{O}/smoke/lite7-smoke-{m}-{p}-s42.requests.jsonl", rows)
print("ON rows", n, "| smoke ids", sum(map(len, SMOKE.values())))
