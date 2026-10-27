#!/usr/bin/env python3
"""JUDGE-V1_1 addendum 1 aggregation (0 LLM). FLOOR rule-2 estimator on the v0.1 57 under judge.v1 (existing rows) and judge.v1_1 (W1): U per arm with CI,
paired dU = U(1.7B K0 ctl s42) - U(1.5B closed-book), CI of 2000 joint item bootstraps (default_rng(11)). Position: ABOVE iff dU CI low > 0; BELOW iff dU CI high < 0;
else LEVEL. SEPARABLE (FLOOR rule 2) iff dU >= 0.05 and CI low > 0. 'Went to zero' = item with s = 1.000 under v1.1 and s > 1 under v1, per arm (listed)."""
import json, os, collections, numpy as np
V = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); H = os.path.dirname(V); A = os.path.dirname(H)
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
def load(p):
    J = collections.defaultdict(dict)
    for l in open(p):
        r = json.loads(l)
        if r.get("ok") and r["order"] not in J[r["queryId"]]: J[r["queryId"]][r["order"]] = r["mapped"]
    return {q: {"s": (mr(v["boarA"]["boar"]) + mr(v["boarB"]["boar"])) / 2, "r": (mr(v["boarA"]["ref"]) + mr(v["boarB"]["ref"])) / 2,
                "c": (v["boarA"]["boar"]["correctness"] + v["boarB"]["boar"]["correctness"]) / 2} for q, v in J.items() if set(v) == {"boarA", "boarB"}}
ids = open(f"{A}/litepacks/data/v01-57.ids").read().split()
src = {"v1": {"ctl17": f"{A}/lp-screens/control/judgments/lpctl-K0-main-s42-v01.judgments.jsonl", "onebee": f"{H}/judgments/floor-anchors-K0-main-sub3e6183-s42-v01.judgments.jsonl"},
       "v1_1": {"ctl17": f"{V}/judgments/W1-sep-ctl17.judgments.jsonl", "onebee": f"{V}/judgments/W1-sep-onebee.judgments.jsonl"}}
D = {j: {a: load(p) for a, p in d.items()} for j, d in src.items()}
U = lambda S, R: (S - 1).sum() / (R - 1).sum(); ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
out = {"criterion_addendum_sha256": open(f"{H}/JUDGE-V1_1-criterion-addendum1.sha256").read().split()[0]}
for j in D:
    X, Y = D[j]["ctl17"], D[j]["onebee"]; q = [i for i in ids if i in X and i in Y]
    SX, RX, SY, RY = (np.array([d[i][k] for i in q]) for d, k in ((X, "s"), (X, "r"), (Y, "s"), (Y, "r")))
    rng = np.random.default_rng(11); B = []
    for _ in range(2000):
        ii = rng.integers(0, len(q), len(q)); B.append((U(SX[ii], RX[ii]), U(SY[ii], RY[ii]), U(SX[ii], RX[ii]) - U(SY[ii], RY[ii])))
    B = np.array(B); d = U(SX, RX) - U(SY, RY); c = ci(B[:, 2])
    out[j] = dict(n=len(q), U_ctl17=round(float(U(SX, RX)), 4), U_ctl17_ci=ci(B[:, 0]), U_onebee=round(float(U(SY, RY)), 4), U_onebee_ci=ci(B[:, 1]),
                  dU=round(float(d), 4), dU_ci=c, items_ctl_better_worse=[int((SX > SY).sum()), int((SX < SY).sum())],
                  zero_items_ctl17=int((SX == 1).sum()), zero_items_onebee=int((SY == 1).sum()),
                  position="ABOVE" if c[0] > 0 else ("BELOW" if c[1] < 0 else "LEVEL"), separable=bool(d >= 0.05 and c[0] > 0))
for a in ("ctl17", "onebee"):
    out[f"went_to_zero_{a}"] = [i for i in ids if i in D["v1_1"][a] and D["v1_1"][a][i]["s"] == 1 and D["v1"][a][i]["s"] > 1]
js = json.dumps(out, indent=1); print(js); open(f"{V}/aggregates/W1-sep.json", "w").write(js + "\n")
