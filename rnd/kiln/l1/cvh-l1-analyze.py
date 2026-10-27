#!/usr/bin/env python3
"""CVH v0.1 EN L1 read-out (criterion arms/cvh/CVH-criterion.md): cut 3 verdicts rebuilt exactly as cut3-confirm-analyze.py (cut 2 judge.v1-med verdicts reused for byte-identical items,
vgar/new for the 5 changed), CVH verdicts = cut 3's for byte-identical answers, new judge.v1-med for the changed ones. Two-level paired bootstrap CI90 (2000, seed 11)."""
import json, random, importlib.util
from pathlib import Path
B = Path("<workspace>"); E = B / "boar-eval/runs/kiln"; D = E / "cut3-confirm"; V = E / "cut3-vgar-l1"; OV = E / "overnight"; C = E / "cvh-l1"
SEEDS = (44, 45); K = ("correctness", "completeness", "usefulness")
tr = lambda p: {t["itemId"]: t for t in (json.loads(l) for l in open(p) if l.strip())}
def jud(p):
    J = {}
    if not Path(p).exists(): return J
    for l in open(p):
        r = json.loads(l)
        if r.get("ok"): J.setdefault(r["queryId"], []).append(r["mapped"])
    return {q: v for q, v in J.items() if len(v) == 2}
BENCH = {json.loads(l)["id"]: json.loads(l) for l in open(B / "boar-eval/bench/v0.1/questions.public.jsonl")}
T = {}; J = {}
for s in SEEDS:
    T["c", s] = tr(V / f"cut2-v01-s{s}.traces.jsonl"); T["v", s] = tr(V / f"vgar-v01-s{s}.traces.jsonl"); T["x", s] = tr(D / f"cut3-v01-s{s}.traces.jsonl"); T["y", s] = tr(C / f"cvh-v01-s{s}.traces.jsonl")
txt = lambda a, s, i: T[a, s][i]["answer"]["text"]
JV = {s: jud(V / f"vgar-v01-s{s}.judgments.v1-med.jsonl") for s in SEEDS}
for s in SEEDS:
    J["c", s] = jud(OV / f"ov-cut2-v01-s{s}.judgments.v1-med.jsonl"); JN = jud(D / f"cut3-v01-s{s}.judgments.v1-med.jsonl"); J["x", s] = {}
    for q, v in J["c", s].items():
        if txt("x", s, q) == txt("c", s, q): J["x", s][q] = v
        elif txt("x", s, q) == txt("v", s, q) and q in JV[s]: J["x", s][q] = JV[s][q]
        else: J["x", s][q] = JN[q]
    JY = jud(C / f"cvh-v01-s{s}.judgments.v1-med.jsonl"); J["y", s] = {}
    for q, v in J["x", s].items():
        if txt("y", s, q) == txt("x", s, q): J["y", s][q] = v
        else: J["y", s][q] = JY[q]
items = sorted(set.intersection(*(set(v) for v in J.values())))
pt = lambda m: sum(m[k] for k in K) / 3
sc = {(a, s, q): (sum(pt(m["boar"]) for m in J[a, s][q]) / 2, sum(pt(m["ref"]) for m in J[a, s][q]) / 2) for a in "xy" for s in SEEDS for q in items}
rub = lambda a, q: sum(sc[a, s, q][0] for s in SEEDS) / 2
ratio = lambda a, draw: sum(sc[a, s, q][0] for q, s in draw) / sum(sc[a, s, q][1] for q, s in draw)
full = [(q, s) for q in items for s in SEEDS]; d = ratio("y", full) - ratio("x", full)
rng = random.Random(11); bs = []
for _ in range(2000):
    draw = [(q, rng.choice(SEEDS)) for q in (rng.choice(items) for _ in items) for _ in SEEDS]
    bs.append(ratio("y", draw) - ratio("x", draw))
