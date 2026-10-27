#!/usr/bin/env python3
"""PIN2 scorer (0 LLM). Frozen metrics of PIN2-criterion.md (sha d026c9bb). usage: python3 -I score.py <out json>"""
import json, sys, math, statistics, os, re
CM = "<workspace>/rnd/research/coordinator/arms/coverage-map/"; T27 = CM + "../topics27/"; K = CM + "pin2/"
src = open(CM + "tools/chunklevel.py").read(); exec(src[:src.index("ARMS = {")])   # score(path) -> per-item chunk-level, ids92, V01, CMI
rdd = lambda f: {json.loads(l)["id"]: json.loads(l) for l in open(f) if l.strip()}
ids = lambda r: [c["chunkId"] for c in r["keptFull"]]
bodies = lambda r: [(c["chunkId"], c["body"]) for c in r["keptFull"]]
ctx = lambda r: sum(math.ceil(len(c["title"] + "\n" + c["body"]) / 4) for c in r["keptFull"])
def budget(r):
    m = [int(x.split("-")[-1]) for x in r["reasonCodes"] if x.startswith("context:pin2-budget-")]
    return min(m) if m else None
EXP = {'b13': ['Mosquito-borne disease', 'Mosquito'], 'b15': ['Kyoto', 'Heian-kyō'], 'b19': ['AC power plugs and sockets', 'Mains electricity'], 'b20': ['Japan', 'Germany', 'Population density', 'Population ageing']}
OTHER = 'q1 q2 q4 q7 q8 q9 b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b14 b16 b17 b18 b21'.split()
H27 = 'q2 q4 b2 b8 b13 b14 b21'.split()
def ident(b, o):
    return dict(raw=sum([x["chunkId"] for x in b[i]["rawFull"]] == [x["chunkId"] for x in o[i]["rawFull"]] for i in b if i in o), kept=sum(ids(b[i]) == ids(o[i]) for i in b if i in o), codes=sum(b[i]["reasonCodes"] == o[i]["reasonCodes"] for i in b if i in o), n=len(o))
def changes(B, X, keys):
    st, ro, bo = [], [], []
    for i in keys:
        if set(ids(B[i])) != set(ids(X[i])): st.append(i)
        elif ids(B[i]) != ids(X[i]): ro.append(i)
        elif bodies(B[i]) != bodies(X[i]): bo.append(i)
    return st, ro, bo
def detail(B, X, keys):
    return {i: dict(lost=[(c["title"], c["chunkId"]) for c in B[i]["keptFull"] if c["chunkId"] not in ids(X[i])], added=[(c["title"], c["chunkId"]) for c in X[i]["keptFull"] if c["chunkId"] not in ids(B[i])],
                    codes=[c for c in X[i]["reasonCodes"] if "pin2" in c and "budget" not in c], ctx=[ctx(B[i]), ctx(X[i])]) for i in keys}
def ctxstats(B, X):
    pb = statistics.median(ctx(B[i]) for i in B); px = statistics.median(ctx(X[i]) for i in X)
    rr = {i: ctx(X[i]) / ctx(B[i]) for i in X if ctx(B[i])}
    mx = max(rr, key=rr.get)
    over = [i for i in X if budget(X[i]) is not None and ctx(X[i]) > budget(X[i])]
    nob = [i for i in X if budget(X[i]) is None]
    return dict(p50_base=pb, p50_arm=px, p50_ratio=round(px / pb, 4), max_item_ratio=round(rr[mx], 4), max_item=mx, over_budget=over, no_budget_code=len(nob))
