"""exp-35 verdict helper (Sonar): v0.1 EN paired ratio delta R - A pooled over seeds (per-item mean across seeds, bootstrap
90% CI by item), V-exact knowledge items per arm, and the frozen GO/KILL rule (L1-criterion.md 64ede784).
Safety (unsafe v0.8.7) comes from Kiln's report.  python3 verdict.py <judgments dir>"""
import json, sys, glob, random, statistics as st, collections
D = sys.argv[1] if len(sys.argv) > 1 else "<workspace>/boar-eval/runs/kiln/rv2-l1"
ids = open("<workspace>/rnd/research/anvil/exp/outofkit/v01-en-ids.txt").read().strip().split(",")
VX = ["vx-001", "vx-002", "vit-hum-001", "vit-hum-004"]
def per(files):
    d = collections.defaultdict(list)
    for f in files:
        for l in open(f):
            r = json.loads(l)
            if r.get("ok"): d[r["queryId"]].append((st.mean(r["mapped"]["boar"].values()), st.mean(r["mapped"]["ref"].values())))
    return {k: (st.mean(x for x, _ in v), st.mean(y for _, y in v), len(v)) for k, v in d.items()}
A = per(glob.glob(f"{D}/*A-s4[23]*.judgments.jsonl") + glob.glob("<workspace>/boar-eval/runs/kiln/bigpack-l1/bigpack-A-s42.*.judgments.jsonl"))
R = per(glob.glob(f"{D}/*R-s4[23]*.judgments.jsonl") + glob.glob(f"{D}/*rv2-s4[23]*.judgments.jsonl"))
common = [i for i in ids if i in A and i in R]
def ratio(M, s): return sum(M[i][0] for i in s) / sum(M[i][1] for i in s)
delta = ratio(R, common) - ratio(A, common)
random.seed(1)
bs = sorted(ratio(R, s) - ratio(A, s) for s in ([random.choice(common) for _ in common] for _ in range(4000)))
lo, hi = bs[int(0.05 * len(bs))], bs[int(0.95 * len(bs))]
print(f"v0.1 EN n={len(common)} (judgments per item A~{st.mean(A[i][2] for i in common):.1f} R~{st.mean(R[i][2] for i in common):.1f})")
print(f"ratio A {ratio(A, common):.3f}  R {ratio(R, common):.3f}  delta {delta:+.4f}  CI90 [{lo:+.4f}, {hi:+.4f}]")
worse = []
for i in VX:
    a, r = A.get(i, (float("nan"),))[0], R.get(i, (float("nan"),))[0]
    print(f"  {i}: A {a:.2f}  R {r:.2f}")
    if r <= a - 1: worse.append(i)
go = delta >= 0.02 and lo > 0 and not worse
kill = delta <= 0 or hi < 0.02
print("RULE (safety from Kiln):", "GO (if unsafe R <= A)" if go else "KILL" if kill else "INCONCLUSIVE -> one more seed pair (s44)", "| V-exact worse:", worse)
