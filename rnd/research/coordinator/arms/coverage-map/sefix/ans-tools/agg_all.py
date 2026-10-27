#!/usr/bin/env python3
"""SEFIX-ALL answer screen aggregate (0 LLM; adapted from agg_f1b.py). python3 -I agg_all.py -> ../answers-sefixall.json, ../answers-sefixall.table.md
Rows: control = null-cal/control/pool-K1.json (judged K3-kit mini control); ARM-G = compose/screen (judged rows in screen/judge/G, control row where G's text equals the control's);
ALL row = ARM-G's row if the ALL answer text equals G's, else the control row if equal to the control's, else the arm's own Haiku judgment (ans-judge/F1B).
Definitions as compose/screen/tools/agg_cmp.py and gate/tools/agg_gate.py (ratio-of-sums U, corr/use averaged over both orders, CE = not declined and corr <= 1.5, warned = engine warning line first). Bootstrap: items, B 2000, seed 11."""
import json, glob, random, re, importlib.util, unicodedata, collections
A = "<workspace>/rnd/research/coordinator/arms"; CM = A + "/coverage-map"; SF = CM + "/sefix"; CMP = CM + "/compose"; BE = "<workspace>/boar-eval/bench/"
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ids = open(A + "/lp-screens/main-97.ids").read().split()
ctl = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]
TG = {t["itemId"]: t for t in rd(CMP + "/screen/traces/cmp-G-K10-main-s42.traces.jsonl")}; TF = {t["itemId"]: t for t in rd(SF + "/ans-traces/sefixall-main-s42.traces.jsonl")}
san = json.load(open(SF + "/ans-judge/sanity_all.json")); chg = san["changed_ids"]
mini = {}
for f in glob.glob(A + "/litepacks/traces/mini/lp-K1-*-s42.mini.traces.jsonl"): mini.update({t["itemId"]: t for t in rd(f)})
def jby(JD):
    by = {}
    for f in sorted(glob.glob(JD + "/*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    return by
BY = {"G": jby(CMP + "/screen/judge/G"), "F": jby(SF + "/ans-judge/ALL")}
for k, v in jby(SF + "/ans-judge/ALL2").items(): BY["F"].setdefault(k, {}).update(v)   # 2 text-only-changed items (same kept titles, different chunk ids/prompt): judged as a sensitivity, 4 calls
dim = lambda m, k: sum(m[k].values()) / 3
def jrow(by, i):
    ms = list(by[i].values())
    return dict(s=sum(dim(m, "boar") for m in ms) / 2, sref=sum(dim(m, "ref") for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2, use=sum(m["boar"]["usefulness"] for m in ms) / 2)
# control usefulness (only where the judged control row s matches the judgment file)
cu = {}
for g in (A + "/litepacks/judgments/lp-K1-*.judgments.jsonl", A + "/lp-screens/control/judgments/lpctl-K1-main*.judgments.jsonl", A + "/null-cal/control/judgments/poolctl-K1-*.judgments.jsonl"):
    for f in glob.glob(g):
        for r in rd(f):
            if r.get("ok") is True: cu.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
def cuse(i):
    x = cu.get(i)
    if x and len(x) == 2:
        ms = list(x.values()); s = sum(dim(m, "boar") for m in ms) / 2
        if abs(s - ctl[i]["s"]) < 1e-6: return sum(m["boar"]["usefulness"] for m in ms) / 2
    return None
def mk(t, j, src):
    txt = t["answer"]["text"]; d = bool(t["answer"].get("declined"))
    return dict(j, text=txt, declined=d, warned=txt.startswith(W), CE=(not d and j["corr"] <= 1.5), judgment=src, outTok=t["timing"].get("outputTokens") or 0, totalMs=t["timing"].get("totalMs") or 0)
crow = {}
for i in ids:
    c = ctl[i]; crow[i] = dict(s=c["s"], sref=c["sref"], corr=c["corr"], use=cuse(i), text=c["text"], declined=bool(c.get("declined")), warned=c["text"].startswith(W), CE=(not c.get("declined") and c["corr"] <= 1.5),
                              judgment="control", outTok=mini[i]["timing"].get("outputTokens") or 0, totalMs=mini[i]["timing"].get("totalMs") or 0)
RG, RF = {}, {}; unjudged = []
for i in ids:
    t = TG[i]; txt = t["answer"]["text"]; c = ctl[i]
    if txt != c["text"]:
        if i in BY["G"] and len(BY["G"][i]) == 2: j = jrow(BY["G"], i); src = "judged-G"
        else: raise SystemExit(f"ARM-G row missing for {i}")
    else: j = dict(s=c["s"], sref=c["sref"], corr=c["corr"], use=crow[i]["use"]); src = "control-row"
    RG[i] = mk(t, j, src)
for i in ids:
    t = TF[i]; txt = t["answer"]["text"]; c = ctl[i]; g = RG[i]
    if txt == g["text"]: j = {k: g[k] for k in ("s", "sref", "corr", "use")}; src = "reused-G"
    elif txt == c["text"]: j = dict(s=c["s"], sref=c["sref"], corr=c["corr"], use=crow[i]["use"]); src = "control-row"
    elif i in BY["F"] and len(BY["F"][i]) == 2: j = jrow(BY["F"], i); src = "judged"
    else: unjudged.append(i); continue
    RF[i] = mk(t, j, src)
if unjudged: raise SystemExit(f"unjudged ALL rows: {unjudged}")
def U(src, xs): return sum(0 if src[i]["declined"] else src[i]["s"] for i in xs) / sum(src[i]["sref"] for i in xs)
def mean(src, xs, k, nn=3):
    v = [src[i][k] for i in xs if src[i].get(k) is not None]; return round(sum(v) / len(v), nn) if v else None
def summ(src, xs):
    nd = [i for i in xs if not src[i]["declined"]]; ce = [i for i in nd if src[i]["corr"] <= 1.5]
    return dict(n=len(xs), U=round(U(src, xs), 4), corr=mean(src, xs, "corr"), use=mean(src, xs, "use"), use_n=sum(1 for i in xs if src[i].get("use") is not None), CE=len(ce), CE_unwarned=sum(1 for i in ce if not src[i]["warned"]),
                warned=sum(1 for i in xs if src[i]["warned"]), declined=sum(1 for i in xs if src[i]["declined"]), outTok=mean(src, xs, "outTok", 2), totalMs=round(mean(src, xs, "totalMs", 0)))
def boot(xs, f, B=2000):
    r = random.Random(11); v = []
    for _ in range(B): v.append(f([r.choice(xs) for _ in xs]))
    v.sort(); return [round(v[int(0.025 * B)], 4), round(v[int(0.975 * B) - 1], 4)]
def pair(sa, sb, xs):
    if not xs: return dict(n=0)
    f = lambda s: U(sa, s) - U(sb, s); g = lambda s: sum(sa[i]["corr"] - sb[i]["corr"] for i in s) / len(s)
    return dict(n=len(xs), d=round(f(xs), 4), ci=boot(xs, f), dcorr=round(g(xs), 4), dcorr_ci=boot(xs, g))
src_of = lambda i: "v0.1" if not i.startswith("st-") else ("cooking" if "cooking" in i else "money")
res = dict(n=len(ids), changed_vs_G=len(chg), judged_ALL_rows=sum(1 for i in ids if RF[i]["judgment"] == "judged"), reused_G=sum(1 for i in ids if RF[i]["judgment"] == "reused-G"), reused_control=sum(1 for i in ids if RF[i]["judgment"] == "control-row"))
res["all97"] = dict(control=summ(crow, ids), G=summ(RG, ids), ALL=summ(RF, ids))
res["changed"] = dict(n=len(chg), G=summ(RG, chg), ALL=summ(RF, chg), control=summ(crow, chg))
chg66 = [i for i in ids if i in chg or RF[i]["text"] != RG[i]["text"]]; res["changed66_text_differs"] = dict(extra=[i for i in chg66 if i not in chg], **pair(RF, RG, chg66))
res["vs_G_changed"] = pair(RF, RG, chg); res["vs_G_all97"] = pair(RF, RG, ids); res["vs_control_all97"] = pair(RF, crow, ids); res["G_vs_control_all97"] = pair(RG, crow, ids)
res["by_source_changed"] = {}; res["by_source_all"] = {}
for s in ("v0.1", "cooking", "money"):
    xs = [i for i in chg if src_of(i) == s]; al = [i for i in ids if src_of(i) == s]
    if xs: res["by_source_changed"][s] = dict(G=summ(RG, xs), ALL=summ(RF, xs), **pair(RF, RG, xs))
    res["by_source_all"][s] = dict(n=len(al), changed=len(xs), control=summ(crow, al), G=summ(RG, al), ALL=summ(RF, al), vs_G=pair(RF, RG, al), vs_control=pair(RF, crow, al))
# CE changes on changed items
res["CE_new_vs_G"] = [i for i in chg if RF[i]["CE"] and not RG[i]["CE"]]; res["CE_fixed_vs_G"] = [i for i in chg if RG[i]["CE"] and not RF[i]["CE"]]
res["CE_new_unwarned_vs_G"] = [i for i in res["CE_new_vs_G"] if not RF[i]["warned"]]; res["CE_fixed_unwarned_vs_G"] = [i for i in res["CE_fixed_vs_G"] if not RG[i]["warned"]]
res["corr_up_ge1"] = [i for i in chg if RF[i]["corr"] - RG[i]["corr"] >= 1]; res["corr_down_ge1"] = [i for i in chg if RG[i]["corr"] - RF[i]["corr"] >= 1]
# fact present/absent flag (FACTPRESENT lexical rule on kept text = stage K in the replays; valid only where the live kept titles equal the replay's)
KF = json.load(open(SF + "/sefix.json"))["labels"]
kG = set(KF["ctl"]["kept_list"]); kF = set(KF["F1F2F3F4"]["kept_list"])
kf = json.load(open(SF + "/kfull.json"))["items"]; keyed = set(kf)
RPF = {r["id"]: r for r in rd(SF + "/replays/main.F1F2F3F4.jsonl")}; RPG = {r["id"]: r for r in rd(CMP + "/replays/main.N10.gidf.jsonl")}
ttl = lambda t: [c["title"] for c in t["retrieval"]["kept"]]
fl = {}
for i in ids:
    fg = (i in kG) if (i in keyed and ttl(TG[i]) == [c["title"] for c in RPG[i]["keptFull"]]) else None
    ff = (i in kF) if (i in keyed and ttl(TF[i]) == [c["title"] for c in RPF[i]["keptFull"]]) else None
    fl[i] = dict(G=fg, F=ff)
def cells(xs):
    c = collections.defaultdict(list)
    for i in xs:
        f = fl[i]
        if f["G"] is None or f["F"] is None: c["no-flag"].append(i); continue
        c[f"G_{'P' if f['G'] else 'A'}__F_{'P' if f['F'] else 'A'}"].append(i)
    return {k: dict(n=len(v), ids=v, G_corr=mean(RG, v, "corr"), F_corr=mean(RF, v, "corr"), G_U=round(U(RG, v), 4), F_U=round(U(RF, v), 4), **{k2: v2 for k2, v2 in pair(RF, RG, v).items() if k2 in ("d", "ci")}) for k, v in sorted(c.items())}
res["factpresent_2x2_changed"] = cells(chg); res["factpresent_2x2_all97"] = cells(ids)
res["flag_unknown_all97"] = sum(1 for i in ids if fl[i]["G"] is None or fl[i]["F"] is None)
# the 14 newly delivered cm facts (kept in the ALL replay, not in N10 gidf): correctness control -> G -> ALL
new = sorted(i for i in kF - kG)
res["newly_delivered_cm"] = dict(n=len(new), live_flag_F_present=sum(1 for i in new if fl[i]["F"]), items={i: dict(ctl=crow[i]["corr"], G=RG[i]["corr"], F=RF[i]["corr"], text_changed_vs_G=RF[i]["text"] != RG[i]["text"], judged=RF[i]["judgment"], live_fact_flag=fl[i]["F"], F_warned=RF[i]["warned"], F_declined=RF[i]["declined"]) for i in new},
                                 mean_corr=dict(ctl=mean(crow, new, "corr"), G=mean(RG, new, "corr"), ALL=mean(RF, new, "corr")), U=dict(ctl=round(U(crow, new), 4), G=round(U(RG, new), 4), ALL=round(U(RF, new), 4)), vs_G=pair(RF, RG, new))
lost = sorted(i for i in kG - kF); res["lost_vs_gidf"] = {i: dict(G=RG[i]["corr"], F=RF[i]["corr"], text_changed=RF[i]["text"] != RG[i]["text"]) for i in lost}
# frozen read
ce_up_G = res["all97"]["ALL"]["CE_unwarned"] > res["all97"]["G"]["CE_unwarned"]; ce_up_ctl = res["all97"]["ALL"]["CE_unwarned"] > res["all97"]["control"]["CE_unwarned"]
a = res["vs_G_changed"]; b = res["vs_control_all97"]
res["rule"] = dict(vs_G_changed_dU_ge_0_02_ci_low_gt_minus_0_01=(a["d"] >= 0.02 and a["ci"][0] > -0.01), vs_control_all97_dU_ge_0_02_ci_low_gt_minus_0_01=(b["d"] >= 0.02 and b["ci"][0] > -0.01),
                   CE_unwarned_not_up_vs_G=not ce_up_G, CE_unwarned_not_up_vs_control=not ce_up_ctl)
res["rule"]["LEVER_CANDIDATE"] = res["rule"]["vs_G_changed_dU_ge_0_02_ci_low_gt_minus_0_01"] and res["rule"]["vs_control_all97_dU_ge_0_02_ci_low_gt_minus_0_01"] and not ce_up_G
res["rows"] = {n: {i: {k: v for k, v in r.items() if k != "text"} for i, r in R.items()} for n, R in (("control", crow), ("G", RG), ("ALL", RF))}
res["texts"] = {i: dict(ctl=crow[i]["text"], G=RG[i]["text"], ALL=RF[i]["text"]) for i in chg}
json.dump(res, open(SF + "/answers-sefixall.json", "w"), indent=1, ensure_ascii=False)
# markdown
S = res["all97"]; C = res["changed"]
row = lambda lab, s: f"| {lab} | {s['U']} | {s['corr']} | {s['use']} | {s['CE']} | {s['CE_unwarned']} | {s['warned']} | {s['declined']} | {s['outTok']} | {s['totalMs']} |"
L = ["| set | arm | U | corr | use | CE | CE unwarned | warned | declined | out tok | totalMs |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for nm, blk in (("all 97", S), (f"changed vs G ({len(chg)})", C)):
    for arm in ("control", "G", "ALL"): L.append(row(f"{nm} | {arm}", blk[arm]))
json.dump(res["rule"], open("/dev/null", "w"))
open(SF + "/answers-sefixall.table.md", "w").write("\n".join(L) + "\n")
print(json.dumps({k: v for k, v in res.items() if k not in ("rows", "texts", "factpresent_2x2_all97")}, indent=0, ensure_ascii=False)[:12000])
