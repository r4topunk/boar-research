#!/usr/bin/env python3
"""D2Q scorer (criterion 83b06185; 0 LLM). python3 -I score.py -> ../d2q.json"""
import json, re, sqlite3, statistics as st, unicodedata
CO = "<workspace>/rnd/research/coordinator/"; A = CO + "arms/"; CM = A + "coverage-map/"; D = A + "d2q/"; RP = D + "replay/"
SD = "<workspace>/shared-data/packs/"
src = open(CM + "tools/chunklevel.py").read(); exec(src[:src.index("ARMS = {")])  # score(), ids92, V01, CMI
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ARMS = ["off", "x1", "x2"]; HF = ("boar-medlineplus-en", "boar-firstaid-en", "qa-health-se"); FB = "boar-factbook"
ishealth = lambda r: any(x.startswith("grounding:health") or x.startswith("instant:off-health") for x in r["reasonCodes"])
kid = lambda r: [c["chunkId"] for c in (r.get("keptFull") or [])]
hdocs = lambda r: {c["docId"] for c in (r.get("keptFull") or []) if any(c["docId"].startswith(f"pack:local-{p}:") for p in HF)}
fbk = lambda r: [c for c in (r.get("keptFull") or []) if c["docId"].startswith(f"pack:local-{FB}:")]
def health(base, arm):
    items = [i for i in base if i in arm and (ishealth(base[i]) or ishealth(arm[i]))]
    loss = {i: sorted(hdocs(base[i]) - hdocs(arm[i])) for i in items}; loss = {i: v for i, v in loss.items() if v}
    return dict(items=len(items), changed=[i for i in items if kid(base[i]) != kid(arm[i])], losses=loss)
p50 = lambda rows: round(st.median([r["ms"] for r in rows.values() if r.get("ms") is not None]), 1)
OUT = dict(criterion=open(D + "D2Q-criterion.sha256").read().split()[0])
# ---- identity (off on the d2q kit = K13 on rs-SEFIX)
M = {a: {r["id"]: r for r in rd(RP + f"main.{a}.jsonl")} for a in ARMS}
ref = {r["id"]: r for r in rd(CM + "sefix/replays/main.F1F2F4.jsonl")}
G = ["on-k13", "on-k13+qa-ethereum-se", "on-k13+qa-bitcoin-se"]
S = {a: {} for a in ARMS}; NW = {}
for g in G:
    NW.update({r["id"]: r for r in rd(CM + f"nowiki/replay/st.K13.{g}.jsonl")})
    for a in ARMS: S[a].update({r["id"]: r for r in rd(RP + f"st.{a}.{g}.jsonl")})
OUT["identity_off"] = dict(main_kept=sum(kid(M["off"][i]) == kid(ref[i]) for i in ref), main_codes=sum(M["off"][i]["reasonCodes"] == ref[i]["reasonCodes"] for i in ref), main_n=len(ref),
                           st_kept=sum(kid(S["off"][i]) == kid(NW[i]) for i in NW), st_n=len(NW))
# ---- factbook self-tests
OWN = json.load(open(A + "packproof/in/own.json")); ITEMS = json.load(open(A + "packproof/in/items.json"))["items"]; PK = {x["id"]: x["pack"] for x in ITEMS}
STI = {}
for p in set(PK.values()):
    for l in open(f"<workspace>/rnd/research/packs/selftest/{p}.jsonl"): x = json.loads(l); STI[x["id"]] = x
URL = {}
def url(pack, aid):
    if pack not in URL: URL[pack] = sqlite3.connect(f"file:{SD}v3proto/{pack}.sqlite?mode=ro", uri=True)
    r = URL[pack].execute("select url from article_meta where article_id=?", (aid,)).fetchone(); return r[0] if r else ""
def own_in(i, lst):
    for c in (lst or []):
        m = re.match(r"pack:local-(.+):a(\d+)$", c.get("docId", ""))
        if not m or m.group(1) != PK[i]: continue
        u = url(m.group(1), int(m.group(2)))
        for a in OWN[i]:
            if re.search(re.escape(a["url"]) + r"(?![\w/])", u or "") and a["title"].lower() in c["title"].lower(): return True
    return False
