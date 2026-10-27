#!/usr/bin/env python3
"""NATIVE-RC question files for the JVM harness (0 LLM). Writes work/q-r1.jsonl (UXMATRIX 60 ON + OFF rows), work/q-probes.jsonl (65 f3-safety probes,
kit ON), work/q-r2.jsonl (20 boar-factbook self-tests, kit ON; run twice: factbook v1 / shaped v2). Kit = K13 pack list in the app's order with the
app's ids (catalog packs: catalog id; non-catalog files: local-<name>), see NATIVE-RC.md."""
import json, os
B = "<workspace>"; C = B + "/rnd/research/coordinator/arms"; W = C + "/native-rc/work"; BE = B + "/boar-eval/bench/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
CATALOG = {"wiki-vital5", "boar-crypto", "boar-wikivoyage-en", "boar-factbook", "boar-firstaid-en", "boar-medlineplus-en", "qa-health-se", "qa-outdoors-se",
           "qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "boar-simplewiki-en"}
nid = lambda p: p if p in CATALOG else "local-" + p
Q = {r["id"]: r["question"] for r in rd(BE + "v0.1/questions.public.jsonl")}
def st(i):
    p = i.rsplit("-", 1)[0][3:]
    for r in rd(f"{BE}selftest/{p}/questions.jsonl"):
        if r["id"] == i: return r["question"]
    raise KeyError(i)
q = lambda i: Q[i] if i in Q else st(i)
os.makedirs(W, exist_ok=True)
items = json.load(open(C + "/uxmatrix/items.json"))["items"]
with open(W + "/q-r1.jsonl", "w") as o:
    for x in items:
        o.write(json.dumps(dict(id=x["id"], arm="on", question=q(x["id"]), packsOff=[])) + "\n")
        if x["off_minus"]: o.write(json.dumps(dict(id=x["id"], arm="off", question=q(x["id"]), packsOff=[nid(p) for p in x["off_minus"]])) + "\n")
with open(W + "/q-probes.jsonl", "w") as o:
    for r in rd(C + "/coverage-map/sefix/f3-safety/req/f3safety-off-s42.requests.jsonl"):
        o.write(json.dumps(dict(id=r["item"]["id"], arm="probe", question=r["item"]["question"], packsOff=[])) + "\n")
pp = json.load(open(C + "/packproof/in/items.json"))["items"]
with open(W + "/q-r2.jsonl", "w") as o:
    for x in pp:
        if x["pack"] == "boar-factbook": o.write(json.dumps(dict(id=x["id"], arm="fb", question=q(x["id"]), packsOff=[])) + "\n")
for f in ("q-r1", "q-probes", "q-r2"): print(f, sum(1 for _ in open(f"{W}/{f}.jsonl")))
