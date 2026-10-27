#!/usr/bin/env python3
"""LITEPACKS requests (0 LLM). Usage: python3 -I mkreq.py <out dir>
Per arm K0..K4 and set: v01 (healthgap c7-replay-v01, 60), cm (selftest qa-cooking-se + qa-money-se, 40, built on the LITE5 request template),
st (LITE5-180 requests, 180). Everything identical across arms except config.kit (the installed set) and runId lp-<K>-<set>-s42.
modelId qwen3-1.7b-q4km, seed 42, settings quickFirst + packHeadPass a2 + packDense2 append-budget (X2b) everywhere."""
import json, sys, copy
A = "<workspace>/rnd/research/coordinator/arms"; BE = "<workspace>/boar-eval/bench"; out = sys.argv[1]
P = {"crypto": ("boar-crypto", "ae9fbd2c7a46a46a815d46d0283e7b192adb4c342b38a2adc4881e8f9d8831fb"),
     "voy": ("boar-wikivoyage-en", "ff8595e32f56b8b84e20464afd8bf88532d47d2d82d799e3df8489440004b66e"),
     "sw": ("boar-simplewiki-en", "99bcec306de73d2d8ca5d081531c99f8197d099a85105a5608fce49fb0777472"),
     "fb": ("boar-factbook", "4ce447e8ab188b1641fb840ea3d18f58a55f2c6ad54dbd93aebe1b75f25662e6"),
     "ml": ("boar-medlineplus-en", "e805ccea3aa7d75224a81fa44e60d881161c6a6029255b461f8ff6ee5399ebd0"),
     "fa": ("boar-firstaid-en", "0a7dffa614490199477cc469a06aa92561f89713d16d1ab43d1a0d53f813e9c6"),
     "wk": ("boar-wiki-en-top100k", "9123b3720abd8472" )}
ARMS = {"K0": ["crypto", "voy"], "K1": ["crypto", "voy", "sw"], "K2": ["crypto", "voy", "sw", "fb"],
        "K3": ["crypto", "voy", "sw", "fb", "ml", "fa"], "K4": ["crypto", "voy", "wk"]}
WK = sys.argv[2] if len(sys.argv) > 2 else None  # full sha256 of the top100k pack (computed by the caller)
if WK: P["wk"] = ("boar-wiki-en-top100k", WK)
ST = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def w(p, rows): open(p, "w").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
SET = {"quickFirst": True, "alwaysComplete": False, "packHeadPass": "a2", "packDense2": "append-budget"}
tmpl = rd(f"{A}/lite5/runs/180/lite5-180-on-boar-factbook-s42.requests.jsonl")[0]
base = {"v01": [], "cm": [], "st": []}
for r in rd(f"{A}/healthgap/runs/c7-replay-v01.requests.jsonl"):
    assert r["config"]["arm"] == "cut7" and r["seed"] == 42
    r = {k: v for k, v in r.items() if k != "question" or v}; base["v01"].append(r)
assert len(base["v01"]) == 60
for s in ("qa-cooking-se", "qa-money-se"):
    for q in rd(f"{BE}/selftest/{s}/questions.jsonl"):
        r = copy.deepcopy(tmpl); r["item"] = {"id": q["id"], "question": q["question"], "lang": q.get("lang", "en")}; base["cm"].append(r)
assert len(base["cm"]) == 40
for p in ST:
    rows = rd(f"{A}/lite5/runs/180/lite5-180-on-{p}-s42.requests.jsonl"); assert len(rows) == 20; base["st"] += rows
for arm, ks in ARMS.items():
    assert len(P[ks[-1]][1]) == 64, ks
    for s, rows in base.items():
        o = []
        for r in rows:
            r = copy.deepcopy(r); r["runId"] = f"lp-{arm}-{s}-s42"; c = r["config"]
            c["arm"] = "cut7-headpass-x2+litepacks"; c["modelId"] = "qwen3-1.7b-q4km"; c["settings"] = dict(SET)
            c["kit"] = [{"id": P[k][0], "sha256": P[k][1]} for k in ks]; r["seed"] = 42; o.append(r)
        w(f"{out}/lp-{arm}-{s}-s42.requests.jsonl", o)
    print(arm, {s: len(v) for s, v in base.items()})
