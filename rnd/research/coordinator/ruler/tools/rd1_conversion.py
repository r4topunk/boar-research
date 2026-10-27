#!/usr/bin/env python3
"""RD-1 CONVERSION-MAP (2026-10-21; 0 LLM, 0 generation, 0 judge). Criterion ruler/RD1-criterion.md (sha256 84c2c5a2...).
Does fact use (judge correctness >= 4, both-order mean) depend on chunk features when the fact chunk is in the reader's context?
Usage: python3 -I rd1_conversion.py <factpresent_replay_dir> <out_json>"""
import json, sys, re, glob, random, unicodedata, hashlib, math
import numpy as np
RD, OUTF = sys.argv[1], sys.argv[2]
A = "<workspace>/rnd/research/coordinator/arms/"; BE = "<workspace>/boar-eval/bench/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
Q = {q["id"]: q for q in rd(BE + "v0.1/questions.public.jsonl")}
for f in glob.glob(BE + "selftest/*/questions.jsonl"):
    for q in rd(f): Q[q["id"]] = q
BYQ = {q["question"]: i for i, q in Q.items()}
ORA = json.load(open(A + "oracle-st/tools/oracle-facts.json"))
GOLD = json.load(open(A + "chunkclean/gold-chunks.json"))       # read only (CHUNKCLEAN inputs)
EXT = json.load(open(A + "chunkclean/extractions.json"))
GL = {r[0]: r for r in (l.rstrip("\n").split("\t") for l in open(A + "oracle-real/gold-labels.tsv") if not l.startswith("#") and not l.startswith("item\t"))}
OR_IDS = [l.strip() for l in open(A + "oracle-real/items.ids") if l.strip()]
# PACK-HOLES strong patterns (copied from arms/pack-holes/holes.py, unchanged)
src = open(A + "pack-holes/holes.py").read()
ns = {"re": re}; exec(src[src.index("PREP = "):src.index("def u16")], ns)
HOLES = [ns["PATTERNS"][k] for k in ns["STRONG"]]
# ---------------- text helpers ----------------
STOP = set("the a an and or of to in on for with is are was were be been it its this that as at by from not no but if then than so do does did can could "
           "will would should may might has have had you your they their there which what when where who how why also more most very just only into "
           "out up about over after before such these those other some any all each".split())
def nrm(s):
    s = unicodedata.normalize("NFKC", s or "").lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[‐-―−]", "-", s); return re.sub(r"\s+", " ", s).strip()
toks = lambda s: [w for w in re.findall(r"[a-z0-9][a-z0-9'.%-]*[a-z0-9%]|[a-z0-9]", nrm(s)) if len(w) >= 3 and w not in STOP]
def blocks_of(sysm):
    c = sysm.split("\n\nContext:\n", 1)[1] if "\n\nContext:\n" in sysm else ""
    return [b for b in re.split(r"(?:^|\n\n)\[\d+\] ", c) if b.strip()]
def split_tb(b):
    t, _, body = b.partition("\n"); return t.strip(), body.strip()
def sentences(body):
    out, pos = [], 0
    for m in re.finditer(r"[^\n.!?]+(?:[.!?]+|\n|$)", body):
        s = m.group(0)
        if s.strip(): out.append((m.start(), s))
    return out
def locate(body, quote):
    """(char offset of the fact sentence, sentence index) or (None, None)."""
    sents = sentences(body)
    if not sents: return None, None
    nb, nq = body, quote
    i = nb.find(nq) if nq else -1
    if i < 0 and nq:
        i = nrm(nb).find(nrm(nq))
        if i >= 0:  # map normalised offset approximately back by ratio
            i = int(i * len(nb) / max(1, len(nrm(nb))))
    if i >= 0:
        for k, (st, s) in enumerate(sents):
            if st <= i < st + len(s): return st, k
        return i, len(sents) - 1
    tq = set(toks(quote))
    if not tq: return None, None
    best = max(range(len(sents)), key=lambda k: len(tq & set(toks(sents[k][1]))))
    if len(tq & set(toks(sents[best][1]))) / len(tq) >= 0.6: return sents[best][0], best
    return None, None
