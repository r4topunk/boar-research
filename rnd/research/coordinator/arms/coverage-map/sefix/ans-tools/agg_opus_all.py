#!/usr/bin/env python3
"""SEFIX-ALL Opus confirm aggregate (0 calls). python3 -I agg_opus_all.py -> ../opus-sefixall.json, ../opus-sefixall.md
Arms on the CV5 51 (v0.1 dev): control = MINI-BASELINE K1 (litepacks/traces/mini/lp-K1-v01-s42.mini.traces.jsonl), ALL = ans-traces/sefixall-main-s42.
Opus judge.v1 row per (id, answer text): existing pool row (ruler/tools/cv5_opus_pool.py, v0.1 frame bd235bb9/568b3ece, seed 7) else opus/{all,ctl}.judgments.jsonl.
Set S = plan.json (42 ids: cap fit, see CALLS.md). U = sum(s-1)/sum(r-1); item bootstrap B 2000, numpy default_rng(11), pct 2.5/97.5, paired on the same draws."""
import json, sys, os, numpy as np
R = "<workspace>/rnd/research/coordinator"; A = R + "/arms"; SF = A + "/coverage-map/sefix"; O = SF + "/opus"
sys.path.insert(0, R + "/ruler/tools"); import cv5_opus_pool as CP
sys.path.insert(0, A + "/null-cal/tools"); import labels as LB
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
plan = json.load(open(O + "/plan.json")); S = plan["S"]
cv5 = json.load(open(R + "/ruler/cv5-ladder/in/set.json"))["ids"]
TC = {t["itemId"]: t for t in rd(A + "/litepacks/traces/mini/lp-K1-v01-s42.mini.traces.jsonl")}
TA = {t["itemId"]: t for t in rd(SF + "/ans-traces/sefixall-main-s42.traces.jsonl")}
P = CP.pool("bd235bb9811f6d1ae88ba2d2ae3973e3572d75b6c451ee4cdd3a2e7644db48b1", "568b3ececd8afe5cad63a7f39bffe414e6dd45bcef9d03ef112faecad2981b18")
def own(f):
    J = {}
    for r in rd(f):
        if r.get("ok") and not r.get("floorScored"): J.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    return J
OA, OC = own(O + "/all.judgments.jsonl"), own(O + "/ctl.judgments.jsonl")
def row(i, T, own_):
    tx = T[i]["answer"]["text"]; u = P.get(CP.key(i, tx)); src = "new" if u and u["src"].startswith(O) else "pool"
    if u is None:
        o = own_.get(i)
        if o is None and T is TC:   # shared-text unit judged once on the ALL traces
            if TA[i]["answer"]["text"] == tx: o = OA.get(i)
        assert o and set(o) == {"boarA", "boarB"}, i; u = o; src = "new"
    a, b = u["boarA"], u["boarB"]
    return dict(s=(mr(a["boar"]) + mr(b["boar"])) / 2, r=(mr(a["ref"]) + mr(b["ref"])) / 2, corr=(a["boar"]["correctness"] + b["boar"]["correctness"]) / 2, src=src)
J = {"ctl": {}, "all": {}}
for i in S:
    J["ctl"][i] = row(i, TC, OC); J["all"][i] = row(i, TA, OA)
    if TC[i]["answer"]["text"] == TA[i]["answer"]["text"]: assert abs(J["ctl"][i]["s"] - J["all"][i]["s"]) < 1e-9, i   # identical text -> identical row
def fl(T, i):
    a = T[i]["answer"]; d = bool(LB.is_decline(a["text"], a.get("declined"))); return dict(warned=a["text"].startswith(W), declined=d)
FL = {"ctl": {i: fl(TC, i) for i in S}, "all": {i: fl(TA, i) for i in S}}
Uf = lambda s, r: (s - 1).sum() / (r - 1).sum()
ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
def arr(a, ii, k): return np.array([J[a][i][k] for i in ii])
def stats(ii, d=None):
    n = len(ii); rng = np.random.default_rng(11); dr = [rng.integers(0, n, n) for _ in range(2000)]
    M = {a: (arr(a, ii, "s"), arr(a, ii, "r")) for a in J}; out = {"n": n, "arms": {}}
    bs = {a: np.array([Uf(M[a][0][x], M[a][1][x]) for x in dr]) for a in M}
    for a in J:
        corr = arr(a, ii, "corr"); dec = np.array([FL[a][i]["declined"] for i in ii]); war = np.array([FL[a][i]["warned"] for i in ii])
        ce = (corr <= 1.5) & ~dec; cor = (corr >= 4) & ~dec
        out["arms"][a] = dict(U=round(Uf(*M[a]), 4), U_ci=ci(bs[a]), corr=round(float(corr.mean()), 3), correct_per100=round(100 * cor.mean(), 1), CE_per100=round(100 * ce.mean(), 1), decline_per100=round(100 * dec.mean(), 1),
                              CE=int(ce.sum()), CE_unwarned=int((ce & ~war).sum()), warned=int(war.sum()), declined=int(dec.sum()))
    dU = Uf(*M["all"]) - Uf(*M["ctl"]); db = bs["all"] - bs["ctl"]; ds = M["all"][0] - M["ctl"][0]
    out["dU"] = round(float(dU), 4); out["dU_ci"] = ci(db); out["win"] = int((ds > .25).sum()); out["tie"] = int((abs(ds) <= .25).sum()); out["loss"] = int((ds < -.25).sum())
    out["dcorr"] = round(float((arr("all", ii, "corr") - arr("ctl", ii, "corr")).mean()), 3)
    return out
