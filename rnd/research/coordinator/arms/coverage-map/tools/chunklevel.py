#!/usr/bin/env python3
"""CHUNKLEVEL (0 LLM / judge / Opus / paid / phone). Re-score every MAIN-97 delivery replay at CHUNK level vs the article-level flag.
Article-level = the existing stage-K flag (score_kfull.py lexical `present` over the UNION of kept 'title\\nbody' blocks, best-of cm_stage.py docId oracle for the 40 cooking/money items).
Chunk-level = the fact must sit inside ONE kept chunk's BODY (no titles, no cross-chunk union):
  v0.1 (52 keyed): share_v01(q,[body]) per kept chunk, PRESENT = any chunk share >= 0.5 (STRICT = share 1.0).
  cm (40): normalised (NFKC lower, strip punctuation, collapse ws) in_pack_facts quote is a substring of a kept chunk body; any quote = delivered ('all' = every quote found in some kept chunk).
Usage: python3 -I chunklevel.py <out json>"""
import json, sys, re, os, glob, unicodedata, importlib.util
CO = "<workspace>/rnd/research/coordinator/"; A = CO + "arms/"; CM = A + "coverage-map/"; R = A + "retrieve-sweep"; BE = "<workspace>/boar-eval/bench/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
src = open(R + "/tools/sweep.py").read().split("\n")
a = next(i for i, l in enumerate(src) if l.startswith("spec = importlib.util.spec_from_file_location")); b = next(i for i, l in enumerate(src) if l.startswith("FUN = json.load"))
exec("\n".join(src[a:b]))   # pc, QS, share_v01, share_st, present, tok_in_block
POOL = json.load(open(CM + "aggregates/coverage-pool.json"))["items"]; O = json.load(open(CM + "aggregates/cm-oracle.json"))
ids92 = list(POOL); V01 = [i for i in ids92 if POOL[i]["set"] == "v0.1"]; CMI = [i for i in ids92 if POOL[i]["set"] == "cm"]
assert len(ids92) == 92 and len(V01) == 52 and len(CMI) == 40
def n2(s):
    s = unicodedata.normalize("NFKC", s or "").lower().replace("’", "'")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s)).strip()
def chunk_cm(i, kept):
    facts = QS[i]["selftest"]["in_pack_facts"]; bodies = [n2(c["body"]) for c in kept]
    qs = [n2(f.get("quote", "")) for f in facts]
    hit = [bool(q) and any(q in bd for bd in bodies) for q in qs]
    # sensitivity: looser token rule inside one chunk (80 % of quote tokens, as FACTPRESENT)
    loose = [h or any(tok_in_block(f.get("quote", ""), [c["body"]], 4) or tok_in_block(f.get("fact", ""), [c["body"]], 3) for c in kept) for h, f in zip(hit, facts)]
    return dict(any=any(hit), all=all(hit), loose_any=any(loose), n_quotes=len(qs), n_hit=sum(hit))
def chunk_v01(i, kept):
    sh = [share_v01(QS[i], [c["body"]]) or 0.0 for c in kept]
    m = max(sh, default=0.0); return dict(any=m >= 0.5, strict=m >= 1.0, best=m)
def doc_oracle(i, rows_i):
    o = O[i]; doc = f"pack:local-{o['pack']}:a{o['article_id']}"
    return any(c.get("docId") == doc for c in rows_i["keptFull"])
def score(path):
    rows = {r["id"]: r for r in rd(path)}; out = {}
    for i in ids92:
        r = rows.get(i)
        if r is None: out[i] = None; continue
        kept = r["keptFull"]
        if i in O:
            art = bool(present(i, kept)) or doc_oracle(i, r); ch = chunk_cm(i, kept); c = ch["any"]
            out[i] = dict(art=art, chunk=c, chunk_all=ch["all"], chunk_loose=ch["loose_any"], nq=ch["n_quotes"], nh=ch["n_hit"], set="cm", nkept=len(kept), titles=[k["title"] for k in kept])
        else:
            art = bool(present(i, kept)); ch = chunk_v01(i, kept)
            out[i] = dict(art=art, chunk=ch["any"], chunk_strict=ch["strict"], set="v0.1", nkept=len(kept), titles=[k["title"] for k in kept])
    return out
ARMS = {  # label -> replay
 "B0 stock (retrieve-sweep)": R + "/replay/B0.main.jsonl",
 "K3 (cm replay, 6-pack)": CM + "replay/main.K3.jsonl", "KFULL (cm replay)": CM + "replay/main.KFULL.jsonl",
 "searchpar off": CM + "searchpar/replays/main.off.jsonl",
 "g2 v2": R + "/g2-fullkit/runs/main.v2.jsonl", "g2 v3": R + "/g2-fullkit/runs/main.v3.jsonl",
}
for n in (0, 2, 4, 6, 8, 10):
    for v in ("stock", "gidf"): ARMS[f"compose N{n}.{v}"] = CM + f"compose/replays/main.N{n}.{v}.jsonl"