def fact_chunk(i, r):
    qs = [n2(f.get("quote", "")) for f in STI[i]["in_pack_facts"]]; bodies = [n2(c["body"]) for c in fbk(r)] if PK[i] == FB else [n2(c["body"]) for c in (r.get("keptFull") or [])]
    return sum(1 for q in qs if q and any(q in b for b in bodies)), len(qs)
fb = sorted(i for i in PK if PK[i] == FB); sm = {}
for a in ARMS:
    rows = S[a]; per = {}
    for i in fb:
        r = rows[i]; nh, nq = fact_chunk(i, r)
        per[i] = dict(raw=own_in(i, r.get("rawFull")), kept=own_in(i, r.get("keptFull")), fact_any=nh > 0, facts=f"{nh}/{nq}", n_fb_kept=len(fbk(r)), codes=[c for c in r["reasonCodes"] if c.startswith("grounding") or c.startswith("answer:")])
    ok180 = {i: own_in(i, rows[i].get("keptFull")) for i in rows}
    sm[a] = dict(raw=sum(v["raw"] for v in per.values()), kept=sum(v["kept"] for v in per.values()), fact_chunk=sum(v["fact_any"] for v in per.values()),
                 fb_kept_items=sum(v["n_fb_kept"] > 0 for v in per.values()), per_item=per, kept180=sum(ok180.values()),
                 per_pack180={p: sum(ok180[i] for i in ok180 if PK[i] == p) for p in sorted(set(PK.values()))},
                 st_kept_changed_set=sum(set(kid(rows[i])) != set(kid(S["off"][i])) for i in rows), st_ms_p50=p50(rows))
OUT["factbook20"] = sm
# ---- MAIN
SC = {a: score(RP + f"main.{a}.jsonl") for a in ARMS}; mm = {}
for a in ARMS:
    s = SC[a]; b = SC["off"]
    mm[a] = dict(chunk=sum(1 for i in ids92 if s[i] and s[i]["chunk"]), chunk_cm=sum(1 for i in CMI if s[i] and s[i]["chunk"]), chunk_v01=sum(1 for i in V01 if s[i] and s[i]["chunk"]),
                 lost=[i for i in ids92 if b[i]["chunk"] and not s[i]["chunk"]], gained=[i for i in ids92 if s[i]["chunk"] and not b[i]["chunk"]],
                 kept_changed_set=[i for i in M["off"] if set(kid(M[a][i])) != set(kid(M["off"][i]))],
                 fb_crowding_items=sum(1 for r in M[a].values() if fbk(r)), fb_crowding_ids=[i for i, r in M[a].items() if fbk(r)], ms_p50=p50(M[a]))
OUT["main"] = mm
# ---- health and gate
gate = {}
for a in ["x1", "x2"]:
    hm, hs = health(M["off"], M[a]), health(S["off"], S[a]); hl = len(hm["losses"]) + len(hs["losses"])
    c = dict(own_kept=sm[a]["kept"] - sm["off"]["kept"] >= 6, main_facts=mm[a]["chunk"] >= 41, health=hl == 0)
    gate[a] = dict(clauses=c, pass_=all(c.values()), d_kept=sm[a]["kept"] - sm["off"]["kept"], health_main=hm, health_st=hs)
OUT["gate"] = gate
OUT["verdict_gate"] = "PASS-X1" if gate["x1"]["pass_"] else ("PASS-X2" if gate["x2"]["pass_"] else "FAIL")
json.dump(OUT, open(D + "d2q.json", "w"), indent=1)
print(json.dumps(OUT["identity_off"]))
for a in ARMS: e = sm[a]; print("FB20", a, "raw", e["raw"], "kept", e["kept"], "fact", e["fact_chunk"], "fbItems", e["fb_kept_items"], "180", e["kept180"], e["per_pack180"], "stchg", e["st_kept_changed_set"], "ms", e["st_ms_p50"])
for a in ARMS: e = mm[a]; print("MAIN", a, e["chunk"], "cm", e["chunk_cm"], "v01", e["chunk_v01"], "lost", e["lost"], "gained", e["gained"], "chg", len(e["kept_changed_set"]), "fbcrowd", e["fb_crowding_items"], "ms", e["ms_p50"])
for a, g in gate.items(): print("GATE", a, g["clauses"], g["d_kept"], g["health_main"]["losses"], g["health_st"]["losses"])
print(OUT["verdict_gate"])