def haiku(ii):   # same ids, Haiku rows of the answer screen (control = pool-K1 row, ALL = reused/judged row)
    h = json.load(open(SF + "/answers-sefixall.json"))["rows"]; n = len(ii); rng = np.random.default_rng(11); dr = [rng.integers(0, n, n) for _ in range(2000)]
    s = {a: np.array([h[a][i]["s"] for i in ii]) for a in ("control", "ALL")}; r = {a: np.array([h[a][i]["sref"] for i in ii]) for a in s}
    f = lambda x: Uf(s["ALL"][x], r["ALL"][x]) - Uf(s["control"][x], r["control"][x])
    return dict(U_ctl=round(Uf(s["control"], r["control"]), 4), U_all=round(Uf(s["ALL"], r["ALL"]), 4), dU=round(float(f(np.arange(n))), 4), dU_ci=ci([f(x) for x in dr]))
sefix = [i for i in S if json.load(open(SF + "/ans-judge/sanity_all.json"))["changed_ids"].count(i)]
differ = [i for i in S if TC[i]["answer"]["text"] != TA[i]["answer"]["text"]]
res = {"S": S, "n": len(S), "dropped_for_cap": plan["drop"], "excluded_identical_no_row": plan["excluded_identical_missing"],
       "rows_new": {a: sum(1 for i in S if J[a][i]["src"] == "new") for a in J}, "rows_pool": {a: sum(1 for i in S if J[a][i]["src"] == "pool") for a in J}}
res["S42"] = stats(S); res["differing30"] = stats(differ); res["sefix_changed6"] = stats(sefix)
res["haiku_same_ids"] = {"S42": haiku(S), "differing30": haiku(differ), "sefix_changed6": haiku(sefix)}
res["items"] = {i: dict(ctl_s=round(J["ctl"][i]["s"], 3), all_s=round(J["all"][i]["s"], 3), ctl_corr=J["ctl"][i]["corr"], all_corr=J["all"][i]["corr"], same_text=i not in differ, sefix_changed=i in sefix) for i in S}
d = res["S42"]
res["verdict"] = "LEVER" if d["dU"] >= 0.03 and d["dU_ci"][0] > 0 else f"not decided at n {len(S)} (dU {d['dU']:+.3f}, CI {d['dU_ci'][0]:+.3f}..{d['dU_ci'][1]:+.3f})"
json.dump(res, open(SF + "/opus-sefixall.json", "w"), indent=1)
L = ["# SEFIX-ALL Opus confirm (judge.v1, claude-opus-5-5, N 4, both orders, seed 7), CV5 51 subset n %d" % len(S), "",
     "Set: 42 of the CV5 51 (cap fit, outcome-blind; dropped %s; excluded identical-text ids without an Opus row %s). Control = MINI-BASELINE K1 mini traces. Rows: pool (identical unit) / new: ctl %d/%d, ALL %d/%d. Opus calls 102 of 110." % (", ".join(plan["drop"]), ", ".join(plan["excluded_identical_missing"]), res["rows_pool"]["ctl"], res["rows_new"]["ctl"], res["rows_pool"]["all"], res["rows_new"]["all"]), "",
     "| set | n | U ctl | U ALL | dU (CI) | win/tie/loss | dcorr | correct/100 ctl>ALL | CE/100 ctl>ALL | CE-unwarned ctl>ALL | decl/100 ctl>ALL |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for k, nm in (("S42", "S (42)"), ("differing30", "text differs (30)"), ("sefix_changed6", "SEFIX-changed vs ARM-G (6)")):
    x = res[k]; c, a = x["arms"]["ctl"], x["arms"]["all"]
    L.append(f"| {nm} | {x['n']} | {c['U']} {c['U_ci']} | {a['U']} {a['U_ci']} | {x['dU']:+.4f} {x['dU_ci']} | {x['win']}/{x['tie']}/{x['loss']} | {x['dcorr']:+.3f} | {c['correct_per100']} > {a['correct_per100']} | {c['CE_per100']} > {a['CE_per100']} | {c['CE_unwarned']} > {a['CE_unwarned']} | {c['decline_per100']} > {a['decline_per100']} |")
L += ["", "Haiku read, same ids (answer screen rows):"] + [f"- {k}: U ctl {v['U_ctl']} ALL {v['U_all']} dU {v['dU']:+.4f} {v['dU_ci']}" for k, v in res["haiku_same_ids"].items()]
L += ["", "Verdict: " + res["verdict"]]
open(SF + "/opus-sefixall.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
