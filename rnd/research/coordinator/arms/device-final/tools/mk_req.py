#!/usr/bin/env python3
"""DEVICE-FINAL requests (never prints item text): req/<name>.json for the device eval runner (pipeline legacy, Qwen3-1.7B, followUps).
M1 v0.4 (75 items, turns[0] + followUps), M2 65 F3 probes (prior user turns first, then the probe), M3 PACKPROOF on-k13 (140), M4 UXMATRIX on (60)."""
import json, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); C = os.path.dirname(D); B = "<workspace>"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def req(rid, ver, qs):
    p = f"{D}/req/{rid}.json"
    json.dump(dict(requestId=rid, pipeline="legacy", models=["qwen3-1.7b-q4km"], evalSetVersion=ver, questions=qs), open(p, "w"), ensure_ascii=False)
    print(rid, len(qs), "questions", sum(1 + len(q.get("followUps", [])) for q in qs), "turns", os.path.getsize(p), "bytes")
v4 = [dict(id=i["id"], query=i["turns"][0], category=i.get("family") or "v04", followUps=i["turns"][1:]) for i in rd(B + "/boar-eval/bench/v0.4/items.jsonl")]
for s in (42, 43, 44): req(f"df-m1-v04-s{s}", "v0.4", v4)
pr = []
for r in rd(C + "/coverage-map/sefix/f3-safety/req/f3safety-off-s42.requests.jsonl"):
    it = r["item"]; prior = [t["text"] for t in (it.get("history") or {}).get("turns", []) if t["role"] == "user"]
    pr.append(dict(id=it["id"], query=prior[0], category="probe", followUps=prior[1:] + [it["question"]]) if prior else dict(id=it["id"], query=it["question"], category="probe"))
req("df-m2-probes-s42", "f3-safety-65", pr)
req("df-m3-packproof-s42", "packproof-on-k13", [dict(id=r["item"]["id"], query=r["item"]["question"], category="selftest") for r in rd(C + "/packproof/in/on-k13.requests.jsonl")])
req("df-m4-uxmatrix-s42", "uxmatrix-on", [dict(id=r["item"]["id"], query=r["item"]["question"], category="ux") for r in rd(C + "/uxmatrix/in/succinct/on.requests.jsonl")])
