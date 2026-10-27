#!/usr/bin/env python3
"""NOWIKI scorer (criterion 5d40edcd; 0 LLM). python3 -I score.py -> ../nowiki.json"""
import json, os, re, sqlite3, statistics as st
CO = "<workspace>/rnd/research/coordinator/"; A = CO + "arms/"; CM = A + "coverage-map/"; D = CM + "nowiki/"; RP = D + "replay/"
SD = "<workspace>/shared-data/packs/"
src = open(CM + "tools/chunklevel.py").read(); exec(src[:src.index("ARMS = {")])  # score(), ids92, V01, CMI
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
KITS = ["K13", "NOWIKI", "NOWIKI2"]; HF = ("boar-medlineplus-en", "boar-firstaid-en", "qa-health-se")
ishealth = lambda r: any(x.startswith("grounding:health") or x.startswith("instant:off-health") for x in r["reasonCodes"])
kid = lambda r: [c["chunkId"] for c in (r.get("keptFull") or [])]
hdocs = lambda r: {c["docId"] for c in (r.get("keptFull") or []) if any(c["docId"].startswith(f"pack:local-{p}:") for p in HF)}
def health(base, arm):
    items = [i for i in base if i in arm and (ishealth(base[i]) or ishealth(arm[i]))]
    loss = {i: sorted(hdocs(base[i]) - hdocs(arm[i])) for i in items}; loss = {i: v for i, v in loss.items() if v}
    return dict(items=len(items), changed=[i for i in items if kid(base[i]) != kid(arm[i])], losses=loss)
def p50ms(rows): v = [r["ms"] for r in rows.values() if r.get("ms") is not None]; return round(st.median(v), 1) if v else None
def packs_of(r): return sorted({c["docId"].split(":")[1][6:] for c in (r.get("keptFull") or []) if c["docId"].startswith("pack:")})
OUT = dict(criterion="5d40edcd6edc7008edfad86cd84f6abde3b7f6e95c1f14637ab5265e998095d7")
# ---- MAIN
M = {k: {r["id"]: r for r in rd(RP + f"main.{k}.jsonl")} for k in KITS}
ref = {r["id"]: r for r in rd(CM + "sefix/replays/main.F1F2F4.jsonl")}
OUT["main_identity_K13_vs_F1F2F4"] = dict(kept=sum(kid(M["K13"][i]) == kid(ref[i]) for i in ref), codes=sum(M["K13"][i]["reasonCodes"] == ref[i]["reasonCodes"] for i in ref), n=len(ref))
S = {k: score(RP + f"main.{k}.jsonl") for k in KITS}; mm = {}
for k in KITS:
    s = S[k]; b = S["K13"]
    e = dict(chunk=sum(1 for i in ids92 if s[i] and s[i]["chunk"]), chunk_cm=sum(1 for i in CMI if s[i] and s[i]["chunk"]), chunk_v01=sum(1 for i in V01 if s[i] and s[i]["chunk"]),
             article=sum(1 for i in ids92 if s[i] and s[i]["art"]),
             lost=[i for i in ids92 if b[i]["chunk"] and not s[i]["chunk"]], gained=[i for i in ids92 if s[i]["chunk"] and not b[i]["chunk"]])
    e["lost_v01"] = [i for i in e["lost"] if i in V01]
    ch = [i for i in M["K13"] if kid(M[k][i]) != kid(M["K13"][i])]; chs = [i for i in M["K13"] if set(kid(M[k][i])) != set(kid(M["K13"][i]))]
    e.update(kept_changed_order=len(ch), kept_changed_set=len(chs), changed_ids=chs, health=health(M["K13"], M[k]), ms_p50=p50ms(M[k]),
             nkept_mean=round(st.mean(len(r.get("keptFull") or []) for r in M[k].values()), 2),
             wiki_kept_items=sum(1 for r in M[k].values() if {"boar-simplewiki-en", "wiki-vital5"} & set(packs_of(r))))
    mm[k] = e
OUT["main"] = mm
# ---- self-tests
OWN = json.load(open(A + "packproof/in/own.json")); ITEMS = json.load(open(A + "packproof/in/items.json"))["items"]; PK = {x["id"]: x["pack"] for x in ITEMS}
URL = {}
def url(pack, aid):
    if pack not in URL: URL[pack] = sqlite3.connect(f"file:{SD}v3proto/{pack}.sqlite?mode=ro", uri=True)
    r = URL[pack].execute("select url from article_meta where article_id=?", (aid,)).fetchone(); return r[0] if r else ""
def own_kept(i, r):
    for c in (r.get("keptFull") or []):
        m = re.match(r"pack:local-(.+):a(\d+)$", c["docId"])
        if not m or m.group(1) != PK[i]: continue
        u = url(m.group(1), int(m.group(2)))
        for a in OWN[i]:
            if re.search(re.escape(a["url"]) + r"(?![\w/])", u or "") and a["title"].lower() in c["title"].lower(): return True
    return False
G = ["on-k13", "on-k13+qa-ethereum-se", "on-k13+qa-bitcoin-se"]
STR = {k: {} for k in KITS}
for k in KITS:
    for g in G: STR[k].update({r["id"]: r for r in rd(RP + f"st.{k}.{g}.jsonl")})
live = {}
for g in G:
    for t in rd(A + f"packproof/gen/{g}/traces.jsonl"): live[t["itemId"]] = [x["title"] for x in t["retrieval"]["kept"]]
