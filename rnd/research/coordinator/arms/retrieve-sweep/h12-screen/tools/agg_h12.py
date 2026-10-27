#!/usr/bin/env python3
"""H1+H2 answer screen aggregate (0 LLM). python3 -I agg_h12.py <h12.traces.jsonl> <sanity dir> <judgments dir> <out basename (no ext)>
Per item (agg_run.py definitions): s = mean of the 3 judge dims averaged over both orders, sref likewise, corr = correctness averaged over orders; declined = trace
answer.declined; CE = not declined and corr <= 1.5; warned = text starts with the CMP30OFF warning line. Control = null-cal/control/pool-K1.json (judged mini K1 control;
text == the mini baseline except lan-exp-007, st-qa-money-se-005). Arm rows: judged where the item is in the changed set (kept differs AND text differs) and was judged;
every other item reuses the control row (divergence-first: dU 0 by construction). Paired dU on the changed items: ratio-of-sums U, item bootstrap B 2000 seed 11."""
import json, sys, glob, random, re, importlib.util, unicodedata, collections, os
A = "<workspace>/rnd/research/coordinator/arms"; RS = A + "/retrieve-sweep"; BE = "<workspace>/boar-eval/bench/"
TRF, SD, JD, OUT = sys.argv[1:5]
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ids = open(A + "/lp-screens/main-97.ids").read().split()
T = {t["itemId"]: t for t in rd(TRF)}
ctl = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]
mini = {}
for f in glob.glob(A + "/litepacks/traces/mini/lp-K1-*-s42.mini.traces.jsonl"): mini.update({t["itemId"]: t for t in rd(f)})
san = json.load(open(SD + "/sanity.json")); chg = san["changed_ids"]
by = {}
for f in sorted(glob.glob(JD + "/*.judgments.jsonl")):
    for r in rd(f):
        if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
