#!/usr/bin/env python3
"""FACTPRESENT (2026-10-21, 0 LLM, 0 generation, 0 judge, 0 paid). Do packs lift an answer only when the item's key fact is in the KEPT context?

Inputs
- Kept-context text per item x arm: stub-server replays (0 generation) of the LITEPACKS K0/K1/K3 requests on the mini with the
  RETFLOOR tree at variant `base` (= LITEPACKS behaviour; logs kept chunk ids), adapter --dump-prompts. Job: ruler/tools/mini_fp.sh.
  Replay dir given as argv[1] (holds <K>-V01 / <K>-CM / <K>-ST .traces.jsonl + .prompts.jsonl). Parity vs the LITEPACKS traces is checked
  (kept titles per item) and reported; items whose replay kept titles differ from the judged run are excluded from the cells.
- Key facts (lexical, stated rule, never tuned):
  * bench v0.1: grading.must_any groups + must_k (the precheck contract), matched against the kept context with the vendored
    precheck term semantics (word-boundary terms, re: regexes, echo filter = plain terms that appear in the question are ignored).
    share = groups hit / groups (must_k counts as one group, hit when >= k distinct live terms hit). Items with no lexical key
    (judge-only, firstaid scorer: trv-002, trv-004, dng-001/002/005) are excluded.
  * self-tests (incl. MAIN cooking/money): selftest.in_pack_facts; a fact is hit when its pack quote is a substring of the
    normalised context, or >= 80 % of the quote's content tokens (>= 4 tokens) sit in one kept block, or >= 80 % of the fact
    statement's content tokens (>= 3 tokens) sit in one kept block. share = facts hit / facts.
  * PRESENT (primary) = share >= 0.5; STRICT (sensitivity) = share == 1.
  * self-tests only, cross-check: ORACLE = any oracle fact chunk id (arms/oracle-st/tools/oracle-facts.json) in the kept chunk ids.
- U per item: the existing Haiku 5.5-low judgments (s0 = 0 when declined; K1/K3 reuse K0 rows for byte-identical answers), as
  ruler/tools/inpack_split.py. Systems: 1.7B LITEPACKS K0/K1/K3 (MacBook), Gemma E2B K0/K1 s42 (MAIN), Gemma K0/K3 cand80.
  Gemma/4B kept titles equal the 1.7B's per arm on every item, so the 1.7B replay contexts stand in for them (titles-level parity).
Cells for a contrast Kx - K0: a = present in Kx, absent in K0; b = present in both; c = absent in both; d = present in K0 only.
Delta = U(Kx) - U(K0) (ratio of sums) inside the cell, paired item bootstrap B 2000 seed 11, 2.5/97.5 pct.
Usage: python3 -I factpresent.py <replay_dir> <out_json>"""
import json, sys, re, glob, random, unicodedata, importlib.util, hashlib
RD, OUTF = sys.argv[1], sys.argv[2]
A = "<workspace>/rnd/research/coordinator/arms/"; BE = "<workspace>/boar-eval/bench/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
spec = importlib.util.spec_from_file_location("pc", "<workspace>/boar-eval/scorers/vendor/lantern/precheck.py")
pc = importlib.util.module_from_spec(spec); spec.loader.exec_module(pc)
asg = json.load(open("<workspace>/rnd/research/coordinator/ruler/inpack-assignment.json"))["items"]
KIT = {"K0": {"crypto", "travel"}, "K1": {"crypto", "travel", "general-encyclopedia"},
       "K3": {"crypto", "travel", "general-encyclopedia", "country", "health", "firstaid"}}
MAIN = [l.strip() for l in open(A + "lp-screens/main-97.ids") if l.strip()]
V01 = [l.strip() for l in open(A + "litepacks/data/v01-57.ids") if l.strip()]
# ---------------- questions / key facts ----------------
Q = {q["id"]: q for q in rd(BE + "v0.1/questions.public.jsonl")}
for f in glob.glob(BE + "selftest/*/questions.jsonl"):
    for q in rd(f): Q[q["id"]] = q
