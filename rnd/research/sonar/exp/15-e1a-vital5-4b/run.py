"""Sonar exp-15: E1(a) step a, vital5 on the Android 4B. Paired (same items, same seed) judge ratio Δ, and-qwen-s4x
(kit A, no vital5) -> and-main-v5-s4x (kit A + vital5), pooled over seeds 42/43, percentile item bootstrap (2,000, seed 11).
Also exact-free key-in-context (article mode raw/pre; no -kic text for these runs) and confident-wrong proxy counts."""
import json, collections, random, statistics, sys
R = "<workspace>/boar-eval/runs/night-2026-10-01/"
def judge(f):
    s = collections.defaultdict(list)
    for l in open(R + f + ".judgments.jsonl"):
        j = json.loads(l)
        if j.get("ok") and j.get("mapped"):
            b, r = j["mapped"]["boar"], j["mapped"]["ref"]; s[j["queryId"]].append((sum(b.values()) / 3, sum(r.values()) / 3, b["correctness"]))
    return {k: (statistics.mean(x[0] for x in v), statistics.mean(x[1] for x in v), statistics.mean(x[2] for x in v)) for k, v in s.items()}
pairs = [("and-qwen-s42", "and-main-v5-s42"), ("and-qwen-s43", "and-main-v5-s43")]
J = {f: judge(f) for p in pairs for f in p}
ids = sorted(set.intersection(*[set(v) for v in J.values()]))
for a, b in pairs:
    ra = sum(J[a][i][0] for i in ids) / sum(J[a][i][1] for i in ids); rb = sum(J[b][i][0] for i in ids) / sum(J[b][i][1] for i in ids)
    print(f"{a} {ra:.4f} -> {b} {rb:.4f}  Δ {rb - ra:+.4f}")
def pooled(sel):
    A = sum(J[a][i][0] for a, _ in pairs for i in sel) / sum(J[a][i][1] for a, _ in pairs for i in sel)
    B = sum(J[b][i][0] for _, b in pairs for i in sel) / sum(J[b][i][1] for _, b in pairs for i in sel)
    return B - A
d = pooled(ids); random.seed(11); bs = sorted(pooled([random.choice(ids) for _ in ids]) for _ in range(2000))
print(f"POOLED 2 seeds, n={len(ids)} items: Δratio {d:+.4f}  95% CI {bs[50]:+.4f} … {bs[1949]:+.4f}")
# per-item movers (mean over seeds)
mv = sorted(((statistics.mean(J[b][i][0] / J[b][i][1] - J[a][i][0] / J[a][i][1] for a, b in pairs), i) for i in ids))
print("largest losses:", [(i, round(x, 3)) for x, i in mv[:5]]); print("largest gains:", [(i, round(x, 3)) for x, i in mv[-5:]])
