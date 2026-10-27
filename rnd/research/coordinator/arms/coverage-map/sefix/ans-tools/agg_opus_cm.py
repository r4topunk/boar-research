#!/usr/bin/env python3
"""SEFIX Opus read on the cooking/money units (0 calls). python3 -I agg_opus_cm.py -> ../opus-cm.json, ../opus-cm.md
Arms (seed 42): K3 control = MINI-BASELINE K1 cm traces (litepacks/traces/mini/lp-K1-cm-s42), ALL = ans-traces/sefixall-main-s42. Opus judge.v1 row per (id, answer text): existing pool row
(cv5_opus_pool, frame = the self-test's refs/questions hashes, seed 7) else opus-cm/{CTL,ALL}.<unit>.judgments.jsonl. Judged set = opus-cm/plan.json 'selected' (differing text, priority newly delivered).
U = ratio of sums; item bootstrap B 2000, default_rng(11), pct 2.5/97.5, paired on the same draws. CE = corr <= 1.5 and not declined; correct = corr >= 4."""
import json, sys, glob, numpy as np
R = "<workspace>/rnd/research/coordinator"; A = R + "/arms"; SF = A + "/coverage-map/sefix"; O = SF + "/opus-cm"
sys.path.insert(0, R + "/ruler/tools"); import cv5_opus_pool as CP
sys.path.insert(0, A + "/null-cal/tools"); import labels as LB
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
plan = json.load(open(O + "/plan.json")); sel = plan["selected"]; new = plan["newly_delivered_cm"]; fr = plan["frames"]
TC = {t["itemId"]: t for t in rd(A + "/litepacks/traces/mini/lp-K1-cm-s42.mini.traces.jsonl")}; TA = {t["itemId"]: t for t in rd(SF + "/ans-traces/sefixall-main-s42.traces.jsonl")}
unit = lambda i: "qa-cooking-se" if "cooking" in i else "qa-money-se"
P = {u: CP.pool(*fr[u]) for u in fr}
OWN = {"ctl": {}, "all": {}}
for arm in ("ctl", "all"):
    for f in glob.glob(f"{O}/{arm.upper()}.*.judgments.jsonl"):
        for r in rd(f):
            if r.get("ok") and not r.get("floorScored") and "opus" in str(r.get("judgeModel")): OWN[arm].setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
def row(i, T, arm):
    tx = T[i]["answer"]["text"]; u = P[unit(i)].get(CP.key(i, tx)); src = "new" if u and u["src"].startswith(O) else "pool"   # the pool walk also indexes this run's own files
    if u is None:
        u = OWN[arm].get(i); src = "new"
        assert u and set(u) == {"boarA", "boarB"}, (arm, i)
    a, b = u["boarA"], u["boarB"]
    return dict(s=(mr(a["boar"]) + mr(b["boar"])) / 2, r=(mr(a["ref"]) + mr(b["ref"])) / 2, corr=(a["boar"]["correctness"] + b["boar"]["correctness"]) / 2, src=src)
