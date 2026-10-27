#!/usr/bin/env python3
"""W63 aggregation (0 LLM). Reads norepack/traces/<arm>.jsonl (MacBook) and norepack/mini/<arm>.jsonl (mini); writes aggregates/norepack.json."""
import json, itertools, os, statistics as st
H = "<workspace>/rnd/research/coordinator/arms/litepacks"
arms = {}
for a in ("mac-def1", "mac-def2", "mac-nr", "mac-nr2"): arms[a] = f"{H}/norepack/traces/{a}.jsonl"
for a in ("mini-def1", "mini-def2", "mini-nr", "mini-nr2"): arms[a] = f"{H}/norepack/mini/{a}.jsonl"
T = {a: {json.loads(l)["itemId"]: json.loads(l) for l in open(p) if l.strip()} for a, p in arms.items() if os.path.exists(p)}
txt = lambda a, i: T[a][i]["answer"]["text"]
w32 = lambda s: s.split()[:32]
ids = sorted(T["mac-def1"])
def ident(a, b): return dict(text=sum(txt(a, i) == txt(b, i) for i in ids), w32=sum(w32(txt(a, i)) == w32(txt(b, i)) for i in ids), n=len(ids))
pairs = [("mac-def1", "mac-nr"), ("mini-def1", "mini-nr"), ("mac-def1", "mini-def1"), ("mac-nr", "mini-nr"), ("mac-def1", "mini-nr"), ("mac-nr", "mini-def1")]
extra = [("mac-def1", "mac-def2"), ("mini-def1", "mini-def2"), ("mac-nr", "mac-nr2"), ("mini-nr", "mini-nr2")]
out = {"ids": ids, "pairs": {f"{a} vs {b}": ident(a, b) for a, b in pairs if a in T and b in T},
       "repeats": {f"{a} vs {b}": ident(a, b) for a, b in extra if a in T and b in T}, "speed": {}}
for a in T:
    d = [T[a][i]["timing"] for i in ids if T[a][i]["timing"].get("decodeTokPerSec")]
    pf = [t["promptTokens"] / (t["prefillMs"] / 1000) for t in d if t.get("prefillMs")]
    out["speed"][a] = dict(decode_tok_s_median=round(st.median(t["decodeTokPerSec"] for t in d), 2), prefill_tok_s_median=round(st.median(pf), 1),
                           total_ms_sum=round(sum(T[a][i]["timing"]["totalMs"] for i in ids)), n=len(d),
                           extra_args=T[a][ids[0]]["runtime"]["versions"].get("server.extra_args"))
json.dump(out, open(f"{H}/aggregates/norepack.json", "w"), indent=1)
print(json.dumps(out, indent=1))