for f in sorted(glob.glob(CM + "sefix/replays/main.*.jsonl")):
    lab = os.path.basename(f)[5:-6]
    if lab == "RD1-off": continue  # 65 rows, partial
    ARMS["sefix " + lab] = f
ARMS["sefix RD1-off (65 rows)"] = CM + "sefix/replays/main.RD1-off.jsonl"
ARMS["gate off"] = CM + "gate/replays/off.jsonl"; ARMS["gate p1"] = CM + "gate/replays/p1.jsonl"
ARMS["reader RD3off"] = CM + "reader/replays/main.RD3off.jsonl"; ARMS["reader RD3on"] = CM + "reader/replays/main.RD3on.jsonl"
ARMS["searchpar r4 (81 rows)"] = CM + "searchpar/replays/main.r4.jsonl"
RES = {}
for lab, f in ARMS.items():
    if not os.path.exists(f): continue
    RES[lab] = score(f)
def summ(s):
    have = [i for i in ids92 if s[i]]
    f = lambda ids, k: sum(1 for i in ids if s[i] and s[i][k])
    hv = [i for i in V01 if s[i]]; hc = [i for i in CMI if s[i]]
    return dict(n=len(have), art=f(ids92, "art"), chunk=f(ids92, "chunk"), art_cm=f(CMI, "art"), chunk_cm=f(CMI, "chunk"), chunk_cm_all=f(CMI, "chunk_all"), chunk_cm_loose=f(CMI, "chunk_loose"),
                art_v01=f(V01, "art"), chunk_v01=f(V01, "chunk"), chunk_v01_strict=f(V01, "chunk_strict"),
                over=f(ids92, "art") - f(ids92, "chunk"),
                flip_art_not_chunk=[i for i in have if s[i]["art"] and not s[i]["chunk"]], flip_chunk_not_art=[i for i in have if s[i]["chunk"] and not s[i]["art"]])
SUM = {lab: summ(s) for lab, s in RES.items()}
# live traces vs matching replay: title parity, chunk-level on parity subset
LIVE = {  # live trace -> replay label
 "sefix f1b (ans-traces)": (CM + "sefix/ans-traces/f1b-main-s42.traces.jsonl", "sefix v3-extra"),
 "sefix sefixall s42": (CM + "sefix/ans-traces/sefixall-main-s42.traces.jsonl", "sefix F1F2F3F4"),
 "sefix sefixall s43": (CM + "sefix/ans-traces/sefixall-main-s43.traces.jsonl", "sefix F1F2F3F4"),
 "compose ARM-G": (CM + "compose/screen/traces/cmp-G-K10-main-s42.traces.jsonl", "compose N10.gidf"),
 "compose ARM-S": (CM + "compose/screen/traces/cmp-S-K10-main-s42.traces.jsonl", "compose N10.stock"),
 "reader rd1 main": (CM + "reader/rd1/traces/rd1-main-s42.traces.jsonl", "sefix v3-extra"),
 "reader rd2 main": (CM + "reader/traces/rd2-main-s42.traces.jsonl", "sefix v3-extra"),
 "reader rd3 main": (CM + "reader/rd3/traces/rd3-main-s42.traces.jsonl", "reader RD3on"),
 "gate P1 main": (CM + "gate/traces/gate-P1-main-s42.traces.jsonl", "gate p1"),
}
LV = {}
for lab, (f, rl) in LIVE.items():
    if not os.path.exists(f) or rl not in RES: continue
    tr = {t["itemId"]: t for t in rd(f)}; s = RES[rl]
    par = [i for i in ids92 if i in tr and s[i] and [k["title"] for k in tr[i]["retrieval"]["kept"]] == s[i]["titles"]]
    g = lambda ids, k: sum(1 for i in ids if s[i][k])
    LV[lab] = dict(replay=rl, n_trace=len([i for i in ids92 if i in tr]), title_parity=len(par), art_parity=g(par, "art"), chunk_parity=g(par, "chunk"), art_all=g(ids92, "art"), chunk_all=g(ids92, "chunk"),
                   nonparity=[i for i in ids92 if i in tr and i not in par])
json.dump(dict(method=__doc__, arms=SUM, live=LV, per_item={l: {i: {k: v for k, v in x.items() if k != "titles"} for i, x in s.items() if x} for l, s in RES.items()}), open(sys.argv[1], "w"), indent=1)
for lab, e in SUM.items(): print(f"{lab:32s} n{e['n']} art {e['art']:3d} chunk {e['chunk']:3d} | cm {e['art_cm']:2d}/{e['chunk_cm']:2d} (all {e['chunk_cm_all']}, loose {e['chunk_cm_loose']}) | v01 {e['art_v01']:2d}/{e['chunk_v01']:2d} (strict {e['chunk_v01_strict']}) | over {e['over']}")
for lab, e in LV.items(): print(lab, e["replay"], "parity", e["title_parity"], "/", e["n_trace"], "art/chunk on parity", e["art_parity"], e["chunk_parity"])
