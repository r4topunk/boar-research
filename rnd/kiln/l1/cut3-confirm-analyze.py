#!/usr/bin/env python3
"""cut 3 confirmation read-out (rnd/research/coordinator/cut3-confirm-criterion.md fdd06c4a). Usage: cut3-confirm-analyze.py [--plan]
--plan: identity check vs the cut3-vgar arm + the (item, seed) list that needs new judge.v1-med verdicts. Otherwise: (a) gates + ratio."""
import json, random, sys
from pathlib import Path
E = Path("<workspace>/boar-eval/runs/kiln"); D = E / "cut3-confirm"; V = E / "cut3-vgar-l1"; OV = E / "overnight"
SEEDS = (44, 45)
BENCH = {json.loads(l)["id"] for l in open("<workspace>/boar-eval/bench/v0.1/questions.public.jsonl")}
tr = lambda p: {t["itemId"]: t for t in (json.loads(l) for l in open(p) if l.strip())}
T = {}
for s in SEEDS: T["c", s] = tr(V / f"cut2-v01-s{s}.traces.jsonl"); T["v", s] = tr(V / f"vgar-v01-s{s}.traces.jsonl"); T["x", s] = tr(D / f"cut3-v01-s{s}.traces.jsonl")
txt = lambda a, s, i: T[a, s][i]["answer"]["text"]
vg = lambda s, i: [c for c in T["x", s][i]["route"]["reasonCodes"] if c.startswith("verdict-guard:")]
ident = {s: [] for s in SEEDS}; unexpl = []
for s in SEEDS:
    for i in T["x", s]:
        if txt("x", s, i) != txt("v", s, i):
            why = "dng-001 (SBt)" if i == "dng-001" else ("VG v3 vs v1" if vg(s, i) or [c for c in T["v", s][i]["route"]["reasonCodes"] if c.startswith("verdict-guard:")] else "UNEXPLAINED")
            ident[s].append((i, why))
            if why == "UNEXPLAINED": unexpl.append((s, i))
changed = {s: sorted(i for i in T["x", s] if txt("x", s, i) != txt("c", s, i)) for s in SEEDS}
reuse = {s: sorted(i for i in changed[s] if txt("x", s, i) == txt("v", s, i) and i in changed and True) for s in SEEDS}
def jud(p):
    J = {}
    if not p.exists(): return J
    for l in open(p):
        r = json.loads(l)
        if r.get("ok"): J.setdefault(r["queryId"], []).append(r["mapped"])
    return {q: v for q, v in J.items() if len(v) == 2}
JV = {s: jud(V / f"vgar-v01-s{s}.judgments.v1-med.jsonl") for s in SEEDS}
need = {s: sorted(i for i in changed[s] if i in BENCH and not (txt("x", s, i) == txt("v", s, i) and i in JV[s])) for s in SEEDS}
out = {"diff_vs_vgar_arm": ident, "unexplained": unexpl, "changed_vs_cut2": changed, "not_in_judged_bench": {s: [i for i in changed[s] if i not in BENCH] for s in SEEDS}, "need_new_verdicts": need}
if "--plan" in sys.argv: print(json.dumps(out, indent=1)); sys.exit()
K = ("correctness", "completeness", "usefulness"); pt = lambda m: sum(m[k] for k in K) / 3
J = {}
for s in SEEDS:
    J["c", s] = jud(OV / f"ov-cut2-v01-s{s}.judgments.v1-med.jsonl"); JN = jud(D / f"cut3-v01-s{s}.judgments.v1-med.jsonl")
    J["x", s] = {}
    for q, v in J["c", s].items():
        if q not in changed[s]: J["x", s][q] = v; continue
        src = JN.get(q) if q in need[s] else JV[s].get(q)
        assert src, f"missing verdict s{s} {q}"; J["x", s][q] = src
items = sorted(set.intersection(*(set(v) for v in J.values())))
sc = {(a, s, q): (sum(pt(m["boar"]) for m in J[a, s][q]) / 2, sum(pt(m["ref"]) for m in J[a, s][q]) / 2) for a in "cx" for s in SEEDS for q in items}
rub = lambda a, q: sum(sc[a, s, q][0] for s in SEEDS) / 2
ratio = lambda a, draw: sum(sc[a, s, q][0] for q, s in draw) / sum(sc[a, s, q][1] for q, s in draw)
full = [(q, s) for q in items for s in SEEDS]; d = ratio("x", full) - ratio("c", full)
rng = random.Random(11); bs = []
for _ in range(2000):
    draw = [(q, rng.choice(SEEDS)) for q in (rng.choice(items) for _ in items) for _ in SEEDS]
    bs.append(ratio("x", draw) - ratio("c", draw))
bs.sort()
ch = sorted(set(changed[44]) | set(changed[45]))
table = [{"id": q, "seeds": [s for s in SEEDS if q in changed[s]], "verdicts": {s: ("new" if q in need[s] else "reused-vgar") for s in SEEDS if q in changed[s]},
          "cut2": round(rub("c", q), 3), "cut3": round(rub("x", q), 3), "delta": round(rub("x", q) - rub("c", q), 3)} if q in items else {"id": q, "not_judged": True} for q in ch]
cw = {(a, s): sum(1 for q in items if sum(m["boar"]["correctness"] for m in J[a, s][q]) / 2 <= 1.0) for a in "cx" for s in SEEDS}
out["a"] = {"n_items": len(items), "ratio_cut2": round(ratio("c", full), 4), "ratio_cut3": round(ratio("x", full), 4), "delta": round(d, 4), "ci90": [round(bs[100], 4), round(bs[1899], 4)],
            "per_seed": {f"{a}{s}": round(ratio(a, [(q, s) for q in items]), 4) for a in "cx" for s in SEEDS}, "cw": {f"{a}{s}": cw[a, s] for a in "cx" for s in SEEDS},
            "table": table, "drops_ge_1": [r["id"] for r in table if r.get("delta", 0) <= -1.0]}
print(json.dumps(out, indent=1))
