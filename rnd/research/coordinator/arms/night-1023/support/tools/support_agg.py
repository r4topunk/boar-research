#!/usr/bin/env python3
"""SUPPORT aggregate (0 LLM). python3 -I support_agg.py <prep.json> -> ../support-2x2.json, ../support-2x2.md. Reuses b_agg.py machinery (exec'd with its b-table.json write redirected)."""
import json, sys, os, io, contextlib, collections
NB = "<workspace>/rnd/research/coordinator/arms/night-1023"
src = open(NB + "/b/tools/b_agg.py").read().replace('open(NB + "/b-table.json", "w")', 'open(os.devnull, "w")')
PREP = sys.argv[1]; g = {"__name__": "bagg"}; sys.argv = ["b_agg.py", "agg"]
with contextlib.redirect_stdout(io.StringIO()): exec(compile(src, "b_agg.py", "exec"), g)
S, P, ids, KEYED, V01, CMI, FLAG, U, boot, cellstats, two_by_two, band_gap, pair, band = (g[k] for k in "S P ids KEYED V01 CMI FLAG U boot cellstats two_by_two band_gap pair band".split())
NEW_X, CT = g["NEW_X"], g["CT"]
prep = json.load(open(PREP)); MAP = prep["map"]
# ---- labels: A; B if borderline; C on A/B disagreement -> majority
L = collections.defaultdict(dict)
for l in open(NB + "/support/labels.jsonl"):
    r = json.loads(l)
    if r["ok"]: L[r["key"]][r["call"]] = r
def final(k):
    d = L[k]; a = d["A"]["label"]
    if "B" not in d: return a == "SUPPORTS", ("single" if d["A"]["conf"] == "borderline" else "clear")
    if d["B"]["label"] == a: return a == "SUPPORTS", "AB"
    lab = collections.Counter([a, d["B"]["label"], d["C"]["label"]]).most_common(1)[0][0] if "C" in d else a
    return lab == "SUPPORTS", ("ABC" if "C" in d else "single")
SUP = {"X": {}, "C": {}}; HOW = collections.Counter()
for i in ids:
    for arm in ("X", "C"):
        u = MAP[f"{arm}:{i}"]["unit"]
        if u is None: SUP[arm][i] = False; HOW["empty"] += 1
        else: SUP[arm][i], how = final(u); HOW[how] += 1
LEX = {"X": lambda i: bool(FLAG["sefix F1F2F4"][i]["chunk"]) if FLAG["sefix F1F2F4"].get(i) else False,
       "C": lambda i: bool(FLAG["B0 stock (retrieve-sweep)"][i]["chunk"]) if FLAG["B0 stock (retrieve-sweep)"].get(i) else False}
UNK = [i for i in ids if i not in KEYED]
SETS = {"MAIN97": list(ids), "MAIN92 keyed": KEYED, "v0.1 57": V01 + UNK, "cm 40": CMI}
fl = lambda arm: (lambda i: SUP[arm][i])
res = dict(how=dict(HOW), calls=dict(A=sum("A" in d for d in L.values()), B=sum("B" in d for d in L.values()), C=sum("C" in d for d in L.values())), share={}, sets={}, agree={}, within={}, sens={}, cross={})
for arm in ("X", "C"):
    res["share"][arm] = {nm: dict(yes=sum(SUP[arm][i] for i in xs), n=len(xs)) for nm, xs in SETS.items()}
def cell(R, xs, f):
    o = two_by_two(R, xs, f, False)
    y = [i for i in xs if f(i)]; n = [i for i in xs if not f(i)]
    return dict(yes=dict(o["delivered"], P_band_ge35=o["delivered"]["P_band_ge35"]), no=dict(o["not_delivered"], P_band_ge35=o["not_delivered"]["P_band_ge35"]), gap_U=o["gap_U"], band_gap=band_gap(R, xs, f))
for nm, xs in SETS.items():
    r = {}
    for arm in ("X", "C"):
        r[arm] = {f"s{s}": cell(S[s][arm], xs, fl(arm)) for s in (42, 43)}
        r[arm]["pooled"] = cell(P[arm], xs, fl(arm))
    res["sets"][nm] = r
