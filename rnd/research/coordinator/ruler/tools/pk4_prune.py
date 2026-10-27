#!/usr/bin/env python3
"""PK-4 PACK-PRUNE (2026-10-21; 0 LLM, 0 generation, 0 judge, 0 paid). Rule frozen in ruler/PK34-criterion.md (sha 0f78d13f...).
Under A-union (KA: crypto, wikivoyage, visa, factbook, medlineplus, firstaid), which packs ever reach the kept context on dev items?
Input: pk4_replay.sh out dir with <ARM>-{V01,CM,ST}.traces.jsonl + .prompts.jsonl; ARM = KA (full) and KA-minus-<pack...> variants.
Per item x pack: raw (fun:raw), dense (fun:dense), kept (retfloor:kept) chunk ids; fact contribution = a kept id equal to the item's gold
(self-tests: oracle-facts fact_chunks; v0.1: gold-labels.tsv Y/P). Variant diff vs KA: kept titles (title+section, in order) and the dumped
Context block bytes (union over the item's generation calls). Usage: python3 -I pk4_prune.py <out dir> <out json>"""
import json, sys, re, glob, hashlib, sqlite3, math, collections
RD, OUTF = sys.argv[1], sys.argv[2]
R = "<workspace>"; A = R + "/rnd/research/coordinator/arms/"; SD = R + "/shared-data/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
PACKS = ["boar-crypto", "boar-wikivoyage-en", "boar-visa-en", "boar-factbook", "boar-medlineplus-en", "boar-firstaid-en"]
MAIN = [l.strip() for l in open(A + "lp-screens/main-97.ids") if l.strip()]
V01 = [l.strip() for l in open(A + "litepacks/data/v01-57.ids") if l.strip()]
ORA = json.load(open(A + "oracle-st/tools/oracle-facts.json")); ST = sorted(ORA)
GOLD = {}
for l in open(A + "oracle-real/gold-labels.tsv"):
    if l.startswith("#") or l.startswith("item\t") or not l.strip(): continue
    it, ch, lab = l.rstrip("\n").split("\t")[:3]
    if lab in ("Y", "P"): GOLD.setdefault(it, set()).add(ch)
for i, o in ORA.items(): GOLD[i] = set(o["fact_chunks"])
OWN = {i: ORA[i]["pack"] for i in ST}
norm = lambda c: c.replace("pack:local-", "pack:", 1)
pk_of = lambda c: (re.match(r"^pack:([^:]+):\d+$", c) or [None, None])[1]
def codes(t, pre):
    ks = [c for c in t["route"]["reasonCodes"] if c.startswith(pre)]
    return [norm(x) for x in ks[-1][len(pre):].split(",") if x] if ks else []
def kept_ids(t):
    ks = [c for c in t["route"]["reasonCodes"] if c.startswith("retfloor:kept:")]
    return [norm(x) for x in ks[-1].split(":", 3)[3].split(",") if x] if ks else []
def load(arm):
    tr, ctx = {}, {}
    for s in ("V01", "CM", "ST"):
        f = f"{RD}/{arm}-{s}.traces.jsonl"
        if not glob.glob(f): continue
        for t in rd(f): tr[t["itemId"]] = t
        for p in rd(f"{RD}/{arm}-{s}.prompts.jsonl"):
            sysm = next((m["content"] for m in p["messages"] if m["role"] == "system"), "")
            c = sysm.split("\n\nContext:\n", 1)[1] if "\n\nContext:\n" in sysm else ""
            ctx.setdefault(p["itemId"], []).append(c)
    return tr, ctx
ARMS = sorted({re.sub(r"-(V01|CM|ST)\.traces\.jsonl$", "", f.split("/")[-1]) for f in glob.glob(RD + "/*.traces.jsonl")})
D = {a: load(a) for a in ARMS}
TR, CTX = D["KA"]
ALL = sorted(TR)
# parity vs the judged KA traces (coverage-matrix, mini)
par = {}
for f in glob.glob(A + "coverage-matrix/q17/traces/*KA*.traces.jsonl"):
    for t in rd(f):
        i = t["itemId"]
        if i in TR: par[i] = [(k["title"], k.get("section")) for k in t["retrieval"]["kept"]] == [(k["title"], k.get("section")) for k in TR[i]["retrieval"]["kept"]]