RES_LINE = re.compile(r"(\|.*\|)|^\s*(?:[-*•#>]|\*\*)|\d+°|\bCategory:|\bFile:|\bImage:")
def residue(body):
    tot = len(body) or 1; bad = 0
    for line in body.split("\n"):
        s = line.strip()
        if not s: continue
        if RES_LINE.search(s) or (len(s) < 40 and not re.search(r"[.!?:;)\"]$", s)): bad += len(line)
    return bad / tot
def feats(blocks, k, fact_quote, ext_span=None):
    t, body = split_tb(blocks[k])
    if ext_span is not None:
        off, si = locate(body, ext_span)
    else:
        off, si = locate(body, fact_quote)
    return dict(tokens=math.ceil(len(body) / 4), slot=k + 1, n_kept=len(blocks), residue=round(residue(body), 4),
                holes=int(any(r.search(body) for r in HOLES)), fact_offset=off, fact_first2=None if si is None else int(si <= 1),
                siblings=sum(1 for j, b in enumerate(blocks) if j != k and split_tb(b)[0] == t))
def find_block(blocks, quote, gold_text=None):
    if gold_text is not None:
        g = set(toks(gold_text))
        sc = [(len(g & set(toks(b))) / max(1, len(g)), j) for j, b in enumerate(blocks)]
        s, j = max(sc) if sc else (0, None)
        return j if s >= 0.8 else None
    nq = nrm(quote)
    for j, b in enumerate(blocks):
        if len(nq) >= 12 and nq in nrm(b): return j
    tq = set(toks(quote))
    for j, b in enumerate(blocks):
        if len(tq) >= 3 and len(tq & set(toks(b))) / len(tq) >= 0.8: return j
    return None
def oracle_quote(i):
    for f in Q[i]["selftest"]["in_pack_facts"]:
        if f.get("chunk_index") is not None: return f.get("quote") or f.get("fact", "")
    return Q[i]["selftest"]["in_pack_facts"][0].get("quote", "")
# ---------------- judgments ----------------
def jrows(files):
    by = {}
    for f in files:
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    o = {}
    for q, v in by.items():
        if len(v) == 2:
            ms = list(v.values()); m3 = lambda d: sum(d.values()) / 3
            o[q] = dict(s=sum(m3(m["boar"]) for m in ms) / 2, sref=sum(m3(m["ref"]) for m in ms) / 2,
                        corr=sum(m["boar"]["correctness"] for m in ms) / 2)
    return o
def lp_tr(arm):
    o = {}
    for f in sorted(glob.glob(f"{A}litepacks/traces/lp-{arm}-*-s42.traces.jsonl")):
        if "smoke" not in f:
            for t in rd(f): o[t["itemId"]] = t
    return o
TR = {a: lp_tr(a) for a in ("K0", "K1", "K3")}
JL = {a: jrows(sorted(glob.glob(f"{A}litepacks/judgments/lp-{a}-*.judgments.jsonl"))) for a in ("K0", "K1", "K3")}
def lp_score(a, i):
    t = TR[a].get(i)
    if not t: return None
    j = JL["K0"].get(i) if (a != "K0" and t["answer"]["text"] == TR["K0"][i]["answer"]["text"]) else JL[a].get(i)
    if not j: return None
    return dict(j, s=0.0 if t["answer"].get("declined") else j["s"], gen=(t["timing"].get("outputTokens") or 0) > 0)
# ---------------- replay contexts (1.7B; FACTPRESENT) ----------------
def replay(arm):
    pr, kid, kt = {}, {}, {}
    for s in ("V01", "CM", "ST"):
        for p in rd(f"{RD}/{arm}-{s}.prompts.jsonl"):
            sysm = next((m["content"] for m in p["messages"] if m["role"] == "system"), "")
            b = blocks_of(sysm)
            if b: pr.setdefault(p["itemId"], []).append(b)
        for t in rd(f"{RD}/{arm}-{s}.traces.jsonl"):
            i = t["itemId"]; kt[i] = [(k["title"], k.get("section")) for k in t["retrieval"]["kept"]]
            ks = [c for c in t["route"]["reasonCodes"] if c.startswith("retfloor:kept:")]
            kid[i] = {c.replace("pack:local-", "pack:", 1) for c in ks[-1].split(":", 3)[3].split(",")} - {""} if ks else set()
    return pr, kid, kt