OUT["st_parity_K13_vs_live_titles"] = dict(same=sum(live.get(i) == [c["title"] for c in (r.get("keptFull") or [])] for i, r in STR["K13"].items()), n=len(STR["K13"]))
packs = list(dict.fromkeys(PK[i] for i in PK if i in STR["K13"])); sm = {}
for k in KITS:
    ok = {i: own_kept(i, STR[k][i]) for i in STR[k]}
    e = dict(per_pack={p: sum(ok[i] for i in ok if PK[i] == p) for p in packs}, kept160=sum(ok[i] for i in ok if PK[i] != "boar-simplewiki-en"),
             kept_simplewiki20=sum(ok[i] for i in ok if PK[i] == "boar-simplewiki-en"), kept180=sum(ok.values()),
             gained=[i for i in ok if ok[i] and not own_kept(i, STR["K13"][i])], lost=[i for i in ok if not ok[i] and own_kept(i, STR["K13"][i])],
             health=health(STR["K13"], STR[k]), ms_p50=p50ms(STR[k]),
             kept_changed_set=sum(set(kid(STR[k][i])) != set(kid(STR["K13"][i])) for i in STR[k]),
             wiki_kept_items=sum(1 for r in STR[k].values() if {"boar-simplewiki-en", "wiki-vital5"} & set(packs_of(r))))
    sm[k] = e
OUT["selftests"] = sm
# ---- 27 topics
T = json.load(open(A + "topics27/aggregates/titles.json")); ANC = {t["key"]: {x.lower() for g in t["groups"] for x in g} for t in T}
def t27(rows): return {i: any(x.lower() in ANC[i] for x in r["sources"]) for i, r in rows.items()}
TR = {k: {r["id"]: r for r in rd(RP + f"t27.{k}.jsonl")} for k in KITS}; TR["A1 vital5-only (ref)"] = {r["id"]: r for r in rd(A + "topics27/replay/misses.A1.jsonl")}
OUT["topics27"] = {k: dict(in_kept=sum(t27(v).values()), hits=[i for i, x in t27(v).items() if x], ms_p50=p50ms(v),
                           health=health(TR["K13"], v) if k in KITS else None) for k, v in TR.items()}
# ---- bytes (W78C accounting, computed)
dl = {}
for l in open(CM + "w78/replays-c/main.B.jsonl.denselog"):
    x = json.loads(l); dl[x["pack"]] = x["rows"]
f1 = {}
for l in open(CM + "w78/replays-c/main.B.jsonl.f1log"):
    x = json.loads(l); f1[x["pack"]] = x["rows"]
SIMPLE = "Simple English Wikipedia (2026-10-01)"
st1 = sum(dl.values()) * 384; f1b = sum(f1.values()) * 384
import importlib.util; s_ = importlib.util.spec_from_file_location("kk", D + "tools/kits.py"); kk = importlib.util.module_from_spec(s_); s_.loader.exec_module(kk)
by = {}
for k in KITS:
    rows = sum(v for p, v in dl.items() if not (k != "K13" and p == SIMPLE))
    by[k] = dict(stage1_bytes_q=rows * 384, f1_bytes_q=f1b, kit_bytes_q=rows * 384 + f1b, vital5_pool_rerank_upper=(400 * 384 if k == "K13" else 0),
                 pack_disk_bytes=sum(os.path.getsize(p) for p in kk.kit(k)), packs=len(kk.kit(k)))
OUT["bytes"] = by; OUT["bytes_rows"] = dict(dense=dl, f1=f1)
# ---- gate
b = mm["K13"]; floor = (42 if OUT["main_identity_K13_vs_F1F2F4"]["kept"] == 97 else b["chunk"]) - 2; gate = {}
for k in ["NOWIKI", "NOWIKI2"]:
    hl = len(mm[k]["health"]["losses"]) + len(sm[k]["health"]["losses"]) + len(OUT["topics27"][k]["health"]["losses"])
    c = dict(a=mm[k]["chunk"] >= floor, b=len(mm[k]["lost_v01"]) <= 3, c=sm[k]["kept160"] - sm["K13"]["kept160"] >= 5, d=hl == 0)
    gate[k] = dict(clauses=c, health_losses=hl, pass_=all(c.values()), floor=floor, relief160=sm[k]["kept160"] - sm["K13"]["kept160"])
v = "DROP" if gate["NOWIKI"]["pass_"] else ("KEEP-AS-OPTIONAL" if any(g["clauses"]["c"] and g["clauses"]["d"] for g in gate.values()) else "KEEP")
OUT["gate"] = gate; OUT["verdict"] = v; OUT["recommended_default"] = ("NOWIKI2" if gate["NOWIKI2"]["pass_"] else "NOWIKI") if v == "DROP" else "K13"
json.dump(OUT, open(D + "nowiki.json", "w"), indent=1)
print(json.dumps({k: OUT[k] for k in ["main_identity_K13_vs_F1F2F4", "st_parity_K13_vs_live_titles", "gate", "verdict", "recommended_default"]}, indent=0))
for k in KITS: e = mm[k]; print("MAIN", k, e["chunk"], "cm", e["chunk_cm"], "v01", e["chunk_v01"], "art", e["article"], "lost", e["lost"], "gained", e["gained"], "chg", e["kept_changed_set"], "health", e["health"]["items"], len(e["health"]["changed"]), e["health"]["losses"], "ms", e["ms_p50"], "wiki items", e["wiki_kept_items"])
for k in KITS: e = sm[k]; print("ST", k, e["kept180"], e["kept160"], e["kept_simplewiki20"], e["per_pack"], "gained", e["gained"], "lost", e["lost"], "health", e["health"]["items"], e["health"]["losses"], "ms", e["ms_p50"], "chg", e["kept_changed_set"])
for k, e in OUT["topics27"].items(): print("T27", k, e["in_kept"], "ms", e["ms_p50"], e["health"]["losses"] if e["health"] else "")
for k, e in by.items(): print("BYTES", k, e)
