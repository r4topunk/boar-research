#!/usr/bin/env python3
"""WEB-ACTIONS-B item 1 (T1.4 / W3): warning-line precision split by 'no source kept' (answerability proxy) vs 'source kept, low support'
(correctness proxy). 0 LLM, 0 judge. Reuses ruler/tools/warncal_showanyway.py + hon67.py definition blocks unchanged (exec).
Usage: python3 -I b1_warn_axes.py -> ../aggregates/b1-warn-axes.json"""
import json, hashlib, os, collections, glob
R0 = "<workspace>/rnd/research/coordinator"; HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
WC = f"{R0}/ruler/tools/warncal_showanyway.py"; src = open(WC).read()
G = {"__file__": WC, "__name__": "warncal_defs"}; seg = lambda a, b: src[src.index(a):src.index(b)]
exec(src[:src.index("LPR = [r for r")], G)  # builds R (LP K0/K1/K3 + MINI K0/K1 rows) and helpers
R, wilson, cboot = G["R"], G["wilson"], G["cboot"]
# per-tier desktop frame (HON-7: MAIN 97 K0 s42; 4B / Gemma E2B / 1.7B ctl)
hs = open(f"{R0}/ruler/tools/hon67.py").read()
H = {"__file__": f"{R0}/ruler/tools/hon67.py", "__name__": "hon67_defs"}
exec(hs[:hs.index("LP = G[\"LP\"]")], H)
TIERS = {t: list(H["D"][t].values()) for t in ("4B", "Gemma", "1.7B")}
def split(rows):
    a = [r for r in rows if not r["dec"]]
    grp = {"warned:no-source": [r for r in a if r["w"] and r["kept"] == 0], "warned:kept-low-support": [r for r in a if r["w"] and r["kept"] > 0],
           "unwarned:no-kept(banner)": [r for r in a if not r["w"] and r["kept"] == 0 and r["ot"] > 0], "unwarned:kept": [r for r in a if not r["w"] and r["kept"] > 0 and r["ot"] > 0]}
    o = {}
    for g, rs in grp.items():
        n = len(rs); ce = sum(r["CE"] for r in rs); ok = sum(r["correct"] for r in rs)
        o[g] = dict(n=n, ce=ce, p_ce=round(ce / n, 3) if n else None, p_ce_ci=wilson(ce, n), correct=ok, p_corr=round(ok / n, 3) if n else None, p_corr_ci=wilson(ok, n))
    allce = sum(r["CE"] for r in a)
    o["share_of_warned_no_source"] = round(o["warned:no-source"]["n"] / max(1, o["warned:no-source"]["n"] + o["warned:kept-low-support"]["n"]), 3)
    o["recall_contrib"] = {g: round(o[g]["ce"] / allce, 3) if allce else None for g in ("warned:no-source", "warned:kept-low-support")}
    def dprec(s):
        x = [r for r in s if not r["dec"] and r["w"]]; ns = [r for r in x if r["kept"] == 0]; kp = [r for r in x if r["kept"] > 0]
        return (sum(r["CE"] for r in ns) / len(ns) - sum(r["CE"] for r in kp) / len(kp)) if ns and kp else None
    o["diff_p_ce_nosrc_minus_kept"] = round(dprec(rows), 3) if dprec(rows) is not None else None
    o["diff_ci"] = cboot(rows, dprec)
    return o
res = {"note": "kept = retrieval.kept count in the trace; CE corr<=1.5, correct corr>=4 (labels.py); Haiku 5.5-low judge.v1 labels; cluster CI B2000 seed11",
       "reason_code_agreement": collections.Counter(f'{r["bucket"]}|kept={"0" if r["kept"]==0 else ">0"}' for r in R if r["w"] and not r["dec"])}
LPR = [r for r in R if r["src"] == "LP"]; MIN = [r for r in R if r["src"] == "MINI"]
res["LP_pooled"] = split(LPR); res["MINI_pooled"] = split(MIN)
res["LP_by_set"] = {s: split([r for r in LPR if r["set"] == s]) for s in ("MAIN", "ST-cand", "ST-SE")}
res["tier_MAIN_K0"] = {t: split(v) for t, v in TIERS.items()}
# Opus labels (WARN-OPUS sample, warned strata W-nh + W-h; unweighted, direction only)
D = json.load(open(f"{R0}/ruler/warn-opus/in/set.json")); OP = json.load(open(f"{R0}/ruler/warn-opus/warn-opus-opus.json"))
ex = {}
src2 = open(f"{R0}/ruler/tools/warn_opus_analyze.py").read(); E = {"__name__": "x", "__file__": f"{R0}/ruler/tools/warn_opus_analyze.py"}
exec(src2[:src2.index("CE = lambda c")], E)
opc = collections.defaultdict(lambda: collections.Counter())
for s in ("W-nh", "W-h"):
    for u in D["sample"][s]:
        g = "no-source" if u["rows"][0]["bucket"] == "W:no-source" else "kept-low-support"
        c = E["OP"][u["key"]]["corr"]; hc = u["rows"][0]["haiku_corr"]
        opc[f"{s}|{g}"].update(n=1, opus_ce=c <= 1.5, opus_correct=c >= 4, haiku_ce=hc <= 1.5, haiku_correct=hc >= 4)
res["opus_warned_units"] = {k: dict(v) for k, v in sorted(opc.items())}
s = json.dumps(res, indent=1, default=lambda o: dict(o)); open(f"{OUT}/aggregates/b1-warn-axes.json", "w").write(s)
print(s[:200]); print("sha256", hashlib.sha256(s.encode()).hexdigest())
