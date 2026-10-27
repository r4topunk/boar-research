#!/usr/bin/env python3
"""KEEP-E step A comparison (0 LLM): changed MAIN rows = dumped prompt differs (or trace route/kept ids differ), tokens = ceil(chars/4) of the
prompt message contents (engine approxTokens), mean over prompted rows. Usage: compare.py <job dir> -> aggregates/replay.json"""
import json, sys, os, math
J = sys.argv[1]; H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
P = {v: {} for v in ("base", "E")}; T = {}
for v in P:
    for r in rd(f"{J}/{v}-MAIN.prompts.jsonl"): P[v].setdefault(r["itemId"], []).append(r["messages"])
    T[v] = {t["itemId"]: t for t in rd(f"{J}/{v}-MAIN.traces.jsonl")}
tok = lambda ms: sum(math.ceil(len(m["content"]) / 4) for p in ms for m in p)
kept = lambda t: [k.get("chunkId") or k.get("id") for k in (t.get("retrieval") or {}).get("kept", [])]
ids = sorted(set(T["base"]) | set(T["E"])); ch = []
for i in ids:
    if P["base"].get(i) != P["E"].get(i) or kept(T["base"][i]) != kept(T["E"][i]): ch.append(i)
k1 = json.load(open(f"{H}/../keep-k1/aggregates/keep-replay.json"))["variants"]
k1e = next(v for k, v in k1.items() if k.split("+")[0] == "E" and "V1orC" not in k)["changed_main_ids"]
pr = [i for i in ids if i in P["base"]]
tb = sum(tok(P["base"][i]) for i in pr) / len(pr); te = sum(tok(P["E"].get(i, P["base"][i])) for i in pr) / len(pr)
rows = [dict(id=i, tok_base=tok(P["base"].get(i, [])), tok_E=tok(P["E"].get(i, [])), kept_base=len(kept(T["base"][i])), kept_E=len(kept(T["E"][i])),
             codes_E=[c for c in T["E"][i].get("reasonCodes", T["E"][i].get("answer", {}).get("reasonCodes", [])) if c.startswith(("keep-e", "headpass"))]) for i in ch]
res = dict(n_rows=len(ids), n_prompted=len(pr), changed=ch, n_changed=len(ch), k1_E_changed=k1e, same_as_k1=sorted(ch) == sorted(k1e),
           tok_mean_base=round(tb, 1), tok_mean_E=round(te, 1), tok_pct=round(100 * (te / tb - 1), 1),
           tok_changed_pct=round(100 * (sum(r["tok_E"] for r in rows) / max(1, sum(r["tok_base"] for r in rows)) - 1), 1), rows=rows)
json.dump(res, open(f"{H}/aggregates/replay.json", "w"), indent=1)
print({k: v for k, v in res.items() if k != "rows"})
for r in rows: print(r)
