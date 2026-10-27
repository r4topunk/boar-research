#!/usr/bin/env python3
"""RAG-FUNNEL (2026-10-21; 0 LLM, 0 generation, 0 judge, 0 paid). Where is the key fact of a real dev item lost, per pack set (K0, K1, K3)?

Items: MAIN 97 (= v0.1 57 + qa-cooking/qa-money self-tests 40), keyed under FACTPRESENT's lexical rule (92: v0.1 52 + cm 40).
Stages, first failing stage wins (per item x pack set):
  S1 not in any installed pack   : no chunk of the arm's installed packs (pool search below) holds the fact, and neither S2-S5 holds.
  S2 in a pack, not retrieved    : a pack chunk holds it, but no retrieved candidate does. S2r = the router ran no retrieval (route has no
                                   retrieve:yes); S2s = retrieval ran (lexical + dense search missed it).
  S3 retrieved, dropped at keep  : the union of candidates (retrieve() list + the two-stage dense candidates + the X1/dense pending appends)
                                   holds it, the kept context does not. Sub-split by where the fact chunk left: compress (not in the compressed
                                   list), grounding (compressed, not kept, not an append), budget/append (only in dense/x1 candidates).
  S4 kept, answer wrong/unsupported : FACTPRESENT PRESENT in the kept context, judge correctness (Haiku 5.5-low, mean of both orders) < 3.5,
                                   or declined. S4ce = correctness <= 1.5 (confident-error band).
  S5 kept and used correctly     : PRESENT in the kept context and correctness >= 3.5.
Fact rule = FACTPRESENT's (tools/factpresent.py): v0.1 grading must_any/must_k with the vendored precheck semantics, share >= 0.5;
self-tests in_pack_facts (quote substring, or >= 80 % of quote tokens (>= 4) / fact tokens (>= 3) in one block), share >= 0.5.
Candidate presence: the same rule over the union of candidate chunk texts (full chunk text read from the pack file by chunk id).
Pack presence (pool search): per installed pack, FTS5 bm25 top 200 for OR(question content tokens) and top 200 for OR(question tokens +
plain grading terms / fact-statement tokens); a pool chunk holds the fact when the rule on that chunk ALONE gives share >= 0.5 AND its topic
anchor >= 0.5, anchor = idf-weighted share of the question's content tokens found in the chunk (title + text; crude plural stemming; idf =
log(N/df) on the simplewiki kit pack's FTS, the same reference for every pack). Rule v2: v1 (anchor = >= min(2, n) question tokens) failed the
10-gold read (4/10 real fact chunks: generic grading terms + 2 generic question words, e.g. 'World Bank' for 'countries bigger than India');
v2 was written after that read and before any other number was looked at. Pool search is a generous retriever, not exhaustive, so S1 is an
upper bound on 'absent' and S2 a lower bound on 'present'.
Gold chunk (ORACLE-REAL input): among the K3 packs' qualifying pool chunks, max share, then title hit (a question token with idf >= 2 in the
chunk's title; v3, added after the v2 10-gold read gave 6/10), then max anchor, then best bm25 rank. Every gold chunk is then read and labelled
Y/P/N by hand (arms/oracle-real/gold-labels.tsv); only Y/P items enter ORACLE-REAL.
Usage: python3 -I ragfunnel.py <funnel replay out dir> <FACTPRESENT json> <out json>"""
import json, sys, re, glob, sqlite3, functools, random, hashlib, importlib.util, unicodedata
from compression import zstd
RD, FPJ, OUTF = sys.argv[1:4]
A = "<workspace>/rnd/research/coordinator/arms/"; BE = "<workspace>/boar-eval/bench/"; SD = "<workspace>/shared-data/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
spec = importlib.util.spec_from_file_location("pc", "<workspace>/boar-eval/scorers/vendor/lantern/precheck.py")
pc = importlib.util.module_from_spec(spec); spec.loader.exec_module(pc)
FP = json.load(open(FPJ))["items"]
MAIN = [l.strip() for l in open(A + "lp-screens/main-97.ids") if l.strip()]
V01 = set(l.strip() for l in open(A + "litepacks/data/v01-57.ids") if l.strip())
Q = {q["id"]: q for q in rd(BE + "v0.1/questions.public.jsonl")}
for f in glob.glob(BE + "selftest/*/questions.jsonl"):
    for q in rd(f): Q[q["id"]] = q
