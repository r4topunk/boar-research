#!/usr/bin/env python3
"""Token accounting of captured prompts on a tokenize-only llama-server (port arg): rendered template, system head, context, question."""
import json, re, sys, urllib.request, statistics as S
P = sys.argv[1]
def post(path, body):
    r = urllib.request.Request(f"http://127.0.0.1:{P}{path}", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r).read())
ntok = lambda s: len(post("/tokenize", {"content": s, "add_special": False})["tokens"])
first = True; agg = {}
for run in ["lp-K0-v01-s42", "lp-K0-cm-s42", "lp-K1-v01-s42", "lp-K1-cm-s42", "lp-K3-st-s42"]:
    orig = {json.loads(l)["itemId"]: json.loads(l)["timing"]["promptTokens"] for l in open(f"<workspace>/rnd/research/coordinator/arms/litepacks/traces/{run}.traces.jsonl")}
    rows = []
    for l in open(f"cap/{run}.prompts.jsonl"):
        p = json.loads(l); m = p["messages"]
        rendered = post("/apply-template", {"messages": m, "chat_template_kwargs": {"enable_thinking": False}})["prompt"]
        if first: print("RENDERED SAMPLE (repr, first 400 + last 300):", repr(rendered[:400]), "...", repr(rendered[-300:])); first = False
        s = m[0]["content"]; head, ctx = (s.split("\n\nContext:\n", 1) + [""])[:2]
        rows.append({"total": ntok(rendered), "orig": orig.get(p["itemId"]), "head": ntok(head), "ctx": ntok(ctx) if ctx else 0, "user": ntok(m[-1]["content"])})
    agg[run] = {k: round(S.mean(r[k] for r in rows), 1) for k in ("total", "orig", "head", "ctx", "user")}
    agg[run]["total_eq_orig"] = f'{sum(r["total"] == r["orig"] for r in rows)}/{len(rows)}'
    agg[run]["head_share"] = round(S.mean(r["head"] / r["total"] for r in rows), 3)
print(json.dumps(agg, indent=1))
