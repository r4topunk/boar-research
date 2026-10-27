#!/usr/bin/env python3
"""k3-on-cut2 read-out (rnd/research/coordinator/k3-criterion.md 7d8fcd81). Usage: k3-analyze.py [--no-judge]
Deterministic gates (unsafe, prompt tokens) + descriptive timers/contexts; with judgments: Δ, two-level paired bootstrap CI90, cw."""
import json, random, statistics, sys, importlib.util
from pathlib import Path
E = Path("<workspace>/boar-eval/runs/kiln"); D = E / "k3-on-cut2"; OV = E / "overnight"
SEEDS = (44, 45); GEN = "generate:user-model-qwen3-4b-instruct-2507-q4km"
tr = lambda p: {t["itemId"]: t for t in (json.loads(l) for l in open(p) if l.strip())}
T = {("c", s): tr(D / f"cut2-v01-s{s}.traces.jsonl") for s in SEEDS} | {("k", s): tr(D / f"k3-v01-s{s}.traces.jsonl") for s in SEEDS}
out = {}
# prompt tokens on the 4B answer path, paired by (item, seed)
on = lambda t: GEN in t["route"]["reasonCodes"] and t["timing"].get("promptTokens") is not None
pairs = [(T["c", s][i]["timing"]["promptTokens"], T["k", s][i]["timing"]["promptTokens"], i, s) for s in SEEDS for i in T["c", s] if i in T["k", s] and on(T["c", s][i]) and on(T["k", s][i])]
mc, mk = statistics.mean(p[0] for p in pairs), statistics.mean(p[1] for p in pairs)
k4 = lambda t: any(e.get("type") == "retrieve" and e.get("k") == 4 for e in t["events"])
nl = [p for p in pairs if k4(T["c", p[3]][p[2]])]
out["prompt_tokens"] = {"n_pairs": len(pairs), "cut2": round(mc, 1), "k3": round(mk, 1), "saved": round(mc - mk, 1),
                        "non_lookup_n": len(nl), "non_lookup_saved": round(statistics.mean(p[0] - p[1] for p in nl), 1) if nl else None,
                        "pairs_changed": sum(p[0] != p[1] for p in pairs)}
ctx = lambda t: tuple(x.get("title") for x in (t.get("retrieval") or {}).get("kept") or [])
out["kept_ctx_changed"] = {s: sorted(i for i in T["c", s] if ctx(T["c", s][i]) != ctx(T["k", s][i])) for s in SEEDS}
out["route_changed"] = {s: sorted(i for i in T["c", s] if (T["c", s][i]["route"]["task"], T["c", s][i]["route"]["tier"]) != (T["k", s][i]["route"]["task"], T["k", s][i]["route"]["tier"])) for s in SEEDS}
def pct(v, p): v = sorted(x for x in v if x is not None); return round(v[min(len(v) - 1, int(p * len(v)))]) if v else None
out["timers_desktop"] = {a: {m: (pct([t["timing"].get(m) for s in SEEDS for t in T[a, s].values() if on(t)], .5), pct([t["timing"].get(m) for s in SEEDS for t in T[a, s].values() if on(t)], .9))
                             for m in ("prefillMs", "ttftMs", "totalMs")} for a in ("c", "k")}
if "--no-judge" not in sys.argv:
    K = ("correctness", "completeness", "usefulness"); pt = lambda m: sum(m[k] for k in K) / 3
    def jud(p):
        J = {}
        for l in open(p):
            r = json.loads(l)
            if r.get("ok"): J.setdefault(r["queryId"], []).append(r["mapped"])
        return {q: v for q, v in J.items() if len(v) == 2}
    J = {("c", s): jud(OV / f"ov-cut2-v01-s{s}.judgments.v1-med.jsonl") for s in SEEDS} | {("k", s): jud(D / f"k3-v01-s{s}.judgments.v1-med.jsonl") for s in SEEDS}
    items = sorted(set.intersection(*(set(v) for v in J.values())))
    sc = {(a, s, q): (sum(pt(m["boar"]) for m in J[a, s][q]) / 2, sum(pt(m["ref"]) for m in J[a, s][q]) / 2) for a in "ck" for s in SEEDS for q in items}
    def ratio(a, draw):  # draw = list of (item, seed)
        return sum(sc[a, s, q][0] for q, s in draw) / sum(sc[a, s, q][1] for q, s in draw)
    full = [(q, s) for q in items for s in SEEDS]; d = ratio("k", full) - ratio("c", full)
    rng = random.Random(11); bs = []
    for _ in range(2000):
        draw = [(q, rng.choice(SEEDS)) for q in (rng.choice(items) for _ in items) for _ in SEEDS]
        bs.append(ratio("k", draw) - ratio("c", draw))
    bs.sort()
    cw = {(a, s): sorted(q for q in items if sum(m["boar"]["correctness"] for m in J[a, s][q]) / 2 <= 1.0) for a in "ck" for s in SEEDS}
    per = {q: round(sum(sc["k", s, q][0] - sc["c", s, q][0] for s in SEEDS) / 2, 2) for q in items}
    out["judge"] = {"n_items": len(items), "ratio_cut2": round(ratio("c", full), 4), "ratio_k3": round(ratio("k", full), 4), "delta": round(d, 4),
                    "ci90": [round(bs[100], 4), round(bs[1899], 4)], "per_seed_ratio": {f"{a}{s}": round(ratio(a, [(q, s) for q in items]), 4) for a in "ck" for s in SEEDS},
                    "cw": {f"{a}{s}": len(cw[a, s]) for a in "ck" for s in SEEDS}, "cw_new": {s: sorted(set(cw["k", s]) - set(cw["c", s])) for s in SEEDS},
                    "biggest_moves": sorted(((v, q) for q, v in per.items() if abs(v) >= 0.5), key=lambda x: x[0])}
print(json.dumps(out, indent=1))
