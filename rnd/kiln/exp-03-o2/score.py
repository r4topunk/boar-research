#!/usr/bin/env python3
"""Score an O2 variant against the hand labels: what the rule would change if it declined the flagged answers.

Input: inputs.jsonl (build_inputs.py) + a decisions jsonl {src, model, queryId, o2Decline: bool, why}.
An answer the rule declines becomes "refused" (the app shows its decline message). Rows the app already declined stay
declined. Everything else keeps its hand label.

Per (src, model) group, before vs after:
- cw → refused   (the goal: confident-wrong answers removed)
- pass → refused (the cost: new false refusals)
- fail → refused (neutral for pass/cw; a vague answer becomes an honest decline)
- pass% / cw% / refused% and the paired ±5 pp rule (coordinator, hypotheses.md §3b), with the rule applied the
  other way round for a filter: the variant is KEPT only if pass drops ≤ 5 pp; the gain is the cw drop.
Usage: python3 score.py inputs.jsonl decisions.jsonl [out.md] [--label NAME]
"""
import json, math, sys
from collections import defaultdict

inp, dec = sys.argv[1], sys.argv[2]
out = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else None
name = sys.argv[sys.argv.index("--label") + 1] if "--label" in sys.argv else dec
rows = [json.loads(l) for l in open(inp)]
D = {(d["src"], d["model"], d["queryId"]): d for d in map(json.loads, open(dec))}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0, 0)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)


def exact_mcnemar(b, c):
    n, k = b + c, min(b, c)
    return min(1.0, 2 * sum(math.comb(n, j) for j in range(k + 1)) / 2 ** n) if n else 1.0


REF = ("refused", "declined")
groups = defaultdict(list)
for r in rows:
    d = D.get((r["src"], r["model"], r["queryId"]))
    after = r["label"]
    if r["label"] not in REF and d and d["o2Decline"]:
        after = "refused"
    groups[(r["src"], r["model"])].append((r, r["label"], after, d))

L = [f"# O2 variant: {name}", "",
     "| Group | n | flagged | cw→refused | pass→refused (new false refusal) | fail→refused | pass before → after | cw before → after | refused before → after | Δpass pp | Δcw pp | McNemar p (pass) | ±5 pp |",
     "|---|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---|"]
tot = defaultdict(int)
detail = []
for (src, model), g in sorted(groups.items()):
    n = len(g)
    cnt = lambda idx, labs: sum(x[idx] in labs for x in g)
    pb, pa = cnt(1, ("pass",)), cnt(2, ("pass",))
    cb, ca = cnt(1, ("cw",)), cnt(2, ("cw",))
    rb, ra = cnt(1, REF), cnt(2, REF)
    flagged = sum(1 for x in g if x[3] and x[3]["o2Decline"] and x[1] not in REF)
    cw2r = sum(1 for x in g if x[1] == "cw" and x[2] == "refused")
    p2r = sum(1 for x in g if x[1] == "pass" and x[2] == "refused")
    f2r = sum(1 for x in g if x[1] in ("fail", "empty") and x[2] == "refused")
    dp, dc = 100 * (pa - pb) / n, 100 * (ca - cb) / n
    verdict = "keep" if dp >= -5 else "REJECT (pass −>5 pp)"
    L.append(f"| {src} {model} | {n} | {flagged} | {cw2r} | {p2r} | {f2r} | {pb} → {pa} | {cb} → {ca} | {rb} → {ra} | {dp:+.1f} | {dc:+.1f} | {exact_mcnemar(0, p2r):.2f} | {verdict} |")
    for k, v in (("n", n), ("flagged", flagged), ("cw2r", cw2r), ("p2r", p2r), ("f2r", f2r), ("pb", pb), ("pa", pa), ("cb", cb), ("ca", ca), ("rb", rb), ("ra", ra)):
        tot[k] += v
    for x in g:
        if x[3] and x[3]["o2Decline"] and x[1] not in REF:
            detail.append(f"| {src} | {model} | {x[0]['queryId']} | {x[1]} | {x[3].get('why', '')} |")
n = tot["n"]
L.append(f"| **all groups** | {n} | {tot['flagged']} | **{tot['cw2r']}** | **{tot['p2r']}** | {tot['f2r']} | {tot['pb']} → {tot['pa']} | {tot['cb']} → {tot['ca']} | {tot['rb']} → {tot['ra']} | "
         f"{100 * (tot['pa'] - tot['pb']) / n:+.1f} | {100 * (tot['ca'] - tot['cb']) / n:+.1f} | {exact_mcnemar(0, tot['p2r']):.2f} | "
         f"{'keep' if 100 * (tot['pa'] - tot['pb']) / n >= -5 else 'REJECT'} |")
prec = tot["cw2r"] / tot["flagged"] if tot["flagged"] else 0
rec = tot["cw2r"] / tot["cb"] if tot["cb"] else 0
L += ["", f"Flag precision for cw (cw among flagged non-declined answers): {tot['cw2r']}/{tot['flagged']} = {prec:.0%}. "
      f"Recall of cw: {tot['cw2r']}/{tot['cb']} = {rec:.0%}. Pass answers lost: {tot['p2r']}/{tot['pb']} = {tot['p2r'] / max(tot['pb'], 1):.0%}.",
      "", "## Flagged answers", "", "| src | model | id | hand label | why |", "|---|---|---|---|---|", *detail]
text = "\n".join(L) + "\n"
print(text)
if out:
    open(out, "w").write(text)
