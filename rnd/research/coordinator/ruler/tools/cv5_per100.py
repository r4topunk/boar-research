#!/usr/bin/env python3
"""CV5-PER100-OPUS analysis (0 calls). Criterion ../CV5-PER100-OPUS-criterion.md. python3 -I cv5_per100.py <out.json>
hon67.py's per-100 code (per100/pboot/table/decide) is exec'd unchanged on rows whose labels are swapped to Opus judge.v1; the Haiku columns are
the same functions on hon67's own rows (= HON6-TIER-PER100 desktop_primary)."""
import json, sys, os, random, collections, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import cv5_opus_pool as CP, cv5_per100_common as PC
RUL = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); W = RUL + "/cv5-per100/"
crit = open(RUL + "/CV5-PER100-OPUS-criterion.sha256").read().split()[0]
assert hashlib.sha256(open(RUL + "/CV5-PER100-OPUS-criterion.md", "rb").read()).hexdigest() == crit
G, TRF, TX, H67SHA = PC.load(); D = G["D"]; S_ = json.load(open(W + "in/set.json")); TIERS = ("4B", "Gemma", "1.7B")
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
lab = lambda a, b: dict(corr=(a["boar"]["correctness"] + b["boar"]["correctness"]) / 2, s=(mr(a["boar"]) + mr(b["boar"])) / 2, sref=(mr(a["ref"]) + mr(b["ref"])) / 2)
OP = {}
for f in sorted(os.listdir(W + "out")):
    if not f.endswith(".judgments.jsonl"): continue
    t = f.split("-")[0]; by = collections.defaultdict(dict)
    for l in open(W + "out/" + f):
        r = json.loads(l)
        if r.get("ok") and not r.get("floorScored"): by[r["queryId"]].setdefault(r["order"], r["mapped"])
    for q, v in by.items():
        if set(v) == {"boarA", "boarB"}: OP[CP.key(q, TX[t][q])] = lab(v["boarA"], v["boarB"])
P = {}
for fr, fq in S_["frames"].values(): P.update(CP.pool(fr, fq, exclude_prefix=W))
for k, u in S_["units"].items():
    if u["reuse"]:
        assert k in P and P[k]["src"] == u["reuse"], k; OP.setdefault(k, lab(P[k]["boarA"], P[k]["boarB"]))
miss = [k for k in S_["units"] if k not in OP]; assert not miss, f"{len(miss)} units without Opus rows: {miss[:5]}"
TRS = {t: G["G"]["traces"]([f]) for t, f in TRF.items()}
def orow(t, i):
    j = OP[CP.key(i, TX[t][i])]; r = G["row"]("D", t, i, TRS[t][i], j); r["weak"] = bool(TRS[t][i]["answer"].get("weakSources")); return r
# item-level Opus sref for the U denominators of unjudged hidden rows (declared imputation)
isref = collections.defaultdict(list)
for k, j in OP.items(): isref[k.split("|")[0]].append(j["sref"])
jd = [(OP[CP.key(i, TX[t][i])]["sref"], D[t][i]["sref"]) for t in TIERS for i in D[t] if CP.key(i, TX[t][i]) in OP]
off = sum(a - b for a, b in jd) / len(jd)
DO, imput = {}, collections.Counter()
for t in TIERS:
    DO[t] = {}
    for i, r in D[t].items():
        if CP.key(i, TX[t][i]) in OP and (not r["hidden"] or not r["dec"]): DO[t][i] = orow(t, i); continue
        x = dict(r)
        if i in isref: x["sref"] = sum(isref[i]) / len(isref[i]); imput["item_opus_sref"] += 1
        else: x["sref"] = r["sref"] + off; imput["haiku_sref_plus_offset"] += 1
        assert x["hidden"], (t, i); DO[t][i] = x
PAIRS = [("4B", "1.7B"), ("4B", "Gemma"), ("Gemma", "1.7B")]
TH = G["table"](D, "D", G["DETP"], TIERS, PAIRS); TO = G["table"](DO, "D", G["DETP"], TIERS, PAIRS)
out = {"criterion_sha256": crit, "hon67_sha256": H67SHA, "n_units": len(S_["units"]), "reused_units": sum(1 for u in S_["units"].values() if u["reuse"]),
       "sref_offset_opus_minus_haiku": round(off, 4), "sref_imputation_rows": dict(imput)}
REF = ("correct", "ce", "partial", "hidden", "U", "U_fa")
def side(sp):
    o = {}
    for t in TIERS:
        h = TH["splits"][sp]["tiers"][t]["refuse"]; p = TO["splits"][sp]["tiers"][t]["refuse"]
        o[t] = {"haiku": {k: h[k] for k in REF}, "opus": {k: p[k] for k in REF}, "opus_minus_haiku": {k: round(p[k] - h[k], 3) for k in REF}}
    pr = {}
    for a, b in PAIRS:
        n = f"{a} - {b}"; pr[n] = {"haiku": {"point": TH["splits"][sp]["paired"][n]["refuse"]["point"], "ci": TH["splits"][sp]["paired"][n]["refuse"]["ci"]},
                                   "opus": {"point": TO["splits"][sp]["paired"][n]["refuse"]["point"], "ci": TO["splits"][sp]["paired"][n]["refuse"]["ci"]}}
    return {"n": TH["splits"][sp]["n"], "tiers": o, "paired": pr}