RP = {a: replay(a) for a in ("K1", "K3")}
rows = []
def add(reader, arm, i, blocks_list, score, quote=None, gold_text=None, ext=None, kind=""):
    if score is None or not score.get("gen", True): return
    for blocks in blocks_list:
        k = find_block(blocks, quote, gold_text)
        if k is not None:
            f = feats(blocks, k, quote, ext)
            q = Q[i]; fam = "v0.1" if "selftest" not in q else ("SE" if i.startswith("st-qa-") else "topic")
            pack = q["selftest"]["pack"] if "selftest" in q else GOLD[i]["pack"]
            rows.append(dict(reader=reader, arm=arm, item=i, conv=int(score["corr"] >= 4), corr=score["corr"], s=score["s"], sref=score["sref"],
                             pack=pack, qtype=q.get("category"), family=fam, kind=kind, **f))
            return
ST = sorted(i for i in Q if i.startswith("st-") and not re.match(r"st-qa-(cooking|money)-se-", i))
# R-A / R-B: 1.7B LITEPACKS K3 / K1 self-tests
for a, tag in (("K3", "R-A"), ("K1", "R-B")):
    pr, kid, _ = RP[a]
    for i in ST:
        o = ORA.get(i)
        if o and set(o["fact_chunks"]) & kid.get(i, set()):
            add("1.7B", a, i, pr.get(i, []), lp_score(a, i), quote=oracle_quote(i), kind=tag)
# R-C: 1.7B K3 v0.1 with the ORACLE-REAL gold chunk kept
pr, kid, kt3 = RP["K3"]
for i in OR_IDS:
    g = GOLD[i]; gid = f"pack:{g['pack']}:{g['chunk_id']}"
    if gid in kid.get(i, set()):
        add("1.7B", "K3", i, pr.get(i, []), lp_score("K3", i), quote=EXT[i]["spans"][0], ext=EXT[i]["spans"][0], kind="R-C")  # kept blocks are compressed excerpts: match the fact span, not the whole chunk
# R-D: ORACLE-REAL arm (gold in [1]); context = gold block + the kept list (no prompt dump)
ORR = json.load(open(A + "oracle-real/aggregates/oracle-real.json"))["items"]
for t in rd(A + "oracle-real/traces/oracle-K3-v01gold-s42.traces.jsonl"):
    i = t["itemId"]; g = GOLD[i]; o = ORR[i]["oracle"]
    if not (t["timing"].get("outputTokens") or 0): continue
    kept = t["retrieval"]["kept"]
    blocks = [g["title"] + "\n" + g["text"]] + [k["title"] + "\n" for k in kept[1:]]
    sc = dict(corr=o["corr"], s=0.0 if o["declined"] else o["s"], sref=o["sref"], gen=True)
    add("1.7B", "ORACLE", i, [blocks], sc, gold_text=g["text"], ext=EXT[i]["spans"][0], kind="R-D")
# R-E / R-F: Gemma / 4B K3 cand80 on the 1.7B K3 replay context when kept titles match
C80 = [l.strip() for l in open(A + "gemma4-e2b/packs/cand80.ids") if l.strip()]
for reader, tr_f, ag_f, tag in (("Gemma", A + "gemma4-e2b/packs/traces/gemma4-e2b-eng-K3-cand80-s42.traces.jsonl", A + "gemma4-e2b/packs/aggregates/gemma4-e2b-eng-K3-cand80-s42.json", "R-E"),
                                ("4B", A + "coverage-matrix/q4b/traces/q4b-K3-cand80-s42.traces.jsonl", A + "coverage-matrix/q4b/aggregates/q4b-K3-cand80-s42.json", "R-F")):
    trs = {t["itemId"]: t for t in rd(tr_f)}; ag = json.load(open(ag_f))["items"]
    for i in C80:
        t = trs.get(i); v = ag.get(i); o = ORA.get(i)
        if not t or not v or not o or v.get("corr") is None: continue
        if [(k["title"], k.get("section")) for k in t["retrieval"]["kept"]] != kt3.get(i): continue
        if not (set(o["fact_chunks"]) & kid.get(i, set())) or not (t["timing"].get("outputTokens") or 0): continue
        add(reader, "K3", i, pr.get(i, []), dict(corr=v["corr"], s=0.0 if v.get("declined") else v["s"], sref=v["sref"], gen=True), quote=oracle_quote(i), kind=tag)
