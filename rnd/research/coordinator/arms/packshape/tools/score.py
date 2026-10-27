#!/usr/bin/env python3
"""PACKSHAPE stage-1 scorer (criterion PACKSHAPE-criterion.md; 0 LLM). python3 -I score.py -> ../packshape.json"""
import json, os, re, sqlite3, sys, statistics as st, unicodedata
CO = "<workspace>/rnd/research/coordinator/"; A = CO + "arms/"; CM = A + "coverage-map/"; D = A + "packshape/"; RP = D + "replay/"
sys.path.insert(0, D + "tools"); import fbread
SH = "<workspace>/kiln-local/shape-packs/"
src = open(CM + "tools/chunklevel.py").read(); exec(src[:src.index("ARMS = {")])  # score(), ids92, V01, CMI, tok_in_block
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ARMS = ["BASE", "SHAPED"]; HF = ("boar-medlineplus-en", "boar-firstaid-en", "qa-health-se"); PFX = "pack:local-boar-factbook:"
ishealth = lambda r: any(x.startswith("grounding:health") or x.startswith("instant:off-health") for x in r["reasonCodes"])
kid = lambda r: [c["chunkId"] for c in (r.get("keptFull") or [])]
hdocs = lambda r: {c["docId"] for c in (r.get("keptFull") or []) if any(c["docId"].startswith(f"pack:local-{p}:") for p in HF)}
def health(base, arm):
    items = [i for i in base if i in arm and (ishealth(base[i]) or ishealth(arm[i]))]
    loss = {i: sorted(hdocs(base[i]) - hdocs(arm[i])) for i in items}; return dict(items=len(items), losses={i: v for i, v in loss.items() if v})
def fbshare(rows):
    slots = [c for r in rows.values() for c in (r.get("keptFull") or [])]
    return dict(slots=len(slots), factbook=sum(c["docId"].startswith(PFX) for c in slots), share=round(sum(c["docId"].startswith(PFX) for c in slots) / max(1, len(slots)), 4),
                items_with_factbook=sum(1 for r in rows.values() if any(c["docId"].startswith(PFX) for c in (r.get("keptFull") or []))))
p50 = lambda rows: round(st.median([r["ms"] for r in rows.values() if r.get("ms") is not None]), 1)
OUT = dict(criterion=open(D + "PACKSHAPE-criterion.sha256").read().split()[0])
# ---- source units of the original text (Key-facts lines, category/Background paragraphs)
ORIG = {a["id"]: a for a in fbread.articles()}
def units(a):
    body = re.sub(r"^# [^\n]*\n+", "", a["text"]); parts = re.split(r"\n\n(?=## )", body); u = {}
    if parts and parts[0].startswith("Key facts:"):
        for i, l in enumerate(parts[0].split("\n")[1:]): u[f"kf:{i}"] = l
        parts = parts[1:]
    for p in parts:
        m = re.match(r"## ([^\n]*)\n+", p); cat = m.group(1).strip()
        for j, x in enumerate([x for x in p[m.end():].split("\n\n") if x.strip()]): u[f"{cat}:{j}"] = x
    return u
PROV = json.load(open(SH + "in-shaped/provenance.json"))
# ---- MAIN
M = {k: {r["id"]: r for r in rd(RP + f"main.{k}.jsonl")} for k in ARMS}
ref = {r["id"]: r for r in rd(CM + "nowiki/replay/main.K13.jsonl")}
OUT["main_identity_BASE_vs_nowiki_K13"] = dict(kept=sum(kid(M["BASE"][i]) == kid(ref[i]) for i in ref), n=len(ref))
S = {k: score(RP + f"main.{k}.jsonl") for k in ARMS}; mm = {}
for k in ARMS:
    s = S[k]; b = S["BASE"]
    e = dict(chunk=sum(1 for i in ids92 if s[i] and s[i]["chunk"]), chunk_cm=sum(1 for i in CMI if s[i] and s[i]["chunk"]), chunk_v01=sum(1 for i in V01 if s[i] and s[i]["chunk"]),
             lost=[i for i in ids92 if b[i]["chunk"] and not s[i]["chunk"]], gained=[i for i in ids92 if s[i]["chunk"] and not b[i]["chunk"]],
             kept_changed_set=sum(set(kid(M[k][i])) != set(kid(M["BASE"][i])) for i in M["BASE"]), health=health(M["BASE"], M[k]), factbook=fbshare(M[k]), ms_p50=p50(M[k]))
    e["changed_ids"] = [i for i in M["BASE"] if set(kid(M[k][i])) != set(kid(M["BASE"][i]))]
    mm[k] = e
OUT["main"] = mm
# ---- self-tests (on-k13 group: 140)
OWN = json.load(open(A + "packproof/in/own.json")); PK = {x["id"]: x["pack"] for x in json.load(open(A + "packproof/in/items.json"))["items"]}
STQ = {r["id"]: r for r in rd("<workspace>/rnd/research/packs/selftest/boar-factbook.jsonl")}
STR = {k: {r["id"]: r for r in rd(RP + f"st.{k}.on-k13.jsonl")} for k in ARMS}
nref = {r["id"]: r for r in rd(CM + "nowiki/replay/st.K13.on-k13.jsonl")}
OUT["st_identity_BASE_vs_nowiki_K13"] = dict(kept=sum(kid(STR["BASE"][i]) == kid(nref[i]) for i in nref), n=len(nref))
URL = {}
def url(pack, aid, arm):
    f = (SH + "shaped/boar-factbook.sqlite") if (arm == "SHAPED" and pack == "boar-factbook") else f"<workspace>/shared-data/packs/v3proto/{pack}.sqlite"
    if f not in URL: URL[f] = sqlite3.connect(f"file:{f}?mode=ro", uri=True)
    r = URL[f].execute("select url from article_meta where article_id=?", (aid,)).fetchone(); return r[0] if r else ""
