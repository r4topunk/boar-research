# Frozen detectors (v1 6f18dddf, SIT 7a73aeb9, fa-cards 294ddd5d) on 400 random FirstAidQA questions (independent, synthetic, CC BY 4.0).
import json, re, sys, random, collections, numpy as np
sys.path.insert(0, "../fa-cards"); from terms import regex_condition
S = json.load(open("sample400.json")); E = json.load(open("emb.json")); RX = json.load(open("rx.json"))
h = json.load(open("../health-embed-v1/health-lr.v1.json")); w, b = np.array(h["w"]), h["b"]
src = open("../chat-route/situation.py").read()
pat = re.search(r'SIT = re\.compile\((r".*?"\s*\n\s*r".*?")\s*,\s*re\.I\)', src, re.S).group(1)
SIT = re.compile(eval(pat.replace("\n", " ")), re.I)
P = json.load(open("../fa-cards/protos.json")); EP = json.load(open("../fa-cards/emb-protos.json"))
n = lambda v: (lambda a: a / np.linalg.norm(a))(np.array(v)); conds = list(P)
C = np.array([n(np.mean([n(EP[t]) for t in P[c]], 0)) for c in conds])
rows = []
for i, q in enumerate(S):
    v = n(E[q]); p = 1 / (1 + np.exp(-(v @ w + b)))
    r = regex_condition(q); cond = r if (r and not r.startswith("MULTI")) else None; via = "regex" if cond else None
    if r is None:
        s = C @ v; o = np.argsort(-s)
        if s[o[0]] >= .75 and s[o[0]] - s[o[1]] >= .03: cond, via = conds[o[0]], "emb"
    rows.append({"q": q, "v1": bool(p > .5), "p": float(p), "rx": RX[i], "sit": bool(SIT.search(q)), "cond": cond, "via": via, "multi": bool(r and r.startswith("MULTI"))})
N = len(rows); f = lambda k: sum(r[k] for r in rows)
print(f"n={N}  v1 {f('v1')} ({f('v1')/N:.0%})  health-regex {f('rx')} ({f('rx')/N:.0%})  v1 OR regex {sum(r['v1'] or r['rx'] for r in rows)}  SIT {f('sit')} ({f('sit')/N:.0%})")
gated = [r for r in rows if r["v1"] or r["rx"]]
print(f"condition card fires (gated by v1 OR regex): {sum(1 for r in gated if r['cond'])}/{len(gated)}  regex {sum(1 for r in gated if r['via']=='regex')}  emb {sum(1 for r in gated if r['via']=='emb')}  multi {sum(1 for r in gated if r['multi'])}")
print("by condition:", collections.Counter(r["cond"] for r in gated if r["cond"]).most_common())
json.dump(rows, open("rows.json", "w"))
random.seed(3)
fired = [r for r in gated if r["cond"]]
print("\n--- all fired cards for hand check (cond | via | question) ---")
for r in fired: print(f"{r['cond']:11} {r['via']:5} | {r['q']}")
