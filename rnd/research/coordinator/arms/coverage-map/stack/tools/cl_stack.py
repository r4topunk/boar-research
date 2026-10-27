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
# ---- STACK reads ----
ARMS = {
 "N10.gidf (ARM-G)": CM + "compose/replays/main.N10.gidf.jsonl",
 "F1b (v3 sidecars, extra)": CM + "sefix/replays/main.v3-extra.jsonl",
 "R1 mix (on F1b)": CM + "searchpar/r1/replays/main.mix.jsonl",
 "SEFIX-124 (F1+F2+F4, v2)": CM + "sefix/replays/main.F1F2F4.jsonl",
 "SEFIX-ALL (F1F2F3F4, v2)": CM + "sefix/replays/main.F1F2F3F4.jsonl",
 "STACK": CM + "stack/replays/main.on.jsonl",
 "diag STACK+RS_SE_SCOPE=all": CM + "stack/replays/main.scopeall.jsonl",
}
import statistics
RES = {l: score(f) for l, f in ARMS.items()}
ROWS = {l: {r["id"]: r for r in rd(f)} for l, f in ARMS.items()}
def tok(r): return sum(len((c.get("body") or "").split()) for c in r["keptFull"])
def summ(l):
    s = RES[l]; rows = ROWS[l]
    f = lambda ids, k: sum(1 for i in ids if s[i] and s[i][k])
    nofact = [i for i in ids92 if s[i] and not s[i]["chunk"]]
    junk = statistics.mean([s[i]["nkept"] for i in nofact]) if nofact else 0
    return dict(art=f(ids92, "art"), chunk=f(ids92, "chunk"), cm=f(CMI, "chunk"), v01=f(V01, "chunk"), art_cm=f(CMI, "art"), art_v01=f(V01, "art"),
                junk_own=round(junk, 3), n_nofact=len(nofact), kept_chunks=sum(s[i]["nkept"] for i in ids92 if s[i]), kept_words=sum(tok(rows[i]) for i in ids92 if i in rows))
SUM = {l: summ(l) for l in ARMS}
ref = "SEFIX-124 (F1+F2+F4, v2)"; st = "STACK"
deliv_ref = {i for i in ids92 if RES[ref][i]["chunk"]}
lost = sorted(i for i in deliv_ref if not RES[st][i]["chunk"]); gained = sorted(i for i in ids92 if RES[st][i]["chunk"] and not RES[ref][i]["chunk"])
# junk on the control's no-fact set (items the ref leaves without fact): mean kept chunks stack vs ref
nf_ref = [i for i in ids92 if not RES[ref][i]["chunk"]]
junk_ctlset = (statistics.mean(RES[st][i]["nkept"] for i in nf_ref), statistics.mean(RES[ref][i]["nkept"] for i in nf_ref))
nf_both = [i for i in ids92 if not RES[ref][i]["chunk"] and not RES[st][i]["chunk"]]
junk_both = (statistics.mean(RES[st][i]["nkept"] for i in nf_both), statistics.mean(RES[ref][i]["nkept"] for i in nf_both))
out = dict(summary=SUM, lost_vs_sefix124=lost, gained_vs_sefix124=gained, junk_ctlset=junk_ctlset, junk_both=junk_both, n_nf_ref=len(nf_ref), n_nf_both=len(nf_both),
           lost_vs_sefixall=sorted(i for i in ids92 if RES["SEFIX-ALL (F1F2F3F4, v2)"][i]["chunk"] and not RES[st][i]["chunk"]),
           gained_vs_sefixall=sorted(i for i in ids92 if RES[st][i]["chunk"] and not RES["SEFIX-ALL (F1F2F3F4, v2)"][i]["chunk"]),
           lost_vs_r1mix=sorted(i for i in ids92 if RES["R1 mix (on F1b)"][i]["chunk"] and not RES[st][i]["chunk"]),
           lost_vs_f1b=sorted(i for i in ids92 if RES["F1b (v3 sidecars, extra)"][i]["chunk"] and not RES[st][i]["chunk"]),
           per_item={l: {i: {k: v for k, v in x.items() if k != "titles"} for i, x in s.items() if x} for l, s in RES.items()})
json.dump(out, open(sys.argv[1], "w"), indent=1)
for l, e in SUM.items(): print(f"{l:30s} art {e['art']:3d} chunk {e['chunk']:3d} cm {e['cm']:2d} v01 {e['v01']:2d} | junk_own {e['junk_own']} (n {e['n_nofact']}) | kept chunks {e['kept_chunks']} words {e['kept_words']}")
print("lost vs SEFIX-124", lost); print("gained vs SEFIX-124", gained); print("junk ctl-set stack/ref", junk_ctlset, len(nf_ref), "both-set", junk_both, len(nf_both))
for k in ("lost_vs_sefixall", "gained_vs_sefixall", "lost_vs_r1mix", "lost_vs_f1b"): print(k, out[k])