def own_kept(i, r, arm):
    for c in (r.get("keptFull") or []):
        m = re.match(r"pack:local-(.+):a(\d+)$", c["docId"])
        if not m or m.group(1) != PK[i]: continue
        u = url(m.group(1), int(m.group(2)), arm)
        for a in OWN[i]:
            if re.search(re.escape(a["url"]) + r"(?![\w/])", u or "") and a["title"].lower() in c["title"].lower(): return True
    return False
def heading_of(title, body):
    pv = PROV[title]; best = ""
    for h in pv:
        if h and body.startswith(h + ": ") and len(h) > len(best): best = h
    return best
def fb20(i, r, arm):
    q = STQ[i]; aid = q["source"]["article_id"]; doc = f"{PFX}a{aid}"; title = q["source"]["title"]
    raw = any(c.get("docId") == doc for c in (r.get("rawFull") or [])); kept = [c for c in (r.get("keptFull") or []) if c["docId"] == doc]
    qs = [n2(f["quote"]) for f in q["in_pack_facts"]]; U = units(ORIG[aid])
    if arm == "BASE": prim = [c for c in kept if any(x and x in n2(c["body"]) for x in qs)]; hit = sorted({x for c in kept for x in qs if x and x in n2(c["body"])})
    else:
        prim, hit = [], set()
        for c in kept:
            us = PROV[title].get(heading_of(title, c["body"]), [])
            hx = {x for x in qs for u in us if x and x in n2(U.get(u, ""))}
            if hx: prim.append(c); hit |= hx
        hit = sorted(hit)
    loose = [c for c in kept if any(tok_in_block(f["quote"], [c["body"]], 4) for f in q["in_pack_facts"])]
    return dict(raw=raw, kept=bool(kept), fact=bool(prim), fact_loose=bool(loose), quotes_hit=len(hit), quotes=len(qs), n_own_kept=len(kept),
                n_fb_kept=sum(c["docId"].startswith(PFX) for c in (r.get("keptFull") or [])), n_kept=len(r.get("keptFull") or []))
sm = {}
for k in ARMS:
    R = STR[k]; f20 = {i: fb20(i, R[i], k) for i in R if PK[i] == "boar-factbook"}
    ok = {i: own_kept(i, R[i], k) for i in R}
    packs = sorted({PK[i] for i in R})
    e = dict(fb20={m: sum(x[m] for x in f20.values()) for m in ("raw", "kept", "fact", "fact_loose", "quotes_hit")}, fb20_items=f20,
             own_kept_per_pack={p: sum(ok[i] for i in ok if PK[i] == p) for p in packs}, own_kept_other120=sum(ok[i] for i in ok if PK[i] != "boar-factbook"),
             health=health(STR["BASE"], R), factbook_other120=fbshare({i: R[i] for i in R if PK[i] != "boar-factbook"}),
             kept_changed_set=sum(set(kid(R[i])) != set(kid(STR["BASE"][i])) for i in R), ms_p50=p50(R))
    sm[k] = e
for k in ARMS:
    b, s = sm["BASE"]["fb20_items"], sm[k]["fb20_items"]
    sm[k]["fact_gained"] = [i for i in s if s[i]["fact"] and not b[i]["fact"]]; sm[k]["fact_lost"] = [i for i in s if b[i]["fact"] and not s[i]["fact"]]
OUT["selftests"] = sm
# ---- pack size
v3 = "<workspace>/shared-data/packs/v3proto/boar-factbook.sqlite"; shp = SH + "shaped/boar-factbook.sqlite"
cnt = lambda f: sqlite3.connect(f"file:{f}?mode=ro", uri=True).execute("select count(*) from chunks").fetchone()[0]
OUT["pack"] = dict(base_bytes=os.path.getsize(v3), shaped_bytes=os.path.getsize(shp), delta=round(os.path.getsize(shp) / os.path.getsize(v3) - 1, 3), base_chunks=cnt(v3), shaped_chunks=cnt(shp))
# ---- gate
base_main = mm["BASE"]["chunk"]; floor = (42 if base_main == 42 else base_main) - 1
d = sm["SHAPED"]["fb20"]["fact"] - sm["BASE"]["fb20"]["fact"]
c = dict(a=d >= 5, b=mm["SHAPED"]["chunk"] >= floor, c=len(mm["SHAPED"]["health"]["losses"]) == 0)
OUT["gate"] = dict(clauses=c, fact_delta=d, main_floor=floor, pass_=all(c.values()))
json.dump(OUT, open(D + "packshape.json", "w"), indent=1)
print(json.dumps({k: OUT[k] for k in ("main_identity_BASE_vs_nowiki_K13", "st_identity_BASE_vs_nowiki_K13", "pack", "gate")}))
for k in ARMS:
    e = mm[k]; print("MAIN", k, e["chunk"], "cm", e["chunk_cm"], "v01", e["chunk_v01"], "lost", e["lost"], "gained", e["gained"], "chg", e["kept_changed_set"], "health", e["health"], "fb", e["factbook"], "ms", e["ms_p50"])
for k in ARMS:
    e = sm[k]; print("ST", k, e["fb20"], "other120", e["own_kept_other120"], e["own_kept_per_pack"], "health", e["health"]["losses"], "fb other", e["factbook_other120"], "chg", e["kept_changed_set"], "gained", e["fact_gained"], "lost", e["fact_lost"], "ms", e["ms_p50"])
