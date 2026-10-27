#!/usr/bin/env python3
"""FLOOR-ANCHORS aggregation (0 LLM; estimator of FLOOR-criterion.md). Usage: python3 -I floor_agg.py [--no-1b]
U = sum(s-1)/sum(r-1) (floor-adjusted), raw = sum s/sum r; CI 2.5/97.5 of 2000 item bootstraps, default_rng(11)."""
import json, sys, os, collections, numpy as np
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = os.path.dirname(H)
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
def load(*paths):
    J = collections.defaultdict(dict)
    for p in paths:
        for l in open(p):
            r = json.loads(l)
            if r.get("ok") and r["order"] not in J[r["queryId"]]: J[r["queryId"]][r["order"]] = r["mapped"]
    out = {}
    for q, v in J.items():
        if set(v) != {"boarA", "boarB"}: print(f"WARN {q} one order only; dropped", file=sys.stderr); continue
        a, b = v["boarA"], v["boarB"]
        out[q] = {"s": (mr(a["boar"]) + mr(b["boar"])) / 2, "r": (mr(a["ref"]) + mr(b["ref"])) / 2,
                  "dims": {k: (a["boar"][k] + b["boar"][k]) / 2 for k in K}, "w": a["winner"] if a["winner"] == b["winner"] else "tie"}
    return out
U = lambda S, R: ((S - 1).sum() / (R - 1).sum(), S.sum() / R.sum())
ci = lambda x: [round(float(v), 3) for v in np.percentile(x, [2.5, 97.5])]
def boot(f, n): rng = np.random.default_rng(11); return np.array([f(rng.integers(0, n, n)) for _ in range(2000)])
def stats(d, ids):
    S = np.array([d[q]["s"] for q in ids]); R = np.array([d[q]["r"] for q in ids]); pt = U(S, R); b = boot(lambda ii: U(S[ii], R[ii]), len(ids))
    w = collections.Counter(d[q]["w"] for q in ids)
    return {"n": len(ids), "U": round(pt[0], 4), "U_ci": ci(b[:, 0]), "raw": round(pt[1], 3), "raw_ci": ci(b[:, 1]), "wtl": [w["boar"], w["tie"], w["ref"]],
            "mean_dims": {k: round(float(np.mean([d[q]["dims"][k] for q in ids])), 3) for k in K}, "items_s_gt_1": int((S > 1).sum())}
def paired(X, Y, ids):  # U(X) - U(Y)
    SX, RX, SY, RY = (np.array([D[q][k] for q in ids]) for D, k in ((X, "s"), (X, "r"), (Y, "s"), (Y, "r")))
    f = lambda ii: [U(SX[ii], RX[ii])[j] - U(SY[ii], RY[ii])[j] for j in (0, 1)]
    pt = f(np.arange(len(ids))); b = boot(f, len(ids))
    return {"n": len(ids), "dU": round(pt[0], 4), "dU_ci": ci(b[:, 0]), "d_raw": round(pt[1], 3), "d_raw_ci": ci(b[:, 1]),
            "items_X_better_worse": [int(sum(X[q]["s"] > Y[q]["s"] for q in ids)), int(sum(X[q]["s"] < Y[q]["s"] for q in ids))]}
out = {"criterion_sha256": open(f"{H}/FLOOR-criterion.sha256").read().split()[0], "decline": {}}
ids30 = open(f"{H}/decline-30.ids").read().split()
ok = True
for v in "abc":
    d = load(f"{H}/judgments/fa-decline-{v}.judgments.jsonl"); st = stats(d, [q for q in ids30 if q in d]); out["decline"][v] = st
    st["valid"] = st["U_ci"][1] <= 0.05; ok &= st["valid"]
    st["nonzero_items"] = sorted([(q, round(d[q]["s"], 3)) for q in ids30 if q in d and d[q]["s"] > 1], key=lambda x: -x[1])
out["decline_verdict"] = "VALID" if ok else "INVALID"
if "--no-1b" not in sys.argv:
    ids57 = open(f"{A}/litepacks/data/v01-57.ids").read().split()
    run = "floor-anchors-K0-main-sub3e6183-s42"
    C = f"{A}/lp-screens/control/judgments/lpctl-K0-main-s42-v01.judgments.jsonl"; ctl = load(C)
    one = load(f"{H}/judgments/{run}-v01.judgments.jsonl", C)  # answers byte-identical to the control reuse its rows (run_arm.sh rule)
    c43 = load(f"{A}/gemma4-e2b-confirm-c43/judgments/gemma4-e2b-confirm-c43-K0-main-s42-v01.judgments.jsonl", C)
    ids = [q for q in ids57 if q in one and q in ctl]
    out["onebee"] = stats(one, ids); out["control_17_s42"] = stats(ctl, ids)
    sep = paired(ctl, one, ids); out["separability"] = sep
    out["separability_verdict"] = "SEPARABLE" if sep["dU"] >= 0.05 and sep["dU_ci"][0] > 0 else "NOT SEPARABLE ON DEV"
    two = {q: {"s": (ctl[q]["s"] + c43[q]["s"]) / 2, "r": (ctl[q]["r"] + c43[q]["r"]) / 2} for q in ids if q in c43}
    out["sens_two_seed_control"] = paired(two, one, [q for q in ids if q in two])
    tr = {json.loads(l)["itemId"]: json.loads(l) for l in open(f"{H}/traces/{run}.traces.jsonl")}
    ct = {json.loads(l)["itemId"]: json.loads(l) for l in open(f"{A}/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl")}
    nonmodel = [q for q in ids if tr[q]["answer"]["text"] == ct[q]["answer"]["text"]]  # deterministic layers (calculator, first-aid cards): same text in both arms
    out["nonmodel_path_items"] = nonmodel
    out["sens_model_path_only"] = paired(ctl, one, [q for q in ids if q not in nonmodel])
    out["onebee_fail_like"] = [q for q in ids if one[q]["s"] <= 2 and ctl[q]["s"] >= 4]
    out["onebee_declined"] = [q for q in ids if tr[q]["answer"].get("declined")]
js = json.dumps(out, indent=1); print(js); open(f"{H}/aggregates/floor.json" if "--no-1b" not in sys.argv else f"{H}/aggregates/floor-decline.json", "w").write(js + "\n")
