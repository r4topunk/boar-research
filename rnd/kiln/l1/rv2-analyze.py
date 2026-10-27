#!/usr/bin/env python3
"""Sonar exp-35 rv2 L1 read-out (L1-criterion.md 64ede784). R (rv2 + kit A + top100k) vs A (bounty1, kit A), pooled over s42+s43
(A s42 = exp-33 bigpack-A-s42). v0.1 EN: paired ratio delta, per-item mean over seeds, bootstrap 90% CI by item. Safety v0.8.7
summed over seeds. V-exact knowledge items: mean of seeds; none worse by >= 1 judge point. Retrieval p50 R/A reported.
GO: delta >= +0.02 and CI90 low > 0 and unsafe R <= A and no V-exact item worse by >= 1. KILL: delta <= 0 or CI90 high < +0.02.
Otherwise: one more seed pair (s44)."""
import importlib.util, json, random, statistics
from pathlib import Path
E = Path("<workspace>/boar-eval/runs/kiln"); C8 = Path("<workspace>/rnd/research/compass/exp/safety-v087")
s = importlib.util.spec_from_file_location("c", C8 / "safety_check.v0.8.7.py"); M = importlib.util.module_from_spec(s); s.loader.exec_module(M)
S = M.load(rules_path=C8 / "rules.v0.8.7.json", overlay_path=C8 / "overlay.v0.4.json")
V01 = {}
for f in ("questions.public.jsonl", "safety/track.v0.3.jsonl"):
    for l in open(f"<workspace>/boar-eval/bench/v0.1/{f}"): q = json.loads(l); V01[q["id"]] = q
for l in open("<workspace>/rnd/research/compass/exp/bounty-eval/bench-vslice/questions.jsonl"): q = json.loads(l); V01.setdefault(q["id"], q)
RUNS = {("A", 42): E / "bigpack-l1/bigpack-A-s42", ("A", 43): E / "rv2-l1/rv2l1-A-s43", ("R", 42): E / "rv2-l1/rv2l1-R-s42", ("R", 43): E / "rv2-l1/rv2l1-R-s43"}
K = ("correctness", "completeness", "usefulness"); pt = lambda m: sum(m[k] for k in K) / 3
def judged(base):
    J = {}
    for part in ("v01", "vx"):
        for l in open(f"{base}.{part}.judgments.jsonl"):
            r = json.loads(l)
            if r.get("ok"): J.setdefault(r["queryId"], []).append((pt(r["mapped"]["boar"]), pt(r["mapped"]["ref"])))
    return {q: (sum(a for a, _ in v) / 2, sum(b for _, b in v) / 2) for q, v in J.items() if len(v) == 2}
tr = lambda base: {json.loads(l)["itemId"]: json.loads(l) for l in open(f"{base}.traces.jsonl")}
def retr(t): v = [float(e["ms"]) for e in t["events"] if e.get("type") == "retrieve" and e.get("ms") is not None]; return sum(v) if v else None
unsafe = lambda T: sorted(i for i, t in T.items() if i in V01 and any(h.get("status", "unsafe") == "unsafe" for h in M.check(t["answer"]["text"], M.rules_for_v085(V01[i], S), S)))
J = {k: judged(v) for k, v in RUNS.items()}; T = {k: tr(v) for k, v in RUNS.items()}
v01ids = open("<workspace>/rnd/research/sonar/exp/33-bigpack-l1/v01-en-ids.txt").read().split()
items = [q for q in v01ids if all(q in J[k] for k in J)]
mean = lambda arm, q, i: (J[(arm, 42)][q][i] + J[(arm, 43)][q][i]) / 2
rat = lambda arm, ii: sum(mean(arm, q, 0) for q in ii) / sum(mean(arm, q, 1) for q in ii)
d = rat("R", items) - rat("A", items); rng = random.Random(11); bs = []
for _ in range(2000):
    ii = [rng.choice(items) for _ in items]; bs.append(rat("R", ii) - rat("A", ii))
bs.sort(); lo, hi = bs[100], bs[1899]
KNOW = ["vx-001", "vx-002", "vit-hum-001", "vit-hum-004"]
know = {i: (round(mean("A", i, 0), 2), round(mean("R", i, 0), 2), round(mean("R", i, 0) - mean("A", i, 0), 2)) for i in KNOW}
worse = [i for i, v in know.items() if v[2] <= -1]
uA = {s_: unsafe(T[("A", s_)]) for s_ in (42, 43)}; uR = {s_: unsafe(T[("R", s_)]) for s_ in (42, 43)}
pA = statistics.median([x for s_ in (42, 43) for x in (retr(t) for t in T[("A", s_)].values()) if x is not None])
pR = statistics.median([x for s_ in (42, 43) for x in (retr(t) for t in T[("R", s_)].values()) if x is not None])
go = d >= 0.02 and lo > 0 and sum(map(len, uR.values())) <= sum(map(len, uA.values())) and not worse
kill = d <= 0 or hi < 0.02
out = {"v01_n": len(items), "ratio_A": round(rat("A", items), 4), "ratio_R": round(rat("R", items), 4), "delta": round(d, 4), "ci90": [round(lo, 4), round(hi, 4)],
       "know(A,R,delta)": know, "worse": worse, "unsafe_A": uA, "unsafe_R": uR, "retr_p50_ms": {"A": round(pA, 1), "R": round(pR, 1), "ratio": round(pR / pA, 2)},
       "verdict": "GO" if go else ("KILL" if kill else "MORE SEEDS (s44 both arms)")}
json.dump(out, open(E / "rv2-l1/rv2-verdict.json", "w"), indent=1); print(json.dumps(out, indent=1))
