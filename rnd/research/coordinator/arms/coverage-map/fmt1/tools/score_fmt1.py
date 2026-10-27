#!/usr/bin/env python3
"""FMT1-SCAN scorer (criterion coverage-map/FMT1-criterion.md sha 79fefb9c). 0 LLM. Usage: python3 -I score_fmt1.py <out json>"""
import json, sys, statistics as st
CM = "<workspace>/rnd/research/coordinator/arms/coverage-map/"; F = CM + "fmt1/replays/"
src = open(CM + "tools/chunklevel.py").read(); exec(src[:src.index("\nARMS = {")])   # score(), ids92, QS ...
ARMS = ["P400", "P400f65", "P2000", "P2000f65", "FULL", "FULLf65"]
L = lambda f: {json.loads(l)["id"]: json.loads(l) for l in open(f) if l.strip()}
def pct(xs, p):
    xs = sorted(xs); k = (len(xs) - 1) * p; f = int(k); c = min(f + 1, len(xs) - 1); return round(xs[f] + (xs[c] - xs[f]) * (k - f), 1)
def ms(rows): x = [r["ms"] for r in rows.values() if r.get("ms") is not None]; return dict(p50=pct(x, .5), p95=pct(x, .95), n=len(x))
HP = ("pack:local-qa-health-se:", "pack:local-boar-firstaid-en:", "pack:local-boar-medlineplus-en:", "pack:wiki-vital5:")
kid = lambda r: [c["chunkId"] for c in r["keptFull"]]
OUT = {"criterion": "79fefb9cc799a6056cae4eec45de1e6f0649ca0e181ce71541f67fd191936daa", "main": {}, "t27": {}}
# MAIN
base = L(F + "main.P400.jsonl"); bs = score(F + "main.P400.jsonl")
hitems = [i for i, r in base.items() if "-hlt-" in i or any(c.startswith(("grounding:health", "instant:off-health")) for c in r["reasonCodes"])]
bms = ms(base)
for a in ARMS:
    try: X = L(F + f"main.{a}.jsonl")
    except FileNotFoundError: continue
    s = score(F + f"main.{a}.jsonl")
    n = sum(bool(v and v["chunk"]) for v in s.values()); nb = sum(bool(v and v["chunk"]) for v in bs.values())
    gained = [i for i in ids92 if s[i] and s[i]["chunk"] and not bs[i]["chunk"]]; lost = [i for i in ids92 if bs[i]["chunk"] and not (s[i] and s[i]["chunk"])]
    changed = [i for i in base if set(kid(base[i])) != set(kid(X[i]))]
    hl = {i: [c for c in kid(base[i]) if c.startswith(HP) and c not in kid(X[i])] for i in hitems}; hl = {i: v for i, v in hl.items() if v}
    fmt1_kept = sum(c.startswith("pack:wiki-vital5:") for r in X.values() for c in kid(r))
    m = ms(X)
    OUT["main"][a] = dict(chunk92=n, base=nb, delta=n - nb, cm=sum(bool(s[i] and s[i]["chunk"]) for i in CMI), v01=sum(bool(s[i] and s[i]["chunk"]) for i in V01),
        gained=gained, lost=lost, keptChanged=len(changed), changedIds=changed, healthItems=len(hitems), healthLoss=hl, vital5Kept=fmt1_kept, ms=m,
        changes={i: dict(minus=[t["title"] for t in base[i]["keptFull"] if t["chunkId"] not in kid(X[i])], plus=[t["title"] for t in X[i]["keptFull"] if t["chunkId"] not in kid(base[i])]) for i in changed})
# TOPICS
EXP = {'b13': ['Mosquito-borne disease', 'Mosquito'], 'b15': ['Kyoto', 'Heian-kyō'], 'b19': ['AC power plugs and sockets', 'Mains electricity'], 'b20': ['Japan', 'Germany', 'Population density', 'Population ageing']}
OTHER = 'q1 q2 q4 q7 q8 q9 b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b14 b16 b17 b18 b21'.split(); HEALTH = 'q2 q4 b2 b8 b13 b14 b21'.split()
tb = L(F + "t27.P400.jsonl"); tms = ms(tb)
for a in ARMS:
    try: X = L(F + f"t27.{a}.jsonl")
    except FileNotFoundError: continue
    rec = {k: [t for t in v if t in X[k]["sources"] and t not in tb[k]["sources"]] for k, v in EXP.items()}; rec = {k: v for k, v in rec.items() if v}
    ch = [i for i in OTHER if X[i]["sources"] != tb[i]["sources"]]
    hl = {i: [t for t in tb[i]["sources"] if t not in X[i]["sources"]] for i in HEALTH}; hl = {i: v for i, v in hl.items() if v}
    OUT["t27"][a] = dict(recovered=rec, nrec=len(rec), changed=ch, keptChanged=sum(set(kid(tb[i])) != set(kid(X[i])) for i in tb), healthLoss=hl, ms=ms(X),
        kept={i: X[i]["sources"] for i in list(EXP) + ch}, misses_raw={k: [(c["title"], c["similarity"]) for c in X[k]["rawFull"]] for k in EXP})
for a in ARMS:
    M, T = OUT["main"].get(a), OUT["t27"].get(a)
    if not (M and T): continue
    ga = M["delta"] >= 3 or (T["nrec"] >= 2 and len(T["changed"]) <= 2)
    gb = not M["healthLoss"] and not T["healthLoss"]
    gc = M["ms"]["p95"] <= 2 * bms["p95"] and T["ms"]["p95"] <= 2 * tms["p95"]
    OUT.setdefault("verdict", {})[a] = dict(a=ga, b=gb, c=gc, verdict="LEVER-CANDIDATE" if (ga and gb and gc and a != "P400") else "NO")
json.dump(OUT, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
for a in ARMS:
    M, T = OUT["main"].get(a), OUT["t27"].get(a)
    if M: print("MAIN", a, M["chunk92"], f"d{M['delta']:+d}", "cm", M["cm"], "v01", M["v01"], "+", M["gained"], "-", M["lost"], "chg", M["keptChanged"], "hl", M["healthLoss"], "v5kept", M["vital5Kept"], M["ms"])
    if T: print("T27 ", a, "rec", T["recovered"], "chg", T["changed"], "hl", T["healthLoss"], T["ms"])
    if a in OUT.get("verdict", {}): print("   ", OUT["verdict"][a])
