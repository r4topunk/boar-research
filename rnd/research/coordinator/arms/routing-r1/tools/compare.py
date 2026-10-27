#!/usr/bin/env python3
"""ROUTING-R1 step A (0 LLM): route-signature diff of each rule flag vs flags off, per set, + the safety gate.
Usage: python3 -I compare.py <job dir> -> ../aggregates/replay.json + stdout."""
import json, os, sys
J = sys.argv[1]; OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "aggregates")
PFX = ("task:", "retrieve:", "answer:", "places:", "near:", "grounding:health", "grounding:fa-card", "headpass:health", "headpass:dense:health", "routing-r1:")
def safety(c): return c.startswith(("grounding:health-strict", "grounding:fa-card-", "answer:first-aid", "answer:co", "answer:emergency", "grounding:health-card",
                                    "grounding:health-extractive", "grounding:health-no-source")) or "card" in c
def load(f):
    out = {}
    for l in open(f):
        t = json.loads(l); rc = t["route"]["reasonCodes"]
        kept = sorted(str(k.get("chunkId") or k.get("id") or k.get("title")) for k in ((t.get("retrieval") or {}).get("kept") or []))
        out[t["itemId"]] = dict(sig=sorted(c for c in rc if c.startswith(PFX)), kept=kept, safe=sorted(c for c in rc if safety(c)), q=t["question"])
    return out
SAFE_MAIN = ("dng-", "vit-hlt-", "lan-hlt-")
res = {}
for K in ["K1", "K3"]:
    for s in ["v01", "cm", "probes"]:
        base = load(f"{J}/out/off-{K}-{s}.traces.jsonl")
        for F in ["P", "T", "H"]:
            new = load(f"{J}/out/{F}-{K}-{s}.traces.jsonl"); ch = []; lost = []
            for i, b in base.items():
                n = new[i]
                if n["sig"] != b["sig"] or n["kept"] != b["kept"]:
                    ch.append(dict(id=i, off=b["sig"], new=n["sig"], kept_changed=n["kept"] != b["kept"], q=b["q"][:120]))
                if (s == "probes" or i.startswith(SAFE_MAIN)) and set(b["safe"]) - set(n["safe"]):
                    lost.append(dict(id=i, lost=sorted(set(b["safe"]) - set(n["safe"])), q=b["q"][:120]))
            res[f"{F}-{K}-{s}"] = dict(changed=ch, safety_lost=lost)
            print(f"{F} {K} {s:6} changed={len(ch):2} safety_lost={len(lost)}  {[c['id'] for c in ch]}  LOST {[l['id'] for l in lost]}")
os.makedirs(OUT, exist_ok=True); json.dump(res, open(f"{OUT}/replay.json", "w"), indent=1)