# agreement with lexical chunk-level flag
def kappa(a, b, c, d):
    n = a + b + c + d; po = (a + d) / n; pe = ((a + b) * (a + c) + (c + d) * (b + d)) / n ** 2
    return round((po - pe) / (1 - pe), 3) if pe < 1 else None
for nm, xs in (("MAIN92 keyed", KEYED), ("v0.1 52", V01), ("cm 40", CMI)):
    res["agree"][nm] = {}
    for arm in ("X", "C"):
        a = sum(1 for i in xs if SUP[arm][i] and LEX[arm](i)); b = sum(1 for i in xs if SUP[arm][i] and not LEX[arm](i)); c = sum(1 for i in xs if not SUP[arm][i] and LEX[arm](i)); d = sum(1 for i in xs if not SUP[arm][i] and not LEX[arm](i))
        res["agree"][nm][arm] = dict(sup_lex=a, sup_nolex=b, nosup_lex=c, nosup_nolex=d, raw=round((a + d) / len(xs), 3), kappa=kappa(a, b, c, d))
# within-item arm - control, split by the arm's support flag
for lab, xs in (("MAIN97", ids),):
    res["within"][lab] = {}
    for tag, R in (("s42", (S[42]["X"], S[42]["C"])), ("s43", (S[43]["X"], S[43]["C"])), ("pooled", (P["X"], P["C"]))):
        res["within"][lab][tag] = {k: pair(R[0], R[1], [i for i in xs if SUP["X"][i] == v]) for k, v in (("support_yes", True), ("support_no", False))}
    res["within"][lab]["flip_ctlNO_armYES"] = sum(1 for i in ids if not SUP["C"][i] and SUP["X"][i]); res["within"][lab]["flip_ctlYES_armNO"] = sum(1 for i in ids if SUP["C"][i] and not SUP["X"][i])
# sensitivity: live-title parity subset
# NEW_X / CT are {seed: {id: trace}}
for arm, D in (("X", NEW_X), ("C", CT)):
    par = [i for i in ids if [c["title"] for c in D[42][i]["retrieval"]["kept"]] == MAP[f"{arm}:{i}"]["titles"]]
    res["sens"][arm] = dict(parity_n=len(par), s42=cell(S[42][arm], par, fl(arm))["gap_U"], s43=cell(S[43][arm], par, fl(arm))["gap_U"], yes_n=sum(SUP[arm][i] for i in par))
# lexical x support cross cells (arm, MAIN92, pooled and s42): U of each
for arm in ("X", "C"):
    o = {}
    for sv in (True, False):
        for lv in (True, False):
            xs = [i for i in KEYED if SUP[arm][i] == sv and LEX[arm](i) == lv]
            o[f"sup={'Y' if sv else 'N'},lex={'Y' if lv else 'N'}"] = dict(n=len(xs), U42=round(U(S[42][arm], xs), 3) if xs else None, Upooled=round(U(P[arm], xs), 3) if xs else None)
    res["cross"][arm] = o
# rule
rule = {}
for arm in ("X", "C"):
    gp = res["sets"]["MAIN97"][arm]["s42"]["gap_U"]; rule[arm] = dict(gap=gp["d"], ci=gp["ci"], ok=bool(gp["d"] >= 0.2 and gp["ci"][0] > 0))
