#!/usr/bin/env python3
"""exp-02 kill criterion with ONE instrument on all sides: Plumb's blind hand labels.

Inputs:
  maple labels     rnd/plumb/data/hand-labels-run4-maple.json      {queryId: [class, note]}
  baseline labels  (Plumb, blind mixed file)                       {b-NNN: [class, note]}
  sealed map       rnd/kiln/exp-02-maple/blind/map-SEALED.json     {map: {b-NNN: {model, queryId, ...}}}
Classes: pass / cw / fail / refused / empty.
Kill rule (pre-registered by the coordinator): Maple is out if its % correct < Qwen3-4B's, or its cw % > Qwen3-4B's.
Reported with and without Maple's 2 empty answers (Maple reasons; the other two run with thinking off).
Usage: python3 kill-criterion.py <maple-labels.json> <baseline-labels.json> <map-SEALED.json> [out.md]
"""
import json, math, sys

maple_p, base_p, map_p = sys.argv[1:4]
out = sys.argv[4] if len(sys.argv) > 4 else None
strip = lambda d: {k: v for k, v in d.items() if not k.startswith("_")}
maple = {q: v[0] for q, v in strip(json.load(open(maple_p))).items()}
seal = json.load(open(map_p))["map"]
base = strip(json.load(open(base_p)))
labels = {"maple-preview": maple, "qwen3-4b": {}, "ling-3.0-tiny": {}}
for bid, v in base.items():
    s = seal[bid]
    labels[s["model"]][s["queryId"]] = v[0] if isinstance(v, list) else v
ids = sorted(maple)
for m, d in labels.items():
    assert set(d) == set(ids), f"{m}: ids differ ({len(d)} vs {len(ids)})"


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)


def mcnemar(a, b, qs):
    ao = [q for q in qs if a[q] == "pass" and b[q] != "pass"]
    bo = [q for q in qs if b[q] == "pass" and a[q] != "pass"]
    n, k = len(ao) + len(bo), min(len(ao), len(bo))
    p = min(1.0, 2 * sum(math.comb(n, j) for j in range(k + 1)) / 2 ** n) if n else 1.0
    return ao, bo, p


L = ["# exp-02 kill criterion: blind hand labels (Plumb) on the factual 38", ""]
empties = [q for q in ids if maple[q] == "empty"]
for tag, qs in (("all 38", ids), (f"without Maple's {len(empties)} empty answers ({', '.join(empties)})", [q for q in ids if q not in empties])):
    n = len(qs)
    L += [f"## {tag} (n={n})", "", "| Model | pass (95% CI) | cw | fail | refused | empty |", "|---|---|---:|---:|---:|---:|"]
    stats = {}
    for m, d in labels.items():
        c = lambda k: sum(d[q] == k for q in qs)
        lo, hi = wilson(c("pass"), n)
        stats[m] = (c("pass") / n, c("cw") / n)
        L.append(f"| {m} | {c('pass')}/{n} = {c('pass')/n:.0%} ({lo:.0%}–{hi:.0%}) | {c('cw')} | {c('fail')} | {c('refused')} | {c('empty')} |")
    L.append("")
    for other in ("qwen3-4b", "ling-3.0-tiny"):
        ao, bo, p = mcnemar(labels["maple-preview"], labels[other], qs)
        L.append(f"- Maple vs {other}: Maple-only pass {len(ao)} {ao}; {other}-only pass {len(bo)} {bo}; exact McNemar p = {p:.2f}")
    ao, bo, p = mcnemar(labels["ling-3.0-tiny"], labels["qwen3-4b"], qs)
    L.append(f"- Ling vs qwen3-4b: Ling-only {len(ao)}; 4B-only {len(bo)}; p = {p:.2f}")
    mp, mc = stats["maple-preview"]; qp, qc = stats["qwen3-4b"]
    killed = mp < qp or mc > qc
    L += ["", f"**Kill rule ({tag}):** Maple pass {mp:.0%} vs 4B {qp:.0%}; Maple cw {mc:.0%} vs 4B {qc:.0%} → "
          f"**{'KILLED' if killed else 'SURVIVES'}**" + (f" ({'pass lower' if mp < qp else ''}{' and ' if mp < qp and mc > qc else ''}{'cw higher' if mc > qc else ''})" if killed else ""), ""]
text = "\n".join(L) + "\n"
print(text)
if out:
    open(out, "w").write(text)