per = {}
for i in ALL:
    t = TR[i]; raw, dense, kept = codes(t, "fun:raw:"), codes(t, "fun:dense:"), kept_ids(t)
    per[i] = dict(set="v0.1" if i in V01 else "MAIN-cm" if i in MAIN else "selftest" if i in ORA else "other",
                  own=OWN.get(i), retrieve=any(c == "retrieve:yes" or c.startswith("retrieve:yes") for c in t["route"]["reasonCodes"]),
                  raw=collections.Counter(pk_of(c) for c in raw), dense=collections.Counter(pk_of(c) for c in dense), kept=collections.Counter(pk_of(c) for c in kept),
                  fact_kept=sorted({pk_of(c) for c in kept if c in GOLD.get(i, set())}), kept_ids=kept)
DEV = [i for i in ALL if per[i]["set"] in ("v0.1", "MAIN-cm", "selftest")]
def dev_for(p): return [i for i in DEV if per[i]["own"] != p]
tab = {}
for p in PACKS:
    ids = dev_for(p)
    by = {s: [i for i in ids if per[i]["set"] == s] for s in ("v0.1", "MAIN-cm", "selftest")}
    tab[p] = dict(n_dev=len(ids),
                  raw_items=sum(per[i]["raw"][p] > 0 for i in ids), dense_items=sum(per[i]["dense"][p] > 0 for i in ids),
                  kept_items=sum(per[i]["kept"][p] > 0 for i in ids), kept_chunks=sum(per[i]["kept"][p] for i in ids),
                  fact_kept_items=sum(p in per[i]["fact_kept"] for i in ids),
                  kept_items_by_set={s: sum(per[i]["kept"][p] > 0 for i in v) for s, v in by.items()},
                  fact_kept_by_set={s: sum(p in per[i]["fact_kept"] for i in v) for s, v in by.items()},
                  own_selftests=dict(n=sum(per[i]["own"] == p for i in ALL), kept_items=sum(per[i]["own"] == p and per[i]["kept"][p] > 0 for i in ALL),
                                     fact_kept=sum(per[i]["own"] == p and p in per[i]["fact_kept"] for i in ALL)),
                  kept_item_ids=[i for i in ids if per[i]["kept"][p] > 0][:40])
cands = [p for p in PACKS if tab[p]["kept_items"] <= 2]
# latency (AUNION-PIXEL aunion73-a sql ms per db / 73)
S = json.load(open(A + "aunion-pixel/aunion73-a/aunion-summary.json"))
lat = {p: round(S["sql_ms_by_db"].get(p + ".sqlite", 0) / 1000 / S["rows"], 3) for p in PACKS}
phone_hits = S["pack_hits_questions"]
# variant diffs
var = {}
for a in ARMS:
    if a == "KA": continue
    tr2, ctx2 = D[a]; ids = [i for i in ALL if i in tr2]
    kt = lambda T, i: [(k["title"], k.get("section")) for k in T[i]["retrieval"]["kept"]]
    dt = [i for i in ids if kt(TR, i) != kt(tr2, i)]; dc = [i for i in ids if "\x00".join(CTX.get(i, [])) != "\x00".join(ctx2.get(i, []))]
    dev = [i for i in ids if i in DEV]
    var[a] = dict(n=len(ids), titles_differ=len(dt), context_bytes_differ=len(dc), context_bytes_differ_pct=round(100 * len(dc) / len(ids), 2) if ids else None,
                  dev_n=len(dev), dev_context_differ=sum(i in dc for i in dev), ids_context_differ=dc[:50],
                  answers_differ_note="stub server: answers are not generated; the Context block is what the model would read")
# medlineplus probe
MP = SD + "packs/v3proto/boar-medlineplus-en.sqlite"; mdb = sqlite3.connect(f"file:{MP}?mode=ro", uri=True)
STOP = set("the a an and or of to in on for with is are was were be been it its this that as at by from not no but if then than so do does did can could will would should may might has have had you your they their there which what when where who how why also more most very just only into out up about over after before such these those other some any all each".split())
toks = lambda s: [w for w in re.findall(r"[a-z0-9][a-z0-9'.%-]*[a-z0-9%]|[a-z0-9]", (s or "").lower()) if len(w) >= 3 and w not in STOP]
Q = {q["id"]: q for q in rd(R + "/boar-eval/bench/v0.1/questions.public.jsonl")}
for f in glob.glob(R + "/boar-eval/bench/selftest/*/questions.jsonl"):
    for q in rd(f): Q[q["id"]] = q