J = {"ctl": {}, "all": {}}
for i in sel: J["ctl"][i] = row(i, TC, "ctl"); J["all"][i] = row(i, TA, "all")
free_same = [i for i in new if i not in sel and TC[i]["answer"]["text"] == TA[i]["answer"]["text"]]   # cooking-002: identical text, both pool rows
for i in free_same: J["ctl"][i] = row(i, TC, "ctl"); J["all"][i] = row(i, TA, "all"); assert abs(J["ctl"][i]["s"] - J["all"][i]["s"]) < 1e-9
def fl(T, i): a = T[i]["answer"]; return dict(warned=a["text"].startswith(W), declined=bool(LB.is_decline(a["text"], a.get("declined"))))
FL = {"ctl": {i: fl(TC, i) for i in J["ctl"]}, "all": {i: fl(TA, i) for i in J["all"]}}
Uf = lambda s, r: (s - 1).sum() / (r - 1).sum()
ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
arr = lambda a, ii, k: np.array([J[a][i][k] for i in ii])
def stats(ii):
    n = len(ii); rng = np.random.default_rng(11); dr = [rng.integers(0, n, n) for _ in range(2000)]
    M = {a: (arr(a, ii, "s"), arr(a, ii, "r")) for a in J}; out = {"n": n, "arms": {}}; bs = {a: np.array([Uf(M[a][0][x], M[a][1][x]) for x in dr]) for a in M}
    for a in J:
        corr = arr(a, ii, "corr"); dec = np.array([FL[a][i]["declined"] for i in ii]); war = np.array([FL[a][i]["warned"] for i in ii]); ce = (corr <= 1.5) & ~dec; cor = (corr >= 4) & ~dec
        out["arms"][a] = dict(U=round(Uf(*M[a]), 4), U_ci=ci(bs[a]), corr=round(float(corr.mean()), 3), correct_per100=round(100 * cor.mean(), 1), CE_per100=round(100 * ce.mean(), 1), decline_per100=round(100 * dec.mean(), 1),
                              correct=int(cor.sum()), CE=int(ce.sum()), CE_unwarned=int((ce & ~war).sum()), warned=int(war.sum()), declined=int(dec.sum()))
    db = bs["all"] - bs["ctl"]; ds = M["all"][0] - M["ctl"][0]
    out.update(dU=round(float(Uf(*M["all"]) - Uf(*M["ctl"])), 4), dU_ci=ci(db), win=int((ds > .25).sum()), tie=int((abs(ds) <= .25).sum()), loss=int((ds < -.25).sum()), dcorr=round(float((arr("all", ii, "corr") - arr("ctl", ii, "corr")).mean()), 3))
    return out
H = json.load(open(SF + "/answers-sefixall.json"))["rows"]
for i in J["ctl"]: assert H["control"][i]["text"] == TC[i]["answer"]["text"] if "text" in H["control"][i] else True
def haiku(ii):
    n = len(ii); rng = np.random.default_rng(11); dr = [rng.integers(0, n, n) for _ in range(2000)]
    s = {a: np.array([H[a][i]["s"] for i in ii]) for a in ("control", "ALL")}; r = {a: np.array([H[a][i]["sref"] for i in ii]) for a in s}
    f = lambda x: Uf(s["ALL"][x], r["ALL"][x]) - Uf(s["control"][x], r["control"][x]); c = lambda a: np.array([H[a][i]["corr"] for i in ii])
    return dict(n=n, U_ctl=round(Uf(s["control"], r["control"]), 4), U_all=round(Uf(s["ALL"], r["ALL"]), 4), dU=round(float(f(np.arange(n))), 4), dU_ci=ci([f(x) for x in dr]), corr_ctl=round(float(c("control").mean()), 3), corr_all=round(float(c("ALL").mean()), 3))
allcm = sorted(TC); nj = [i for i in sel if i in new]; oth = [i for i in sel if i not in new]
res = {"selected": sel, "n": len(sel), "left_unjudged": plan["left_unjudged"], "rows": {a: {"new": sum(1 for i in sel if J[a][i]["src"] == "new"), "pool": sum(1 for i in sel if J[a][i]["src"] == "pool")} for a in J}}
res["judged22"] = stats(sel); res["new_delivered_judged"] = stats(nj); res["other_judged"] = stats(oth)
nd21 = [i for i in new if i in J["ctl"]]; res["new_delivered_all21"] = stats(nd21)
res["haiku_same_ids"] = {"judged22": haiku(sel), "new_delivered_judged": haiku(nj), "other_judged": haiku(oth), "new_delivered_all21": haiku(nd21), "all_cm40": haiku(allcm)}
def screenU(ii):
    n = len(ii); rng = np.random.default_rng(11); dr = [rng.integers(0, n, n) for _ in range(2000)]
    g = lambda a, x: sum(0 if FL[a][ii[k]]["declined"] else J[a][ii[k]]["s"] for k in x) / sum(J[a][ii[k]]["r"] for k in x)
    f = lambda x: g("all", x) - g("ctl", x); idx = list(range(n))
    return dict(U_ctl=round(g("ctl", idx), 4), U_all=round(g("all", idx), 4), dU=round(f(idx), 4), dU_ci=ci([f(x) for x in dr]))