# kit files = the sha-pinned LITEPACKS kit (BOAR_EVAL_PACK_DIRS order resolves to these)
PF = {"boar-crypto": SD + "crypto/boar-crypto.sqlite", "boar-wikivoyage-en": SD + "packs/boar-wikivoyage-en.sqlite",
      "boar-simplewiki-en": SD + "packs/v3proto/boar-simplewiki-en.sqlite", "boar-factbook": SD + "packs/v3proto/boar-factbook.sqlite",
      "boar-medlineplus-en": SD + "packs/v3proto/boar-medlineplus-en.sqlite", "boar-firstaid-en": SD + "packs/v3proto/boar-firstaid-en.sqlite"}
KIT = {"K0": ["boar-crypto", "boar-wikivoyage-en"], "K1": ["boar-crypto", "boar-wikivoyage-en", "boar-simplewiki-en"],
       "K3": ["boar-crypto", "boar-wikivoyage-en", "boar-simplewiki-en", "boar-factbook", "boar-medlineplus-en", "boar-firstaid-en"]}
ARMS = ["K0", "K1", "K3"]
DB = {k: sqlite3.connect(f"file:{v}?mode=ro", uri=True) for k, v in PF.items()}
@functools.lru_cache(maxsize=4096)
def block(pk, bid): return zstd.decompress(DB[pk].execute("select zdata from blocks where id=?", (bid,)).fetchone()[0])
@functools.lru_cache(maxsize=200000)
def chunk(pk, cid):
    r = DB[pk].execute("select article_id, start, end from chunks where id=?", (cid,)).fetchone()
    if not r: return None
    b, off, ln, t = DB[pk].execute("select block_id, off, len, title from articles where id=?", (r[0],)).fetchone()
    txt = block(pk, b)[off:off + ln].decode("utf-8", "replace")
    return t, txt[r[1]:r[2]].strip()
def parse_id(cid):
    m = re.match(r"^pack:(?:local-)?([^:]+):(\d+)$", cid); return (m.group(1), int(m.group(2))) if m else None
def ctext(cid):
    p = parse_id(cid)
    if not p or p[0] not in DB: return None
    c = chunk(*p); return None if c is None else c[0] + "\n" + c[1]
# ---------------- fact rule (copied from factpresent.py) ----------------
STOP = set("the a an and or of to in on for with is are was were be been it its this that as at by from not no but if then than so do does did can could "
           "will would should may might has have had you your they their there which what when where who how why also more most very just only into "
           "out up about over after before such these those other some any all each".split())
def nrm(s):
    s = unicodedata.normalize("NFKC", s or "").lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[‐-―−]", "-", s); return re.sub(r"\s+", " ", s).strip()
toks = lambda s: [w for w in re.findall(r"[a-z0-9][a-z0-9'.%-]*[a-z0-9%]|[a-z0-9]", nrm(s)) if len(w) >= 3 and w not in STOP] or []
def tok_in_block(phrase, blocks, need):
    t = set(toks(phrase))
    if len(t) < need: return False
    return any(len(t & set(toks(b))) / len(t) >= 0.8 for b in blocks)
def share_v01(q, blocks):
    g = q.get("grading", {}); text = pc.norm("\n\n".join(blocks)); question = pc.norm(q["question"]); groups = []
    for grp in g.get("must_any", []):
        live = [t for t in grp if not pc.is_echo(t, question)]
        if live: groups.append(any(pc.hits(t, text) for t in live))
    mk = g.get("must_k")
    if mk:
        live = [t for t in mk["terms"] if not pc.is_echo(t, question)]
        groups.append(sum(pc.hits(t, text) for t in live) >= mk["k"])
    return (sum(groups) / len(groups)) if groups else None
def share_st(q, blocks):
    facts = q["selftest"]["in_pack_facts"]; whole = nrm("\n\n".join(blocks)); hit = 0
    for f in facts:
        quote = nrm(f.get("quote", ""))
        hit += bool((len(quote) >= 12 and quote in whole) or tok_in_block(quote, blocks, 4) or tok_in_block(f.get("fact", ""), blocks, 3))
    return hit / len(facts) if facts else None
