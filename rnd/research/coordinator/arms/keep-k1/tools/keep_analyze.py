#!/usr/bin/env python3
"""KEEP-K1 analysis (0 LLM). Usage: python3 -I keep_analyze.py <out json> <out dir>...
Per variant (KEEP_VARIANT+RETFLOOR_VARIANT): over MAIN 97 / v0.1 57 / PM 180 (the 180 self-tests, own pack):
  s3_fixed      = K1 S3 items (RAG-FUNNEL, 17) whose kept chunk texts newly (vs base) pass the FACTPRESENT/RAG-FUNNEL fact rule (share >= 0.5)
  s3_factcand   = K1 S3 items with one of RAG-FUNNEL's fact_cands chunk ids in the kept set
  keyed_gain/lost = MAIN keyed items (92) whose kept-text fact share crosses 0.5 up/down vs base
  changed       = items whose final kept id set differs from base
  ptok          = prompt tokens (engine approxTokens = ceil(chars/4) over the dumped messages), mean per item; pct vs base
  fact_reach    = PM 180 items with an oracle-facts fact chunk in the kept set (RETFLOOR's metric)."""
import json, sys, glob, os, re, math, sqlite3, functools, importlib.util, unicodedata, collections
from compression import zstd
OUTJ, DIRS = sys.argv[1], sys.argv[2:]
C = "<workspace>/rnd/research/coordinator/"; A = C + "arms/"; BE = "<workspace>/boar-eval/bench/"; SD = "<workspace>/shared-data/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
spec = importlib.util.spec_from_file_location("pc", "<workspace>/boar-eval/scorers/vendor/lantern/precheck.py")
pc = importlib.util.module_from_spec(spec); spec.loader.exec_module(pc)
MAIN = [l.strip() for l in open(A + "lp-screens/main-97.ids") if l.strip()]
V01 = [l.strip() for l in open(A + "litepacks/data/v01-57.ids") if l.strip()]
FACTS = json.load(open(A + "oracle-st/tools/oracle-facts.json")); PM = list(FACTS)
FUN = json.load(open(C + "ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
S3 = {i: v["K1"] for i, v in FUN.items() if v.get("K1", {}).get("stage") == "S3"}
KEYED = list(FUN)
Q = {q["id"]: q for q in rd(BE + "v0.1/questions.public.jsonl")}
for f in glob.glob(BE + "selftest/*/questions.jsonl"):
    for q in rd(f): Q[q["id"]] = q
PF = {"boar-crypto": SD + "crypto/boar-crypto.sqlite", "boar-wikivoyage-en": SD + "packs/boar-wikivoyage-en.sqlite", "boar-simplewiki-en": SD + "packs/v3proto/boar-simplewiki-en.sqlite"}
DB = {k: sqlite3.connect(f"file:{v}?mode=ro", uri=True) for k, v in PF.items()}
@functools.lru_cache(maxsize=4096)
def block(pk, bid): return zstd.decompress(DB[pk].execute("select zdata from blocks where id=?", (bid,)).fetchone()[0])
@functools.lru_cache(maxsize=200000)
def ctext(cid):
    m = re.match(r"^pack:(?:local-)?([^:]+):(\d+)$", cid)
    if not m or m.group(1) not in DB: return None
    pk, i = m.group(1), int(m.group(2))
    r = DB[pk].execute("select article_id, start, end from chunks where id=?", (i,)).fetchone()
    if not r: return None
    b, off, ln, t = DB[pk].execute("select block_id, off, len, title from articles where id=?", (r[0],)).fetchone()
    return t + "\n" + block(pk, b)[off:off + ln].decode("utf-8", "replace")[r[1]:r[2]].strip()
# ---- fact rule copied from ragfunnel.py / factpresent.py ----
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
def present(i, kept):
    txt = [t for t in (ctext(c) for c in kept) if t]
    return bool(txt) and (share(Q[i], txt) or 0) >= 0.5
norm = lambda x: x.replace("pack:local-", "pack:")
# ---- load runs ----
def parse(tr):
    rc = tr["route"]["reasonCodes"]; kept = []
    for c in rc:
        if c.startswith("retfloor:kept:"): kept = [x for x in c.split(":", 3)[3].split(",") if x]
    return kept
runs = collections.defaultdict(dict); ptok = collections.defaultdict(dict)
for d in DIRS:
    for f in glob.glob(d + "/*.traces.jsonl"):
        v = os.path.basename(f).split("-", 1)[0]; s = os.path.basename(f)[len(v) + 1:-len(".traces.jsonl")]
        req = f"{A}retfloor/req/{s}.requests.jsonl"
        if len(rd(f)) != len(rd(req)): continue
        for t in rd(f): runs[v][t["itemId"]] = parse(t)
        pf = f.replace(".traces.jsonl", ".prompts.jsonl")
        if os.path.exists(pf):
            per = collections.Counter()
            for r in rd(pf): per[r["itemId"]] += math.ceil(len(json.dumps(r["messages"])) / 4)
            ptok[v].update(per)
B = "base+base"; assert B in runs, "no base run"
res = {}
for v in sorted(runs, key=lambda x: (x != B, x)):
    R = runs[v]
    if not all(i in R for i in MAIN + PM): print("incomplete", v, sum(i in R for i in MAIN + PM)); continue
    b = runs[B]
    s3_fixed = sorted(i for i in S3 if present(i, R[i]) and not present(i, b[i]))  # newly present vs base (2 S3 items already pass on chunk text in base)
    s3_fc = sorted(i for i in S3 if (set(S3[i]["fact_cands"]) & set(R[i])) and not (set(S3[i]["fact_cands"]) & set(b[i])))
    gain = sorted(i for i in KEYED if present(i, R[i]) and not present(i, b[i])); lost = sorted(i for i in KEYED if present(i, b[i]) and not present(i, R[i]))
    ch = lambda ids: sorted(i for i in ids if set(R[i]) != set(b[i]))
    fr = lambda RR: sum(bool({norm(x) for x in FACTS[i]["fact_chunks"]} & {norm(x) for x in RR[i]}) for i in PM)
    pt = lambda ids: (sum(ptok[v].get(i, 0) for i in ids) / len(ids)) if ptok[v] else None
    res[v] = dict(s3_fixed=len(s3_fixed), s3_fixed_ids=s3_fixed, s3_factcand_kept=len(s3_fc), s3_factcand_ids=s3_fc,
                  keyed_present=sum(present(i, R[i]) for i in KEYED), keyed_gain=gain, keyed_lost=lost,
                  changed_main=len(ch(MAIN)), changed_main_ids=ch(MAIN), changed_v01=len(ch(V01)), changed_pm=len(ch(PM)),
                  kept_chunks_main=sum(len(R[i]) for i in MAIN), kept_chunks_pm=sum(len(R[i]) for i in PM),
                  fact_reach_pm=fr(R), ptok_main=pt(MAIN), ptok_v01=pt(V01), ptok_pm=pt(PM))
for v, r in res.items():
    for k in ("main", "v01", "pm"):
        bb = res[B][f"ptok_{k}"]; r[f"ptok_{k}_pct"] = None if not (bb and r[f"ptok_{k}"]) else round(100 * (r[f"ptok_{k}"] / bb - 1), 1)
# parity of base vs the RAG-FUNNEL K1 replay (MAIN) and the RETFLOOR base (PM)
fun = {}
for s in ("V01", "CM"):
    for t in rd(f"<scratch>"): fun[t["itemId"]] = parse(t)
rf = {}
for f in glob.glob(f"{A}retfloor/out/base-PM-*.traces.jsonl"):
    for t in rd(f): rf[t["itemId"]] = parse(t)
par = dict(main_vs_funnel=sum(fun.get(i) == runs[B][i] for i in MAIN), pm_vs_retfloor=sum(rf.get(i) == runs[B][i] for i in PM) if rf else None,
           s3_present_in_base=sum(present(i, runs[B][i]) for i in S3))
json.dump(dict(parity=par, n_s3=len(S3), s3_sub={i: S3[i].get("s3_sub") for i in S3}, variants=res), open(OUTJ, "w"), indent=1)
print("parity", par, "| S3 n", len(S3))
cols = ["s3_fixed", "s3_factcand_kept", "keyed_present", "changed_main", "changed_v01", "changed_pm", "kept_chunks_main", "fact_reach_pm", "ptok_main", "ptok_main_pct", "ptok_pm_pct"]
print("| variant | " + " | ".join(cols) + " | keyed gain/lost |\n|" + "---|" * (len(cols) + 2))
for v, r in res.items():
    print(f"| {v} | " + " | ".join(str(round(r[c], 1) if isinstance(r[c], float) else r[c]) for c in cols) + f" | {len(r['keyed_gain'])}/{len(r['keyed_lost'])} |")