ORA = json.load(open(A + "oracle-st/tools/oracle-facts.json"))
# ---------------- contexts from the replay ----------------
def contexts(arm):
    ctx, kept_ids, kept_titles = {}, {}, {}
    for s in ("V01", "CM", "ST"):
        for p in rd(f"{RD}/{arm}-{s}.prompts.jsonl"):
            sysm = next((m["content"] for m in p["messages"] if m["role"] == "system"), "")
            c = sysm.split("\n\nContext:\n", 1)[1] if "\n\nContext:\n" in sysm else ""
            blocks = [b for b in re.split(r"(?:^|\n\n)\[\d+\] ", c) if b.strip()]
            ctx.setdefault(p["itemId"], []).extend(blocks)  # union over the item's generation calls
        for t in rd(f"{RD}/{arm}-{s}.traces.jsonl"):
            i = t["itemId"]; kept_titles[i] = [(k["title"], k.get("section")) for k in t["retrieval"]["kept"]]
            ks = [c for c in t["route"]["reasonCodes"] if c.startswith("retfloor:kept:")]
            kept_ids[i] = {c.replace("pack:local-", "pack:", 1) for c in ks[-1].split(":", 3)[3].split(",")} - {""} if ks else set()  # trace ids carry a "local-" pack prefix
    return ctx, kept_ids, kept_titles
def lp_tr(arm):
    o = {}
    for f in sorted(glob.glob(f"{A}litepacks/traces/lp-{arm}-*-s42.traces.jsonl")):
        if "smoke" not in f:
            for t in rd(f): o[t["itemId"]] = t
    return o
ARMS = ["K0", "K1", "K3"]
CTX, KID, KT = {}, {}, {}
for a in ARMS: CTX[a], KID[a], KT[a] = contexts(a)
TR = {a: lp_tr(a) for a in ARMS}
PAR = {a: {i: KT[a].get(i) == [(k["title"], k.get("section")) for k in TR[a][i]["retrieval"]["kept"]] for i in TR[a]} for a in ARMS}
# ---------------- matching ----------------
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
    g = q.get("grading", {}); text = pc.norm("\n\n".join(blocks)); question = pc.norm(q["question"])
    groups = []
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
        h = (len(quote) >= 12 and quote in whole) or tok_in_block(quote, blocks, 4) or tok_in_block(f.get("fact", ""), blocks, 3)
        hit += bool(h)
    return hit / len(facts) if facts else None
def share(i, arm):
    q = Q[i]; blocks = CTX[arm].get(i, [])
    return share_st(q, blocks) if "selftest" in q else share_v01(q, blocks)
def oracle(i, arm):
    o = ORA.get(i); return None if o is None else bool(set(o["fact_chunks"]) & KID[arm].get(i, set()))
# ---------------- U per item (as inpack_split.py) ----------------
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
J = {a: lp_j(a) for a in ARMS}
SYS = {}
for a in ARMS:
    d = {}
    for i, t in TR[a].items():
        j = J["K0"].get(i) if (a != "K0" and t["answer"]["text"] == TR["K0"][i]["answer"]["text"]) else J[a].get(i)
        if j: d[i] = (0.0 if t["answer"].get("declined") else j[0], j[1])
    SYS["1.7B " + a] = d
def agg(p):
    it = json.load(open(p))["items"]; return {i: (0.0 if v["declined"] else float(v["s"]), float(v["sref"])) for i, v in it.items()}
SYS["Gemma K0 s42"] = agg(A + "gemma4-e2b/stage2/aggregates/gemma4-e2b-eng-K0-main-s42.json")
SYS["Gemma K1 s42"] = agg(A + "gemma4-e2b-confirm/runs/gk1/aggregates/gemma4-e2b-confirm-gk1-K1-main-s42.json")
SYS["Gemma K0 cand80"] = agg(A + "gemma4-e2b/packs/aggregates/gemma4-e2b-eng-K0-cand80-s42.json")
SYS["Gemma K3 cand80"] = agg(A + "gemma4-e2b/packs/aggregates/gemma4-e2b-eng-K3-cand80-s42.json")
SYS["4B K0 s42"] = agg(A + "gemma4-e2b/vs4b/aggregates/gemma4-e2b-vs4b-K0-main-s42.json")
# ---------------- stats ----------------
B = 2000
U = lambda d, ids: sum(d[i][0] for i in ids) / sum(d[i][1] for i in ids)
def pct(xs): xs = sorted(xs); return [round(xs[int(0.025 * B)], 3), round(xs[int(0.975 * B) - 1], 3)]
def pdelta(d1, d0, ids):
    if len(ids) < 2: return None
    r = random.Random(11); xs = []
    for _ in range(B):
        s = [r.choice(ids) for _ in ids]; xs.append(U(d1, s) - U(d0, s))
    return pct(xs)
def ci1(d, ids):
    r = random.Random(11); return pct([U(d, [r.choice(ids) for _ in ids]) for _ in range(B)])
