#!/usr/bin/env python3
"""cmp.py PROF NEW_GLOBS PREV_GLOBS MAIN_GLOBS: changed answers NEW vs PREV (printed in full), unsafe items (v0.7) vs PREV and vs MAIN."""
import json, sys, glob, importlib.util
from pathlib import Path
V=Path("<workspace>/boar-eval/scorers/vendor/safety")
spec=importlib.util.spec_from_file_location("sc", V/"safety_check.v0.7.py"); sc=importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
S=sc.load(V/"rules.v0.7.json", V/"overlay.v0.4.json")
qmeta={}
for p in ["<workspace>/boar-eval/bench/v0.1/questions.public.jsonl","<workspace>/boar-eval/bench/v0.1/safety/track.v0.3.jsonl"]:
  for l in open(p): x=json.loads(l); qmeta[x["id"]]=x
def unsafe(t):
  q=dict(qmeta.get(t["itemId"],{})); q.setdefault("id",t["itemId"]); q.setdefault("question",t["question"])
  return [h['rule'] for h in sc.check(t["answer"]["text"], sc.rules_for_v06(q,S), S) if h.get("status","unsafe")=="unsafe"]
def load(globs):
  d={}
  for g in globs.split(","):
    for p in sorted(glob.glob(g)):
      for l in open(p):
        if l.strip(): t=json.loads(l); d[t['itemId']]=t
  return d
prof,new,prev,main=sys.argv[1:5]; N,P,M=load(new),load(prev),load(main)
codes=lambda t:[c for c in t['route']['reasonCodes'] if c.startswith(('grounding:health','grounding:fa-card','instant:off','instant:final','grounding:no-good','grounding:danger'))]
ch=[k for k in N if k in P and N[k]['answer']['text']!=P[k]['answer']['text']]
for k in ch:
  print(f"\n=== {k} | {codes(P[k])} -> {codes(N[k])} | unsafe {unsafe(P[k])} -> {unsafe(N[k])}\nQ: {N[k]['question'][:200]}\nPREV: {P[k]['answer']['text'][:500]}\nNEW:  {N[k]['answer']['text'][:500]}")
ks=[k for k in N if k in P and k in M]
print(f"\n{prof}: items {len(N)} (paired {len(ks)}); changed vs prev {len(ch)}; unsafe items main {sum(bool(unsafe(M[k])) for k in ks)} / prev {sum(bool(unsafe(P[k])) for k in ks)} / new {sum(bool(unsafe(N[k])) for k in ks)}; missing in main {len([k for k in N if k not in M])}")
print('unsafe new:', {k:unsafe(N[k]) for k in ks if unsafe(N[k])})
