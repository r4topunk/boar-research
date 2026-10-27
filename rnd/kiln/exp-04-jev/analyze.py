#!/usr/bin/env python3
"""exp-04 metrics for a predictions file (jev_judge.py output) against Plumb's hand labels.

- 4-class agreement, all rows and excluding the app's fixed-message declines (trivial).
- Binary agreement: correct vs not correct.
- confident_wrong: precision, recall, F1 (the precheck's weak point).
- Grey zone: rows whose top choice probability is in [0.35, 0.65] (a human should look), and rows with P(cw) in it.
- Confusion matrix and the list of disagreements (for the README's "where it errs").
Usage: python3 analyze.py preds/v1-tune.jsonl rows-tune.jsonl [--md out.md] [--other-preds name=path ...]
"""
import json, sys
from collections import Counter

preds_p, rows_p = sys.argv[1], sys.argv[2]
md = sys.argv[sys.argv.index("--md") + 1] if "--md" in sys.argv else None
C = ["correct", "confident_wrong", "wrong_or_incomplete_hedged", "refused"]
rows = {(r["src"], r["model"], r["queryId"]): r for r in map(json.loads, open(rows_p))}
P = [json.loads(l) for l in open(preds_p)]


def metrics(ps, label):
    n = len(ps)
    agree = sum(p["hand"] == p["jev"] for p in ps)
    bin_agree = sum((p["hand"] == "correct") == (p["jev"] == "correct") for p in ps)
    tp = sum(p["hand"] == "confident_wrong" and p["jev"] == "confident_wrong" for p in ps)
    fp = sum(p["hand"] != "confident_wrong" and p["jev"] == "confident_wrong" for p in ps)
    fn = sum(p["hand"] == "confident_wrong" and p["jev"] != "confident_wrong" for p in ps)
    prec = tp / (tp + fp) if tp + fp else None
    rec = tp / (tp + fn) if tp + fn else None
    f1 = 2 * prec * rec / (prec + rec) if prec and rec else None
    grey = sum(0.35 <= max((p.get("probs") or {"x": p.get("confidence", 1)}).values()) <= 0.65 for p in ps)
    grey_cw = sum(0.35 <= (p.get("probs") or {}).get("confident_wrong", 0) <= 0.65 for p in ps)
    f = lambda x: "—" if x is None else f"{x:.0%}"
    return (f"| {label} | {n} | {agree}/{n} = {agree / n:.0%} | {bin_agree}/{n} = {bin_agree / n:.0%} | {tp}/{tp + fp} = {f(prec)} | "
            f"{tp}/{tp + fn} = {f(rec)} | {f(f1)} | {grey} ({grey / n:.0%}) | {grey_cw} |")


L = [f"# Jev predictions `{preds_p}` vs hand labels (prompts sha256 {P[0]['prompt_sha'][:16]}…)", "",
     "| Subset | n | 4-class agreement | binary (correct vs not) | CW precision | CW recall | CW F1 | grey zone (top p 0.35-0.65) | P(cw) in grey |",
     "|---|---:|---|---|---|---|---|---|---:|"]
L.append(metrics(P, "all"))
nd = [p for p in P if not rows[(p["src"], p["model"], p["queryId"])]["app_declined"]]
if len(nd) != len(P):
    L.append(metrics(nd, "excluding app fixed-message declines"))
for g in sorted({(p["src"], p["model"]) for p in P}):
    L.append(metrics([p for p in nd if (p["src"], p["model"]) == g], f"{g[0]} {g[1]}"))
L += ["", "Confusion (rows = hand label, columns = Jev), excluding app declines:", "", "| hand \\ jev | " + " | ".join(C) + " |", "|---|" + "---|" * len(C)]
cm = Counter((p["hand"], p["jev"]) for p in nd)
for h in C:
    L.append(f"| {h} | " + " | ".join(str(cm[(h, j)]) for j in C) + " |")
usd = {}
for p in P:
    usd[(p["batch_secs"], p["batch_usd"])] = p["batch_n"]
tot_usd = sum(k[1] for k in usd)
tot_secs = sum(k[0] for k in usd)
L += ["", f"Cost {tot_usd:.5f} USD for {len(P)} items = {tot_usd / len(P) * 1e6:.1f} USD per million answers; "
      f"latency {tot_secs:.1f} s of requests ({tot_secs / len(P) * 1000:.0f} ms per item, batches of ≤ 20). "
      f"unsafe_advice: {sum(p['unsafe_p'] >= 0.5 for p in P)} rows with P ≥ 0.5.", "", "## Disagreements (excluding app declines)", "",
      "| src | model | id | hand (raw) | jev | p(jev) | p(cw) | answer (start) |", "|---|---|---|---|---|---:|---:|---|"]
for p in nd:
    if p["hand"] != p["jev"]:
        r = rows[(p["src"], p["model"], p["queryId"])]
        pj = (p.get("probs") or {}).get(p["jev"])
        L.append(f"| {p['src']} | {p['model']} | {p['queryId']} | {p['hand']} ({r['hand_raw']}) | {p['jev']} | "
                 f"{pj if pj is None else round(pj, 2)} | {round((p.get('probs') or {}).get('confident_wrong', 0), 2)} | "
                 f"{r['answer'][:110].replace('|', '/').replace(chr(10), ' ')} |")
text = "\n".join(L) + "\n"
print(text)
if md:
    open(md, "w").write(text)
