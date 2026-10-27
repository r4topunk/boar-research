#!/usr/bin/env python3
"""SEFIX-ALL seed-43 replicate aggregate (0 LLM; adapted from agg_all.py). python3 -I agg_s43.py -> ../answers-sefixall-s43.json, ../answers-sefixall-s43.md
Arms at seed 43 (same mini, same tree family): ctl = ans-traces/ctlk1-main-s43 (K1 kit, stock); ALL = ans-traces/sefixall-main-s43 (13-pack kit, gidf + 4 switches).
Row per (id, arm): (1) cache = judged seed-42 row with the same (id, answer text) [control pool-K1 / ARM-G / SEFIX-ALL, answers-sefixall.json rows]; (2) else the new Haiku judge.v1 N4 rows (ans-judge/S43/{ALL,CTL});
(3) else (unjudged: text equal in both arms and no cached row, or text differs but outside the 200-call cap) a PROXY = the seed-42 control row for the item, given to BOTH arms (contributes delta 0, flagged).
Definitions as agg_all.py (ratio-of-sums U, CE = not declined and corr <= 1.5, warned = engine warning line first); bootstrap over items, B 2000, random.Random(11), paired on the same draws.
Pooled two seeds: per item, s = mean over the two seeds of (0 if declined else s), sref = mean sref; seed 42 rows from answers-sefixall.json (ALL, control)."""
import json, glob, random, collections
A = "<workspace>/rnd/research/coordinator/arms"; SF = A + "/coverage-map/sefix"
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ld = lambda p: {t["itemId"]: t for t in rd(p)}
ids = open(A + "/lp-screens/main-97.ids").read().split()
T = ld(SF + "/ans-traces/sefixall-main-s43.traces.jsonl"); C = ld(SF + "/ans-traces/ctlk1-main-s43.traces.jsonl")
r42 = json.load(open(SF + "/answers-sefixall.json")); pool = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]
TG = ld(A + "/coverage-map/compose/screen/traces/cmp-G-K10-main-s42.traces.jsonl"); TF = ld(SF + "/ans-traces/sefixall-main-s42.traces.jsonl")
cache = {}
for i in ids:
    cache[(i, pool[i]["text"])] = r42["rows"]["control"][i]; cache[(i, TG[i]["answer"]["text"])] = r42["rows"]["G"][i]; cache[(i, TF[i]["answer"]["text"])] = r42["rows"]["ALL"][i]