probe = {}
health = [i for i in ALL if re.match(r"^(lan|vit)-hlt-|^dng-", i)] + [i for i in ALL if per[i]["own"] == "boar-medlineplus-en"]
for i in health:
    qq = " OR ".join('"' + w + '"' for w in dict.fromkeys(toks(Q[i]["question"])))
    top = [r[0] for r in mdb.execute("select rowid from fts where fts match ? order by rank limit 50", (qq,))] if qq else []
    g = sorted(int(c.rsplit(":", 1)[1]) for c in GOLD.get(i, set()) if c.startswith("pack:boar-medlineplus-en:"))
    probe[i] = dict(retrieve=per[i]["retrieve"], medl_fts_top50=len(top), medl_gold=g, medl_gold_rank=[(top.index(c) + 1 if c in top else None) for c in g],
                    raw=per[i]["raw"]["boar-medlineplus-en"], dense=per[i]["dense"]["boar-medlineplus-en"], kept=per[i]["kept"]["boar-medlineplus-en"],
                    kept_packs=dict(per[i]["kept"]), fact_kept=per[i]["fact_kept"])
pruned = [p for p in cands if tab[p]["kept_items"] == 0]
joint = next((v for a, v in var.items() if a == "KA-minus-" + "+".join(sorted(pruned))), None)
kill = all(tab[p]["kept_items"] >= 3 for p in PACKS) or any(v["context_bytes_differ_pct"] is not None and v["context_bytes_differ_pct"] > 2 and
                                                              set(a.replace("KA-minus-", "").split("+")) <= set(cands) for a, v in var.items())
sup = len(pruned) >= 2 and joint is not None and joint["context_bytes_differ_pct"] <= 2 and sum(lat[p] for p in pruned) >= 0.3
res = dict(method=__doc__.split("Usage:")[0].strip(), criterion_sha256=open(R + "/rnd/research/coordinator/ruler/PK34-criterion.sha256").read().split()[0],
           arms=ARMS, n_items=len(ALL), n_dev=len(DEV), parity_vs_judged_KA=dict(n=len(par), same=sum(par.values()), differ=sorted(i for i, v in par.items() if not v)),
           per_pack=tab, candidates_le2=cands, zero_kept=pruned, latency_s_per_question_pixel=lat, phone_pack_hits_questions_aunion73=phone_hits,
           variants=var, medlineplus_probe=probe,
           verdict="KILL" if kill else "SUPPORTED" if sup else "PARTIAL",
           saving_s=round(sum(lat[p] for p in pruned), 3),
           items={i: dict(set=per[i]["set"], own=per[i]["own"], retrieve=per[i]["retrieve"], raw=dict(per[i]["raw"]), dense=dict(per[i]["dense"]), kept=dict(per[i]["kept"]),
                          fact_kept=per[i]["fact_kept"]) for i in ALL},
           replay_files_sha256={f.split("/")[-1]: hashlib.sha256(open(f, "rb").read()).hexdigest() for f in sorted(glob.glob(RD + "/*.jsonl"))},
           script_sha256=hashlib.sha256(open(__file__, "rb").read()).hexdigest())
json.dump(res, open(OUTF, "w"), indent=1)
print(json.dumps({k: res[k] for k in ("arms", "n_items", "n_dev", "parity_vs_judged_KA", "candidates_le2", "zero_kept", "latency_s_per_question_pixel", "phone_pack_hits_questions_aunion73", "verdict", "saving_s")}, indent=1))
for p in PACKS: print(p, {k: v for k, v in tab[p].items() if k != "kept_item_ids"})
for a, v in var.items(): print(a, {k: x for k, x in v.items() if k not in ("ids_context_differ", "answers_differ_note")}, v["ids_context_differ"][:12])
for i, v in probe.items(): print(i, v)
