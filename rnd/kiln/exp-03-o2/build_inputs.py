#!/usr/bin/env python3
"""exp-03 inputs: one row per (source run, model, question) that has a blind hand label, with what an O2 rule needs.

Row: {src, model, queryId, query, category, answer, label, declined, promptTitles, citedTitles, citedIdx}
- label: Plumb's blind hand label (pass / cw / fail / refused / empty), or "declined" when the app declined
  (iPhone rows the labels file omits because the row was declined).
- promptTitles: titles of the sources the model saw, in [n] order.
- citedTitles: titles of the sources the answer cites.
  - exp-01/02 harness rows: parsed from the [n] markers in the answer, mapped to the captured promptSources.
  - iPhone rows: the app's own `citedTitles` (post-gate).

Sources:
  H1 exp-01 harness, factual 38: qwen2.5-1.5b, qwen3-4b, ling-3.0-tiny (labels: hand-labels-1p5b-factual38.json,
     hand-labels-baseline-mix.json + map-SEALED.json)
  H2 exp-02 harness, factual 38: maple-preview (hand-labels-run4-maple.json)
  P2 iPhone run 2, device 52, 1.5B, build 14de107 (hand-labels-run2.json)
  P3 iPhone run 3, device 52 + wiki-vital5 (hand-labels-run3-vital5.json)
Usage: python3 build_inputs.py <boar root> <out.jsonl>
"""
import json, re, sys

root, out = sys.argv[1], sys.argv[2]
K, PL = f"{root}/rnd/kiln", f"{root}/rnd/plumb/data"
strip = lambda d: {k: v for k, v in d.items() if not k.startswith("_")}
jl = lambda p: [json.loads(l) for l in open(p) if l.strip()]
questions = {q["id"]: q for q in jl(f"{root}/rnd/lantern/handoff/questions.vitalik-lantern.jsonl")}

prompt_titles = {}
for f in ("v2-hard12", "lantern52"):
    for r in jl(f"{K}/exp-01-inram-moe-reader/capture/{f}.jsonl"):
        prompt_titles[r["queryId"]] = [s["title"] for s in (r.get("promptSources") or [])]

CITE = re.compile(r"\[(\d{1,2})\]")


def harness_row(src, model, r, label):
    titles = prompt_titles.get(r["queryId"], [])
    idx = sorted({int(n) for n in CITE.findall(r["answer"]) if 1 <= int(n) <= len(titles)})
    return {"src": src, "model": model, "queryId": r["queryId"], "query": r.get("query") or questions[r["queryId"]]["query"],
            "category": r.get("category") or questions[r["queryId"]]["category"], "answer": r["answer"], "label": label,
            "declined": False, "route": r.get("route"), "promptTitles": titles, "citedIdx": idx,
            "citedTitles": [titles[i - 1] for i in idx]}


rows = []
# H1
seal = json.load(open(f"{K}/exp-02-maple/blind/map-SEALED.json"))["map"]
lab = {"qwen2.5-1.5b": {v[2]: v[0] for v in strip(json.load(open(f"{PL}/hand-labels-1p5b-factual38.json"))).values()},
       "qwen3-4b": {}, "ling-3.0-tiny": {}}
for b, v in strip(json.load(open(f"{PL}/hand-labels-baseline-mix.json"))).items():
    lab[seal[b]["model"]][seal[b]["queryId"]] = v[0]
for m, L in lab.items():
    for r in jl(f"{K}/exp-01-inram-moe-reader/runs/{m}.jsonl"):
        if r["queryId"] in L:
            rows.append(harness_row("H1", m, r, L[r["queryId"]]))
# H2
L = {q: v[0] for q, v in strip(json.load(open(f"{PL}/hand-labels-run4-maple.json"))).items()}
for r in jl(f"{K}/exp-02-maple/runs/maple-preview.jsonl"):
    if r["queryId"] in L:
        rows.append(harness_row("H2", "maple-preview", r, L[r["queryId"]]))
# P2 / P3
for src, runf, labf in (("P2", "qwen2.5-1.5b-instruct-q4km__iphone-14de107-device.jsonl", "hand-labels-run2.json"),
                        ("P3", "qwen2.5-1.5b-instruct-q4km__iphone-14de107-device-vital5.jsonl", "hand-labels-run3-vital5.json")):
    L = strip(json.load(open(f"{PL}/{labf}")))
    L = {k: (v[0] if isinstance(v, list) else v) for k, v in L.items()}
    for r in jl(f"{PL}/{runf}"):
        q = r["queryId"]
        label = L.get(q) or ("declined" if r.get("declined") else None)
        if label is None:
            continue
        rows.append({"src": src, "model": "qwen2.5-1.5b@iphone", "queryId": q, "query": r["query"], "category": r["category"],
                     "answer": r.get("answer") or "", "label": label, "declined": bool(r.get("declined")), "route": r.get("tier"),
                     "promptTitles": r.get("retrievedTitles") or [], "citedIdx": None, "citedTitles": r.get("citedTitles") or []})
with open(out, "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
from collections import Counter
print(len(rows), Counter((r["src"], r["model"]) for r in rows))
print(Counter((r["src"], r["label"]) for r in rows))