share = lambda q, blocks: share_st(q, blocks) if "selftest" in q else share_v01(q, blocks)
# ---------------- pool search ----------------
def fts_or(words): return " OR ".join('"' + w.replace('"', '""') + '"' for w in dict.fromkeys(words) if w)
def grading_words(q):
    if "selftest" in q: return [w for f in q["selftest"]["in_pack_facts"] for w in toks(f.get("fact", ""))]
    g = q.get("grading", {}); ts = [t for grp in g.get("must_any", []) for t in grp] + (g.get("must_k") or {}).get("terms", [])
    return [t for t in ts if not t.startswith("re:")]
def stem(w):
    w = w.replace("'s", "")
    if len(w) > 4 and w.endswith("ies"): return w[:-3] + "y"
    if len(w) > 4 and w.endswith("es") and not w.endswith("ses"): return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"): return w[:-1]
    return w
NREF = DB["boar-simplewiki-en"].execute("select count(*) from chunks").fetchone()[0]
@functools.lru_cache(maxsize=None)
def idf(w):
    import math
    try: df = DB["boar-simplewiki-en"].execute("select count(*) from fts where fts match ?", ('"' + w.replace('"', '""') + '"',)).fetchone()[0]
    except sqlite3.OperationalError: df = 0
    return math.log((NREF + 1) / (df + 1))
def anchor(qt, txt):
    have = {stem(w) for w in toks(txt)}; tot = sum(idf(w) for w in set(qt))
    return round(sum(idf(w) for w in set(qt) if stem(w) in have) / tot, 3) if tot else 0.0
def pool_hits(i, pk):
    q = Q[i]; qt = list(dict.fromkeys(toks(q["question"]))); out = {}
    for qq in (fts_or(qt), fts_or(qt + grading_words(q))):
        if not qq: continue
        try:
            for r, (rid,) in enumerate(DB[pk].execute("select rowid from fts where fts match ? order by rank limit 200", (qq,))):
                out.setdefault(rid, r)
        except sqlite3.OperationalError as e: print("fts err", i, pk, e, file=sys.stderr)
    best = None
    for rid, rank in out.items():
        c = chunk(pk, rid)
        if not c: continue
        txt = c[0] + "\n" + c[1]; sh = share(q, [txt])
        if sh is None or sh < 0.5: continue
        anc = anchor(qt, txt)
        if anc < 0.5: continue
        th = int(bool({stem(w) for w in qt if idf(w) >= 2.0} & {stem(w) for w in toks(c[0])}))  # v3: subject named in the title
        key = (sh, th, anc, -rank)
        if best is None or key > best[0]: best = (key, f"pack:{pk}:{rid}", c[0], round(sh, 3), anc, rank)
    return best
# ---------------- replay traces ----------------
def load(arm):
    o = {}
    for s in ("V01", "CM"):
        for t in rd(f"{RD}/{arm}-{s}.traces.jsonl"):
            rc = t["route"]["reasonCodes"]; e = o.setdefault(t["itemId"], dict(raw=[], dense=[], pend=[], comp=[], kept=[], retrieve=False, kept_titles=[]))
            e["retrieve"] |= "retrieve:yes" in rc
            for c in rc:
                if c.startswith("fun:raw:"): e["raw"] += [x for x in c[8:].split(",") if x]
                elif c.startswith("fun:dense:"): e["dense"] += [x for x in c[10:].split(",") if x]
                elif c.startswith("fun:compressed:"): e["comp"] += [x for x in c[15:].split(",") if x]
                elif c.startswith("retfloor:cand:"): e["pend"].append(":".join(c.split(":")[3:6]))
                elif c.startswith("retfloor:kept:"): e["kept"] += [x for x in c.split(":", 3)[3].split(",") if x]
            e["kept_titles"] = [(k["title"], k.get("section")) for k in t["retrieval"]["kept"]]
    return o
TRF = {a: load(a) for a in ARMS}
def lp_tr(arm):
    o = {}
    for f in sorted(glob.glob(f"{A}litepacks/traces/lp-{arm}-*-s42.traces.jsonl")):
        if "smoke" not in f:
            for t in rd(f): o[t["itemId"]] = t
    return o
