#!/usr/bin/env python3
"""cut3-vgar stacked L1 read-out (rnd/research/coordinator/cut3-vgar-L1-criterion.md bf96feb6). Usage: cut3-vgar-analyze.py [--ids-only]
--ids-only: byte-identity check + changed ids per seed (no judgments needed). Otherwise: full gates."""
import json, random, statistics, sys
from pathlib import Path
E = Path("<workspace>/boar-eval/runs/kiln"); D = E / "cut3-vgar-l1"; OV = E / "overnight"
SEEDS = (44, 45); GEN = "generate:user-model-qwen3-4b-instruct-2507-q4km"
VG_T = ["lan-ref-003", "vit-sci-002", "lan-cmp-003"]; AR_T = ["vit-sci-003"]
tr = lambda p: {t["itemId"]: t for t in (json.loads(l) for l in open(p) if l.strip())}
T = {("c", s): tr(D / f"cut2-v01-s{s}.traces.jsonl") for s in SEEDS} | {("a", s): tr(D / f"vgar-v01-s{s}.traces.jsonl") for s in SEEDS}
kept = lambda t: tuple(x.get("title") for x in (t.get("retrieval") or {}).get("kept") or [])
comp = lambda t: sorted({"VG" for c in t["route"]["reasonCodes"] if c.startswith("verdict-guard:")} | {"AR" for c in t["route"]["reasonCodes"] if c.startswith("answer:calculator-") or c == "detector:numeric-guard"})
changed, ident_bad = {}, []
for s in SEEDS:
    C, A = T["c", s], T["a", s]; assert set(C) == set(A)
    changed[s] = sorted(i for i in C if C[i]["answer"]["text"] != A[i]["answer"]["text"])
    for i in C:
        if i in changed[s]: continue
        a, c = A[i], C[i]
        if (a["route"]["task"], a["route"]["tier"], kept(a)) != (c["route"]["task"], c["route"]["tier"], kept(c)): ident_bad.append((s, i))
attr = {s: {i: comp(T["a", s][i]) for i in changed[s]} for s in SEEDS}
codes = {s: {i: [c for c in T["a", s][i]["route"]["reasonCodes"] if c.startswith(("verdict-guard:", "answer:calculator", "detector:"))] for i in changed[s]} for s in SEEDS}
out = {"changed": changed, "attribution": attr, "codes": codes, "unchanged_answer_but_route_or_ctx_diff": ident_bad,
       "byte_identity_pass": not ident_bad, "n_unchanged": {s: 60 - len(changed[s]) for s in SEEDS}}
if "--ids-only" in sys.argv: print(json.dumps(out, indent=1)); sys.exit()
K = ("correctness", "completeness", "usefulness"); pt = lambda m: sum(m[k] for k in K) / 3
def jud(p):
    J = {}
    for l in open(p):
        r = json.loads(l)
        if r.get("ok"): J.setdefault(r["queryId"], []).append(r["mapped"])
    return {q: v for q, v in J.items() if len(v) == 2}
J = {("c", s): jud(OV / f"ov-cut2-v01-s{s}.judgments.v1-med.jsonl") for s in SEEDS}
for s in SEEDS:
    new = jud(D / f"vgar-v01-s{s}.judgments.v1-med.jsonl"); miss = [i for i in changed[s] if i in J["c", s] and i not in new]
    assert not miss, f"unjudged changed items s{s}: {miss}"
    J["a", s] = {q: (new[q] if q in changed[s] else v) for q, v in J["c", s].items()}