bs.sort()
changed = sorted({q for s in SEEDS for q in items if txt("y", s, q) != txt("x", s, q)})
print(f"n judged items {len(items)}; changed vs cut 3: {changed}")
for q in changed:
    seeds = [s for s in SEEDS if txt("y", s, q) != txt("x", s, q)]
    print(f"  {q} seeds {seeds}: cut3 {rub('x', q):.3f} -> CVH {rub('y', q):.3f}  delta {rub('y', q) - rub('x', q):+.3f}")
print("per-seed per-item boar rubric:")
for q in changed:
    print("  ", q, {s: (round(sc['x', s, q][0], 2), round(sc['y', s, q][0], 2)) for s in SEEDS})
print(f"ratio cut3 {ratio('x', full):.4f}  CVH {ratio('y', full):.4f}  delta {d:+.4f}  CI90 [{bs[100]:+.4f}, {bs[1899]:+.4f}]")
cw = {(a, s): [q for q in items if sum(m["correctness"] for m in (n["boar"] for n in J[a, s][q])) / 2 <= 1.0] for a in "xy" for s in SEEDS}
print("confident-wrong (mean correctness <= 1.0):", {f"{'cut3' if a == 'x' else 'CVH'} s{s}": len(cw[a, s]) for a in "xy" for s in SEEDS})
for s in SEEDS: print(f"  s{s} cut3 {cw['x', s]}  CVH {cw['y', s]}")
drops = [q for q in changed if rub("y", q) - rub("x", q) <= -1.0]
print("changed items down >= 1.0:", drops)
# safety v0.9.1
def mod(p, n):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
D91 = B / "rnd/research/compass/exp/safety-v091"; sc91 = mod(D91 / "safety_check.v0.9.1.py", "sc91")
S91 = sc91.load(rules_path=D91 / "rules.v0.9.1.json", overlay_path=D91 / "overlay.v0.4.json")
for a, name in (("x", "cut3"), ("y", "CVH")):
    for s in SEEDS:
        uns = []
        for i, t in T[a, s].items():
            q = dict(BENCH[i]); rules = sc91.rules_for_v085(q, S91)
            h = sc91.check(t["answer"]["text"], rules, S91) if rules else []
            if any(x.get("status", "unsafe") == "unsafe" for x in h): uns.append(i)
        print(f"safety v0.9.1 {name} s{s}: unsafe {len(uns)} {uns}")
# routed items (answer:cv-hint) and added time (desktop proxy: CVH totalMs minus cut 3 totalMs, same item and seed)
import statistics
hinted = {s: sorted(i for i, t in T["y", s].items() if "answer:cv-hint" in t["route"]["reasonCodes"]) for s in SEEDS}
print("routed (answer:cv-hint):", hinted)
print("changed but not hinted:", {s: [q for q in items if txt("y", s, q) != txt("x", s, q) and q not in hinted[s]] for s in SEEDS})
print("hinted but byte-identical:", {s: [q for q in hinted[s] if txt("y", s, q) == txt("x", s, q)] for s in SEEDS})
dt = [(s, q, T["y", s][q]["timing"]["totalMs"] - T["x", s][q]["timing"]["totalMs"]) for s in SEEDS for q in hinted[s]]
for s, q, d_ in dt: print(f"  time {q} s{s}: cut3 {T['x', s][q]['timing']['totalMs']/1000:.2f}s CVH {T['y', s][q]['timing']['totalMs']/1000:.2f}s diff {d_/1000:+.2f}s")
if dt: print(f"median added time on routed items: {statistics.median(d_ for _, _, d_ in dt)/1000:+.2f} s (n={len(dt)})")
allt = [T["y", s][q]["timing"]["totalMs"] - T["x", s][q]["timing"]["totalMs"] for s in SEEDS for q in T["x", s]]
print(f"median diff over all 120 items: {statistics.median(allt)/1000:+.2f} s")
print("hint present in text of hinted items?", {s: [("computed check" in txt('y', s, q)) for q in hinted[s]] for s in SEEDS})
for s in SEEDS:
    for q in hinted[s]:
        print(f"--- {q} s{s}\n CUT3: {txt('x', s, q)[:700]!r}\n CVH: {txt('y', s, q)[:700]!r}")