# ---------------- per-item table ----------------
ST = sorted(i for i in TR["K0"] if i.startswith("st-") and not re.match(r"st-qa-(cooking|money)-se-", i))
C80 = [l.strip() for l in open(A + "gemma4-e2b/packs/cand80.ids") if l.strip()]
TOP60 = [i for i in C80 if not i.startswith("st-boar-simplewiki-en-")]
ITEMS = sorted(set(MAIN) | set(ST))
per = {}
for i in ITEMS:
    e = dict(set="v0.1" if i in V01 else "MAIN-cm" if i in MAIN else "selftest", tag=asg[i]["tag"], side=asg[i]["side"],
             parity={a: PAR[a].get(i) for a in ARMS})
    for a in ARMS:
        sh = share(i, a)
        e[a] = dict(share=None if sh is None else round(sh, 3), present=None if sh is None else sh >= 0.5,
                    strict=None if sh is None else sh == 1.0, oracle=oracle(i, a), n_blocks=len(CTX[a].get(i, [])),
                    pack_loaded=asg[i]["tag"] in KIT[a])
    per[i] = e
# ---------------- cells ----------------
def cells(ids, ka, k0, d1, d0, key="present"):
    ids = [i for i in ids if per[i][ka][key] is not None and per[i]["parity"][ka] and per[i]["parity"][k0] and i in d1 and i in d0]
    g = {"a: present in %s only" % ka: [], "b: present in both": [], "c: absent in both": [], "d: present in K0 only": []}
    for i in ids:
        p1, p0 = per[i][ka][key], per[i][k0][key]
        g[("a: present in %s only" % ka) if p1 and not p0 else "b: present in both" if p1 and p0 else "c: absent in both" if not p1 and not p0 else "d: present in K0 only"].append(i)
    o = {}
    for k, v in g.items():
        o[k] = dict(n=len(v), U0=round(U(d0, v), 3) if v else None, U1=round(U(d1, v), 3) if v else None,
                    d=round(U(d1, v) - U(d0, v), 3) if v else None, ci=pdelta(d1, d0, v), ids=v)
    o["all"] = dict(n=len(ids), d=round(U(d1, ids) - U(d0, ids), 3), ci=pdelta(d1, d0, ids))
    return o
IN_MAIN = [i for i in MAIN if per[i]["side"] == "in"]
res = dict(method=__doc__.split("Usage:")[0].strip(), replay_dir=RD,
           parity={a: dict(n=len(PAR[a]), same_kept_titles=sum(PAR[a].values()),
                           differ=sorted(i for i, v in PAR[a].items() if not v)) for a in ARMS},
           keyed=dict(MAIN=sum(per[i]["K0"]["share"] is not None for i in MAIN), v01=sum(per[i]["K0"]["share"] is not None for i in V01),
                      no_key=sorted(i for i in MAIN if per[i]["K0"]["share"] is None)),
           contrasts={})
S17 = {a: SYS["1.7B " + a] for a in ARMS}
for key in ("present", "strict"):
    c = res["contrasts"].setdefault(key, {})
    for nm, ids in [("MAIN 97", MAIN), ("v0.1 57", V01), ("MAIN in-pack", IN_MAIN), ("MAIN-cm 40", [i for i in MAIN if i not in V01])]:
        c[f"1.7B K1-K0 | {nm}"] = cells(ids, "K1", "K0", S17["K1"], S17["K0"], key)
        c[f"1.7B K3-K0 | {nm}"] = cells(ids, "K3", "K0", S17["K3"], S17["K0"], key)
    c["Gemma K1-K0 s42 | MAIN 97"] = cells(MAIN, "K1", "K0", SYS["Gemma K1 s42"], SYS["Gemma K0 s42"], key)
    c["Gemma K1-K0 s42 | v0.1 57"] = cells(V01, "K1", "K0", SYS["Gemma K1 s42"], SYS["Gemma K0 s42"], key)
    # self-test reference (pack-written; upper bound)
    c["1.7B K3-K0 | self-tests topical 60"] = cells(TOP60, "K3", "K0", S17["K3"], S17["K0"], key)
    c["1.7B K3-K0 | self-tests 180"] = cells(ST, "K3", "K0", S17["K3"], S17["K0"], key)
    c["1.7B K1-K0 | self-tests 180"] = cells(ST, "K1", "K0", S17["K1"], S17["K0"], key)
    c["Gemma K3-K0 | self-tests topical 60"] = cells(TOP60, "K3", "K0", SYS["Gemma K3 cand80"], SYS["Gemma K0 cand80"], key)