out["refuse_by_default"] = {sp: side(sp) for sp in ("all", "divergent", "deterministic") if sp in TO["splits"]}
out["decision_hon67_rule"] = {"haiku": G["decide"](TH["splits"]["all"]), "opus_refuse_fields_only": {k: v for k, v in G["decide"](TO["splits"]["all"]).items() if "refuse" in k or k == "pair"}}
# hidden (text) answers: stratified estimate under Opus vs Haiku census; show-all estimate = shown census + hidden estimate
hid = {}
for t in TIERS:
    n = len(D[t]); smp = S_["hidden_sample"][t]; pop = S_["hidden_text_pop"][t]
    def est(sm, f):
        return sum(pop[k] * (sum(f(DO[t][i]) for i in sm[k]) / len(sm[k])) for k in pop if sm.get(k))
    fK = lambda r: r["correct"]; fC = lambda r: r["CE"]
    eK, eC = est(smp, fK), est(smp, fC); rnd = random.Random(11); bK, bC = [], []
    for _ in range(2000):
        sm = {k: [v[rnd.randrange(len(v))] for _ in v] for k, v in smp.items() if v}; bK.append(est(sm, fK)); bC.append(est(sm, fC))
    cI = lambda v: [round(100 * sorted(v)[50] / n, 2), round(100 * sorted(v)[1949] / n, 2)]
    hk = sum(D[t][i]["correct"] for t_ in [t] for i in D[t] if D[t][i]["hidden"] and not D[t][i]["dec"]); hc = sum(D[t][i]["CE"] for i in D[t] if D[t][i]["hidden"] and not D[t][i]["dec"])
    sh = out["refuse_by_default"]["all"]["tiers"][t]
    agree = [(D[t][i]["CE"], DO[t][i]["CE"], D[t][i]["correct"], DO[t][i]["correct"]) for k in smp for i in smp[k]]
    hid[t] = {"hidden_text_rows": sum(pop.values()), "sample": sum(len(v) for v in smp.values()),
              "correct_hidden_per100": {"haiku_census": round(100 * hk / n, 2), "opus_est": round(100 * eK / n, 2), "opus_ci": cI(bK)},
              "ce_hidden_per100": {"haiku_census": round(100 * hc / n, 2), "opus_est": round(100 * eC / n, 2), "opus_ci": cI(bC)},
              "show_all_est_per100": {"opus_correct": round(sh["opus"]["correct"] + 100 * eK / n, 2), "opus_ce": round(sh["opus"]["ce"] + 100 * eC / n, 2),
                                      "haiku_correct": round(sh["haiku"]["correct"] + 100 * hk / n, 2), "haiku_ce": round(sh["haiku"]["ce"] + 100 * hc / n, 2)},
              "sample_agreement": {"n": len(agree), "ce_agree": sum(a == b for a, b, _, _ in agree), "correct_agree": sum(c == d for _, _, c, d in agree),
                                   "haiku_ce": sum(a for a, _, _, _ in agree), "opus_ce": sum(b for _, b, _, _ in agree), "haiku_correct": sum(c for _, _, c, _ in agree), "opus_correct": sum(d for _, _, _, d in agree)}}
out["hidden"] = hid
# agreement on shown rows
ag = {}
for t in TIERS:
    xs = [(D[t][i], DO[t][i]) for i in D[t] if not D[t][i]["hidden"]]
    ag[t] = {"n": len(xs), "ce_agree": sum(a["CE"] == b["CE"] for a, b in xs), "correct_agree": sum(a["correct"] == b["correct"] for a, b in xs),
             "haiku_only_ce": sorted(a["id"] for a, b in xs if a["CE"] and not b["CE"]), "opus_only_ce": sorted(a["id"] for a, b in xs if b["CE"] and not a["CE"]),
             "corr_mean_opus_minus_haiku": round(sum(b["corr"] - a["corr"] for a, b in xs) / len(xs), 3)}
out["shown_agreement"] = ag
A_ = out["refuse_by_default"]["all"]; tz = A_["tiers"]; pz = A_["paired"]
dce = pz["4B - 1.7B"]["opus"]; dk = {n: pz[n]["opus"]["point"]["correct"] for n in pz}
r = {"ce_move_per_tier": {t: tz[t]["opus_minus_haiku"]["ce"] for t in TIERS}, "correct_rise_per_tier": {t: tz[t]["opus_minus_haiku"]["correct"] for t in TIERS},
     "dCE_4B_minus_17B_opus": dce["point"]["ce"], "dCE_ci": dce["ci"]["ce"], "dK_pairs_opus": dk}
r["kill_ce_move"] = any(abs(v) > 2 for v in r["ce_move_per_tier"].values())
r["kill_ce_order"] = bool(dce["point"]["ce"] > 0 and dce["ci"]["ce"][0] > 0)
r["kill_tie"] = any(abs(v) >= 5 for v in dk.values())
r["pred_correct_rise_ge3_all"] = all(v >= 3 for v in r["correct_rise_per_tier"].values())
r["ce_order_4B_le_17B_opus"] = bool(dce["point"]["ce"] <= 0)
r["verdict"] = "KILLED" if (r["kill_ce_move"] or r["kill_ce_order"] or r["kill_tie"]) else ("SUPPORTED" if r["pred_correct_rise_ge3_all"] else "HOLDS, PREDICTION PARTIAL")
out["rules"] = r
js = json.dumps(out, indent=1, ensure_ascii=False); open(sys.argv[1], "w").write(js + "\n"); print(json.dumps(r, indent=1))
