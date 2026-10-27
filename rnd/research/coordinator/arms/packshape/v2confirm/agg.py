#!/usr/bin/env python3
"""FACTBOOK-V2-CONFIRM aggregate (0 calls). python3 -I agg.py -> ../V2-CONFIRM.json, prints the table. Criterion f17179a5 (definitions as sefix agg_opus_cm.py)."""
import json, sys, numpy as np
A = "<workspace>/rnd/research/coordinator/arms"; O = A + "/packshape/v2confirm"
sys.path.insert(0, A + "/null-cal/tools"); import labels as LB
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
TR = {"BASE": A + "/packproof/gen/on-k13/traces.jsonl", "S42": A + "/packshape/gen/on-k13s/traces.jsonl", "S43": A + "/packshape/gen/on-k13s43/traces.jsonl"}
ids = [l.strip() for l in open(O + "/ids.txt") if l.strip()]
J, FL, calls = {}, {}, 0
for arm, tf in TR.items():
    T = {t["itemId"]: t for t in rd(tf)}; R = {}
    rows = rd(f"{O}/{arm}.judgments.jsonl"); calls += len(rows)
    for r in rows:
        if r.get("ok") and not r.get("floorScored"):
            assert "opus" in str(r["judgeModel"]) and r["judgeVersion"] == "judge.v1" and r["seed"] == 7, r["judgeModel"]
            R.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    J[arm], FL[arm] = {}, {}
    for i in ids:
        u = R[i]; assert set(u) == {"boarA", "boarB"}, (arm, i); a, b = u["boarA"], u["boarB"]
        J[arm][i] = dict(s=(mr(a["boar"]) + mr(b["boar"])) / 2, r=(mr(a["ref"]) + mr(b["ref"])) / 2, corr=(a["boar"]["correctness"] + b["boar"]["correctness"]) / 2)
        x = T[i]["answer"]; FL[arm][i] = dict(warned=x["text"].startswith(W), declined=bool(LB.is_decline(x["text"], x.get("declined"))))
J["POOL"] = {i: {k: (J["S42"][i][k] + J["S43"][i][k]) / 2 for k in ("s", "r", "corr")} for i in ids}
Uf = lambda s, r: (s - 1).sum() / (r - 1).sum()
ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
arr = lambda a, k: np.array([J[a][i][k] for i in ids])
n = len(ids); rng = np.random.default_rng(11); dr = [rng.integers(0, n, n) for _ in range(2000)]
M = {a: (arr(a, "s"), arr(a, "r")) for a in J}; BS = {a: np.array([Uf(M[a][0][x], M[a][1][x]) for x in dr]) for a in M}
def armstats(a):
    corr = arr(a, "corr")
    if a == "POOL": return dict(U=round(Uf(*M[a]), 4), U_ci=ci(BS[a]), corr=round(float(corr.mean()), 3))
    dec = np.array([FL[a][i]["declined"] for i in ids]); war = np.array([FL[a][i]["warned"] for i in ids]); ce = (corr <= 1.5) & ~dec; cor = (corr >= 4) & ~dec
    return dict(U=round(Uf(*M[a]), 4), U_ci=ci(BS[a]), corr=round(float(corr.mean()), 3), correct=int(cor.sum()), correct_per100=round(100 * cor.mean(), 1), CE=int(ce.sum()), CE_per100=round(100 * ce.mean(), 1),
                CE_unwarned=int((ce & ~war).sum()), warned=int(war.sum()), declined=int(dec.sum()), CE_ids=[i for i, c in zip(ids, ce) if c])
res = {"criterion": "f17179a5", "calls_rows": calls, "arms": {a: armstats(a) for a in J}, "delta": {}}
for a in ("S42", "S43", "POOL"):
    ds = M[a][0] - M["BASE"][0]
    res["delta"][a] = dict(dU=round(float(Uf(*M[a]) - Uf(*M["BASE"])), 4), dU_ci=ci(BS[a] - BS["BASE"]), better=int((ds > .25).sum()), tie=int((abs(ds) <= .25).sum()), worse=int((ds < -.25).sum()),
                           dcorr=round(float((arr(a, "corr") - arr("BASE", "corr")).mean()), 3))
bce = set(res["arms"]["BASE"]["CE_ids"])
new_ce = [(i, a) for a in ("S42", "S43") for i in res["arms"][a]["CE_ids"] if i not in bce]
res["new_CE"] = new_ce
H = {s: json.load(open(f"{A}/packshape/{f}"))["rows"] for s, f in (("S42", "stage2.json"), ("S43", "stage2-s43.json"))}
res["items"] = {i: dict(base_s=round(J["BASE"][i]["s"], 3), s42=round(J["S42"][i]["s"], 3), s43=round(J["S43"][i]["s"], 3), base_corr=J["BASE"][i]["corr"], s42_corr=J["S42"][i]["corr"], s43_corr=J["S43"][i]["corr"],
                    haiku_base=H["S42"][i]["base"], haiku_s42=H["S42"][i]["shaped"], haiku_s43=H["S43"][i]["shaped"], fact_shaped=H["S42"][i]["shaped_fact"], fact_base=H["S42"][i]["base_fact"]) for i in ids}
d = res["delta"]["POOL"]
res["verdict"] = "CONFIRMED" if d["dU_ci"][0] > 0 and not new_ce else "NOT-CONFIRMED"
json.dump(res, open(A + "/packshape/V2-CONFIRM.json", "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "items"}, indent=1))
for i, x in res["items"].items(): print(i[-3:], x)