dim = lambda m, k: sum(m[k].values()) / 3
rows, judged, missing = {}, [], []
for i in ids:
    t = T[i]; txt = t["answer"]["text"]; d = bool(t["answer"].get("declined")); c = ctl[i]
    if i in chg and txt != c["text"]:
        if i in by and len(by[i]) == 2:
            ms = list(by[i].values())
            j = dict(s=sum(dim(m, "boar") for m in ms) / 2, sref=sum(dim(m, "ref") for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2,
                     use=sum(m["boar"]["usefulness"] for m in ms) / 2, comp=sum(m["boar"]["completeness"] for m in ms) / 2); src = "judged"; judged.append(i)
        else: missing.append(i); continue
    else: j = dict(s=c["s"], sref=c["sref"], corr=c["corr"], use=None, comp=None); src = "control-row"
    rows[i] = dict(j, text=txt, declined=d, warned=txt.startswith(W), CE=(not d and j["corr"] <= 1.5), judgment=src, outTok=t["timing"].get("outputTokens") or 0, totalMs=t["timing"].get("totalMs") or 0)
if missing: sys.exit(f"MISSING judgments: {missing}")
# control usefulness from the control judgment files (only where the recomputed s equals the pool s)
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
    return dict(n=len(xs), U=round(U(src, xs), 4), Q=round(sum(src[i]["s"] for i in xs) / sum(src[i]["sref"] for i in xs), 4), corr=round(sum(src[i]["corr"] for i in xs) / len(xs), 3),
                CE=len(ce), CE_unwarned=sum(1 for i in ce if not src[i]["warned"]), warned=sum(1 for i in xs if src[i]["warned"]), declined=sum(1 for i in xs if src[i]["declined"]))
def boot(xs, f, B=2000):
    r = random.Random(11); v = []
    for _ in range(B): s = [r.choice(xs) for _ in xs]; v.append(f(s))
    v.sort(); return [round(v[int(0.025 * B)], 4), round(v[int(0.975 * B) - 1], 4)]
dU = lambda xs: U(rows, xs) - U(crow, xs)
dcorr = lambda xs: sum(rows[i]["corr"] - crow[i]["corr"] for i in xs) / len(xs)
cj = [i for i in chg]  # changed set; items with identical text to the control row count as dU 0
res = dict(n=len(ids), changed_n=len(cj), judged_n=len(judged), judged_ids=judged)
res["all97"] = dict(ctl=summ(crow, ids), arm=summ(rows, ids))
res["changed"] = dict(ctl=summ(crow, cj), arm=summ(rows, cj))
res["all97"]["dU"] = dict(d=round(dU(ids), 4), ci=boot(ids, dU))
res["changed"]["dU"] = dict(d=round(dU(cj), 4), ci=boot(cj, dU)); res["changed"]["dcorr"] = dict(d=round(dcorr(cj), 4), ci=boot(cj, dcorr))
uj = [i for i in cj if rows[i]["use"] is not None and crow[i]["use"] is not None]
res["changed"]["usefulness"] = dict(n=len(uj), ctl=round(sum(crow[i]["use"] for i in uj) / max(1, len(uj)), 3), arm=round(sum(rows[i]["use"] for i in uj) / max(1, len(uj)), 3))
res["changed"]["outTok_mean"] = dict(ctl=round(sum(mini[i]["timing"].get("outputTokens") or 0 for i in cj) / len(cj), 2), arm=round(sum(rows[i]["outTok"] for i in cj) / len(cj), 2))
res["changed"]["totalMs_mean"] = dict(ctl=round(sum(mini[i]["timing"].get("totalMs") or 0 for i in cj) / len(cj), 0), arm=round(sum(rows[i]["totalMs"] for i in cj) / len(cj), 0))
res["all97"]["outTok_mean"] = dict(ctl=round(sum(mini[i]["timing"].get("outputTokens") or 0 for i in ids) / 97, 2), arm=round(sum(rows[i]["outTok"] for i in ids) / 97, 2))
res["all97"]["totalMs_mean"] = dict(ctl=round(sum(mini[i]["timing"].get("totalMs") or 0 for i in ids) / 97, 0), arm=round(sum(rows[i]["totalMs"] for i in ids) / 97, 0))
# gained / lost
res["changed"]["corr_up"] = [i for i in cj if rows[i]["corr"] - crow[i]["corr"] >= 1]; res["changed"]["corr_down"] = [i for i in cj if crow[i]["corr"] - rows[i]["corr"] >= 1]
res["changed"]["CE_new"] = [i for i in cj if rows[i]["CE"] and not crow[i]["CE"]]; res["changed"]["CE_fixed"] = [i for i in cj if crow[i]["CE"] and not rows[i]["CE"]]
res["changed"]["CE_new_unwarned"] = [i for i in res["changed"]["CE_new"] if not rows[i]["warned"]]; res["changed"]["CE_fixed_unwarned"] = [i for i in res["changed"]["CE_fixed"] if not crow[i]["warned"]]
# targets
H1 = ["lan-rsn-005", "lan-cmp-004", "vit-hum-003", "vit-sci-001", "st-qa-money-se-012"]; H2 = ["vit-hlt-001", "vit-hlt-002"]
res["targets"] = {i: dict(grp="H1" if i in H1 else "H2", changed=i in chg, ctl_corr=crow[i]["corr"], arm_corr=rows[i]["corr"], ctl_s=round(crow[i]["s"], 3), arm_s=round(rows[i]["s"], 3),
                        ctl_declined=crow[i]["declined"], arm_declined=rows[i]["declined"], ctl_warned=crow[i]["warned"], arm_warned=rows[i]["warned"], judgment=rows[i]["judgment"],
                        ctl_text=crow[i]["text"][:260], arm_text=rows[i]["text"][:260]) for i in H1 + H2}
# fact-present 2x2 (FACTPRESENT lexical rule on the kept text; arm flag from the replay whose kept title sequence equals the run's kept titles: H1.main, else H2.main.sub)
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
r0 = {r["id"]: r for r in rd(RS + "/replay/B0.main.jsonl")}; r1 = {r["id"]: r for r in rd(RS + "/replay/H1.main.jsonl")}; r2 = {r["id"]: r for r in rd(RS + "/replay/h2/H2.main.sub.jsonl")}
fp = {}
for i in ids:
    tt = [c["title"] for c in T[i]["retrieval"]["kept"]]; a = None; src = None
    if tt == [c["title"] for c in r1[i]["keptFull"]]: a = present(i, r1[i]["keptFull"]); src = "H1replay"
    elif i in r2 and tt == [c["title"] for c in r2[i]["keptFull"]]: a = present(i, r2[i]["keptFull"]); src = "H2replay"
    fp[i] = dict(ctl=present(i, r0[i]["keptFull"]), arm=a, src=src)
cells = collections.defaultdict(list)
for i in cj:
    f = fp[i]
    if f["ctl"] is None or f["arm"] is None: cells["no-flag"].append(i); continue
    cells[f"ctl_{'P' if f['ctl'] else 'A'}__arm_{'P' if f['arm'] else 'A'}"].append(i)
res["factpresent_2x2_changed"] = {k: dict(n=len(v), ids=v, dcorr=round(sum(rows[i]["corr"] - crow[i]["corr"] for i in v) / len(v), 3),
                                  ctl_corr=round(sum(crow[i]["corr"] for i in v) / len(v), 3), arm_corr=round(sum(rows[i]["corr"] for i in v) / len(v), 3),
                                  dU=round(dU(v), 4)) for k, v in sorted(cells.items())}
res["factpresent_flag_unknown_all97"] = [i for i in ids if fp[i]["arm"] is None]
res["rows"] = {i: {k: v for k, v in rows[i].items() if k != "text"} | dict(ctl_corr=crow[i]["corr"], ctl_s=crow[i]["s"], ctl_declined=crow[i]["declined"], ctl_warned=crow[i]["warned"], fp=fp[i]) for i in ids}
res["texts"] = {i: dict(ctl=crow[i]["text"], arm=rows[i]["text"]) for i in cj}
json.dump(res, open(OUT + ".json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in res.items() if k not in ("rows", "texts", "targets")}, indent=0, ensure_ascii=False)); print(json.dumps(res["targets"], indent=0, ensure_ascii=False)[:3000])
