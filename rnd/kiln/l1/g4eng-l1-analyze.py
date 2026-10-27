#!/usr/bin/env python3
"""G4ENG L1 read-out (criterion arms/g4eng/G4ENG-criterion.md): same-day cut 3 control (ctl, Qwen3-4B) vs G4ENG (Gemma 4 E4B), s44+s45, ALL judged (judge.v1-med, both orders).
Paired ratio delta with two-level bootstrap CI90 (2000, seed 11), unsafe (safety v0.9.1), cw, time p50, empties/leaks, route-code identity."""
import json, random, re, statistics, importlib.util
from pathlib import Path
B = Path("<workspace>"); C = B / "boar-eval/runs/kiln/g4eng-l1"; SEEDS = (44, 45); K = ("correctness", "completeness", "usefulness")
tr = lambda p: {t["itemId"]: t for t in (json.loads(l) for l in open(p) if l.strip())}
def jud(p):
    J = {}
    for l in open(p):
        r = json.loads(l)
        if r.get("ok"): J.setdefault(r["queryId"], []).append(r["mapped"])
    return {q: v for q, v in J.items() if len(v) == 2}
BENCH = {json.loads(l)["id"]: json.loads(l) for l in open(B / "boar-eval/bench/v0.1/questions.public.jsonl")}
A = {"x": "ctl", "y": "g4eng"}; NAME = {"x": "cut3 (Qwen3-4B)", "y": "G4ENG (Gemma 4 E4B)"}
T = {(a, s): tr(C / f"{A[a]}-v01-s{s}.traces.jsonl") for a in "xy" for s in SEEDS}
J = {(a, s): jud(C / f"{A[a]}-v01-s{s}.judgments.v1-med.jsonl") for a in "xy" for s in SEEDS}
items = sorted(set.intersection(*(set(v) for v in J.values())))
pt = lambda m: sum(m[k] for k in K) / 3
sc = {(a, s, q): (sum(pt(m["boar"]) for m in J[a, s][q]) / 2, sum(pt(m["ref"]) for m in J[a, s][q]) / 2) for a in "xy" for s in SEEDS for q in items}
ratio = lambda a, draw: sum(sc[a, s, q][0] for q, s in draw) / sum(sc[a, s, q][1] for q, s in draw)
full = [(q, s) for q in items for s in SEEDS]
print(f"n judged items {len(items)} (both arms, both seeds)")
for a in "xy": print(f"ratio {NAME[a]}: {ratio(a, full):.4f}  per seed " + ", ".join(f"s{s} {ratio(a, [(q, s) for q in items]):.4f}" for s in SEEDS))
d = ratio("y", full) - ratio("x", full)
rng = random.Random(11); bs = []
for _ in range(2000):
    draw = [(q, rng.choice(SEEDS)) for q in (rng.choice(items) for _ in items) for _ in SEEDS]
    bs.append(ratio("y", draw) - ratio("x", draw))
bs.sort()
print(f"paired delta {d:+.4f}  CI90 [{bs[100]:+.4f}, {bs[1899]:+.4f}]")
cw = {(a, s): [q for q in items if sum(n["boar"]["correctness"] for n in J[a, s][q]) / 2 <= 1.0] for a in "xy" for s in SEEDS}
lab = lambda a, s: (sum(1 for q in items if sum(n["boar"]["correctness"] for n in J[a, s][q]) / 2 >= 4), sum(1 for q in items if sum(n["boar"]["correctness"] for n in J[a, s][q]) / 2 <= 2))
print("confident-wrong (mean correctness <= 1.0):", {f"{NAME[a]} s{s}": len(cw[a, s]) for a in "xy" for s in SEEDS})
print("pass(>=4) / cw(<=2) per arm-seed:", {f"{A[a]} s{s}": lab(a, s) for a in "xy" for s in SEEDS})
# safety v0.9.1
def mod(p, n):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
D91 = B / "rnd/research/compass/exp/safety-v091"; sc91 = mod(D91 / "safety_check.v0.9.1.py", "sc91")
S91 = sc91.load(rules_path=D91 / "rules.v0.9.1.json", overlay_path=D91 / "overlay.v0.4.json")
for a in "xy":
    for s in SEEDS:
        uns = []
        for i, t in T[a, s].items():
            q = dict(BENCH[i]); rules = sc91.rules_for_v085(q, S91)
            h = sc91.check(t["answer"]["text"], rules, S91) if rules else []
            if any(x.get("status", "unsafe") == "unsafe" for x in h): uns.append(i)
        print(f"safety v0.9.1 {NAME[a]} s{s}: unsafe {len(uns)} {uns}")
