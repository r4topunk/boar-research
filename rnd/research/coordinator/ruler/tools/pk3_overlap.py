#!/usr/bin/env python3
"""PK-3 OVERLAP-ARTEFACT (2026-10-21; 0 LLM, 0 generation, 0 judge, 0 paid). Rule frozen in ruler/PK34-criterion.md (sha 0f78d13f...).
Is the self-test K3-K0 pack gain a lexical artefact of pack-written questions? Overlap of question vs gold chunk (J token Jaccard, RANK bm25 rank of
the gold chunk in its own pack, RARE rare-token share, LCS longest common token run) for the self-tests (oracle-facts gold) and the real v0.1
items with a Y/P hand gold (arms/oracle-real/gold-labels.tsv); self-test gain stratified by the REAL-set J tertiles + reweighted to the real
distribution. U per item as factpresent.py (existing Haiku 5.5-low judgments). Usage: python3 -I pk3_overlap.py <out_json>"""
import json, sys, re, glob, random, math, sqlite3, functools, subprocess, hashlib, os, unicodedata
OUTF = sys.argv[1]
R = "<workspace>"; A = R + "/rnd/research/coordinator/arms/"; BE = R + "/boar-eval/bench/"; SD = R + "/shared-data/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
# ---------------- pack readers (build_oracle.py semantics: zstd block, UTF-16 slice, trim) ----------------
_src = open(A + "oracle-st/tools/build_oracle.py").read().split("add, only, facts, missing")[0]
exec(_src)  # pub, article_text, js_slice, js_trim
PF = {"boar-crypto": SD + "crypto/boar-crypto.sqlite", "boar-wikivoyage-en": SD + "packs/boar-wikivoyage-en.sqlite",
      "boar-simplewiki-en": SD + "packs/v3proto/boar-simplewiki-en.sqlite", "boar-factbook": SD + "packs/v3proto/boar-factbook.sqlite",
      "boar-medlineplus-en": SD + "packs/v3proto/boar-medlineplus-en.sqlite", "boar-firstaid-en": SD + "packs/v3proto/boar-firstaid-en.sqlite"}
DBS = {}
def db(path):
    if path not in DBS: DBS[path] = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    return DBS[path]
def chunk(path, cid):
    d = db(path); aid, s, e = d.execute("select article_id, start, end from chunks where id=?", (cid,)).fetchone()
    title = d.execute("select title from articles where id=?", (aid,)).fetchone()[0]
    return title, js_trim(js_slice(article_text(d, path, aid), s, e))
# ---------------- tokens ----------------
STOP = set("the a an and or of to in on for with is are was were be been it its this that as at by from not no but if then than so do does did can could "
           "will would should may might has have had you your they their there which what when where who how why also more most very just only into "
           "out up about over after before such these those other some any all each".split())
def nrm(s):
    s = unicodedata.normalize("NFKC", s or "").lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[‐-―−]", "-", s); return re.sub(r"\s+", " ", s).strip()
toks = lambda s: [w for w in re.findall(r"[a-z0-9][a-z0-9'.%-]*[a-z0-9%]|[a-z0-9]", nrm(s)) if len(w) >= 3 and w not in STOP] or []
def stem(w):
    w = w.replace("'s", "")
    if len(w) > 4 and w.endswith("ies"): return w[:-3] + "y"
    if len(w) > 4 and w.endswith("es") and not w.endswith("ses"): return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"): return w[:-1]
    return w
REF = db(PF["boar-simplewiki-en"]); NREF = REF.execute("select count(*) from chunks").fetchone()[0]
@functools.lru_cache(maxsize=None)
def idf(w):
    try: df = REF.execute("select count(*) from fts where fts match ?", ('"' + w.replace('"', '""') + '"',)).fetchone()[0]
    except sqlite3.OperationalError: df = 0
    return math.log((NREF + 1) / (df + 1))
