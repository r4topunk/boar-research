#!/usr/bin/env python3
"""LITEDECLINE requests (0 LLM). Usage: python3 -I mkreq.py <out dir>
st:  lite5/runs/180/lite5-180-on-<pack>-s42.requests.jsonl (1.7B + X2b settings, each pack installed on top of the claim kit), runId ld-<arm>-st-<pack>-s42.
v01: healthgap/runs/c7-replay-v01.requests.jsonl (cut 7, claim kit crypto + Wikivoyage, 60 public v0.1 items) with modelId -> qwen3-1.7b-q4km, runId ld-<arm>-v01-s42.
Arms ON / OFF / OFF5 get identical requests apart from runId (the arm is the env switch LITEDECLINE_OFF, unset / 3 / 5)."""
import json, sys, copy
A = "<workspace>/rnd/research/coordinator/arms"; out = sys.argv[1]
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def w(p, rows): open(p, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
for arm in ("on", "off", "off5"):
    n = 0
    for p in PACKS:
        rows = rd(f"{A}/lite5/runs/180/lite5-180-on-{p}-s42.requests.jsonl"); assert len(rows) == 20
        o = []
        for r in rows:
            r = copy.deepcopy(r); assert r["config"]["modelId"] == "qwen3-1.7b-q4km" and r["seed"] == 42
            r["runId"] = f"ld-{arm}-st-{p}-s42"; r["config"]["arm"] = "cut7-headpass-x2+litedecline"; o.append(r)
        w(f"{out}/ld-{arm}-st-{p}-s42.requests.jsonl", o); n += len(o)
    rows = rd(f"{A}/healthgap/runs/c7-replay-v01.requests.jsonl"); assert len(rows) == 60
    o = []
    for r in rows:
        r = copy.deepcopy(r); assert r["config"]["arm"] == "cut7" and r["seed"] == 42 and r["config"]["settings"] == {"quickFirst": True, "alwaysComplete": False}
        r["runId"] = f"ld-{arm}-v01-s42"; r["config"]["arm"] = "cut7-headpass-x2+litedecline"; r["config"]["modelId"] = "qwen3-1.7b-q4km"; o.append(r)
    w(f"{out}/ld-{arm}-v01-s42.requests.jsonl", o); n += len(o)
    print(arm, n)