items = sorted(set.intersection(*(set(v) for v in J.values())))
sc = {(a, s, q): (sum(pt(m["boar"]) for m in J[a, s][q]) / 2, sum(pt(m["ref"]) for m in J[a, s][q]) / 2) for a in "ca" for s in SEEDS for q in items}
corr = {(a, s, q): sum(m["boar"]["correctness"] for m in J[a, s][q]) / 2 for a in "ca" for s in SEEDS for q in items}
rub = lambda a, q: sum(sc[a, s, q][0] for s in SEEDS) / 2
ratio = lambda a, draw: sum(sc[a, s, q][0] for q, s in draw) / sum(sc[a, s, q][1] for q, s in draw)
full = [(q, s) for q in items for s in SEEDS]; d = ratio("a", full) - ratio("c", full)
rng = random.Random(11); bs = []
for _ in range(2000):
    draw = [(q, rng.choice(SEEDS)) for q in (rng.choice(items) for _ in items) for _ in SEEDS]
    bs.append(ratio("a", draw) - ratio("c", draw))
bs.sort()
ch_items = sorted(set(changed[44]) | set(changed[45]))
table = []
for q in ch_items:
    comps = sorted(set(x for s in SEEDS for x in attr[s].get(q, [])))
    table.append({"id": q, "seeds_changed": [s for s in SEEDS if q in changed[s]], "components": comps, "codes": sorted(set(c for s in SEEDS for c in codes[s].get(q, []))),
                  "ctl": round(rub("c", q), 3), "arm": round(rub("a", q), 3), "delta": round(rub("a", q) - rub("c", q), 3),
                  "ctl_seeds": [round(sc["c", s, q][0], 2) for s in SEEDS], "arm_seeds": [round(sc["a", s, q][0], 2) for s in SEEDS],
                  "ratio_ctl": round(sum(sc["c", s, q][0] for s in SEEDS) / sum(sc["c", s, q][1] for s in SEEDS), 3),
                  "ratio_arm": round(sum(sc["a", s, q][0] for s in SEEDS) / sum(sc["a", s, q][1] for s in SEEDS), 3)} if q in items else {"id": q, "not_judged_bench_item": True})
T_ = {r["id"]: r for r in table}
drops = [r for r in table if r.get("delta", 0) <= -1.0]
def comp_gate(name, targets):
    tgt = {q: (T_[q]["delta"] if q in T_ and "delta" in T_[q] else 0.0) for q in targets}
    own_drops = [r["id"] for r in drops if name in r["components"] or not r["components"]]
    return {"targets": tgt, "targets_pass": all(v >= 1.0 for v in tgt.values()), "drops_charged": own_drops, "pass": all(v >= 1.0 for v in tgt.values()) and not own_drops}
cw = {(a, s): sorted(q for q in items if corr[a, s, q] <= 1.0) for a in "ca" for s in SEEDS}
out["judge"] = {"n_items": len(items), "ratio_ctl": round(ratio("c", full), 4), "ratio_arm": round(ratio("a", full), 4), "delta": round(d, 4), "ci90": [round(bs[100], 4), round(bs[1899], 4)],
                "per_seed": {f"{a}{s}": round(ratio(a, [(q, s) for q in items]), 4) for a in "ca" for s in SEEDS},
                "cw": {f"{a}{s}": cw[a, s] for a in "ca" for s in SEEDS}, "cw_total": {"ctl": len(cw["c", 44]) + len(cw["c", 45]), "arm": len(cw["a", 44]) + len(cw["a", 45])},
                "VG": comp_gate("VG", VG_T), "AR": comp_gate("AR", AR_T), "table": table}
on = lambda t: GEN in t["route"]["reasonCodes"]
def pct(v, p): v = sorted(x for x in v if x is not None); return round(v[min(len(v) - 1, int(p * len(v)))]) if v else None
out["timers_desktop"] = {a: {m: (pct([t["timing"].get(m) for s in SEEDS for t in T[a, s].values() if on(t)], .5), pct([t["timing"].get(m) for s in SEEDS for t in T[a, s].values() if on(t)], .9)) for m in ("prefillMs", "ttftMs", "totalMs")} for a in "ca"}
out["timers_changed"] = {f"{q}/s{s}": {a: {m: round(T[a, s][q]["timing"].get(m) or 0) for m in ("ttftMs", "totalMs")} for a in "ca"} for s in SEEDS for q in changed[s]}
print(json.dumps(out, indent=1))