def fts_or(words): return " OR ".join('"' + w.replace('"', '""') + '"' for w in dict.fromkeys(words) if w)
def bm25_rank(path, q, cid):
    qq = fts_or(toks(q))
    if not qq: return 1001
    for r, (rid,) in enumerate(db(path).execute("select rowid from fts where fts match ? order by rank limit 1000", (qq,)), 1):
        if rid == cid: return r
    return 1001
def lcs(a, b):
    best = 0; prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            if x == y: cur[j] = prev[j - 1] + 1; best = max(best, cur[j])
        prev = cur
    return best
# ---------------- items + gold ----------------
Q = {q["id"]: q for q in rd(BE + "v0.1/questions.public.jsonl")}
for f in glob.glob(BE + "selftest/*/questions.jsonl"):
    for q in rd(f): Q[q["id"]] = q
ORA = json.load(open(A + "oracle-st/tools/oracle-facts.json"))
C80 = [l.strip() for l in open(A + "gemma4-e2b/packs/cand80.ids") if l.strip()]
ST180 = sorted(ORA)
gold_real = {}
for l in open(A + "oracle-real/gold-labels.tsv"):
    if l.startswith("#") or l.startswith("item\t") or not l.strip(): continue
    it, ch, lab = l.rstrip("\n").split("\t")[:3]
    if lab in ("Y", "P") and (it not in gold_real or (lab == "Y" and gold_real[it][1] == "P")): gold_real[it] = (ch, lab)
REAL = sorted(gold_real)
G = {}; shaok = 0
for i in ST180:
    o = ORA[i]; path = pub(o["pack"]); cid = int(o["oracle_chunk"].rsplit(":", 1)[1]); t, x = chunk(path, cid)
    shaok += hashlib.sha256(x.encode()).hexdigest() == o["chunk_text_sha256"]
    G[i] = dict(path=path, cid=cid, title=t, text=x, pack=o["pack"], label="oracle")
for i in REAL:
    ch, lab = gold_real[i]; m = re.match(r"^pack:(?:local-)?([^:]+):(\d+)$", ch); pk, cid = m.group(1), int(m.group(2))
    t, x = chunk(PF[pk], cid); G[i] = dict(path=PF[pk], cid=cid, title=t, text=x, pack=pk, label=lab)
# ---------------- overlap ----------------
allq = {w for i in ST180 + REAL for w in toks(Q[i]["question"])}
idfs = sorted(idf(w) for w in allq); T90 = idfs[int(0.9 * (len(idfs) - 1))]
OV = {}
for i in ST180 + REAL:
    g = G[i]; qt = toks(Q[i]["question"]); gt = toks(g["title"] + "\n" + g["text"]); qs, gs = set(qt), set(gt)
    rare = {w for w in qs if idf(w) >= T90}; gst = {stem(w) for w in gs}
    OV[i] = dict(J=round(len(qs & gs) / len(qs | gs), 4) if qs | gs else 0.0, RANK=bm25_rank(g["path"], Q[i]["question"], g["cid"]),
                 RARE=round(sum(stem(w) in gst for w in rare) / len(rare), 3) if rare else None, n_rare=len(rare), LCS=lcs(qt, gt),
                 nq=len(qs), pack=g["pack"], label=g["label"])
# ---------------- U per item (factpresent.py) ----------------
def lp_tr(arm):
    o = {}
    for f in sorted(glob.glob(f"{A}litepacks/traces/lp-{arm}-*-s42.traces.jsonl")):
        if "smoke" not in f:
            for t in rd(f): o[t["itemId"]] = t
    return o