res["screenU_definition_opus_judged22"] = screenU(sel)
res["haiku_unjudged_differing16"] = haiku(plan["left_unjudged"])
res["new21_corr"] = {i: dict(ctl=J["ctl"][i]["corr"], all=J["all"][i]["corr"], haiku_ctl=H["control"][i]["corr"], haiku_all=H["ALL"][i]["corr"], all_warned=FL["all"][i]["warned"]) for i in nd21}
d = res["judged22"]
res["verdict"] = "LEVER on the covered domain" if d["dU"] >= 0.03 and d["dU_ci"][0] > 0 else f"not decided at n {len(sel)} (dU {d['dU']:+.3f}, CI {d['dU_ci'][0]:+.3f}..{d['dU_ci'][1]:+.3f})"
res["items"] = {i: dict(ctl_s=round(J["ctl"][i]["s"], 3), all_s=round(J["all"][i]["s"], 3), ctl_corr=J["ctl"][i]["corr"], all_corr=J["all"][i]["corr"], new_delivered=i in new) for i in sel}
json.dump(res, open(SF + "/opus-cm.json", "w"), indent=1)
L = ["# SEFIX-ALL Opus read, cooking/money units (judge.v1, claude-opus-5-5, N 4, both orders, seed 7; seed 42; control = K1 cm traces)", "",
     f"Judged set = {len(sel)} differing-text units of the 40 (20 of the 21 newly delivered cm facts whose text differs + 2 by id order); left unjudged for the 60-call cap: {len(plan['left_unjudged'])} differing units ({', '.join(i.replace('st-qa-','').replace('-se','') for i in plan['left_unjudged'])}). Rows (new/pool): ctl {res['rows']['ctl']['new']}/{res['rows']['ctl']['pool']}, ALL {res['rows']['all']['new']}/{res['rows']['all']['pool']}.", "",
     "| set | n | U ctl | U ALL | dU (CI) | win/tie/loss | dcorr | correct/100 ctl>ALL | CE/100 ctl>ALL | CE-unwarned ctl>ALL | decl/100 ctl>ALL |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for k, nm in (("judged22", "judged (22)"), ("new_delivered_judged", "newly delivered, judged"), ("other_judged", "other judged"), ("new_delivered_all21", "newly delivered, all 21 (incl. identical cooking-002)")):
    x = res[k]; c, a = x["arms"]["ctl"], x["arms"]["all"]
    L.append(f"| {nm} | {x['n']} | {c['U']} {c['U_ci']} | {a['U']} {a['U_ci']} | {x['dU']:+.4f} {x['dU_ci']} | {x['win']}/{x['tie']}/{x['loss']} | {x['dcorr']:+.3f} | {c['correct_per100']} > {a['correct_per100']} | {c['CE_per100']} > {a['CE_per100']} | {c['CE_unwarned']} > {a['CE_unwarned']} | {c['decline_per100']} > {a['decline_per100']} |")
L += ["", "Haiku read on the same ids (answer-screen rows):"] + [f"- {k} (n {v['n']}): U ctl {v['U_ctl']} ALL {v['U_all']} dU {v['dU']:+.4f} {v['dU_ci']}; corr {v['corr_ctl']} > {v['corr_all']}" for k, v in res["haiku_same_ids"].items()]
L += ["", "Sensitivity, answer-screen U definition (decline = 0, sum s / sum sref), Opus judged 22: " + json.dumps(res["screenU_definition_opus_judged22"]), "Haiku on the 16 differing units left unjudged: " + json.dumps(res["haiku_unjudged_differing16"])]
L += ["", "Verdict: " + res["verdict"]]
open(SF + "/opus-cm.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