c = res["contrasts"].setdefault("oracle (self-tests, fact chunk id kept)", {})
c["1.7B K3-K0 | self-tests topical 60"] = cells(TOP60, "K3", "K0", S17["K3"], S17["K0"], "oracle")
c["1.7B K3-K0 | self-tests 180"] = cells(ST, "K3", "K0", S17["K3"], S17["K0"], "oracle")
c["Gemma K3-K0 | self-tests topical 60"] = cells(TOP60, "K3", "K0", SYS["Gemma K3 cand80"], SYS["Gemma K0 cand80"], "oracle")
# lexical rule vs oracle agreement on the 180 self-tests
agree = {}
for a in ARMS:
    xs = [(per[i][a]["present"], per[i][a]["oracle"]) for i in ST if per[i][a]["oracle"] is not None]
    agree[a] = dict(n=len(xs), both=sum(p and o for p, o in xs), lex_only=sum(p and not o for p, o in xs), oracle_only=sum(o and not p for p, o in xs),
                    neither=sum(not p and not o for p, o in xs))
res["lexical_vs_oracle_selftests_180"] = agree
# coverage: share of items whose kept context holds the fact
def cov(ids, a, key="present"):
    v = [per[i][a][key] for i in ids if per[i][a][key] is not None]; return dict(n=len(v), present=sum(v), share=round(sum(v) / len(v), 3) if v else None)
covr = {}
for a in ARMS:
    covr[a] = {"MAIN keyed": cov(MAIN, a), "MAIN in-pack": cov(IN_MAIN, a), "MAIN off-pack": cov([i for i in MAIN if per[i]["side"] == "off"], a),
               "MAIN in-pack, covering pack loaded in arm": cov([i for i in IN_MAIN if per[i][a]["pack_loaded"]], a),
               "MAIN in-pack, covering pack NOT loaded": cov([i for i in IN_MAIN if not per[i][a]["pack_loaded"]], a),
               "v0.1 in-pack": cov([i for i in V01 if per[i]["side"] == "in"], a), "v0.1 off-pack": cov([i for i in V01 if per[i]["side"] == "off"], a),
               "MAIN in-pack (strict)": cov(IN_MAIN, a, "strict"),
               "self-tests 180 (domain pack loaded, tag-level)": cov([i for i in ST if per[i][a]["pack_loaded"]], a),
               "self-tests 180 (domain pack loaded, tag-level, oracle)": cov([i for i in ST if per[i][a]["pack_loaded"]], a, "oracle"),
               "self-tests topical 60": cov(TOP60, a), "self-tests topical 60 (oracle)": cov(TOP60, a, "oracle")}
    covr[a]["by tag (MAIN)"] = {t: cov([i for i in MAIN if per[i]["tag"] == t], a) for t in sorted({per[i]["tag"] for i in MAIN})}
res["coverage"] = covr
# cross-sectional (within K0, any system): U when the fact is present vs absent in the K0 kept context
xs = {}
for nm, d in [("1.7B K0", S17["K0"]), ("Gemma K0 s42", SYS["Gemma K0 s42"]), ("4B K0 s42", SYS["4B K0 s42"]), ("1.7B K3 (K3 context)", S17["K3"])]:
    a = "K3" if "K3" in nm else "K0"
    ids = [i for i in MAIN if per[i][a]["present"] is not None and per[i]["parity"][a] and i in d]
    pr = [i for i in ids if per[i][a]["present"]]; ab = [i for i in ids if not per[i][a]["present"]]
    r = random.Random(11); gaps = []
    for _ in range(B):
        sp = [r.choice(pr) for _ in pr]; sa = [r.choice(ab) for _ in ab]; gaps.append(U(d, sp) - U(d, sa))
    xs[nm] = dict(n_present=len(pr), U_present=round(U(d, pr), 3), ci_present=ci1(d, pr), n_absent=len(ab), U_absent=round(U(d, ab), 3),
                  ci_absent=ci1(d, ab), gap=round(U(d, pr) - U(d, ab), 3), gap_ci=pct(gaps))
res["cross_sectional_MAIN"] = xs
res["items"] = {i: {k: v for k, v in e.items()} for i, e in per.items()}
res["script_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
res["replay_files_sha256"] = {f.rsplit("/", 1)[1]: hashlib.sha256(open(f, "rb").read()).hexdigest() for f in sorted(glob.glob(RD + "/*-*.traces.jsonl") + glob.glob(RD + "/*-*.prompts.jsonl"))}
open(OUTF, "w").write(json.dumps(res, indent=1, sort_keys=False) + "\n")
def show(c):
    for k, v in c.items():
        if k == "all": print(f"    all n {v['n']} d {v['d']} {v['ci']}")
        else: print(f"    {k:28s} n {v['n']:3d} U0 {v['U0']} U1 {v['U1']} d {v['d']} {v['ci']}")
print(json.dumps(res["parity"])[:600]); print(json.dumps(res["keyed"])); print(json.dumps(agree))
for key, cc in res["contrasts"].items():
    print("==", key)
    for nm, c in cc.items(): print("  ", nm); show(c)
print(json.dumps(covr, indent=0)[:4000]); print(json.dumps(xs, indent=0))
