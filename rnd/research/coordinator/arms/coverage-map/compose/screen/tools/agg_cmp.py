#!/usr/bin/env python3
"""COMPOSE answer screen aggregate (0 LLM). python3 -I agg_cmp.py <S traces> <G traces> <sanity dir> <S judgments dir> <G judgments dir> <out basename (no ext)>
Same definitions as retrieve-sweep/h12-screen/tools/agg_h12.py: per item s = mean of the 3 judge dims over both orders, corr = correctness averaged over orders; CE = not declined and corr <= 1.5;
warned = text starts with the CMP30OFF warning line; control = null-cal/control/pool-K1.json (judged mini K1 control). Arm row = judged if the item is in that arm's changed set
(kept differs AND text differs) and its text differs from the control row; an S item whose text equals the G text of the same item reuses G's judgment; every other item reuses the control row (dU 0).
Paired dU on the changed items: ratio-of-sums U, item bootstrap B 2000 seed 11. G - S paired on the items changed in both arms."""
import json, sys, glob, random, re, importlib.util, unicodedata, collections, os
A = "<workspace>/rnd/research/coordinator/arms"; RS = A + "/retrieve-sweep"; BE = "<workspace>/boar-eval/bench/"; CMP = A + "/coverage-map/compose"
TRS, TRG, SD, JDS, JDG, OUT = sys.argv[1:7]
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ids = open(A + "/lp-screens/main-97.ids").read().split()
TT = {"S": {t["itemId"]: t for t in rd(TRS)}, "G": {t["itemId"]: t for t in rd(TRG)}}
ctl = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]
mini = {}
for f in glob.glob(A + "/litepacks/traces/mini/lp-K1-*-s42.mini.traces.jsonl"): mini.update({t["itemId"]: t for t in rd(f)})
san = json.load(open(SD + "/sanity.json"))
def jby(JD):
    by = {}
    for f in sorted(glob.glob(JD + "/*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    return by
BY = {"S": jby(JDS), "G": jby(JDG)}
dim = lambda m, k: sum(m[k].values()) / 3
def jrow(by, i):
    ms = list(by[i].values())
    return dict(s=sum(dim(m, "boar") for m in ms) / 2, sref=sum(dim(m, "ref") for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2,
                use=sum(m["boar"]["usefulness"] for m in ms) / 2, comp=sum(m["boar"]["completeness"] for m in ms) / 2)
rows = {"S": {}, "G": {}}; judged = {"S": [], "G": []}; reused = []; unjudged = {"S": [], "G": []}
for arm in ("G", "S"):
    chg = san[arm]["changed_ids"]
    for i in ids:
        t = TT[arm][i]; txt = t["answer"]["text"]; d = bool(t["answer"].get("declined")); c = ctl[i]
        if i in chg and txt != c["text"]:
            if i in BY[arm] and len(BY[arm][i]) == 2: j = jrow(BY[arm], i); src = "judged"; judged[arm].append(i)
            elif arm == "S" and i in rows["G"] and rows["G"][i]["judgment"] == "judged" and rows["G"][i]["text"] == txt:
                j = {k: rows["G"][i][k] for k in ("s", "sref", "corr", "use", "comp")}; src = "reused-G"; reused.append(i)
            else: unjudged[arm].append(i); continue
        else: j = dict(s=c["s"], sref=c["sref"], corr=c["corr"], use=None, comp=None); src = "control-row"
        rows[arm][i] = dict(j, text=txt, declined=d, warned=txt.startswith(W), CE=(not d and j["corr"] <= 1.5), judgment=src, outTok=t["timing"].get("outputTokens") or 0, totalMs=t["timing"].get("totalMs") or 0)
# control usefulness from the control judgment files
cu = {}
for g in (A + "/litepacks/judgments/lp-K1-*.judgments.jsonl", A + "/lp-screens/control/judgments/lpctl-K1-main*.judgments.jsonl", A + "/null-cal/control/judgments/poolctl-K1-*.judgments.jsonl"):
    for f in glob.glob(g):
        for r in rd(f):
            if r.get("ok") is True: cu.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
crow = {}
for i in ids:
    c = ctl[i]; x = cu.get(i)
    if x and len(x) == 2:
        ms = list(x.values()); s = sum(dim(m, "boar") for m in ms) / 2
        use = sum(m["boar"]["usefulness"] for m in ms) / 2 if abs(s - c["s"]) < 1e-6 else None
    else: use = None
    crow[i] = dict(c, use=use)
def U(src, xs): return sum(0 if src[i]["declined"] else src[i]["s"] for i in xs) / sum(src[i]["sref"] for i in xs)
def summ(src, xs):
    nd = [i for i in xs if not src[i]["declined"]]; ce = [i for i in nd if src[i]["corr"] <= 1.5]
    return dict(n=len(xs), U=round(U(src, xs), 4), corr=round(sum(src[i]["corr"] for i in xs) / len(xs), 3),
                CE=len(ce), CE_unwarned=sum(1 for i in ce if not src[i]["warned"]), warned=sum(1 for i in xs if src[i]["warned"]), declined=sum(1 for i in xs if src[i]["declined"]))
def boot(xs, f, B=2000):
    r = random.Random(11); v = []
    for _ in range(B): s = [r.choice(xs) for _ in xs]; v.append(f(s))
    v.sort(); return [round(v[int(0.025 * B)], 4), round(v[int(0.975 * B) - 1], 4)]
# fact-present flags
spec = importlib.util.spec_from_file_location("pc", "<workspace>/boar-eval/scorers/vendor/lantern/precheck.py"); pc = importlib.util.module_from_spec(spec); spec.loader.exec_module(pc)
QS = {q["id"]: q for q in rd(BE + "v0.1/questions.public.jsonl")}
for f in glob.glob(BE + "selftest/*/questions.jsonl"):
    for q in rd(f): QS[q["id"]] = q
STOP = set("the a an and or of to in on for with is are was were be been it its this that as at by from not no but if then than so do does did can could will would should may might has have had you your they their there which what when where who how why also more most very just only into out up about over after before such these those other some any all each".split())
def fnrm(s):
    s = unicodedata.normalize("NFKC", s or "").lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"'); s = re.sub(r"[‐-―−]", "-", s); return re.sub(r"\s+", " ", s).strip()
toks = lambda s: [w for w in re.findall(r"[a-z0-9][a-z0-9'.%-]*[a-z0-9%]|[a-z0-9]", fnrm(s)) if len(w) >= 3 and w not in STOP] or []
def tib(phrase, blocks, need):
    t = set(toks(phrase)); return len(t) >= need and any(len(t & set(toks(b))) / len(t) >= 0.8 for b in blocks)
def share_v01(q, blocks):
    g = q.get("grading", {}); text = pc.norm("\n\n".join(blocks)); question = pc.norm(q["question"]); groups = []
    for grp in g.get("must_any", []):
        live = [t for t in grp if not pc.is_echo(t, question)]
        if live: groups.append(any(pc.hits(t, text) for t in live))
    mk = g.get("must_k")
    if mk:
        live = [t for t in mk["terms"] if not pc.is_echo(t, question)]; groups.append(sum(pc.hits(t, text) for t in live) >= mk["k"])
    return (sum(groups) / len(groups)) if groups else None
def share_st(q, blocks):
    fs = q["selftest"]["in_pack_facts"]; whole = fnrm("\n\n".join(blocks)); hit = 0
    for f in fs:
        quote = fnrm(f.get("quote", "")); hit += bool((len(quote) >= 12 and quote in whole) or tib(quote, blocks, 4) or tib(f.get("fact", ""), blocks, 3))
    return hit / len(fs) if fs else None
def present(i, kept):
    q = QS[i]; blocks = [f"{c['title']}\n{c['body']}" for c in kept]; s = share_st(q, blocks) if "selftest" in q else share_v01(q, blocks); return None if s is None else s >= 0.5
r0 = {r["id"]: r for r in rd(RS + "/replay/B0.main.jsonl")}
RP = {"S": {r["id"]: r for r in rd(CMP + "/replays/main.N10.stock.jsonl")}, "G": {r["id"]: r for r in rd(CMP + "/replays/main.N10.gidf.jsonl")}}
ttl = lambda t: [c["title"] for c in t["retrieval"]["kept"]]
src_of = lambda i: "v0.1" if not i.startswith("st-") else ("cooking" if "cooking" in i else "money")
res = dict(n=len(ids), judged_n={a: len(judged[a]) for a in judged}, reused_G_for_S=len(reused), unjudged=unjudged)
FP = {}
for arm in ("S", "G"):
    if unjudged[arm]: res[f"WARN_unjudged_{arm}"] = unjudged[arm]
    R = rows[arm]; cj = [i for i in san[arm]["changed_ids"] if i in R]
    dU = lambda xs, R=R: U(R, xs) - U(crow, xs)
    dcorr = lambda xs, R=R: sum(R[i]["corr"] - crow[i]["corr"] for i in xs) / len(xs)
    x = {}
    x["changed_n"] = len(cj)
    x["all97"] = dict(ctl=summ(crow, [i for i in ids if i in R]), arm=summ(R, [i for i in ids if i in R]))
    x["all97"]["dU"] = dict(d=round(dU([i for i in ids if i in R]), 4), ci=boot([i for i in ids if i in R], dU))
    x["changed"] = dict(ctl=summ(crow, cj), arm=summ(R, cj), dU=dict(d=round(dU(cj), 4), ci=boot(cj, dU)), dcorr=dict(d=round(dcorr(cj), 4), ci=boot(cj, dcorr)))
    uj = [i for i in cj if R[i]["use"] is not None and crow[i]["use"] is not None]
    x["changed"]["usefulness"] = dict(n=len(uj), ctl=round(sum(crow[i]["use"] for i in uj) / max(1, len(uj)), 3), arm=round(sum(R[i]["use"] for i in uj) / max(1, len(uj)), 3))
    x["changed"]["outTok_mean"] = dict(ctl=round(sum(mini[i]["timing"].get("outputTokens") or 0 for i in cj) / len(cj), 2), arm=round(sum(R[i]["outTok"] for i in cj) / len(cj), 2))
    x["changed"]["totalMs_mean"] = dict(ctl=round(sum(mini[i]["timing"].get("totalMs") or 0 for i in cj) / len(cj), 0), arm=round(sum(R[i]["totalMs"] for i in cj) / len(cj), 0))
    al = [i for i in ids if i in R]
    x["all97"]["outTok_mean"] = dict(ctl=round(sum(mini[i]["timing"].get("outputTokens") or 0 for i in al) / len(al), 2), arm=round(sum(R[i]["outTok"] for i in al) / len(al), 2))
    x["all97"]["totalMs_mean"] = dict(ctl=round(sum(mini[i]["timing"].get("totalMs") or 0 for i in al) / len(al), 0), arm=round(sum(R[i]["totalMs"] for i in al) / len(al), 0))
    x["changed"]["corr_up"] = [i for i in cj if R[i]["corr"] - crow[i]["corr"] >= 1]; x["changed"]["corr_down"] = [i for i in cj if crow[i]["corr"] - R[i]["corr"] >= 1]
    x["changed"]["CE_new"] = [i for i in cj if R[i]["CE"] and not crow[i]["CE"]]; x["changed"]["CE_fixed"] = [i for i in cj if crow[i]["CE"] and not R[i]["CE"]]
    x["changed"]["CE_new_unwarned"] = [i for i in x["changed"]["CE_new"] if not R[i]["warned"]]; x["changed"]["CE_fixed_unwarned"] = [i for i in x["changed"]["CE_fixed"] if not crow[i]["warned"]]
    # sensitivity: drop the two items whose pool control text differs from the mini baseline
    sx = [i for i in cj if i not in ("lan-exp-007", "st-qa-money-se-005")]
    x["changed"]["dU_excl_pool_text_mismatch"] = dict(n=len(sx), d=round(dU(sx), 4), ci=boot(sx, dU))
    # by source
    x["by_source"] = {}
    for sname in ("v0.1", "cooking", "money"):
        xs = [i for i in cj if src_of(i) == sname]
        if xs: x["by_source"][sname] = dict(n=len(xs), ctl_U=round(U(crow, xs), 4), arm_U=round(U(R, xs), 4), dU=round(dU(xs), 4), ci=boot(xs, dU), ctl_corr=round(sum(crow[i]["corr"] for i in xs) / len(xs), 3), arm_corr=round(sum(R[i]["corr"] for i in xs) / len(xs), 3), CE_new=sum(i in x["changed"]["CE_new"] for i in xs), CE_fixed=sum(i in x["changed"]["CE_fixed"] for i in xs))
    # gold-kept 2x2
    fp = {}
    for i in ids:
        tt = ttl(TT[arm][i]); a = present(i, RP[arm][i]["keptFull"]) if tt == [c["title"] for c in RP[arm][i]["keptFull"]] else None
        fp[i] = dict(ctl=present(i, r0[i]["keptFull"]), arm=a)
    FP[arm] = fp; cells = collections.defaultdict(list)
    for i in cj:
        f = fp[i]
        if f["ctl"] is None or f["arm"] is None: cells["no-flag"].append(i); continue
        cells[f"ctl_{'P' if f['ctl'] else 'A'}__arm_{'P' if f['arm'] else 'A'}"].append(i)
    x["factpresent_2x2_changed"] = {k: dict(n=len(v), ids=v, ctl_corr=round(sum(crow[i]["corr"] for i in v) / len(v), 3), arm_corr=round(sum(R[i]["corr"] for i in v) / len(v), 3), dU=round(dU(v), 4)) for k, v in sorted(cells.items())}
    x["factpresent_flag_unknown_all97"] = len([i for i in ids if fp[i]["arm"] is None])
    x["fact_kept_share"] = dict(ctl=sum(1 for i in ids if fp[i]["ctl"]), arm=sum(1 for i in ids if fp[i]["arm"]))
    # newly kept facts (compose.json N10 kept_list minus N0.stock)
    cl = json.load(open(CMP + "/compose.json"))["labels"]; new = sorted(set(cl["N10.stock" if arm == "S" else "N10.gidf"]["kept_list"]) - set(cl["N0.stock"]["kept_list"]))
    x["newly_kept_facts"] = {i: dict(set=src_of(i), live_changed=i in cj, live_fact_present=fp[i]["arm"], ctl_corr=crow[i]["corr"], arm_corr=R[i]["corr"], ctl_declined=crow[i]["declined"], arm_declined=R[i]["declined"], judgment=R[i]["judgment"] if i in R else None) for i in new if i in R}
    x["newly_kept_dcorr_mean"] = round(sum(R[i]["corr"] - crow[i]["corr"] for i in new if i in R) / max(1, len([i for i in new if i in R])), 3)
    res[arm] = x
# G - S paired on both-changed
both = [i for i in san["both_changed"] if i in rows["S"] and i in rows["G"]]
dGS = lambda xs: U(rows["G"], xs) - U(rows["S"], xs)
res["G_minus_S_both_changed"] = dict(n=len(both), d=round(dGS(both), 4), ci=boot(both, dGS), U_S=round(U(rows["S"], both), 4), U_G=round(U(rows["G"], both), 4),
                                     ctl_U=round(U(crow, both), 4), text_identical=sum(rows["S"][i]["text"] == rows["G"][i]["text"] for i in both))
un = [i for i in san["union_changed"] if i in rows["S"] and i in rows["G"]]
res["G_minus_S_union_changed"] = dict(n=len(un), d=round(dGS(un), 4), ci=boot(un, dGS))
res["G_minus_S_all97"] = dict(d=round(dGS(ids), 4), ci=boot(ids, dGS))
res["rows"] = {arm: {i: {k: v for k, v in rows[arm][i].items() if k != "text"} | dict(ctl_corr=crow[i]["corr"], ctl_s=crow[i]["s"], ctl_declined=crow[i]["declined"], ctl_warned=crow[i]["warned"], fp=FP[arm][i]) for i in rows[arm]} for arm in rows}
res["texts"] = {i: dict(ctl=crow[i]["text"], S=rows["S"][i]["text"], G=rows["G"][i]["text"]) for i in san["union_changed"] if i in rows["S"] and i in rows["G"]}
json.dump(res, open(OUT + ".json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in res.items() if k not in ("rows", "texts")}, indent=0, ensure_ascii=False)[:9000])
