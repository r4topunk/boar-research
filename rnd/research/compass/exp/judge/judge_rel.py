# Judge reliability from boar-eval night judgments (read-only): position effect, judge-only noise on identical answers,
# run-to-run noise decomposition, a within-item length check, and power for arm decisions.
import json, numpy as np, collections, re
R = "<workspace>/boar-eval/runs/night-2026-10-01/"
K = ("correctness", "completeness", "usefulness")
mean = lambda s: sum(s[k] for k in K) / 3
def load(run):
    J = collections.defaultdict(dict)
    for l in open(R + run + ".judgments.jsonl"):
        r = json.loads(l)
        if r.get("ok"): J[r["queryId"]][r["order"]] = r["mapped"]
    T = {}
    for l in open(R + run + ".traces.jsonl"):
        t = json.loads(l); T[t["itemId"]] = t
    return {q: v for q, v in J.items() if len(v) == 2}, T
J42, T42 = load("ios-main-s42"); J43, T43 = load("ios-main-s43")
txt = lambda T, q: (T[q]["answer"]["text"] or "").strip()
# 1. position
allp = [(q, v) for J in (J42, J43) for q, v in J.items()]
agree = np.mean([v["boarA"]["winner"] == v["boarB"]["winner"] for q, v in allp])
dA = np.array([mean(v["boarA"]["boar"]) - mean(v["boarB"]["boar"]) for q, v in allp])
dRef = np.array([mean(v["boarA"]["ref"]) - mean(v["boarB"]["ref"]) for q, v in allp])
firstwins = np.mean([(v["boarA"]["winner"] == "boar") for q, v in allp if v["boarA"]["winner"] != "tie"] + [(v["boarB"]["winner"] == "ref") for q, v in allp if v["boarB"]["winner"] != "tie"])
print(f"pairs {len(allp)}  winner agreement across orders {agree:.1%}  P(answer in slot A wins | not tie) {firstwins:.1%}")
print(f"boar mean score when in slot A minus slot B: {dA.mean():+.3f} (sd {dA.std(ddof=1):.3f}, |diff|>0 in {np.mean(dA!=0):.0%})   ref: {dRef.mean():+.3f}")
comb = lambda v, s: (mean(v["boarA"][s]) + mean(v["boarB"][s])) / 2
# 2. identical answers across seeds -> judge-only noise
common = sorted(set(J42) & set(J43))
same = [q for q in common if txt(T42, q) == txt(T43, q)]
diffj = np.array([comb(J42[q], "boar") - comb(J43[q], "boar") for q in same])
diffall = np.array([comb(J42[q], "boar") - comb(J43[q], "boar") for q in common])
refd = np.array([comb(J42[q], "ref") - comb(J43[q], "ref") for q in common])
decl = sum(T42[q]["answer"]["declined"] and T43[q]["answer"]["declined"] for q in same)
print(f"items judged in both seeds {len(common)}; identical BOAR text {len(same)} ({decl} of them both declined)")
print(f"judge-only noise (identical answers): sd of boar-score diff {diffj.std(ddof=1):.3f}, mean |diff| {np.abs(diffj).mean():.3f}, nonzero {np.mean(diffj!=0):.0%}")
print(f"total run-to-run (all common items): sd {diffall.std(ddof=1):.3f}; reference answer (fixed text) re-scored: sd {refd.std(ddof=1):.3f}, nonzero {np.mean(refd!=0):.0%}")
sref = np.mean([comb(J42[q], "ref") for q in common]); sb42 = sum(comb(J42[q], "boar") for q in common); sb43 = sum(comb(J43[q], "boar") for q in common)
print(f"ratio s42 {sb42/sum(comb(J42[q],'ref') for q in common):.3f}  s43 {sb43/sum(comb(J43[q],'ref') for q in common):.3f}  (common items)")
# variance shares
vj = diffj.var(ddof=1) / 2; vt = diffall.var(ddof=1) / 2; vr = refd.var(ddof=1) / 2
print(f"per-item per-run variance: total {vt:.3f}; judge-only (identical answers) {vj:.3f}; judge noise on fixed ref text {vr:.3f}  → judge share ≈ {vr/vt:.0%}–{vj/vt:.0%}")
# 3. within-item length check (both seeds answered, different text)
L = [(len(txt(T42, q)), len(txt(T43, q)), comb(J42[q], "boar"), comb(J43[q], "boar")) for q in common
     if txt(T42, q) != txt(T43, q) and not T42[q]["answer"]["declined"] and not T43[q]["answer"]["declined"]]
w = [(a > b) == (sa > sb) for a, b, sa, sb in L if a != b and sa != sb]
print(f"length check: {len(L)} items answered in both seeds with different text; longer answer scored higher in {sum(w)}/{len(w)}")
# 4. power: SE of delta-ratio between two arms with k runs each, n items, using the measured per-item run variance
n = len(common)
for k in (1, 2, 3, 5):
    for nn in (60, 120):
        se = np.sqrt(2 * vt / k / nn) / sref
        print(f"  k={k} runs/arm, n={nn} items: SE(Δratio) ≈ {se:.3f}  MDE(80% power, α=.05) ≈ {2.8*se:.3f}")
json.dump({"same": same, "common": common}, open("judge_rel.ids.json", "w"))
