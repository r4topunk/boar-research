#!/usr/bin/env python3
"""KEEPPIN scorer (0 LLM). Frozen metrics of KEEPPIN-criterion.md (sha 83bbae38). usage: python3 -I score.py <out json>"""
import json, sys, math, statistics
CM = "<workspace>/rnd/research/coordinator/arms/coverage-map/"; T27 = CM + "../topics27/"; K = CM + "keeppin/"
src = open(CM + "tools/chunklevel.py").read(); exec(src[:src.index("ARMS = {")])   # score(path) -> per-item chunk-level, ids92, V01, CMI
rdd = lambda f: {json.loads(l)["id"]: json.loads(l) for l in open(f) if l.strip()}
ids = lambda r: [c["chunkId"] for c in r["keptFull"]]
ctx = lambda r: sum(math.ceil(len(c["title"] + "\n" + c["body"]) / 4) for c in r["keptFull"])
EXP = {'b13': ['Mosquito-borne disease', 'Mosquito'], 'b15': ['Kyoto', 'Heian-kyō'], 'b19': ['AC power plugs and sockets', 'Mains electricity'], 'b20': ['Japan', 'Germany', 'Population density', 'Population ageing']}
OTHER = 'q1 q2 q4 q7 q8 q9 b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b14 b16 b17 b18 b21'.split()
H27 = 'q2 q4 b2 b8 b13 b14 b21'.split()
def ident(b, o):
    return dict(raw=sum([x["chunkId"] for x in b[i]["rawFull"]] == [x["chunkId"] for x in o[i]["rawFull"]] for i in b if i in o), kept=sum(ids(b[i]) == ids(o[i]) for i in b if i in o), codes=sum(b[i]["reasonCodes"] == o[i]["reasonCodes"] for i in b if i in o), n=len(o))
OUT = {"criterion_sha256": open(CM + "KEEPPIN-criterion.sha256").read().split()[0], "main": {}, "t27": {}}
# MAIN 97
mb_path = CM + "sefix/replays/main.F1F2F4.jsonl"; MB = rdd(mb_path); SB = score(mb_path)
HM = [i for i in MB if "grounding:health-strict" in MB[i]["reasonCodes"]]
pm_b = statistics.median(ctx(MB[i]) for i in MB)
import os
if os.path.exists(K + "replays/main.off.jsonl"): OUT["main"]["identity_off"] = ident(MB, rdd(K + "replays/main.off.jsonl"))
OUT["main"]["base"] = dict(chunk=sum(1 for i in ids92 if SB[i] and SB[i]["chunk"]), ctx_p50=pm_b, health_items=len(HM))
for arm in ["PIN", "PN", "PINPN", "PNx"]:
    f = K + f"replays/main.{arm}.jsonl"
    if not os.path.exists(f): continue
    X = rdd(f); S = score(f)
    ch = sum(1 for i in ids92 if S[i] and S[i]["chunk"])
    gain = [i for i in ids92 if S[i]["chunk"] and not SB[i]["chunk"]]; loss = [i for i in ids92 if SB[i]["chunk"] and not S[i]["chunk"]]
    changed = {i: dict(lost=[t for t in MB[i]["sources"] if t not in X[i]["sources"]], added=[t for t in X[i]["sources"] if t not in MB[i]["sources"]], codes=[c for c in X[i]["reasonCodes"] if "pin" in c or "keep-pn" in c]) for i in MB if ids(MB[i]) != ids(X[i])}
    hl = {i: [c for c in ids(MB[i]) if c not in ids(X[i])] for i in HM}; hl = {i: v for i, v in hl.items() if v}
    p50 = statistics.median(ctx(X[i]) for i in X)
    fired = {c: [i for i in X if any(rc.startswith(c) for rc in X[i]["reasonCodes"])] for c in ["context:title-pinned", "grounding:title-pin-kept", "grounding:keep-pn-restored"]}
    OUT["main"][arm] = dict(chunk=ch, chunk_cm=sum(1 for i in CMI if S[i]["chunk"]), chunk_v01=sum(1 for i in V01 if S[i]["chunk"]), gained=gain, lost=loss, kept_changed_n=len(changed), kept_changed=changed, health_losses=hl, ctx_p50=p50, ctx_ratio=round(p50 / pm_b, 4), fired={k: len(v) for k, v in fired.items()}, fired_ids=fired)
# 27 topics
TB = rdd(T27 + "replay/misses.A1.jsonl"); pt_b = statistics.median(ctx(TB[i]) for i in TB)
if os.path.exists(K + "replays/t27.off.jsonl"): OUT["t27"]["identity_off"] = ident(TB, rdd(K + "replays/t27.off.jsonl"))
rec = lambda X: {k: [t for t in v if t in X[k]["sources"]] for k, v in EXP.items()}
OUT["t27"]["base"] = dict(recovered=rec(TB), n=sum(bool(v) for v in rec(TB).values()), ctx_p50=pt_b)
for arm in ["PIN", "PN", "PINPN", "PNx"]:
    f = K + f"replays/t27.{arm}.jsonl"
    if not os.path.exists(f): continue
    X = rdd(f); r = rec(X)
    oth = [i for i in OTHER if X[i]["sources"] != TB[i]["sources"]]
    changed = {i: dict(before=TB[i]["sources"], after=X[i]["sources"], ctx=[c for c in X[i]["reasonCodes"] if c.startswith("context:")]) for i in TB if ids(TB[i]) != ids(X[i])}
    hl = {i: [c for c in ids(TB[i]) if c not in ids(X[i])] for i in H27}; hl = {i: v for i, v in hl.items() if v}
    p50 = statistics.median(ctx(X[i]) for i in X)
    OUT["t27"][arm] = dict(recovered=r, n=sum(bool(v) for v in r.values()), other_changed=oth, kept_changed_n=len(changed), kept_changed=changed, health_losses=hl, ctx_p50=p50, ctx_ratio=round(p50 / pt_b, 4))
# gate
for arm in ["PIN", "PN", "PINPN"]:
    m = OUT["main"].get(arm); t = OUT["t27"].get(arm)
    if not m or not t: continue
    c1 = m["chunk"] >= OUT["main"]["base"]["chunk"] + 3 or (t["n"] >= 2 and len(t["other_changed"]) <= 2)
    c2 = not m["health_losses"] and not t["health_losses"]; c3 = m["ctx_ratio"] <= 1.10 and t["ctx_ratio"] <= 1.10
    OUT.setdefault("gate", {})[arm] = dict(clause1=c1, health0=c2, ctx=c3, verdict="LEVER-CANDIDATE" if c1 and c2 and c3 else "NO")
json.dump(OUT, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
for s in ("main", "t27"):
    for a, v in OUT[s].items(): print(s, a, {k: v[k] for k in v if k not in ("kept_changed", "fired_ids", "recovered")} if isinstance(v, dict) else v)
print(OUT.get("gate"))
