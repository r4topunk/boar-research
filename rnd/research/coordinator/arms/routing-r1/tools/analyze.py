#!/usr/bin/env python3
"""ROUTING-R1 step B analysis (0 LLM): per rule, changed items vs the LITEPACKS K1 baseline (frozen metrics). -> ../aggregates/routing-r1.json"""
import json, glob, os, re, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); LP = H + "/../litepacks"
sys.path.insert(0, H + "/tools"); W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
ENGINE_DECLINE = re.compile(r"I don't have a reliable offline source on this, so I won't give health advice from memory|offline places pack is not installed|I didn't find (this in this phone's library|safe first-aid instructions)", re.I)
MODEL_DECLINE = re.compile(r"\b(i (do not|don't) know|i'?m not sure|i cannot answer|i can'?t answer|i don'?t have (enough |reliable )?information|not able to answer|not enough information|(sources?|context|passages?) (do|does) not (contain|provide|mention)|unanswerable)\b", re.I)
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
def judg(files):
    by = {}
    for f in files:
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    m3 = lambda d: sum(d.values()) / 3
    return {q: dict(s=sum(m3(m["boar"]) for m in v.values()) / 2, sref=sum(m3(m["ref"]) for m in v.values()) / 2, corr=sum(m["boar"]["correctness"] for m in v.values()) / 2) for q, v in by.items() if len(v) == 2}
def decl2(t):
    body = t[len(W):].strip() if t.startswith(W) else t
    return bool(ENGINE_DECLINE.search(t)) or (len(body) < 300 and bool(MODEL_DECLINE.search(body))) or body == ""
# baseline K1 (reuse K0 rows for identical answers), MAIN 97 sref
tr = lambda a: {t["itemId"]: t for f in glob.glob(f"{LP}/traces/lp-{a}-*-s42.traces.jsonl") if "-st-" not in f and "smoke" not in f for t in rd(f)}
T0, T1 = tr("K0"), tr("K1"); J0 = judg([f for f in glob.glob(f"{LP}/judgments/lp-K0-*.judgments.jsonl") if "-st-" not in f]); J1 = judg([f for f in glob.glob(f"{LP}/judgments/lp-K1-*.judgments.jsonl") if "-st-" not in f])
JB = {i: (J0.get(i) if T1[i]["answer"]["text"] == T0[i]["answer"]["text"] else J1.get(i)) for i in T1}
SREF = sum(j["sref"] for j in JB.values() if j)  # MAIN 97 judged (food-001/002/006 have no reference)
res = {"sref_main": SREF, "rules": {}}
for F in "PTH":
    TN = {t["itemId"]: t for t in rd(f"{H}/traces/r1-{F}-K1-cm-s42.traces.jsonl")}
    JN = judg(glob.glob(f"{H}/judgments/r1-{F}-*.judgments.jsonl")); rows = []
    for i, t in TN.items():
        b, n = JB[i], JN[i]; bt, nt = T1[i]["answer"]["text"], t["answer"]["text"]
        b_ref = bool(ENGINE_DECLINE.search(bt)); fixed = (b["corr"] <= 2.5 or b_ref) and n["corr"] >= 3.5
        ceu_new = (not decl2(nt)) and (not nt.startswith(W)) and n["corr"] <= 1.5
        ceu_base = (not decl2(bt)) and (not bt.startswith(W)) and b["corr"] <= 1.5
        rows.append(dict(id=i, base_corr=b["corr"], new_corr=n["corr"], base_s=round(b["s"], 3), new_s=round(n["s"], 3), fixed=fixed,
                         new_ceu=ceu_new and not ceu_base, warned=nt.startswith(W), base_refusal=b_ref, answer=nt[:240]))
    dU = sum(r["new_s"] - r["base_s"] for r in rows) / SREF
    res["rules"][F] = dict(n=len(rows), fixed=sum(r["fixed"] for r in rows), new_ceu=sum(r["new_ceu"] for r in rows), dU_main=round(dU, 4), items=rows)
    print(f"{F}: n={len(rows)} fixed={res['rules'][F]['fixed']} new_CEu={res['rules'][F]['new_ceu']} dU(MAIN97)={dU:+.4f}")
    for r in rows: print(f"   {r['id']:22} corr {r['base_corr']} -> {r['new_corr']}  s {r['base_s']} -> {r['new_s']}  warned={int(r['warned'])} fixed={int(r['fixed'])} newCEu={int(r['new_ceu'])}")
json.dump(res, open(f"{H}/aggregates/routing-r1.json", "w"), indent=1)
