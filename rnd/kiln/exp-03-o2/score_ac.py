#!/usr/bin/env python3
"""exp-03: O2 variant A (refuse) vs C (flag) per configuration, scored with Plumb's hand labels.

Decisions come unchanged from Lantern's tools/o2_eval.py (reference implementation of the accepted spec), run over
inputs.jsonl and saved as results/decisions-refA.jsonl. O2 hits are the rows with o2Decline = true.

Scoring convention (coordinator, 2026-09-30):
- A (refuse): an O2 hit becomes "refused", whatever its label.
- C (flag, "Not in your offline sources, from the model's general knowledge:"): a hit on a cw answer becomes "flagged"
  (counts neither as cw nor as pass). A hit on a pass answer stays "pass" (reported separately as pass-flagged, a UX
  cost). A hit on fail/empty stays as it was (reported as other-flagged).
- Rows the app already declined stay "refused".
±5 pp rule per config, paired against the same config without O2 (spec §5.2):
  A4: Δpass ≥ −5 pp;  A5: Δcw ≤ −5 pp (the gain must exceed noise).  Exact McNemar on pass (paired).
Usage: python3 score_ac.py inputs.jsonl results/decisions-refA.jsonl [out.md] [--configs H1:qwen3-4b,P3:qwen2.5-1.5b@iphone,...]
"""
import json, math, sys

inp, dec = sys.argv[1], sys.argv[2]
out = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else None
cfgs = [tuple(c.split(":", 1)) for c in (sys.argv[sys.argv.index("--configs") + 1] if "--configs" in sys.argv else
        "H1:qwen3-4b,P3:qwen2.5-1.5b@iphone").split(",")]
rows = [json.loads(l) for l in open(inp)]
D = {(d["src"], d["model"], d["queryId"]): d for d in map(json.loads, open(dec))}
REF = ("refused", "declined")


def mcnemar(b, c):
    n, k = b + c, min(b, c)
    return min(1.0, 2 * sum(math.comb(n, j) for j in range(k + 1)) / 2 ** n) if n else 1.0


def outcome(label, hit, variant):
    if label in REF:
        return "refused"
    if not hit:
        return label
    if variant == "A":
        return "refused"
    return "flagged" if label == "cw" else label


L = ["# exp-03: O2 variant A (refuse) vs C (flag), per configuration, hand labels", "",
     "| Config | Variant | n | O2 hits | pass | cw | flagged | refused | fail/empty | Δpass pp (A4 ≥ −5) | Δcw pp (A5 ≤ −5) | pass lost (McNemar p) | pass-flagged (UX cost) | Verdict |",
     "|---|---|---:|---:|---|---|---:|---|---:|---:|---:|---|---:|---|"]
summary = {}
for src, model in cfgs:
    g = [r for r in rows if r["src"] == src and r["model"] == model]
    n = len(g)
    hits = {r["queryId"] for r in g if D.get((src, model, r["queryId"]), {}).get("o2Decline") and r["label"] not in REF}
    base = {r["queryId"]: outcome(r["label"], False, "A") for r in g}
    c = lambda o, k: sum(v == k for v in o.values())
    pb, cb, rb = c(base, "pass"), c(base, "cw"), c(base, "refused")
    for var in ("A", "C"):
        o = {r["queryId"]: outcome(r["label"], r["queryId"] in hits, var) for r in g}
        pa, ca, fa, ra = c(o, "pass"), c(o, "cw"), c(o, "flagged"), c(o, "refused")
        other = sum(v in ("fail", "empty") for v in o.values())
        lost = sum(1 for q in o if base[q] == "pass" and o[q] != "pass")
        pflag = sum(1 for r in g if var == "C" and r["queryId"] in hits and r["label"] == "pass")
        dp, dc = 100 * (pa - pb) / n, 100 * (ca - cb) / n
        a4, a5 = dp >= -5, dc <= -5
        verdict = "PASS (A4+A5)" if a4 and a5 else ("A4 only: safe, gain below noise" if a4 else "FAIL A4 (pass −>5 pp)")
        summary[(src, model, var)] = dict(n=n, hits=len(hits), pass_=(pb, pa), cw=(cb, ca), flagged=fa, refused=(rb, ra), dp=dp, dc=dc, lost=lost, pflag=pflag, verdict=verdict)
        L.append(f"| {src} {model} | {var} | {n} | {len(hits)} | {pb} → {pa} | {cb} → {ca} | {fa} | {rb} → {ra} | {other} | {dp:+.1f} | {dc:+.1f} | {lost} (p={mcnemar(0, lost):.2f}) | {pflag} | {verdict} |")
hitlist = ["", "## O2 hits per config (hand label → A / C outcome)", "", "| Config | id | hand label | A | C | reference reason |", "|---|---|---|---|---|---|"]
for src, model in cfgs:
    for r in rows:
        d = D.get((src, model, r["queryId"]))
        if r["src"] == src and r["model"] == model and d and d["o2Decline"] and r["label"] not in REF:
            hitlist.append(f"| {src} {model} | {r['queryId']} | {r['label']} | {outcome(r['label'], True, 'A')} | {outcome(r['label'], True, 'C')} | {d.get('why', '')} |")
text = "\n".join(L + hitlist) + "\n"
print(text)
if out:
    open(out, "w").write(text)