rule["verdict"] = "HOLDS" if rule["X"]["ok"] and rule["C"]["ok"] else ("PARTIAL" if rule["X"]["ok"] or rule["C"]["ok"] else "DOES NOT HOLD"); res["rule"] = rule
json.dump(res, open(NB + "/support-2x2.json", "w"), indent=1, ensure_ascii=False)
# ---------------- markdown
f3 = lambda x: "-" if x is None else f"{x:.3f}"
def row(nm, arm, tag, c):
    y, n = c["yes"], c["no"]; gp = c["gap_U"]
    return f"| {nm} | {arm} {tag} | {y['all']['n']}, {f3(y['all']['U'])} | {y['band_ge35']['n']}, {f3(y['band_ge35']['U'])} | {y['band_lt35']['n']}, {f3(y['band_lt35']['U'])} | {n['all']['n']}, {f3(n['all']['U'])} | {n['band_ge35']['n']}, {f3(n['band_ge35']['U'])} | {n['band_lt35']['n']}, {f3(n['band_lt35']['U'])} | {y.get('P_band_ge35')}/{n.get('P_band_ge35')} | {gp['d']:+.3f} [{gp['ci'][0]:+.3f}, {gp['ci'][1]:+.3f}] |"
M = ["# SUPPORT 2x2 (Haiku judged support flag; criterion sha in SUPPORT-criterion.sha256)", "",
     f"Verdict: **{rule['verdict']}** (rule: MAIN 97, seed 42, gap >= +0.2 with CI low > 0 in both arms): arm {rule['X']['gap']:+.3f} {rule['X']['ci']} ok={rule['X']['ok']}; control {rule['C']['gap']:+.3f} {rule['C']['ci']} ok={rule['C']['ok']}.", "",
     f"Labels: units {len(L)}, calls A/B/C {res['calls']}, how {res['how']}.", "",
     "| set | arm/seed | support-yes n,U | yes corr>=3.5 | yes corr<3.5 | support-no n,U | no corr>=3.5 | no corr<3.5 | band share yes/no | gap U yes-no [CI] |", "|---|---|---|---|---|---|---|---|---|---|"]
for nm in SETS:
    for arm in ("X", "C"):
        for tag in ("s42", "s43", "pooled"):
            M.append(row(nm, "arm" if arm == "X" else "ctl", tag, res["sets"][nm][arm][tag]))
M += ["", "Support share (yes/n): " + "; ".join(f"{('arm' if a == 'X' else 'ctl')} " + ", ".join(f"{nm} {v['yes']}/{v['n']}" for nm, v in res["share"][a].items()) for a in ("X", "C")), "", "Agreement with the lexical chunk-level flag (support/lexical cells; sup&lex, sup&~lex, ~sup&lex, ~sup&~lex):"]
for nm, d in res["agree"].items():
    for arm, v in d.items(): M.append(f"- {nm} {'arm' if arm == 'X' else 'ctl'}: {v['sup_lex']}/{v['sup_nolex']}/{v['nosup_lex']}/{v['nosup_nolex']}, raw {v['raw']}, kappa {v['kappa']}")
M += ["", "Within-item arm - control dU by the arm's support flag (MAIN 97): " + "; ".join(f"{t} yes n{v['support_yes']['n']} {v['support_yes']['d']:+.3f} [{v['support_yes']['ci'][0]:+.3f},{v['support_yes']['ci'][1]:+.3f}] / no n{v['support_no']['n']} {v['support_no']['d']:+.3f} [{v['support_no']['ci'][0]:+.3f},{v['support_no']['ci'][1]:+.3f}]" for t, v in res["within"]["MAIN97"].items() if isinstance(v, dict) and "support_yes" in v),
      f"Flips ctl NO -> arm YES {res['within']['MAIN97']['flip_ctlNO_armYES']}, ctl YES -> arm NO {res['within']['MAIN97']['flip_ctlYES_armNO']}.", "",
      "Parity sensitivity (gap U s42/s43): " + "; ".join(f"{a} n{v['parity_n']} yes{v['yes_n']} {v['s42']['d']:+.3f} {v['s42']['ci']} / {v['s43']['d']:+.3f} {v['s43']['ci']}" for a, v in res["sens"].items()), "",
      "Lexical x support cross (MAIN 92, U s42 / pooled): " + "; ".join(f"{a}: " + ", ".join(f"{k} n{v['n']} {v['U42']}/{v['Upooled']}" for k, v in o.items()) for a, o in res["cross"].items())]
open(NB + "/support-2x2.md", "w").write("\n".join(M) + "\n")
print("\n".join(M))