# time
for a in "xy":
    v = [t["timing"]["totalMs"] for s in SEEDS for t in T[a, s].values()]
    print(f"total time p50 {NAME[a]}: {statistics.median(v)/1000:.2f} s (n={len(v)}, mean {statistics.mean(v)/1000:.2f})")
vx = [t["timing"]["totalMs"] for s in SEEDS for t in T["x", s].values()]; vy = [t["timing"]["totalMs"] for s in SEEDS for t in T["y", s].values()]
print(f"time p50 ratio G4ENG/cut3: {statistics.median(vy)/statistics.median(vx):.3f}")
fx = [T["x", s][q]["timing"]["totalMs"] for s in SEEDS for q in T["x", s] if "fast" == T["x", s][q]["route"]["tier"]]; fy = [T["y", s][q]["timing"]["totalMs"] for s in SEEDS for q in T["y", s] if "fast" == T["y", s][q]["route"]["tier"]]
print(f"  fast-tier-only p50 ratio {statistics.median(fy)/statistics.median(fx):.3f} (cut3 {statistics.median(fx)/1000:.2f}s, G4ENG {statistics.median(fy)/1000:.2f}s)")
for a in "xy":
    dd = [t["timing"].get("decodeTokPerSec") for s in SEEDS for t in T[a, s].values() if t["timing"].get("decodeTokPerSec")]
    print(f"  decode tok/s median {NAME[a]}: {statistics.median(dd):.1f}" if dd else "  decode n/a")
# empties / leaks
LEAK = re.compile(r"<\|?channel|channel\|>|<\|?think|</think>|<\|turn|<turn\|>|<start_of_turn|<end_of_turn|<\|?im_(start|end)|^thought\b|\bthought\n", re.I | re.M)
for a in "xy":
    emp = [(s, i) for s in SEEDS for i, t in T[a, s].items() if not t["answer"]["text"].strip() or t.get("error")]
    lk = [(s, i) for s in SEEDS for i, t in T[a, s].items() if LEAK.search(t["answer"]["text"])]
    wr = sum(1 for s in SEEDS for t in T[a, s].values() if any("think" in w or "channel" in w for w in t["answer"]["warnings"]))
    print(f"{NAME[a]}: empty/error {len(emp)} {emp}; template/channel leaks {len(lk)} {lk}; think/channel warnings {wr}")
# route-code identity
VOL = re.compile(r"^(generate:|grounding:|citations:|context:|instant:|detector:p=|route-gate:score|offer-deep)")
PATH = re.compile(r"^(answer:|places:|near:|diet:|task:|detector:fire|vg|ar:|ar-|card|calc)")
tot = 0; diffs = []; strict = 0
for s in SEEDS:
    for q in T["x", s]:
        cx = set(T["x", s][q]["route"]["reasonCodes"]); cy = set(T["y", s][q]["route"]["reasonCodes"]); tot += 1
        strict += cx == cy
        px = {c for c in cx if not VOL.match(c)}; py = {c for c in cy if not VOL.match(c)}
        if px != py: diffs.append((s, q, sorted(px ^ py)))
print(f"route codes: path-level (excluding model/grounding/context/instant/detector-prob codes) identical on {tot - len(diffs)}/{tot}; fully identical {strict}/{tot}")
for x in diffs: print("  path diff", x)
sp = {s: sorted(q for q in T["x", s] if any(c.startswith(("answer:", "places:", "near:", "diet:")) or "vg" in c or c.startswith(("ar:", "card", "calc")) for c in T["x", s][q]["route"]["reasonCodes"])) for s in SEEDS}
print("special-path items (answer:/places:/near:/diet:/vg/ar/card/calc codes in cut 3):", sp)
for s in SEEDS:
    for q in sp[s]: print(f"  s{s} {q}: cut3 text == G4ENG text: {T['x', s][q]['answer']['text'] == T['y', s][q]['answer']['text']}; outcome {T['x', s][q]['route']['outcome']}/{T['y', s][q]['route']['outcome']}")
# tiers/outcomes
for a in "xy":
    import collections
    print(NAME[a], "outcomes", dict(collections.Counter((t["route"]["tier"], t["route"]["outcome"]) for s in SEEDS for t in T[a, s].values())))
changed = sum(1 for s in SEEDS for q in T["x", s] if T["x", s][q]["answer"]["text"] != T["y", s][q]["answer"]["text"]); print("answers changed:", changed, "of", sum(len(T['x', s]) for s in SEEDS))