# R-G: 4B ORACLE-ST ADD (prompts dumped)
JG = jrows(sorted(glob.glob(A + "oracle-st/runs/st-*-cut7-oracleadd-s42.judgments.jsonl")))
for f in sorted(glob.glob(A + "oracle-st/runs/st-*-cut7-oracleadd-s42.prompts.jsonl")):
    seen = {}
    for p in rd(f):
        i = BYQ.get(p["query"])
        if i is None: continue
        sysm = next((m["content"] for m in p["prompt"] if m["role"] == "system"), "")
        b = blocks_of(sysm)
        if b: seen.setdefault(i, []).append(b)
    for i, bl in seen.items():
        j = JG.get(i)
        if j: add("4B", "ORACLE-ST-ADD", i, bl, dict(j, gen=True), quote=oracle_quote(i), kind="R-G")
# ---------------- stats ----------------
B, SEED = 2000, 11
CONT = ["tokens", "slot", "n_kept", "residue", "fact_offset", "siblings"]
BIN = ["holes", "fact_first2"]
def pct(xs):
    xs = sorted(x for x in xs if x is not None and not math.isnan(x))
    if len(xs) < 50: return None
    return [round(xs[int(0.025 * len(xs))], 3), round(xs[int(0.975 * len(xs)) - 1], 3)]
def clusters(R):
    c = {}
    for r in R: c.setdefault(r["item"], []).append(r)
    return c
def boot(R, stat):
    c = clusters(R); keys = list(c); rng = random.Random(SEED); out = []
    for _ in range(B):
        s = [r for k in (rng.choice(keys) for _ in keys) for r in c[k]]
        try: out.append(stat(s))
        except (ZeroDivisionError, ValueError, np.linalg.LinAlgError): out.append(float("nan"))
    return pct(out)