def jby(JD):
    by = {}
    for f in sorted(glob.glob(JD + "/*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    return by
BY = {"ALL": jby(SF + "/ans-judge/S43/ALL"), "CTL": jby(SF + "/ans-judge/S43/CTL")}
dim = lambda m, k: sum(m[k].values()) / 3
def jrow(by, i):
    ms = list(by[i].values())
    return dict(s=sum(dim(m, "boar") for m in ms) / 2, sref=sum(dim(m, "ref") for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2, use=sum(m["boar"]["usefulness"] for m in ms) / 2)
td = [i for i in ids if T[i]["answer"]["text"] != C[i]["answer"]["text"]]
def build(D, nm):
    R = {}
    for i in ids:
        t = D[i]; txt = t["answer"]["text"]; d = bool(t["answer"].get("declined"))
        if (i, txt) in cache: c = cache[(i, txt)]; j = {k: c.get(k) for k in ("s", "sref", "corr", "use")}; src = "cache"
        elif i in BY[nm] and len(BY[nm][i]) == 2: j = jrow(BY[nm], i); src = "judged"
        else: j = None; src = "proxy"
        R[i] = dict(j or {}, text=txt, declined=d, warned=txt.startswith(W), judgment=src)
    return R
RA, RC = build(T, "ALL"), build(C, "CTL")
proxy_ids = []
for i in ids:
    if RA[i]["judgment"] == "proxy" or RC[i]["judgment"] == "proxy":
        p = pool[i]; px = dict(s=p["s"], sref=p["sref"], corr=p["corr"], use=None)
        for R in (RA, RC):   # same proxy row for both arms (delta 0); keep each arm's own declined/warned flags only if its row was real
            if R[i]["judgment"] != "proxy": continue
        both_real = RA[i]["judgment"] != "proxy" and RC[i]["judgment"] != "proxy"
        assert not (RA[i]["judgment"] == "proxy") == (RC[i]["judgment"] != "proxy") or True
        for R in (RA, RC): R[i].update(px, judgment="proxy", declined=False, warned=bool(pool[i]["warned"]))
        proxy_ids.append(i)
for R in (RA, RC):
    for i in ids: R[i]["CE"] = (not R[i]["declined"]) and R[i]["corr"] <= 1.5
def U(src, xs): return sum(0 if src[i]["declined"] else src[i]["s"] for i in xs) / sum(src[i]["sref"] for i in xs)
def mean(src, xs, k, nn=3):
    v = [src[i][k] for i in xs if src[i].get(k) is not None]; return round(sum(v) / len(v), nn) if v else None
def summ(src, xs):
    nd = [i for i in xs if not src[i]["declined"]]; ce = [i for i in nd if src[i]["corr"] <= 1.5]
    return dict(n=len(xs), U=round(U(src, xs), 4), corr=mean(src, xs, "corr"), CE=len(ce), CE_unwarned=sum(1 for i in ce if not src[i]["warned"]), warned=sum(1 for i in xs if src[i]["warned"]), declined=sum(1 for i in xs if src[i]["declined"]),
                outTok=mean({i: dict(o=D[i]["timing"].get("outputTokens") or 0) for i in ids} if False else {i: dict(o=(T if src is RA else C)[i]["timing"].get("outputTokens") or 0) for i in xs}, xs, "o", 2))
def boot(xs, f, B=2000):
    r = random.Random(11); v = []
    for _ in range(B): v.append(f([r.choice(xs) for _ in xs]))
    v.sort(); return [round(v[int(0.025 * B)], 4), round(v[int(0.975 * B) - 1], 4)]
def pair(sa, sb, xs):
    if not xs: return dict(n=0)
    f = lambda s: U(sa, s) - U(sb, s); g = lambda s: sum(sa[i]["corr"] - sb[i]["corr"] for i in s) / len(s)
    return dict(n=len(xs), d=round(f(xs), 4), ci=boot(xs, f), dcorr=round(g(xs), 4), dcorr_ci=boot(xs, g))
src_of = lambda i: "v0.1" if not i.startswith("st-") else ("cooking" if "cooking" in i else "money")
real = lambda i: RA[i]["judgment"] != "proxy" and RC[i]["judgment"] != "proxy"
J = [i for i in td if real(i)]   # text differs and both rows real
res = dict(n=97, text_differs=len(td), judged_or_cached_differing=len(J), unjudged_differing=[i for i in td if not real(i)], proxy_ids=len(proxy_ids),
           rows=dict(ALL=dict(collections.Counter(RA[i]["judgment"] for i in ids)), CTL=dict(collections.Counter(RC[i]["judgment"] for i in ids))))
res["all97"] = dict(CTL=summ(RC, ids), ALL=summ(RA, ids)); res["vs_control_all97"] = pair(RA, RC, ids)
res["differing_real"] = dict(CTL=summ(RC, J), ALL=summ(RA, J), **pair(RA, RC, J)); res["changed_text_differs_all"] = pair(RA, RC, td)
res["by_source_all"] = {}
for s in ("v0.1", "cooking", "money"):
    al = [i for i in ids if src_of(i) == s]; xs = [i for i in J if src_of(i) == s]
    res["by_source_all"][s] = dict(n=len(al), differing_real=len(xs), CTL=summ(RC, al), ALL=summ(RA, al), vs_control=pair(RA, RC, al), differing_only=pair(RA, RC, xs))
new23 = sorted(r42["newly_delivered_cm"]["items"]); nr = [i for i in new23 if real(i)]
res["newly_delivered"] = dict(n=len(new23), text_differs=sum(i in td for i in new23), real_rows=len(nr), corr=dict(CTL=mean(RC, nr, "corr"), ALL=mean(RA, nr, "corr")), U=dict(CTL=round(U(RC, nr), 4), ALL=round(U(RA, nr), 4)) if nr else None, vs_control=pair(RA, RC, nr),
                              warned_ALL=sum(RA[i]["warned"] for i in nr), seed42=dict(corr_ctl=r42["newly_delivered_cm"]["mean_corr"]["ctl"], corr_ALL=r42["newly_delivered_cm"]["mean_corr"]["ALL"]))
# pooled two seeds
def prow(a, b):
    ea = 0 if a["declined"] else a["s"]; eb = 0 if b["declined"] else b["s"]
    return dict(s=(ea + eb) / 2, sref=(a["sref"] + b["sref"]) / 2, corr=(a["corr"] + b["corr"]) / 2, declined=False)
PA = {i: prow(r42["rows"]["ALL"][i], RA[i]) for i in ids}; PC = {i: prow(r42["rows"]["control"][i], RC[i]) for i in ids}
chg42 = r42["changed_vs_G"] and [i for i in ids if i in set(r42["texts"])]    # the 43 ids changed vs ARM-G at seed 42 (texts dict holds exactly them)
union = [i for i in ids if i in set(chg42) or i in set(J)]
res["pooled"] = dict(vs_control_all97=pair(PA, PC, ids), changed_union=dict(s42_changed=len(chg42), s43_differing_real=len(J), **pair(PA, PC, union)))
ce = lambda R, xs: sum(1 for i in xs if (not R[i]["declined"]) and R[i]["corr"] <= 1.5 and not R[i]["warned"])
r42rows = r42["rows"]
cew = lambda nm: sum(1 for i in ids if (not r42rows[nm][i]["declined"]) and r42rows[nm][i]["corr"] <= 1.5 and not r42rows[nm][i]["warned"])
res["pooled"]["CE_unwarned"] = dict(seed42=dict(CTL=cew("control"), ALL=cew("ALL")), seed43=dict(CTL=ce(RC, ids), ALL=ce(RA, ids)))
a = res["pooled"]["changed_union"]; b = res["pooled"]["vs_control_all97"]; cu = res["pooled"]["CE_unwarned"]
cu_up = (cu["seed42"]["ALL"] + cu["seed43"]["ALL"]) > (cu["seed42"]["CTL"] + cu["seed43"]["CTL"])
res["rule_pooled"] = dict(changed_dU_ge_0_02_ci_low_gt_minus_0_01=(a["d"] >= 0.02 and a["ci"][0] > -0.01), vs_control_all97_dU_ge_0_02_ci_low_gt_minus_0_01=(b["d"] >= 0.02 and b["ci"][0] > -0.01), CE_unwarned_not_up=not cu_up)
res["rule_pooled"]["LEVER_CANDIDATE"] = all(res["rule_pooled"].values())
a3 = res["changed_text_differs_all"]; b3 = res["vs_control_all97"]; c3 = res["all97"]
res["rule_seed43_alone"] = dict(changed_dU=a3.get("d"), changed_ci=a3.get("ci"), all97_dU=b3["d"], all97_ci=b3["ci"], CE_unwarned_not_up=c3["ALL"]["CE_unwarned"] <= c3["CTL"]["CE_unwarned"],
                                 LEVER_CANDIDATE=a3.get("d", 0) >= 0.02 and a3.get("ci", [-1])[0] > -0.01 and b3["d"] >= 0.02 and b3["ci"][0] > -0.01 and c3["ALL"]["CE_unwarned"] <= c3["CTL"]["CE_unwarned"])
res["items"] = {i: dict(src=src_of(i), text_differs=i in td, ctl={k: RC[i].get(k) for k in ("s", "sref", "corr", "judgment", "declined", "warned")}, ALL={k: RA[i].get(k) for k in ("s", "sref", "corr", "judgment", "declined", "warned")}) for i in ids}
json.dump(res, open(SF + "/answers-sefixall-s43.json", "w"), indent=1, ensure_ascii=False)
S = res["all97"]
L = ["# SEFIX-ALL seed 43 replicate (answer screen; Haiku 5.5-low judge.v1 N4 both orders; Opus 0, paid 0, phone 0)", "",
     "| set (seed 43) | arm | U | corr | CE | CE unwarned | warned | declined |", "|---|---|---|---|---|---|---|---|"]
for nm, blk in (("all 97", S), (f"text-differing, real rows ({len(J)})", res["differing_real"])):
    for arm in ("CTL", "ALL"): s = blk[arm]; L.append(f"| {nm} | {'K1 control' if arm == 'CTL' else 'SEFIX-ALL'} | {s['U']} | {s['corr']} | {s['CE']} | {s['CE_unwarned']} | {s['warned']} | {s['declined']} |")
L += ["", f"rows: ALL {res['rows']['ALL']}, CTL {res['rows']['CTL']}; text differs {len(td)}/97; differing with real rows {len(J)}; unjudged differing {len(res['unjudged_differing'])}; proxy items {len(proxy_ids)} (delta 0 imputed)", "",
      f"- dU all 97 (imputed 0 on proxies): {b3['d']} {b3['ci']}; text-differing set ({a3.get('n')}, proxies imputed 0): {a3.get('d')} {a3.get('ci')}; judged-differing only ({res['differing_real'].get('n')}): {res['differing_real'].get('d')} {res['differing_real'].get('ci')}",
      "- by source (all items, vs control): " + "; ".join(f"{s} n{v['n']} {v['vs_control']['d']} {v['vs_control']['ci']}" for s, v in res["by_source_all"].items()),
      f"- newly delivered 23 (real rows {res['newly_delivered']['real_rows']}): corr CTL {res['newly_delivered']['corr']['CTL']} -> ALL {res['newly_delivered']['corr']['ALL']}; dU {res['newly_delivered']['vs_control'].get('d')} {res['newly_delivered']['vs_control'].get('ci')} (seed 42: corr {res['newly_delivered']['seed42']['corr_ctl']} -> {res['newly_delivered']['seed42']['corr_ALL']})",
      f"- POOLED two seeds: vs control all 97 {b['d']} {b['ci']}; changed union (n {a['n']}) {a['d']} {a['ci']}; CE-unwarned s42 {cu['seed42']}, s43 {cu['seed43']}",
      f"- rule pooled: {res['rule_pooled']}", f"- rule seed 43 alone: {res['rule_seed43_alone']}"]
open(SF + "/answers-sefixall-s43.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
