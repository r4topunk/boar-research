#!/usr/bin/env python3
"""PHIFIRST (0 LLM). python3 -I phifirst.py  (paths absolute below). Reuses LOGPROB analyze.py functions (auc, flag_table) and labels."""
import json, math, random, re, importlib.util
B = "<workspace>/rnd/research/coordinator/arms/logprob/"
spec = importlib.util.spec_from_file_location("an", B + "tools/analyze.py"); an = importlib.util.module_from_spec(spec); spec.loader.exec_module(an)
CAGG = "<workspace>/rnd/research/coordinator/arms/lp-screens/control/aggregates/lpctl-K0-main-s42.json"
K = 20
VARS = ["phi_first", "phi_first_content", "phi_first3"]

def phi(tok):
    ps = [math.exp(x) for _, x in tok["top"][:K]]
    s = sum(ps); ps = [p / s for p in ps]
    H = -sum(p * math.log(p) for p in ps if p > 0)
    return 1 - H / math.log(K)

def content_start(g):
    toks = g["logprobs"]; i = 0; acc = ""
    # skip leading non-alphanumeric tokens and a leading 'Answer:'-style / warning-looking line (if generated)
    while i < len(toks) and not re.search(r"[A-Za-z0-9]", toks[i]["token"]):
        i += 1
    txt = g["content"].lstrip()
    m = re.match(r"^(answer\s*:|note\s*:|warning\s*:|⚠[^\n]*\n)", txt, re.I)
    if m:
        n = 0
        while i < len(toks) and n < len(m.group(0).rstrip()):
            n += len(toks[i]["token"].strip()) if toks[i]["token"].strip() else 0; i += 1
            if n >= len(re.sub(r"\s", "", m.group(0))): break
        while i < len(toks) and not re.search(r"[A-Za-z0-9]", toks[i]["token"]): i += 1
    return i

def main():
    ctl = json.load(open(CAGG))["items"]
    ids = [json.loads(l)["itemId"] for l in open(B + "traces/logprob-K0-main-s42.traces.jsonl")]
    gens = {}
    for l in open(B + "traces/logprob-K0-main-s42.logprobs.jsonl"):
        g = json.loads(l); gens.setdefault(g["itemId"], []).append(g)
    rows, shifted = [], []
    for i in ids:
        g = gens.get(i); g = g[-1] if g else None
        f = None
        if g and g["logprobs"]:
            s = content_start(g)
            if s != 0: shifted.append((i, s))
            f = {"phi_first": phi(g["logprobs"][0]), "phi_first_content": phi(g["logprobs"][s]),
                 "phi_first3": sum(phi(t) for t in g["logprobs"][s:s + 3]) / len(g["logprobs"][s:s + 3])}
        rows.append({"id": i, "CE": bool(ctl[i]["CE"]), "corr": ctl[i]["corr"], "warned": bool(ctl[i]["warned"]), "f": f,
                     "score": {k: (-f[k] if f else None) for k in VARS}})
    an.FEATS = VARS
    allr = an.analyse(rows)
    best = max(VARS, key=lambda k: allr["features"][k]["auc"]); bf = allr["features"][best]; f30 = bf["flags"][2]
    go = bf["auc"] >= .75 and bf["ci"][0] >= .65 and f30["recall"] is not None and f30["recall"] >= .5
    res = {"K": K, "start_shifted": shifted, "best": best, "verdict": "GO" if go else "NO", "all": allr,
           "mean_phi_CE_vs_other_llm": {k: [sum(r["f"][k] for r in rows if r["f"] and r["CE"] == c) / max(1, sum(1 for r in rows if r["f"] and r["CE"] == c)) for c in (True, False)] for k in VARS},
           "n_llm_ce": sum(1 for r in rows if r["f"] and r["CE"]), "rows": [{k: v for k, v in r.items()} for r in rows]}
    json.dump(res, open("<workspace>/rnd/research/coordinator/arms/logprob-phifirst/analysis.json", "w"), indent=1)
    print("shifted starts:", shifted, "| CE with features:", res["n_llm_ce"], "of", allr["ce"])
    for k in VARS:
        x = allr["features"][k]
        print(f"{k:18s} AUC {x['auc']:.3f} CI {x['ci'][0]:.3f}-{x['ci'][1]:.3f} llm-only {x['auc_llm_only']:.3f} meanphi CE/other {res['mean_phi_CE_vs_other_llm'][k]}")
        for t in x["flags"]:
            print(f"   @{int(t['rate']*100)}% k{t['k']} flagged {t['flagged']} CE {t['ce_flagged']}/{t['ce_total']} P {t['precision']} R {t['recall']}")
    print("verdict", res["verdict"], best)
main()
