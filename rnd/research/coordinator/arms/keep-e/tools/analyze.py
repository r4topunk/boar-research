#!/usr/bin/env python3
"""KEEP-E analysis (0 LLM), frozen metrics of KEEP-E-criterion.md: per changed row E (mini) vs LITEPACKS K1 baseline (MacBook) -> aggregates/keep-e.json"""
import json, glob, os, re
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
ENGINE_DECLINE = re.compile(r"I don't have a reliable offline source on this, so I won't give health advice from memory|offline places pack is not installed|I didn't find (this in this phone's library|safe first-aid instructions)", re.I)
MODEL_DECLINE = re.compile(r"\b(i (do not|don't) know|i'?m not sure|i cannot answer|i can'?t answer|i don'?t have (enough |reliable )?information|not able to answer|not enough information|(sources?|context|passages?) (do|does) not (contain|provide|mention)|unanswerable)\b", re.I)
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def decl2(t):
    body = t[len(W):].strip() if t.startswith(W) else t
    return bool(ENGINE_DECLINE.search(t)) or (len(body) < 300 and bool(MODEL_DECLINE.search(body))) or body == ""
by = {}
for f in glob.glob(f"{H}/judgments/ke-E-*.judgments.jsonl"):
    for r in rd(f):
        if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
m3 = lambda d: sum(d.values()) / 3
JN = {q: dict(s=sum(m3(m["boar"]) for m in v.values()) / 2, corr=sum(m["boar"]["correctness"] for m in v.values()) / 2) for q, v in by.items() if len(v) == 2}
S1 = {r["textSha256"]: r["attempted"] for r in rd(f"{H}/judgments/stage1/stage1.jsonl") if r.get("ok")}
for r in rd(f"{H}/../../ruler/decline2stage/out/stage1.jsonl"):
    if r.get("ok"): S1.setdefault(r["textSha256"], r["attempted"])
BL = json.load(open(f"{H}/aggregates/baseline.json")); SREF = BL["sref_main"]; RP = {r["id"]: r for r in json.load(open(f"{H}/aggregates/replay.json"))["rows"]}
import hashlib
E = {t["itemId"]: t for t in rd(f"{H}/traces/ke-E-MAIN14-s42.traces.jsonl")}
rows = []
for i in sorted(E):
    b = BL["items"][i]; bt, nt = b["text"], E[i]["answer"]["text"]; n = JN[i]
    bs1, ns1 = S1[b["sha"]], S1[hashlib.sha256(nt.encode()).hexdigest()]
    bref = decl2(bt) or bs1 == "no"; nref = decl2(nt) or ns1 == "no"
    bD, nD = (0.0 if bref else b["judged"]["s"]), (0.0 if nref else n["s"])
    neutral = nref and b["judged"]["corr"] <= 2.5
    d = 0.0 if neutral else nD - bD
    ceu = lambda t, ref, c: (not ref) and (not t.startswith(W)) and c <= 1.5
    rows.append(dict(id=i, base_corr=b["judged"]["corr"], new_corr=n["corr"], base_s=round(bD, 3), new_s=round(nD, 3), delta=round(d, 3),
                     base_warned=bt.startswith(W), new_warned=nt.startswith(W), base_ref=bref, new_ref=nref, neutral=neutral,
                     new_ceu=ceu(nt, nref, n["corr"]) and not ceu(bt, bref, b["judged"]["corr"]), new_refusal_on_answered=(not bref) and nref,
                     cites=bool(re.search(r"\[\d\]", nt)), tok_base=RP[i]["tok_base"], tok_E=RP[i]["tok_E"], answer=nt[:300]))
net = sum(r["delta"] for r in rows) / SREF
ceu_n = sum(r["new_ceu"] for r in rows); ref_n = sum(r["new_refusal_on_answered"] for r in rows)
verdict = "PASS" if net >= 0.010 and ceu_n == 0 and ref_n == 0 else "KILL"
res = dict(sref_main=SREF, n=len(rows), net_U=round(net, 4), sum_delta=round(sum(r["delta"] for r in rows), 3), new_ceu=ceu_n, new_refusals=ref_n,
           improved=sum(r["delta"] > 0 for r in rows), worse=sum(r["delta"] < 0 for r in rows), verdict=verdict, rows=rows)
json.dump(res, open(f"{H}/aggregates/keep-e.json", "w"), indent=1)
print({k: v for k, v in res.items() if k != "rows"})
for r in rows: print(f"{r['id']:22} corr {r['base_corr']} -> {r['new_corr']}  s {r['base_s']} -> {r['new_s']}  d {r['delta']:+.3f} warn {int(r['base_warned'])}->{int(r['new_warned'])} cites {int(r['cites'])} ceu {int(r['new_ceu'])} ref {int(r['new_ref'])}")