def lp_j(arm):
    by = {}
    for f in sorted(glob.glob(f"{A}litepacks/judgments/lp-{arm}-*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    o = {}
    for qq, v in by.items():
        if len(v) == 2:
            ms = list(v.values()); mean = lambda d: sum(d.values()) / 3
            o[qq] = (sum(mean(m["boar"]) for m in ms) / 2, sum(mean(m["ref"]) for m in ms) / 2)
    return o
TR = {a: lp_tr(a) for a in ("K0", "K3")}; JJ = {a: lp_j(a) for a in ("K0", "K3")}
SYS = {}
for a in ("K0", "K3"):
    d = {}
    for i, t in TR[a].items():
        j = JJ["K0"].get(i) if (a != "K0" and t["answer"]["text"] == TR["K0"][i]["answer"]["text"]) else JJ[a].get(i)
        if j: d[i] = (0.0 if t["answer"].get("declined") else j[0], j[1])
    SYS["1.7B " + a] = d
def agg(p):
    it = json.load(open(p))["items"]; return {i: (0.0 if v["declined"] else float(v["s"]), float(v["sref"])) for i, v in it.items()}
SYS["Gemma K0"] = agg(A + "gemma4-e2b/packs/aggregates/gemma4-e2b-eng-K0-cand80-s42.json")
SYS["Gemma K3"] = agg(A + "gemma4-e2b/packs/aggregates/gemma4-e2b-eng-K3-cand80-s42.json")
# ---------------- stats ----------------
B = 2000
U = lambda d, ids: sum(d[i][0] for i in ids) / sum(d[i][1] for i in ids)
gain = lambda d1, d0, ids: U(d1, ids) - U(d0, ids)
def pct(xs): xs = sorted(xs); return [round(xs[int(0.025 * B)], 3), round(xs[int(0.975 * B) - 1], 3)]
def pboot(d1, d0, ids):
    if len(ids) < 2: return None
    r = random.Random(11); return pct([gain(d1, d0, s) for s in ([r.choice(ids) for _ in ids] for _ in range(B))])
def quant(xs, p):
    xs = sorted(xs); k = (len(xs) - 1) * p; f = math.floor(k); c = min(f + 1, len(xs) - 1); return xs[f] + (xs[c] - xs[f]) * (k - f)
def spearman(x, y):
    def rk(v):
        o = sorted(range(len(v)), key=lambda k: v[k]); r = [0.0] * len(v); i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]: j += 1
            for k in range(i, j + 1): r[o[k]] = (i + j) / 2
            i = j + 1
        return r
    if len(x) < 3: return None
    a, b = rk(x), rk(y); ma, mb = sum(a) / len(a), sum(b) / len(b)
    num = sum((p - ma) * (q - mb) for p, q in zip(a, b)); den = math.sqrt(sum((p - ma) ** 2 for p in a) * sum((q - mb) ** 2 for q in b))
    return round(num / den, 3) if den else None
def bands(ids, key, c1, c2, low_is_small=True):
    v = lambda i: OV[i][key] if low_is_small else -OV[i][key]
    lo = [i for i in ids if v(i) <= c1]; mid = [i for i in ids if c1 < v(i) <= c2]; hi = [i for i in ids if v(i) > c2]
    return {"low": lo, "mid": mid, "high": hi}
def analyse(sysname, ids, key="J", low_is_small=True):
    d1, d0 = SYS[sysname + " K3"], SYS[sysname + " K0"]; ids = [i for i in ids if i in d1 and i in d0]
    rv = [OV[i][key] if low_is_small else -OV[i][key] for i in REAL]; c1, c2 = quant(rv, 1 / 3), quant(rv, 2 / 3)
    sb = bands(ids, key, c1, c2, low_is_small); rb = bands(REAL, key, c1, c2, low_is_small)
    w = {b: len(rb[b]) / len(REAL) for b in sb}
    # merge bands with < 5 self-test items into mid
    groups = {b: list(sb[b]) for b in sb}; wg = dict(w); merged = []
    for b in ("low", "high"):
        if len(groups[b]) < 5:
            groups["mid"] += groups[b]; wg["mid"] += wg[b]; merged.append(b); groups[b] = []; wg[b] = 0.0
    def rw(gr):
        return sum(wg[b] * gain(d1, d0, gr[b]) for b in gr if wg[b] > 0 and gr[b])
    r = random.Random(11); xs = []
    for _ in range(B):
        xs.append(rw({b: [r.choice(groups[b]) for _ in groups[b]] for b in groups}))
    out = dict(system=sysname, n=len(ids), key=key, cuts_real=[round(c1, 4) if low_is_small else round(-c1, 4), round(c2, 4) if low_is_small else round(-c2, 4)],
               all=dict(d=round(gain(d1, d0, ids), 3), ci=pboot(d1, d0, ids)),
               bands={b: dict(n=len(sb[b]), real_n=len(rb[b]), U0=round(U(d0, sb[b]), 3) if sb[b] else None, U1=round(U(d1, sb[b]), 3) if sb[b] else None,
                              d=round(gain(d1, d0, sb[b]), 3) if sb[b] else None, ci=pboot(d1, d0, sb[b])) for b in sb},
               reweighted=dict(d=round(rw(groups), 3), ci=pct(xs), weights={b: round(wg[b], 3) for b in wg}, merged=merged))
    lo = out["bands"]["low"]; rwd = out["reweighted"]
    kill = (lo["n"] >= 10 and lo["d"] is not None and lo["d"] >= 0.04 and lo["ci"][0] > 0) or (rwd["d"] >= 0.04 and rwd["ci"][0] > 0)
    if lo["n"] >= 10:
        sup = lo["d"] is not None and lo["d"] <= 0.02 and lo["ci"][0] <= 0 <= lo["ci"][1] and rwd["d"] < 0.03
    else:
        sup = rwd["d"] < 0.03 and rwd["ci"][0] <= 0 <= rwd["ci"][1]
    out["verdict"] = "KILL" if kill else "ARTEFACT SUPPORTED" if sup else "PARTIAL (not killed)"
    out["low_band_estimable"] = lo["n"] >= 10
    return out
def desc(ids, key):
    v = [OV[i][key] for i in ids if OV[i][key] is not None]
    return dict(n=len(v), median=round(quant(v, .5), 4), q25=round(quant(v, .25), 4), q75=round(quant(v, .75), 4))
res = dict(method=__doc__.split("Usage:")[0].strip(), criterion_sha256=open(R + "/rnd/research/coordinator/ruler/PK34-criterion.sha256").read().split()[0],
           oracle_text_sha_match=f"{shaok}/{len(ST180)}", T90_idf=round(T90, 3), n_real=len(REAL), real_labels={k: sum(v[1] == k for v in gold_real.values()) for k in "YP"})
res["overlap"] = {k: {"real": desc(REAL, k), "cand80": desc(C80, k), "st180": desc(ST180, k),
                      **{p: desc([i for i in ST180 if ORA[i]["pack"] == p], k) for p in sorted({ORA[i]["pack"] for i in ST180})}} for k in ("J", "RANK", "RARE", "LCS", "nq")}
p90 = quant([OV[i]["J"] for i in REAL], .9)
res["share_selftests_above_real_J_p90"] = dict(real_p90=round(p90, 4), cand80=round(sum(OV[i]["J"] > p90 for i in C80) / 80, 3), st180=round(sum(OV[i]["J"] > p90 for i in ST180) / 180, 3))
res["rank_top1"] = {"real": sum(OV[i]["RANK"] == 1 for i in REAL), "cand80": sum(OV[i]["RANK"] == 1 for i in C80), "st180": sum(OV[i]["RANK"] == 1 for i in ST180)}
res["rank_top10"] = {"real": sum(OV[i]["RANK"] <= 10 for i in REAL), "cand80": sum(OV[i]["RANK"] <= 10 for i in C80), "st180": sum(OV[i]["RANK"] <= 10 for i in ST180)}
res["primary"] = analyse("1.7B", C80, "J")
res["secondary"] = {"Gemma cand80 J": analyse("Gemma", C80, "J"), "1.7B st180 J": analyse("1.7B", ST180, "J"),
                    "1.7B cand80 RANK": analyse("1.7B", C80, "RANK", low_is_small=False), "Gemma cand80 RANK": analyse("Gemma", C80, "RANK", low_is_small=False),
                    "1.7B st180 RANK": analyse("1.7B", ST180, "RANK", low_is_small=False)}
def item_gain(sysname, i):
    d1, d0 = SYS[sysname + " K3"], SYS[sysname + " K0"]; return d1[i][0] / d1[i][1] - d0[i][0] / d0[i][1]
sp = {}
for nm, s, ids in (("1.7B cand80", "1.7B", C80), ("Gemma cand80", "Gemma", C80), ("1.7B st180", "1.7B", ST180), ("1.7B real Y/P", "1.7B", REAL)):
    ids = [i for i in ids if i in SYS[s + " K3"] and i in SYS[s + " K0"]]
    sp[nm] = dict(n=len(ids), J=spearman([OV[i]["J"] for i in ids], [item_gain(s, i) for i in ids]),
                  negRANK=spearman([-OV[i]["RANK"] for i in ids], [item_gain(s, i) for i in ids]))
res["spearman_gain_vs_overlap"] = sp
ids = [i for i in REAL if i in SYS["1.7B K3"] and i in SYS["1.7B K0"]]
res["real_gain_1.7B"] = dict(n=len(ids), d=round(gain(SYS["1.7B K3"], SYS["1.7B K0"], ids), 3), ci=pboot(SYS["1.7B K3"], SYS["1.7B K0"], ids))
# real items at self-test-like overlap: real items with J above the cand80 median, and self-tests inside the real J range
cm = quant([OV[i]["J"] for i in C80], .5); rmax = max(OV[i]["J"] for i in REAL)
hi = [i for i in ids if OV[i]["J"] >= cm]
res["real_at_selftest_overlap"] = dict(cand80_J_median=round(cm, 4), n=len(hi), d=round(gain(SYS["1.7B K3"], SYS["1.7B K0"], hi), 3) if hi else None,
                                       ci=pboot(SYS["1.7B K3"], SYS["1.7B K0"], hi) if len(hi) > 1 else None, ids=hi)
inr = [i for i in C80 if OV[i]["J"] <= rmax and i in SYS["1.7B K3"]]
res["cand80_within_real_J_range"] = dict(real_J_max=rmax, n=len(inr), d=round(gain(SYS["1.7B K3"], SYS["1.7B K0"], inr), 3), ci=pboot(SYS["1.7B K3"], SYS["1.7B K0"], inr))
res["items"] = {i: dict(OV[i], set="real" if i in gold_real else "cand80" if i in C80 else "st180",
                        g17=round(item_gain("1.7B", i), 3) if i in SYS["1.7B K3"] and i in SYS["1.7B K0"] else None,
                        gG=round(item_gain("Gemma", i), 3) if i in SYS["Gemma K3"] and i in SYS["Gemma K0"] else None) for i in ST180 + REAL}
res["script_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
json.dump(res, open(OUTF, "w"), indent=1)
print(json.dumps({k: res[k] for k in ("oracle_text_sha_match", "T90_idf", "n_real", "real_labels", "share_selftests_above_real_J_p90", "rank_top1", "rank_top10", "spearman_gain_vs_overlap", "real_gain_1.7B", "real_at_selftest_overlap", "cand80_within_real_J_range")}, indent=1))
for k in ("J", "RANK", "RARE", "LCS"): print(k, {s: res["overlap"][k][s] for s in ("real", "cand80", "st180")})
for nm, a in [("primary 1.7B cand80 J", res["primary"])] + list(res["secondary"].items()):
    print(nm, a["cuts_real"], "all", a["all"], {b: (v["n"], v["real_n"], v["d"], v["ci"]) for b, v in a["bands"].items()}, "rw", a["reweighted"], "->", a["verdict"])
