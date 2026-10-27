#!/usr/bin/env python3
"""DEEPSPEED compare: reads the run outputs dir (prompts dir for rendered strings), writes items.csv, prints medians + verdicts."""
import os, re, sys, csv, statistics as st
OUT, PROMPTS, OUTCSV = sys.argv[1], sys.argv[2], sys.argv[3]
CFG = ["K0", "K1", "K2", "K3", "K4"]
items = sorted(f[:-len(".rendered.txt")] for f in os.listdir(PROMPTS) if f.endswith(".rendered.txt"))
def summ(p):
    d = {}
    if os.path.exists(p):
        for l in open(p, errors="replace"):
            if l.startswith("# summary"):
                for kv in l.split()[2:]:
                    k, _, v = kv.partition("="); d[k] = v
    return d
def fp(p):
    m = re.search(r"(\d+)\s+peak memory footprint", open(p, errors="replace").read()) if os.path.exists(p) else None
    return int(m.group(1)) / 2**30 if m else None
def wall(p):
    m = re.search(r"([\d.,]+) real", open(p, errors="replace").read()) if os.path.exists(p) else None
    return float(m.group(1).replace(",", ".")) if m else None
def text(tag, prompt):
    p = f"{OUT}/{tag}.stdout"
    if not os.path.exists(p): return None
    so = open(p, errors="replace").read()
    if not so.startswith(prompt): return None
    rest = so[len(prompt):]; i = rest.rfind("\n\ngeneration: ")
    return None if i < 0 else rest[:i].rstrip()
def ngram(tag):
    p = f"{OUT}/{tag}.stdout"
    m = re.search(r"ngram: (\d+)/(\d+) drafts accepted", open(p, errors="replace").read()) if os.path.exists(p) else None
    return (int(m.group(2)), int(m.group(1))) if m else (None, None)
rows = []
for it in items:
    prompt = open(f"{PROMPTS}/{it}.rendered.txt").read()
    base = text(f"{it}__K0", prompt)
    for k in CFG:
        tag = f"{it}__{k}"; t = text(tag, prompt); s = summ(f"{OUT}/{tag}.csv")
        ident = t is not None and base is not None and t == base
        idx = ""
        if t is not None and base is not None and not ident:
            n = min(len(t), len(base)); idx = next((j for j in range(n) if t[j] != base[j]), n)
            print(f"DIFF {tag} idx={idx} K0={base[max(0,idx-25):idx+25]!r} {k}={t[max(0,idx-25):idx+25]!r} lens={len(base)}/{len(t)}")
        dr, ac = ngram(tag)
        f = fp(f"{OUT}/{tag}.stderr")
        rows.append(dict(config=k, item=it, identical=int(ident) if t is not None else "", first_diff_idx=idx,
                         decode_tok_s=s.get("tok/s"), prefill_s=s.get("prefill_s"), total_s=wall(f"{OUT}/{tag}.stderr"),
                         footprint_gib=None if f is None else round(f, 3), cache_hit_pct=s.get("cache_hit_pct"),
                         drafted=dr if dr is not None else s.get("mtp_drafted"), accepted=ac if ac is not None else s.get("mtp_accepted"),
                         tokens=s.get("tokens")))
with open(OUTCSV, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
def med(k, key):
    v = [float(r[key]) for r in rows if r["config"] == k and r[key] not in (None, "")]
    return st.median(v) if v else None
M = {k: {key: med(k, key) for key in ["decode_tok_s", "prefill_s", "total_s", "footprint_gib", "cache_hit_pct"]} for k in CFG}
print("| config | decode tok/s | prefill s | total s | footprint GiB | cache hit % | identical | drafted/accepted (rate) | verdict |")
print("|---|---|---|---|---|---|---|---|---|")
for k in CFG:
    R = [r for r in rows if r["config"] == k]; n = sum(1 for r in R if r["identical"] == 1)
    d = sum(int(r["drafted"] or 0) for r in R); a = sum(int(r["accepted"] or 0) for r in R)
    acc = f"{d}/{a} ({100*a/d:.1f} %)" if d else "-"
    m, b = M[k], M["K0"]
    if k == "K0": v = "control"
    elif n < len(items): v = "BROKEN"
    elif m["decode_tok_s"] >= 1.15 * b["decode_tok_s"] and m["prefill_s"] <= 1.10 * b["prefill_s"] and m["footprint_gib"] <= b["footprint_gib"] + 0.3: v = "ADOPT"
    else: v = "IDENTICAL-NO-GAIN"
    print(f"| {k} | {m['decode_tok_s']:.2f} ({m['decode_tok_s']/b['decode_tok_s']:.2f}x) | {m['prefill_s']:.2f} | {m['total_s']:.1f} | {m['footprint_gib']:.2f} | {m['cache_hit_pct']:.1f} | {n}/{len(R)} | {acc} | {v} |")