def terc_cuts(R, f):
    v = sorted(r[f] for r in R if r[f] is not None)
    c1, c2 = v[len(v) // 3], v[(2 * len(v)) // 3]
    return c1, c2, not any(x < c1 for x in v)
def tercile(r, f, cuts):
    """0 bottom / 1 mid / 2 top; ties: bottom = x < c1 (x <= c1 when nothing is below c1), top = x >= c2 (x > c1 when c2 == c1)."""
    x = r[f]
    if x is None: return None
    c1, c2, lo_incl = cuts[0], cuts[1], cuts[2] if len(cuts) > 2 else False
    if (x <= c1) if lo_incl else (x < c1): return 0
    if (x >= c2) if c2 > c1 else (x > c1): return 2
    return 1
def rate(R): return sum(r["conv"] for r in R) / len(R)
def terc_stat(R, f, cuts):
    lo = [r for r in R if tercile(r, f, cuts) == 0]; hi = [r for r in R if tercile(r, f, cuts) == 2]
    return rate(hi) - rate(lo)
def bin_stat(R, f):
    a = [r for r in R if r[f] == 1]; b = [r for r in R if r[f] == 0]
    return rate(a) - rate(b)
def logit(R, fs, mu=None, sd=None):
    X = np.array([[r[f] if r[f] is not None else np.nan for f in fs] for r in R], float); y = np.array([r["conv"] for r in R], float)
    ok = ~np.isnan(X).any(1); X, y = X[ok], y[ok]
    if mu is None: mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = np.c_[np.ones(len(X)), (X - mu) / sd]; w = np.zeros(Z.shape[1]); lam = np.eye(Z.shape[1]); lam[0, 0] = 0
    for _ in range(50):
        p = 1 / (1 + np.exp(-Z @ w)); W = p * (1 - p)
        H = Z.T @ (Z * W[:, None]) + lam; g = Z.T @ (y - p) - lam @ w
        step = np.linalg.solve(H, g); w += step
        if np.abs(step).max() < 1e-8: break
    return w[1:], mu, sd
def per_reader(R, name):
    out = dict(n_rows=len(R), n_items=len(clusters(R)), conv_rate=round(rate(R), 3), terciles={}, binary={}, logistic={})
    for f in CONT:
        Rf = [r for r in R if r[f] is not None]
        if len(Rf) < 15: continue
        cuts = terc_cuts(Rf, f)
        if not any(tercile(r, f, cuts) == 0 for r in Rf) or not any(tercile(r, f, cuts) == 2 for r in Rf):
            out["terciles"][f] = dict(note="degenerate (one value)"); continue
        tb = {}
        for t in (0, 1, 2):
            g = [r for r in Rf if tercile(r, f, cuts) == t]; tb[["bottom", "mid", "top"][t]] = dict(n=len(g), rate=round(rate(g), 3) if g else None)
        d = terc_stat(Rf, f, cuts)
        out["terciles"][f] = dict(cuts=[round(c, 3) for c in cuts[:2]] + [cuts[2]], **tb, top_minus_bottom=round(d, 3), ci=boot(Rf, lambda s: terc_stat(s, f, cuts)))
    for f in BIN:
        Rf = [r for r in R if r[f] is not None]
        n1 = sum(r[f] for r in Rf)
        if n1 < 3 or n1 > len(Rf) - 3: out["binary"][f] = dict(n1=n1, n0=len(Rf) - n1, note="too few"); continue
        out["binary"][f] = dict(n1=n1, n0=len(Rf) - n1, rate1=round(rate([r for r in Rf if r[f] == 1]), 3), rate0=round(rate([r for r in Rf if r[f] == 0]), 3),
                                diff=round(bin_stat(Rf, f), 3), ci=boot(Rf, lambda s: bin_stat(s, f)))
    fs = [f for f in CONT + BIN if len({r[f] for r in R if r[f] is not None}) > 1]
    w, mu, sd = logit(R, fs)
    cis = {}
    c = clusters(R); keys = list(c); rng = random.Random(SEED); W = []
    for _ in range(B):
        s = [r for k in (rng.choice(keys) for _ in keys) for r in c[k]]
        try: W.append(logit(s, fs, mu, sd)[0])
        except Exception: pass
    W = np.array(W)
    for j, f in enumerate(fs):
        out["logistic"][f] = dict(coef_per_sd=round(float(w[j]), 3), ci=pct(list(W[:, j])))
    return out
R17 = [r for r in rows if r["reader"] == "1.7B"]; RG = [r for r in rows if r["reader"] == "Gemma"]; R4 = [r for r in rows if r["reader"] == "4B"]
res = dict(criterion_sha256=open("<workspace>/rnd/research/coordinator/ruler/RD1-criterion.sha256").read().split()[0],
           rows_by_kind={k: sum(r["kind"] == k for r in rows) for k in ("R-A", "R-B", "R-C", "R-D", "R-E", "R-F", "R-G")},
           readers={"1.7B": per_reader(R17, "1.7B"), "Gemma": per_reader(RG, "Gemma") if len(RG) >= 15 else None, "4B": per_reader(R4, "4B")})
# 1.7B self-test only (R-A + R-B) sensitivity and v0.1 only
res["readers"]["1.7B self-tests (R-A+R-B)"] = per_reader([r for r in R17 if r["kind"] in ("R-A", "R-B")], "")
res["readers"]["1.7B v0.1 (R-C+R-D)"] = per_reader([r for r in R17 if r["kind"] in ("R-C", "R-D")], "")
# slope difference 1.7B - 4B per feature (logistic per sd on the union scale)
U2 = R17 + R4; fs = [f for f in CONT + BIN if len({r[f] for r in U2 if r[f] is not None}) > 1]
_, mu, sd = logit(U2, fs)
def sdiff(s):
    a = [r for r in s if r["reader"] == "1.7B"]; b = [r for r in s if r["reader"] == "4B"]
    return logit(a, fs, mu, sd)[0] - logit(b, fs, mu, sd)[0]
pt = sdiff(U2); c = clusters(U2); keys = list(c); rng = random.Random(SEED); D = []
for _ in range(B):
    s = [r for k in (rng.choice(keys) for _ in keys) for r in c[k]]
    try: D.append(sdiff(s))
    except Exception: pass
D = np.array(D)
res["slope_diff_1.7B_minus_4B"] = {f: dict(diff=round(float(pt[j]), 3), ci=pct(list(D[:, j]))) for j, f in enumerate(fs)}
# ceiling per feature (1.7B), base R-A rows
RA = [r for r in R17 if r["kind"] == "R-A"]
conv_u = [r["s"] / r["sref"] for r in RA if r["conv"]]; un_u = [r["s"] / r["sref"] for r in RA if not r["conv"]]
ugap = (sum(conv_u) / len(conv_u)) - (sum(un_u) / len(un_u))
ceil = {}
r17 = res["readers"]["1.7B"]
for f, v in r17["terciles"].items():
    if "note" in v: continue
    rates = [v[k]["rate"] for k in ("bottom", "mid", "top") if v[k]["rate"] is not None]
    best, worst = max(rates), min(rates)
    wk = ["bottom", "mid", "top"][[v["bottom"]["rate"], v["mid"]["rate"], v["top"]["rate"]].index(worst)]
    cuts = v["cuts"]; nw = sum(1 for r in RA if r[f] is not None and ["bottom", "mid", "top"][tercile(r, f, cuts)] == wk)
    ceil[f] = dict(best_minus_worst=round(best - worst, 3), worst_tercile=wk, n_worst_RA=nw, U_ceiling_180=round((best - worst) * nw * ugap / 180, 4))
for f, v in r17["binary"].items():
    if "diff" in v:
        nw = sum(1 for r in RA if r[f] == (0 if v["diff"] > 0 else 1))
        ceil[f] = dict(best_minus_worst=round(abs(v["diff"]), 3), n_worst_RA=nw, U_ceiling_180=round(abs(v["diff"]) * nw * ugap / 180, 4))
res["ceiling"] = dict(U_gap_converted_minus_unconverted_RA=round(ugap, 3), n_RA=len(RA), per_feature=ceil)
# by pack / family / qtype (1.7B, descriptive)
def grp(R, key):
    g = {}
    for r in R: g.setdefault(r[key], []).append(r)
    return {k: dict(n=len(v), rate=round(rate(v), 3)) for k, v in sorted(g.items(), key=lambda kv: -len(kv[1]))}
res["descriptive_1.7B"] = dict(pack=grp(R17, "pack"), family=grp(R17, "family"), qtype=grp(R17, "qtype"), kind=grp(R17, "kind"))
res["descriptive_4B"] = dict(pack=grp(R4, "pack"), kind=grp(R4, "kind"))
# verdict
sig = []
for f, v in r17["terciles"].items():
    if "note" in v: continue
    if v["ci"] and abs(v["top_minus_bottom"]) >= 0.10 and (v["ci"][0] > 0 or v["ci"][1] < 0): sig.append(f)
for f, v in r17["binary"].items():
    if "diff" in v and v["ci"] and abs(v["diff"]) >= 0.10 and (v["ci"][0] > 0 or v["ci"][1] < 0): sig.append(f)
cands = sorted(((abs(v.get("top_minus_bottom", v.get("diff", 0))), f) for f, v in [(k, x) for k, x in r17["terciles"].items() if "note" not in x] + [(k, x) for k, x in r17["binary"].items() if "diff" in x]), reverse=True)
top3 = [f for _, f in cands[:3]]
best_ceiling = max((ceil[f]["U_ceiling_180"] for f in sig), default=0)
res["verdict"] = dict(features_10pp_ci_excl_0=sig, top3_by_abs_diff=top3, best_sig_ceiling=best_ceiling,
                      kill=(not sig) or best_ceiling < 0.03)
res["rows"] = rows
res["script_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
open(OUTF, "w").write(json.dumps(res, indent=1) + "\n")
print(json.dumps({k: v for k, v in res.items() if k not in ("rows",)}, indent=1)[:12000])
