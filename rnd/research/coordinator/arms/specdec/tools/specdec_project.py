#!/usr/bin/env python3
"""SPECDEC A15 projection (criterion formula) on the A15-LATENCY-BUDGET model (device/tools/a15_budget.py, cut 5 = cut 4 + gate skip + nosrc KV).
speedup per target pass = (accepted + 1) / (1 + n_max * c); c = draft/target per-token cost = weight bytes ratio (memory-bound decode); c +-50%.
Decode time of every generating item (100 = s44+s45 cut-4 desktop traces, tokens out_i at 2.33 tok/s) is divided by that item's speedup
(per-item accepted/pass measured on the same itemId in the s44 replay; s45 items reuse the s44 item with the same id, else the pooled value).
Extra (NOT in the criterion formula, reported as a caveat): the draft must prefill the whole prompt (no restored KV for it):
prompt_tokens * c_pf / 11.94 tok/s with c_pf = non-embedding params ratio (0.6B: 0.44/3.6 = 0.122).
usage: specdec_project.py RESDIR"""
import json, sys, statistics as st
sys.path.insert(0, "<workspace>/rnd/research/coordinator/device/tools"); sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/specdec/tools")
import a15_budget as a, specdec_analyze as sa
R = sys.argv[1]
A = json.load(open(f"{R}/analysis.json"))
items = a.load_items()
elig = lambda it: it["task"] in ("lookup", "research", "compare") and not any(c.startswith(("detector:fire", "grounding:health")) for c in it["rc"])
base = a.simulate(items, "warm", 1, skip_gate=elig, nosrc_cache=True)
bs = a.summarize(items, base, "cut5")
DC = a.P["decode_tps"][1]; PF = a.P["prefill_tps"][1]
CPF = {"q06": 0.44 / 3.6, "q15": 1.31 / 3.6}
def pct(v, q): return a.pct(v, q)
out = {"baseline": {"gen_total_p50": bs["gen_total_p50"], "decode_mean_gen": bs["comp_gen"]["decode"], "decode_tps": DC, "n_gen": bs["n_gen"]}, "cfg": {}}
for name, r in A["runs"].items():
    if "speedup" not in r: continue
    d = r["cfg"]["draft"]; nmax = r["cfg"]["nmax"]; c0 = sa.C[d]
    per = dict(zip(sorted(sa.load(name)), r_pi := None or [])) if False else None
    rows = sa.load(name); ids = sorted(rows)
    peritem = {i: (rows[i]["draft_n_accepted"] or 0) / max(1, rows[i]["predicted_n"] - (rows[i]["draft_n_accepted"] or 0)) for i in ids}
    o = {}
    gen = r["cfg"].get("pmin") is not None  # p_min runs: drafts stop early, so n_max over-counts the draft cost (exploratory, outside the criterion)
    for lab, f in (("c-50%", .5), ("c", 1.0), ("c+50%", 1.5)):
        c = c0 * f
        pooled = sa.speedup(r["acc_per_pass"], nmax, c)
        if gen:
            o[lab + " generalised"] = {"optimistic (draft forwards = drafted/pass)": sa.speedup(r["acc_per_pass"], r["drafted_per_pass"], c),
                                       "conservative (drafted/pass + 1 failed-p_min forward)": sa.speedup(r["acc_per_pass"], r["drafted_per_pass"] + 1, c)}
        sp = {i: sa.speedup(x, nmax, c) for i, x in peritem.items()}
        res = []
        extra = []
        for it, b in zip(items, base):
            b = dict(b)
            if it["gen"]:
                s = sp.get(it["id"], pooled)
                b["decode"] = b["decode"] / s
                ex = it["prompt"] * CPF[d] / PF
            else: ex = 0.0
            extra.append(ex); res.append(b)
        sm = a.summarize(items, res, lab)
        res2 = [dict(b, answer_prefill=b["answer_prefill"] + ex) for b, ex in zip(res, extra)]
        sm2 = a.summarize(items, res2, lab + "+draftprefill")
        o[lab] = dict(c=c, speedup_pooled=pooled, decode_saving_pct=100 * (1 - 1 / pooled),
                      decode_s_saved_mean=bs["comp_gen"]["decode"] - sm["comp_gen"]["decode"],
                      gen_p50_before=bs["gen_total_p50"], gen_p50_after=sm["gen_total_p50"], gen_p50_saved=bs["gen_total_p50"] - sm["gen_total_p50"],
                      gen_p50_after_with_draft_prefill=sm2["gen_total_p50"], gen_p50_saved_with_draft_prefill=bs["gen_total_p50"] - sm2["gen_total_p50"],
                      draft_prefill_mean_s=sum(extra) / len([1 for it in items if it["gen"]]))
    out["cfg"][name] = o
json.dump(out, open(f"{R}/projection.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=lambda x: round(x, 3)))
