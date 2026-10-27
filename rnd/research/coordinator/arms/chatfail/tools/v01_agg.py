"""CHATFAIL S1 v0.1 non-regression aggregation (0 calls; python3 -I). Estimators as honestprompt/tools/agg.py: per-item score = mean of correctness/completeness/usefulness over both judge
orders; ratio = sum s / sum s_ref; paired contrast A1 - C0 = difference of ratio-of-sums paired on id, item bootstrap B 2000 seed 1. Reads out/judgments-v01-{C0,A1}.jsonl."""
import json, collections, numpy as np, os
O = os.path.dirname(os.path.abspath(__file__)) + "/out/"; K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
def load(p):
    J = collections.defaultdict(dict)
    for l in open(p):
        r = json.loads(l)
        if r.get("ok"): J[r["queryId"]][r["order"]] = r["mapped"]
    out = {}
    for q, v in J.items():
        if set(v) != {"boarA", "boarB"}: continue
        a, b = v["boarA"], v["boarB"]
        out[q] = {"s": (mr(a["boar"]) + mr(b["boar"])) / 2, "r": (mr(a["ref"]) + mr(b["ref"])) / 2, "winner": a["winner"] if a["winner"] == b["winner"] else "tie"}
    return out
C, A = load(O + "judgments-v01-C0.jsonl"), load(O + "judgments-v01-A1.jsonl"); ids = sorted(set(C) & set(A))
ids_all = [l.strip() for l in open(O + "ids-v01.ids") if l.strip()]; assert len(ids) == len(ids_all), (len(ids), len(ids_all))
# which items actually differ in the answer text (the rest are engine-fixed or identical generations)
ans = {a: {json.loads(l)["chat"]: json.loads(l)["answer"] for l in open(O + f"gen-m4-{a}-v01.jsonl")} for a in ("C0", "A1")}
diff_ids = [q for q in ids if ans["C0"][q] != ans["A1"][q]]
def stats(d, sel):
    S = np.array([d[q]["s"] for q in sel]); R = np.array([d[q]["r"] for q in sel]); return float(S.sum() / R.sum())
def paired(sel, B=2000, seed=1):
    SW = np.array([A[q]["s"] for q in sel]); RW = np.array([A[q]["r"] for q in sel]); SN = np.array([C[q]["s"] for q in sel]); RN = np.array([C[q]["r"] for q in sel])
    f = lambda ii: SW[ii].sum() / RW[ii].sum() - SN[ii].sum() / RN[ii].sum(); rng = np.random.default_rng(seed); n = len(sel)
    b = np.array([f(rng.integers(0, n, n)) for _ in range(B)]); dm = SW - SN
    return {"n": n, "d": round(float(f(np.arange(n))), 3), "ci": [round(float(x), 3) for x in np.percentile(b, [2.5, 97.5])], "better_worse_tie": [int((dm > 1e-9).sum()), int((dm < -1e-9).sum()), int((abs(dm) <= 1e-9).sum())]}
out = {"n": len(ids), "ratio_C0": round(stats(C, ids), 3), "ratio_A1": round(stats(A, ids), 3), "paired_all": paired(ids), "n_answers_differ": len(diff_ids), "paired_differing": paired(diff_ids) if diff_ids else None}
w = lambda d: collections.Counter(d[q]["winner"] for q in ids); out["win_tie_loss_C0"] = [w(C)["boar"], w(C)["tie"], w(C)["ref"]]; out["win_tie_loss_A1"] = [w(A)["boar"], w(A)["tie"], w(A)["ref"]]
print(json.dumps(out, indent=1)); json.dump(out, open(O + "v01-agg.json", "w"), indent=1)
