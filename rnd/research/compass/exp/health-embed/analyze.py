# Thresholds fixed a priori (margin>0, LR p>0.5); eval items never used for fitting.
import json, numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
E = [json.loads(l) for l in open("eval.jsonl")]
B = json.load(open("emb.json")); RX = json.load(open("regex.json"))
n = lambda a: (lambda x: x / np.linalg.norm(x, axis=1, keepdims=True))(np.array(a))
P, N, X = n(B["pos"]), n(B["neg"]), n(B["eval"])
y = np.array([e["label"] != "neg" for e in E]); dz = np.array([e["label"] == "danger" for e in E])
sp, sn = X @ P.T, X @ N.T
def topk(s, k): return np.sort(s, axis=1)[:, -k:].mean(1)
scores = {
  "margin_max": sp.max(1) - sn.max(1),
  "margin_top3": topk(sp, 3) - topk(sn, 3),
}
lr = LogisticRegression(C=10, max_iter=2000, class_weight="balanced").fit(np.vstack([P, N]), [1]*len(P) + [0]*len(N))
scores["logreg"] = lr.predict_proba(X)[:, 1] - 0.5
preds = {k: v > 0 for k, v in scores.items()}
preds["regex_iosmain"] = np.array(RX["iosmain"]); preds["regex_fix08c"] = np.array(RX["fix08c"])
preds["iosmain OR margin_top3"] = preds["regex_iosmain"] | preds["margin_top3"]
subsets = {"hm-fresh": [("hm-fresh" in e["src"]) for e in E], "h1-health": [("h1" in e["src"] and e["label"]=="danger") for e in E]}
print(f"n={len(E)} danger={dz.sum()} health_info={(y & ~dz).sum()} neg={(~y).sum()}")
print(f"{'detector':26} {'danger rec':>10} {'hm-fresh':>9} {'h1':>5} {'hinfo':>6} {'FP/neg':>8}  AUC")
for k, p in preds.items():
    hm = np.array(subsets["hm-fresh"]); h1 = np.array(subsets["h1-health"])
    auc = f"{roc_auc_score(y, scores[k]):.3f}" if k in scores else ""
    print(f"{k:26} {p[dz].sum():>4}/{dz.sum():<5} {p[hm].sum():>3}/{hm.sum():<5} {p[h1].sum():>2}/{h1.sum():<2} {p[y&~dz].sum():>2}/{(y&~dz).sum():<3} {p[~y].sum():>3}/{(~y).sum():<4} {auc}")
for k in ["margin_top3", "logreg"]:
    print(f"\n-- {k} misses (danger/health_info):")
    for i in np.where(y & ~preds[k])[0]: print(f"   {scores[k][i]:+.3f} {E[i]['id']:12} {E[i]['q'][:95]}")
    print(f"-- {k} false positives:")
    for i in np.where(~y & preds[k])[0]: print(f"   {scores[k][i]:+.3f} {E[i]['id']:12} {E[i]['q'][:95]}")
print("\n-- regex_iosmain false positives:", [E[i]['id'] for i in np.where(~y & preds['regex_iosmain'])[0]])
# threshold sweep (informational only, not used for the verdict)
s = scores["margin_top3"]
for t in [-0.04, -0.02, 0, 0.02, 0.04]:
    p = s > t; print(f"sweep margin_top3 t={t:+.2f}: danger {p[dz].sum()}/{dz.sum()} FP {p[~y].sum()}/{(~y).sum()}")
