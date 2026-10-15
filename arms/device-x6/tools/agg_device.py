"""DEVICE-X6 aggregation (0 LLM calls). Estimator copied from packs-l2/tools/l2_agg.py (load/ratios/boot/setstats/paired unchanged:
per-item bootstrap of the ratio-of-sums difference, B 2000, seed 11, paired on queryId). Haiku rows only.
Usage: python3 -I agg_device.py <phone.judgments> <desktop.judgments> [--out file.json]"""
import json, sys, os, collections, numpy as np
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
def load(p):
    J = collections.defaultdict(dict)
    if not os.path.exists(p): return {}
    for l in open(p):
        r = json.loads(l)
        if r.get("ok"): J[r["queryId"]][r["order"]] = r["mapped"]
    out = {}
    for q, v in J.items():
        if set(v) != {"boarA", "boarB"}:
            print(f"WARN {os.path.basename(p)}: {q} judged in order(s) {sorted(v)} only; item skipped", file=sys.stderr); continue
        a, b = v["boarA"], v["boarB"]
        out[q] = {"s": (mr(a["boar"]) + mr(b["boar"])) / 2, "r": (mr(a["ref"]) + mr(b["ref"])) / 2, "consistent": a["winner"] == b["winner"],
                  "winner": a["winner"] if a["winner"] == b["winner"] else "tie"}
    return out
def ratios(S, R): return S.sum() / R.sum(), (S - 1).sum() / (R - 1).sum()
def boot(fn, n, B=2000, seed=11):
    rng = np.random.default_rng(seed); return np.array([fn(rng.integers(0, n, n)) for _ in range(B)])
ci = lambda x: [round(float(v), 3) for v in np.percentile(x, [2.5, 97.5])]
def setstats(d, ids):
    S = np.array([d[q]["s"] for q in ids]); R = np.array([d[q]["r"] for q in ids]); pt = ratios(S, R); b = boot(lambda ii: ratios(S[ii], R[ii]), len(ids))
    w = collections.Counter(d[q]["winner"] for q in ids)
    return {"n": len(ids), "raw": round(pt[0], 3), "raw_ci": ci(b[:, 0]), "above_min": round(pt[1], 3), "above_min_ci": ci(b[:, 1]),
            "win_tie_loss": [w["boar"], w["tie"], w["ref"]], "pos_consistency": round(sum(d[q]["consistent"] for q in ids) / len(ids), 3)}
def paired(W, N, ids):
    SW = np.array([W[q]["s"] for q in ids]); RW = np.array([W[q]["r"] for q in ids]); SN = np.array([N[q]["s"] for q in ids]); RN = np.array([N[q]["r"] for q in ids])
    f = lambda ii: [ratios(SW[ii], RW[ii])[j] - ratios(SN[ii], RN[ii])[j] for j in (0, 1)]
    pt = f(np.arange(len(ids))); b = boot(f, len(ids))
    return {"n": len(ids), "d_raw": round(pt[0], 3), "d_raw_ci": ci(b[:, 0]), "d_above_min": round(pt[1], 3), "d_above_min_ci": ci(b[:, 1]),
            "items_better_worse": [int(sum(W[q]["s"] > N[q]["s"] for q in ids)), int(sum(W[q]["s"] < N[q]["s"] for q in ids))]}
def rows(path):
    r = [json.loads(l) for l in open(path) if l.strip()]
    return {"rows": len(r), "ok": sum(bool(x.get("ok")) for x in r), "judgeModel": sorted({str(x.get("judgeModel")) for x in r}),
            "tracesSha256": sorted({str(x.get("tracesSha256"))[:12] for x in r}), "refs": sorted({str(x.get("refsSha256"))[:12] for x in r})}
P, D = sys.argv[1:3]; out = {"estimator": "per-item bootstrap ratio-of-sums diff, B 2000, seed 11, paired on queryId", "files": {"phone": P, "desktop": D}}
p, d = load(P), load(D); ids = sorted(set(p) & set(d)); out["n_paired"] = len(ids)
out["rows"] = {"phone": rows(P), "desktop": rows(D)}
out["sets"] = {"phone": setstats(p, ids), "desktop": setstats(d, ids)}
out["paired"] = {"phone_minus_desktop": paired(p, d, ids)}
pd = out["paired"]["phone_minus_desktop"]; out["reading"] = "device = desktop within noise" if abs(pd["d_raw"]) <= 0.03 and pd["d_raw_ci"][0] >= -0.05 and pd["d_raw_ci"][1] <= 0.05 else "device != desktop (report)"
js = json.dumps(out, indent=1); print(js)
if "--out" in sys.argv: open(sys.argv[sys.argv.index("--out") + 1], "w").write(js + "\n")