fired = lambda X: {c: [i for i in X if any(rc.startswith(c) for rc in X[i]["reasonCodes"])] for c in ["context:pin2-rescued", "context:pin2-evicted", "grounding:pin2-kept"]}
OUT = {"criterion_sha256": open(CM + "PIN2-criterion.sha256").read().split()[0], "main": {}, "t27": {}}
mb_path = CM + "sefix/replays/main.F1F2F4.jsonl"; MB = rdd(mb_path); SB = score(mb_path)
HM = [i for i in MB if "grounding:health-strict" in MB[i]["reasonCodes"]]
if os.path.exists(K + "replays/main.off.jsonl"): OUT["main"]["identity_off"] = ident(MB, rdd(K + "replays/main.off.jsonl"))
OUT["main"]["base"] = dict(chunk=sum(1 for i in ids92 if SB[i] and SB[i]["chunk"]), health_items=len(HM))
f = K + "replays/main.PIN2.jsonl"
if os.path.exists(f):
    X = rdd(f); S = score(f)
    st, ro, bo = changes(MB, X, list(MB))
    hl = {i: [c for c in ids(MB[i]) if c not in ids(X[i])] for i in HM}; hl = {i: v for i, v in hl.items() if v}
    fr = fired(X)
    OUT["main"]["PIN2"] = dict(chunk=sum(1 for i in ids92 if S[i] and S[i]["chunk"]), chunk_cm=sum(1 for i in CMI if S[i]["chunk"]), chunk_v01=sum(1 for i in V01 if S[i]["chunk"]),
        gained=[i for i in ids92 if S[i]["chunk"] and not SB[i]["chunk"]], lost=[i for i in ids92 if SB[i]["chunk"] and not S[i]["chunk"]],
        set_changed=st, reorders=ro, body_only=bo, changed_detail=detail(MB, X, st + ro + bo), health_losses=hl, ctx=ctxstats(MB, X), fired={k: len(v) for k, v in fr.items()}, fired_ids=fr)
TB = rdd(T27 + "replay/misses.A1.jsonl")
if os.path.exists(K + "replays/t27.off.jsonl"): OUT["t27"]["identity_off"] = ident(TB, rdd(K + "replays/t27.off.jsonl"))
rec = lambda X: {k: [t for t in v if t in X[k]["sources"]] for k, v in EXP.items()}
OUT["t27"]["base"] = dict(recovered=rec(TB), n=sum(bool(v) for v in rec(TB).values()))
f = K + "replays/t27.PIN2.jsonl"
if os.path.exists(f):
    X = rdd(f); r = rec(X)
    st, ro, bo = changes(TB, X, OTHER); sta, roa, boa = changes(TB, X, list(TB))
    hl = {i: [c for c in ids(TB[i]) if c not in ids(X[i])] for i in H27}; hl = {i: v for i, v in hl.items() if v}
    fr = fired(X)
    OUT["t27"]["PIN2"] = dict(recovered=r, n=sum(bool(v) for v in r.values()), other_set_changed=st, other_reorders=ro, other_body_only=bo,
        all_set_changed=sta, changed_detail=detail(TB, X, sta + roa + boa), health_losses=hl, ctx=ctxstats(TB, X), fired={k: len(v) for k, v in fr.items()}, fired_ids=fr)
m = OUT["main"].get("PIN2"); t = OUT["t27"].get("PIN2")
if m and t:
    c1 = m["chunk"] >= OUT["main"]["base"]["chunk"] + 2 or t["n"] >= 2
    c2 = len(t["other_set_changed"]) <= 2
    c3 = not m["health_losses"] and not t["health_losses"]
    c4 = m["ctx"]["p50_ratio"] <= 1.10 and t["ctx"]["p50_ratio"] <= 1.10 and not m["ctx"]["over_budget"] and not t["ctx"]["over_budget"]
    OUT["gate"] = dict(gain=c1, other_set_le2=c2, health0=c3, ctx=c4, verdict="LEVER-CANDIDATE" if c1 and c2 and c3 and c4 else "NO")
json.dump(OUT, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
for s in ("main", "t27"):
    for a, v in OUT[s].items(): print(s, a, {k: v[k] for k in v if k not in ("changed_detail", "fired_ids")} if isinstance(v, dict) else v)
print(OUT.get("gate"))
