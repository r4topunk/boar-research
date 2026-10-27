#!/usr/bin/env python3
"""NATIVE-PARITY stage comparison (0 LLM). Usage: python3 -I tools/agg.py  (from anywhere; absolute paths)
His side: work/out/{kb,kbpacks,kbvital5}.jsonl (harness). Ours: LITEPACKS K0/K1 traces (MacBook, 1.7B, s42) + RAG-FUNNEL K0/K1.
Fact rule = FACTPRESENT's (copied from ruler/tools/ragfunnel.py, itself copied from factpresent.py), share >= 0.5 on the kept bodies."""
import json, re, glob, unicodedata, importlib.util, statistics, hashlib, random
B = "<workspace>/"; ARM = B + "rnd/research/coordinator/arms/native-parity/"; W = ARM + "work/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
spec = importlib.util.spec_from_file_location("pc", B + "boar-eval/scorers/vendor/lantern/precheck.py")
pc = importlib.util.module_from_spec(spec); spec.loader.exec_module(pc)
Q = {q["id"]: q for q in rd(B + "boar-eval/bench/v0.1/questions.public.jsonl")}
for f in glob.glob(B + "boar-eval/bench/selftest/*/questions.jsonl"):
    for q in rd(f): Q[q["id"]] = q
MAIN = [l.strip() for l in open(B + "rnd/research/coordinator/arms/lp-screens/main-97.ids") if l.strip()]
V01 = set(l.strip() for l in open(B + "rnd/research/coordinator/arms/litepacks/data/v01-57.ids") if l.strip())
# ---- fact rule (verbatim logic from ragfunnel.py) ----
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
def present(i, chunks):
    if not chunks: return False
    s = share(Q[i], [c["title"] + "\n" + c["body"] for c in chunks]); return s is not None and s >= 0.5
# ---- his side ----
H = {}
for lab in ["kb", "kbpacks", "kbvital5"]:
    for r in rd(W + f"out/{lab}.jsonl"): H[(lab, r["cutoff"], r["persona"], r["id"])] = r
# ---- ours ----
OURS = {}
for arm in ["K0", "K1"]:
    for s in ["v01", "cm"]:
        for t in rd(B + f"rnd/research/coordinator/arms/litepacks/traces/lp-{arm}-{s}-s42.traces.jsonl"): OURS[(arm, t["itemId"])] = t
