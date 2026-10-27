#!/usr/bin/env python3
"""UIFLAG-PRECISION (0 LLM, 0 judge): precision of a UI-only flag the native app could compute without our rules:
flag = model-generated answer AND (no kept source OR no [n] citation in the raw model stream), vs our five-rule warning line (r["w"]).
Raw stream = concatenated token events (before our citation-support check strips [n]). Rows/labels reused unchanged:
 - HON-7 frame (MAIN 97 K0 s42, 4B / Gemma E2B / 1.7B ctl): Haiku 5.5-low judge.v1 labels (hon67.py via cv5_per100.py's loader)
 - same rows with Opus judge.v1 labels where CV5-PER100-OPUS has them (shown answers census + 20-row hidden sample per tier; unweighted)
 - LITEPACKS 1.7B K0/K1 (MacBook, MAIN + ST-SE + ST-cand): Haiku labels (warncal_showanyway.py rows)
Usage: python3 -I uiflag.py -> ../aggregates/uiflag.json"""
import json, os, re, glob, hashlib, collections, random
R0 = "<workspace>/rnd/research/coordinator"; RT = f"{R0}/ruler/tools"; OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIT = re.compile(r"\[\d+\]")
def raw(t):
    s = "".join(e.get("text") or "" for e in t.get("events", []) if e.get("type") == "token")
    return s if s.strip() else t["answer"]["text"]
def wilson(k, n, z=1.96):
    if not n: return None
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z * ((p*(1-p)/n + z*z/(4*n*n)) ** 0.5) / d
    return [round(c-h, 3), round(c+h, 3)]
def stats(rows, flag):
    a = [r for r in rows if not r["dec"]]; f = [r for r in a if flag(r)]; ce = sum(r["CE"] for r in a)
    cf = sum(r["CE"] for r in f); kf = sum(r["correct"] for r in f); llm = [r for r in a if r["ot"] > 0]
    return dict(n=len(a), n_llm=len(llm), flagged=len(f), coverage=round(len(f)/len(a), 3) if a else None,
                p_correct_flag=round(kf/len(f), 3) if f else None, p_correct_ci=wilson(kf, len(f)),
                p_ce_flag=round(cf/len(f), 3) if f else None, p_ce_ci=wilson(cf, len(f)), recall_ce=round(cf/ce, 3) if ce else None,
                ce_flag=cf, correct_flag=kf, ce_all=ce, health_flagged=sum(1 for r in f if r.get("health")))
def ui(r): return r["ot"] > 0 and (r["kept"] == 0 or not CIT.search(r["raw"]))
def line(r): return bool(r["w"])
def both(rows):
    o = {"ui_flag": stats(rows, ui), "our_line": stats(rows, line), "ui_minus_line": stats(rows, lambda r: ui(r) and not line(r)),
         "line_not_ui": sum(1 for r in rows if not r["dec"] and line(r) and not ui(r))}
    nh = [r for r in rows if not r.get("health")]; o["ui_flag_nonhealth"] = stats(nh, ui); o["our_line_nonhealth"] = stats(nh, line)
    return o
# --- HON-7 frame, Haiku + Opus (cv5_per100.py data section, unchanged, exec'd up to PAIRS) ---
CV = f"{RT}/cv5_per100.py"; src = open(CV).read(); C = {"__file__": CV, "__name__": "cv5_defs"}
cwd = os.getcwd(); os.chdir(RT); exec(src[:src.index("PAIRS = ")], C); os.chdir(cwd)
D, DO, OP, CP, TX, TRS = C["D"], C["DO"], C["OP"], C["CP"], C["TX"], C["TRS"]
res = {"note": "CE corr<=1.5, correct corr>=4; declines excluded (HON-7 frame); flag only on model-generated rows (outputTokens>0); raw = token stream before citation stripping",
       "judges": {"haiku": "Haiku 5.5-low judge.v1 (census)", "opus": "Opus judge.v1 (CV5-PER100-OPUS units; unweighted subset, direction only)"}, "hon7_frame": {}, "litepacks_17b": {}}
for t in ("4B", "Gemma", "1.7B"):
    hr = [dict(r, raw=raw(TRS[t][i])) for i, r in D[t].items()]
    orow = [dict(DO[t][i], raw=raw(TRS[t][i])) for i in D[t] if CP.key(i, TX[t][i]) in OP and not DO[t][i]["dec"]]
    res["hon7_frame"][t] = {"haiku": both(hr), "opus_subset": both(orow), "n_opus_rows": len(orow),
                            "deterministic_no_cite_rows": sum(1 for r in hr if r["ot"] == 0 and not r["dec"] and not CIT.search(r["raw"]))}
# --- LITEPACKS 1.7B K0/K1 (warncal rows, unchanged) ---
WC = f"{RT}/warncal_showanyway.py"; ws = open(WC).read(); G = {"__file__": WC, "__name__": "warncal_defs"}
exec(ws[:ws.index("LPR = [r for r")], G)
LP = G["LP"]; TRA = {a: G["traces"](sorted(glob.glob(f"{LP}/traces/lp-{a}-*-s42.traces.jsonl"))) for a in ("K0", "K1")}
for a in ("K0", "K1"):
    rows = [dict(r, raw=raw(TRA[a][r["id"]])) for r in G["R"] if r["src"] == "LP" and r["arm"] == a]
    res["litepacks_17b"][a] = {"all": both(rows), **{s: both([r for r in rows if r["set"] == s]) for s in ("MAIN", "ST-SE", "ST-cand")}}
s = json.dumps(res, indent=1); open(f"{OUT}/aggregates/uiflag.json", "w").write(s); print("sha256", hashlib.sha256(s.encode()).hexdigest())
for t, v in res["hon7_frame"].items():
    for j in ("haiku", "opus_subset"):
        u, l = v[j]["ui_flag"], v[j]["our_line"]
        print(t, j, "UI", u["flagged"], u["n"], u["coverage"], u["p_correct_flag"], u["p_ce_flag"], u["recall_ce"], "| LINE", l["flagged"], l["coverage"], l["p_correct_flag"], l["p_ce_flag"], l["recall_ce"], "| ui-only", v[j]["ui_minus_line"]["flagged"], v[j]["ui_minus_line"]["p_ce_flag"], v[j]["ui_minus_line"]["p_correct_flag"])
    print(t, "det no-cite", v["deterministic_no_cite_rows"], "nonhealth UI", v["haiku"]["ui_flag_nonhealth"]["p_ce_flag"], v["haiku"]["ui_flag_nonhealth"]["coverage"])
for a, v in res["litepacks_17b"].items():
    for sp in ("all", "MAIN", "ST-SE", "ST-cand"):
        u, l = v[sp]["ui_flag"], v[sp]["our_line"]
        print("LP", a, sp, "UI", u["flagged"], u["n"], u["coverage"], u["p_correct_flag"], u["p_ce_flag"], u["recall_ce"], "| LINE", l["flagged"], l["coverage"], l["p_correct_flag"], l["p_ce_flag"], l["recall_ce"], "| line_not_ui", v[sp]["line_not_ui"])