TR = {a: lp_tr(a) for a in ARMS}
PAR = {a: {i: TRF[a][i]["kept_titles"] == [(k["title"], k.get("section")) for k in TR[a][i]["retrieval"]["kept"]] for i in MAIN if i in TRF[a]} for a in ARMS}
def lp_j(arm):
    by = {}
    for f in sorted(glob.glob(f"{A}litepacks/judgments/lp-{arm}-*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    return {qq: sum(m["boar"]["correctness"] for m in v.values()) / 2 for qq, v in by.items() if len(v) == 2}
J = {a: lp_j(a) for a in ARMS}
def corr(arm, i):
    t = TR[arm][i]
    if t["answer"].get("declined"): return 0.0, True
    if arm != "K0" and t["answer"]["text"] == TR["K0"][i]["answer"]["text"]: return J["K0"].get(i), False
    return J[arm].get(i), False
# ---------------- classify ----------------
KEYED = [i for i in MAIN if FP[i]["K0"]["share"] is not None]
POOL = {}
for i in KEYED:
    for pk in KIT["K3"]: POOL[(i, pk)] = pool_hits(i, pk)
per = {}
for i in KEYED:
    q = Q[i]; e = dict(set="v0.1" if i in V01 else "cm", tag=FP[i]["tag"])
    for a in ARMS:
        tr = TRF[a][i]; cands = list(dict.fromkeys(tr["raw"] + tr["dense"] + tr["pend"]))
        texts = {c: ctext(c) for c in cands}; ok_txt = [t for t in texts.values() if t]
        csh = share(q, ok_txt) if ok_txt else 0.0
        cand_present = csh is not None and csh >= 0.5
        fact_cands = [c for c, t in texts.items() if t and (share(q, [t]) or 0) >= 0.5]
        kept_present = bool(FP[i][a]["present"])
        packs = [(pk, POOL[(i, pk)]) for pk in KIT[a] if POOL[(i, pk)]]
        c_, dec = corr(a, i)
        if kept_present: st = "S5" if (c_ is not None and c_ >= 3.5 and not dec) else "S4"
        elif cand_present:
            st = "S3"
            if any(c in tr["comp"] for c in fact_cands): sub = "grounding"
            elif any(c in tr["raw"] for c in fact_cands): sub = "compress"
            elif any(c in tr["pend"] for c in fact_cands): sub = "append-budget"
            elif fact_cands: sub = "dense-rank"
            else: sub = "union-only"
        elif packs: st = "S2"
        else: st = "S1"
        x = dict(stage=st, retrieve=tr["retrieve"], n_cand=len(cands), n_kept=len(tr["kept"]), cand_share=None if csh is None else round(csh, 3),
                 fact_cands=fact_cands[:5], kept_present=kept_present, kept_share=FP[i][a]["share"], pack_hits={pk: b[1] for pk, b in packs},
                 correctness=c_, declined=dec, parity=PAR[a].get(i))
        if st == "S3": x["s3_sub"] = sub
        if st == "S2": x["s2_sub"] = "router" if not tr["retrieve"] else "search"
        if st == "S4": x["s4_ce"] = (c_ is not None and c_ <= 1.5) or dec
        e[a] = x
    g = [b for pk in KIT["K3"] for b in [POOL[(i, pk)]] if b]
    if g:
        b = max(g, key=lambda b: b[0]); e["gold"] = dict(chunk=b[1], title=b[2], share=b[3], anchor=b[4], bm25_rank=b[5])
    per[i] = e
def count(ids, a):
    c = {s: 0 for s in ("S1", "S2", "S3", "S4", "S5")}; sub = {}
    for i in ids:
        x = per[i][a]; c[x["stage"]] += 1
        for k in ("s2_sub", "s3_sub"):
            if k in x: sub[f"{x['stage']}:{x[k]}"] = sub.get(f"{x['stage']}:{x[k]}", 0) + 1
        if x["stage"] == "S4" and x["s4_ce"]: sub["S4:ce"] = sub.get("S4:ce", 0) + 1
    return dict(n=len(ids), stages=c, sub=dict(sorted(sub.items())))
V01K = [i for i in KEYED if i in V01]; CMK = [i for i in KEYED if i not in V01]
res = dict(method=__doc__.split("Usage:")[0].strip(), replay_dir=RD, n_keyed=len(KEYED),
           parity={a: dict(n=len(PAR[a]), same=sum(PAR[a].values()), differ=sorted(i for i, v in PAR[a].items() if not v)) for a in ARMS},
           funnel={a: {"MAIN keyed 92": count(KEYED, a), "v0.1 keyed 52": count(V01K, a), "cm 40": count(CMK, a)} for a in ARMS})
gold = [i for i in KEYED if "gold" in per[i]]
res["gold_K3"] = dict(n=len(gold), v01=sum(i in V01 for i in gold), cm=sum(i not in V01 for i in gold), ids=gold,
                      by_stage_K3={s: sum(per[i]["K3"]["stage"] == s for i in gold) for s in ("S1", "S2", "S3", "S4", "S5")})
# ---------------- verified variant (hand labels, arms/oracle-real/gold-labels.tsv) ----------------
LAB = {}
for l in open("<workspace>/rnd/research/coordinator/arms/oracle-real/gold-labels.tsv"):
    if l.startswith("#") or l.startswith("item\t") or not l.strip(): continue
    it, ch, lab, src, note = l.rstrip("\n").split("\t")
    if lab in "YP": LAB[it] = dict(chunk=ch, label=lab, source=src)
def vstage(i, a):
    x = per[i][a]
    if x["stage"] in ("S3", "S4", "S5"): return x["stage"]
    if i in LAB and LAB[i]["chunk"].split(":")[1] in KIT[a]: return "S2"
    return "S1"
for i in KEYED:
    for a in ARMS: per[i][a]["vstage"] = vstage(i, a)
    if i in LAB: per[i]["gold_verified"] = LAB[i]
def vcount(ids, a):
    c = {s: 0 for s in ("S1", "S2", "S3", "S4", "S5")}
    for i in ids: c[per[i][a]["vstage"]] += 1
    return dict(n=len(ids), stages=c)
res["funnel_verified"] = {a: {"MAIN keyed 92": vcount(KEYED, a), "v0.1 keyed 52": vcount(V01K, a)} for a in ARMS}
# ---------------- U per item and stage ceilings (MAIN 97 denominators) ----------------
def lp_u(arm):
    by = {}
    for f in sorted(glob.glob(f"{A}litepacks/judgments/lp-{arm}-*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    mean = lambda d: sum(d.values()) / 3
    return {qq: (sum(mean(m["boar"]) for m in v.values()) / 2, sum(mean(m["ref"]) for m in v.values()) / 2) for qq, v in by.items() if len(v) == 2}
UJ = {a: lp_u(a) for a in ARMS}
def us(arm, i):
    t = TR[arm][i]; j = UJ["K0"].get(i) if (arm != "K0" and t["answer"]["text"] == TR["K0"][i]["answer"]["text"]) else UJ[arm].get(i)
    return (0.0 if t["answer"].get("declined") else j[0], j[1])
REFSUM = {a: sum(us(a, i)[1] for i in MAIN) for a in ARMS}
ceil = {}
for a in ARMS:
    ceil[a] = {}
    for key in ("stage", "vstage"):
        for st in ("S1", "S2", "S3", "S4"):
            ids = [i for i in KEYED if per[i][a][key] == st]
            gap = sum(us(a, i)[1] - us(a, i)[0] for i in ids) / REFSUM[a]
            ceil[a][f"{key}:{st}"] = dict(n=len(ids), perfect_fix_dU=round(gap, 3), selftest_prior_dU=round(len(ids) * 0.139 * (sum(us(a, i)[1] for i in ids) / max(1, len(ids))) / REFSUM[a], 3),
                                         real_prior_dU=round(len(ids) * -0.010 * (sum(us(a, i)[1] for i in ids) / max(1, len(ids))) / REFSUM[a], 3))
res["ceilings"] = dict(note="dU on MAIN 97 (ratio-of-sums U) if every item of the stage moved one stage down the funnel: perfect_fix = items reach the reference score; selftest_prior = each item gains FACTPRESENT's self-test cell-(a) +0.139 (relative to its reference score); real_prior = the real-item cell-(a) -0.010.", by_arm=ceil)
res["items"] = per
res["script_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
res["replay_files_sha256"] = {f.rsplit("/", 1)[1]: hashlib.sha256(open(f, "rb").read()).hexdigest() for f in sorted(glob.glob(RD + "/*.traces.jsonl"))}
open(OUTF, "w").write(json.dumps(res, indent=1) + "\n")
print(json.dumps(res["parity"])[:400]); print(json.dumps(res["funnel_verified"])); print(json.dumps(res["ceilings"]["by_arm"]["K3"])); print(json.dumps(res["funnel"], indent=1)); print(json.dumps({k: v for k, v in res["gold_K3"].items() if k != "ids"}))