FUN = json.load(open(B + "rnd/research/coordinator/ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
def our_route(t):
    rc = t["route"]["reasonCodes"]; tier = t["route"]["tier"]
    return {"task": t["route"]["task"], "tier": tier, "retrieve": "retrieve:yes" in rc,
            "kept": [k["title"] for k in t["retrieval"]["kept"]], "promptTokens": t["timing"].get("promptTokens"),
            "deterministic": tier == "instant" and not any(c.startswith("generate:") for c in rc)}
norm_title = lambda s: re.sub(r"^(wikivoyage|wikipedia|ethereum\.org|bitcoin bips|ethereum eips/ercs|ethereum specs|appropedia|wikibooks|us government|source): ", "", s.lower()).strip()
med = lambda xs: statistics.median(xs) if xs else None
res = {"n": len(MAIN), "harness_parity": {}, "stage": {}, "cutoff": {}, "factpresent": {}, "items": {}}
fact_ids = {a: [i for i in MAIN if i in FUN and FUN[i][a]["kept_present"]] for a in ["K0", "K1"]}
for i in MAIN:
    row = {"set": "v0.1" if i in V01 else "cm"}
    for a in ["K0", "K1"]:
        t = OURS.get((a, i)); row["ours_" + a] = our_route(t) if t else None
        row["ours_" + a + "_fact"] = bool(FUN.get(i, {}).get(a, {}).get("kept_present")) if i in FUN else None
    for lab in ["kb", "kbpacks", "kbvital5"]:
        for cut in [0.7, 0.5, 0.3]:
            h = H[(lab, cut, "detailed", i)]
            row[f"his_{lab}_{cut}"] = {"task": h["task"], "retrieveRan": h["retrieveRan"], "kept": [c["title"] for c in h["kept"]],
                                       "keptSrc": ["kb" if not c["chunkId"].startswith("pack:") else c["chunkId"].split(":")[1] for c in h["kept"]],
                                       "sims": [c.get("similarity") for c in h["kept"]], "fact": present(i, h["kept"]) if i in FUN else None,
                                       "tokDetailed": h["promptTokens"], "tokSuccinct": H[(lab, cut, "succinct", i)]["promptTokens"],
                                       "style": h["style"], "maxTokens": h["maxTokens"], "tokensAfter": h.get("tokensAfter")}
    res["items"][i] = row
items = res["items"]
def summarize(sub):
    out = {}
    n = len(sub); out["n"] = n
    for a in ["K0", "K1"]:
        o = [items[i]["ours_" + a] for i in sub]
        out["ours_" + a] = {"retrieve_ran": sum(x["retrieve"] for x in o), "kept_any": sum(bool(x["kept"]) for x in o),
                            "deterministic_instant": sum(x["deterministic"] for x in o), "prompt_tok_median": med([x["promptTokens"] for x in o if x["promptTokens"]]),
                            "fact_kept": sum(bool(items[i]["ours_" + a + "_fact"]) for i in sub)}
    for lab in ["kb", "kbpacks", "kbvital5"]:
        for cut in [0.7, 0.5, 0.3]:
            hs = [items[i][f"his_{lab}_{cut}"] for i in sub]
            out[f"his_{lab}_{cut}"] = {"retrieve_ran": sum(h["retrieveRan"] for h in hs), "kept_any": sum(bool(h["kept"]) for h in hs),
                                       "kept_kb_any": sum("kb" in h["keptSrc"] for h in hs), "fact_kept": sum(bool(h["fact"]) for h in hs),
                                       "tok_detailed_median": med([h["tokDetailed"] for h in hs]), "tok_succinct_median": med([h["tokSuccinct"] for h in hs]),
                                       "detailed_style_items": sum(h["style"] == "detailed" for h in hs)}
    return out
res["stage"]["MAIN97"] = summarize(MAIN); res["stage"]["v01_57"] = summarize([i for i in MAIN if i in V01]); res["stage"]["cm40"] = summarize([i for i in MAIN if i not in V01])
# kept-source overlap (his kbpacks 0.7 vs ours K0), items where both kept something
ov = []
for i in MAIN:
    a = set(map(norm_title, items[i]["ours_K0"]["kept"])); b = set(map(norm_title, items[i]["his_kbpacks_0.7"]["kept"]))
    if a and b: ov.append(len(a & b) / len(a | b))
    items[i]["overlap_K0_kbpacks"] = (len(a & b), len(a), len(b))
res["stage"]["kept_title_jaccard_K0_vs_kbpacks"] = {"n_both": len(ov), "mean": round(sum(ov) / len(ov), 3) if ov else None, "any_shared": sum(x > 0 for x in ov)}
res["stage"]["kept_both_empty_or_one"] = {k: sum(1 for i in MAIN if (bool(items[i]["ours_K0"]["kept"]), bool(items[i]["his_kbpacks_0.7"]["kept"])) == k) for k in [(True, True), (True, False), (False, True), (False, False)]}
res["stage"]["kept_both_empty_or_one"] = {f"ours{int(k[0])}_his{int(k[1])}": v for k, v in res["stage"]["kept_both_empty_or_one"].items()}
# FACTPRESENT: ours keeps a fact chunk, his retrieves nothing / keeps no fact
for a in ["K0", "K1"]:
    fp = fact_ids[a]; d = {"ids": fp, "n": len(fp)}
    for lab in ["kb", "kbpacks", "kbvital5"]:
        for cut in [0.7, 0.5, 0.3]:
            hs = {i: items[i][f"his_{lab}_{cut}"] for i in fp}
            d[f"{lab}_{cut}"] = {"his_kept_nothing": sorted(i for i, h in hs.items() if not h["kept"]), "his_no_fact": sorted(i for i, h in hs.items() if not h["fact"])}
    res["factpresent"][a] = d
# cutoff sweep: gated chunks (KB + format-1 packs = chunks with a similarity) admitted below 0.7 (new titles vs the 0.7 run); off-topic rule = no stemmed question content token in the title
stem = lambda w: re.sub(r"(ies)$", "y", re.sub(r"(?<=[a-z]{3})s$", "", w))
def offtopic(q, title): return not ({stem(w) for w in toks(title)} & {stem(w) for w in toks(q)})
for lab in ["kb", "kbpacks", "kbvital5"]:
    base = {i: set(items[i][f"his_{lab}_0.7"]["kept"]) for i in MAIN}
    for cut in [0.5, 0.3]:
        new = []
        for i in MAIN:
            h = H[(lab, cut, "detailed", i)]
            for c in h["kept"]:
                if c.get("similarity") is not None and c["title"] not in base[i]:
                    new.append({"id": i, "title": c["title"], "sim": round(c.get("similarity") or 0, 3), "off_rule": offtopic(Q[i]["question"], c["title"])})
        s = res["stage"]["MAIN97"][f"his_{lab}_{cut}"]
        res["cutoff"][f"{lab}_{cut}"] = {"retrieval_fired": s["kept_any"], "kb_fired": s["kept_kb_any"], "fact_kept": s["fact_kept"],
                                         "new_gated_chunks": len(new), "new_gated_items": len({x["id"] for x in new}), "new_gated_offtopic_rule": sum(x["off_rule"] for x in new),
                                         "new": new}
# X6 replica parity (harness vs the X6 device rows, older commit b075adca)
raw = rd(glob.glob(B + "boar-eval/runs/device-poco-x6pro/native-x6-v01/raw/eval-*.jsonl")[0]); X = {r["id"]: r for r in rd(W + "out/x6replica.jsonl")}
same = sum((r.get("retrievedTitles") or []) == [c["title"] for c in X[r["queryId"]]["kept"]] for r in raw if r["queryId"] in X)
res["harness_parity"] = {"x6_titles_identical": same, "x6_n": sum(r["queryId"] in X for r in raw),
                         "x6_task_identical": sum(r.get("taskType") == X[r["queryId"]]["task"] for r in raw if r["queryId"] in X),
                         "rc1_pixel": "9/9 task, kept titles and contextTokens identical (lan-exp-005 Sahara 66/66, other 8 empty)"}
res["script_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
res["inputs_sha256"] = {f.rsplit("/", 1)[1]: hashlib.sha256(open(f, "rb").read()).hexdigest() for f in sorted(glob.glob(W + "out/*.jsonl"))}
open(ARM + "aggregates/native-parity.json", "w").write(json.dumps(res, indent=1) + "\n")
st = res["stage"]
print(json.dumps({k: v for k, v in st.items()}, indent=0)[:6000])
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "new"} for k, v in res["cutoff"].items()}, indent=0))
for a in ["K0", "K1"]:
    d = res["factpresent"][a]; print(a, d["n"], {k: (len(v["his_kept_nothing"]), len(v["his_no_fact"])) for k, v in d.items() if k not in ("ids", "n")})
print(res["harness_parity"])
