#!/usr/bin/env python3
"""PACKSHAPE-FIRSTAID stage-1 scorer (criterion FIRSTAID-criterion.md; 0 LLM). python3 -I score_fa.py -> ../firstaid.json"""
import json, os, re, sys, sqlite3
CO = "<workspace>/rnd/research/coordinator/"; A = CO + "arms/"; CM = A + "coverage-map/"; D = A + "packshape/"; RP = D + "replay/"
sys.path.insert(0, D + "tools"); import shape_firstaid as SF
src = open(CM + "tools/chunklevel.py").read(); exec(src[:src.index("ARMS = {")])
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ARMS = ["BASE", "FASHAPED"]; HF = ("boar-medlineplus-en", "boar-firstaid-en", "qa-health-se"); PFX = "pack:local-boar-firstaid-en:"
ishealth = lambda r: any(x.startswith("grounding:health") or x.startswith("instant:off-health") for x in r["reasonCodes"])
kid = lambda r: [c["chunkId"] for c in (r.get("keptFull") or [])]
hdocs = lambda r: {c["docId"] for c in (r.get("keptFull") or []) if any(c["docId"].startswith(f"pack:local-{p}:") for p in HF)}
def health(base, arm):
    items = [i for i in base if i in arm and (ishealth(base[i]) or ishealth(arm[i]))]
    loss = {i: sorted(hdocs(base[i]) - hdocs(arm[i])) for i in items}; return dict(items=len(items), losses={i: v for i, v in loss.items() if v})
def share(rows):
    s = [c for r in rows.values() for c in (r.get("keptFull") or [])]; f = sum(c["docId"].startswith(PFX) for c in s)
    return dict(slots=len(s), firstaid=f, share=round(f / max(1, len(s)), 4))
OUT = dict(criterion=open(D + "FIRSTAID-criterion.sha256").read().split()[0])
M = {k: {r["id"]: r for r in rd(RP + f"main.{k}.jsonl")} for k in ARMS}; S = {k: score(RP + f"main.{k}.jsonl") for k in ARMS}
OUT["main"] = {k: dict(chunk=sum(1 for i in ids92 if S[k][i] and S[k][i]["chunk"]), lost=[i for i in ids92 if S["BASE"][i]["chunk"] and not S[k][i]["chunk"]],
                       gained=[i for i in ids92 if S[k][i]["chunk"] and not S["BASE"][i]["chunk"]], kept_changed_set=sum(set(kid(M[k][i])) != set(kid(M["BASE"][i])) for i in M["BASE"]),
                       health=health(M["BASE"], M[k]), firstaid=share(M[k])) for k in ARMS}
STQ = {r["id"]: r for r in rd("<workspace>/rnd/research/packs/selftest/boar-firstaid-en.jsonl")}
PK = {x["id"]: x["pack"] for x in json.load(open(A + "packproof/in/items.json"))["items"]}
STR = {k: {r["id"]: r for r in rd(RP + f"st.{k}.on-k13.jsonl")} for k in ARMS}
TP = {}
for l in open("<workspace>/kiln-local/shape-packs/fa-in-shaped/firstaid.jsonl"): pass
def f20(i, r, arm):
    q = STQ[i]; doc = f"{PFX}a{q['source']['article_id']}"; tp = SF.topic_of(q["source"]["title"])
    raw = any(c.get("docId") == doc for c in (r.get("rawFull") or [])); kept = [c for c in (r.get("keptFull") or []) if c["docId"] == doc]
    body = lambda c: c["body"].replace(tp + ": ", "") if arm != "BASE" else c["body"]
    qs = [n2(f["quote"]) for f in q["in_pack_facts"]]
    fact = any(x and x in n2(body(c)) for c in kept for x in qs)
    loose = any(tok_in_block(f["quote"], [body(c)], 4) for c in kept for f in q["in_pack_facts"])
    return dict(raw=raw, kept=bool(kept), fact=fact, fact_loose=loose, n_kept=len(r.get("keptFull") or []))
sm = {}
for k in ARMS:
    R = STR[k]; it = {i: f20(i, R[i], k) for i in R if PK[i] == "boar-firstaid-en"}
    sm[k] = dict(fb20={m: sum(x[m] for x in it.values()) for m in ("raw", "kept", "fact", "fact_loose")}, items=it, health=health(STR["BASE"], R),
                 kept_changed_set=sum(set(kid(R[i])) != set(kid(STR["BASE"][i])) for i in R), empty_kept=sum(1 for x in it.values() if x["n_kept"] == 0),
                 other_changed=sum(1 for i in R if PK[i] != "boar-firstaid-en" and set(kid(R[i])) != set(kid(STR["BASE"][i]))))
b, s = sm["BASE"]["items"], sm["FASHAPED"]["items"]
sm["FASHAPED"]["gained"] = [i for i in s if s[i]["fact"] and not b[i]["fact"]]; sm["FASHAPED"]["lost"] = [i for i in s if b[i]["fact"] and not s[i]["fact"]]
OUT["selftests"] = sm
v3 = SF.F; sh = "<workspace>/kiln-local/shape-packs/fa-shaped/boar-firstaid-en.sqlite"
cnt = lambda f: sqlite3.connect(f"file:{f}?mode=ro", uri=True).execute("select count(*) from chunks").fetchone()[0]
OUT["pack"] = dict(base_bytes=os.path.getsize(v3), shaped_bytes=os.path.getsize(sh), delta=round(os.path.getsize(sh) / os.path.getsize(v3) - 1, 3), base_chunks=cnt(v3), shaped_chunks=cnt(sh))
d = sm["FASHAPED"]["fb20"]["fact"] - sm["BASE"]["fb20"]["fact"]; hl = len(OUT["main"]["FASHAPED"]["health"]["losses"]) + len(sm["FASHAPED"]["health"]["losses"])
c = dict(a=d >= 5, b=OUT["main"]["FASHAPED"]["chunk"] >= 41, c=hl == 0)
OUT["gate"] = dict(clauses=c, fact_delta=d, health_losses=hl, pass_=all(c.values()))
json.dump(OUT, open(D + "firstaid.json", "w"), indent=1)
print(json.dumps({k: OUT[k] for k in ("pack", "gate")}))
for k in ARMS: print("MAIN", k, {x: y for x, y in OUT["main"][k].items()})
for k in ARMS: e = sm[k]; print("ST", k, e["fb20"], "empty kept", e["empty_kept"], "health", e["health"], "chg", e["kept_changed_set"], "other chg", e["other_changed"], e.get("gained"), e.get("lost"))
