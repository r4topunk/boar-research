"""GEMMA4-PHONE-JUDGE aggregation (0 LLM calls). Imports load/setstats/paired from arms/device-x6/tools/agg_device.py unchanged
(estimator frozen in JUDGE-criterion.md). Desktop candidate runs reuse lpctl-K0-main-s42 rows for byte-identical answers (run_arm.sh rule).
Usage: python3 -I agg_gemma_phone.py --out aggregate.json"""
import json, sys, os, types, collections, numpy as np
A = "<workspace>/rnd/research/coordinator/arms/"; R = "<workspace>/boar-eval/runs/"
src = open(A + "device-x6/tools/agg_device.py").read().split("P, D, N = sys.argv")[0]
m = types.ModuleType("agg"); exec(src, m.__dict__); load, setstats, paired = m.load, m.setstats, m.paired
ids = [l.strip() for l in open(A + "gemma4-e2b/phone/judge/v01-57.ids") if l.strip()]
def txt(p):
    d = {}
    for l in open(p):
        r = json.loads(l); d[r.get("itemId") or r.get("queryId")] = r["answer"]["text"]
    return d
CT = A + "lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl"; CJ = A + "lp-screens/control/judgments/lpctl-K0-main-s42-v01.judgments.jsonl"
ctl_t, ctl_j = txt(CT), load(CJ)
def cand(tr, jf):
    t, j = txt(tr), load(jf); out = dict(j); reused = 0
    for q in ids:
        if q not in j:
            assert t[q] == ctl_t[q], f"{tr}: {q} unjudged and not identical to control"; out[q] = ctl_j[q]; reused += 1
    return out, reused
def mean2(a, b):
    return {q: {"s": (a[q]["s"] + b[q]["s"]) / 2, "r": (a[q]["r"] + b[q]["r"]) / 2, "consistent": a[q]["consistent"] and b[q]["consistent"],
                "winner": a[q]["winner"] if a[q]["winner"] == b[q]["winner"] else "tie"} for q in ids if q in a and q in b}
G = A + "gemma4-e2b-confirm/runs/"
S = {"P_G": load(R + "device-pixel8a/gemma73-a/judgments.haiku.jsonl"), "P_4": load(R + "device-pixel8a/final-cut7-v01/judgments.haiku.jsonl"),
     "D_4_cut7_s42": load(A + "stack/runs/v01-cut7-stack-off-s42.judgments.jsonl"), "X6_4_cut7": load(A + "device-x6/judgments/phone-cut7-v01.judgments.jsonl"),
     "P_17_cmp30": load(R + "device-pixel8a/cmp30-q17/judgments.haiku.jsonl"), "P_17_cmp30off_info": load(R + "device-pixel8a/cmp30off-q17/judgments.haiku.jsonl")}
reuse = {}
S["D_G_s42"], reuse["D_G_s42"] = cand(A + "gemma4-e2b/stage2/traces/gemma4-e2b-eng-K0-main-s42.traces.jsonl", A + "gemma4-e2b/stage2/judgments/gemma4-e2b-eng-K0-main-s42-v01.judgments.jsonl")
S["D_G_s43"], reuse["D_G_s43"] = cand(G + "g43/traces/gemma4-e2b-confirm-g43-K0-main-s42.traces.jsonl", G + "g43/judgments/gemma4-e2b-confirm-g43-K0-main-s42-v01.judgments.jsonl")
S["D_17_s42"] = ctl_j
S["D_17_s43"], reuse["D_17_s43"] = cand(G + "c43/traces/gemma4-e2b-confirm-c43-K0-main-s42.traces.jsonl", G + "c43/judgments/gemma4-e2b-confirm-c43-K0-main-s42-v01.judgments.jsonl")
S["D_G_2seed"] = mean2(S["D_G_s42"], S["D_G_s43"]); S["D_17_2seed"] = mean2(S["D_17_s42"], S["D_17_s43"])
def common(*ks): return [q for q in ids if all(q in S[k] for k in ks)]
out = {"estimator": "agg_device.py: ratio-of-sums, item bootstrap B 2000 seed 11, paired on queryId", "reused_control_rows": reuse,
       "sets_57": {k: setstats(S[k], common(k)) for k in ["P_G", "P_4", "D_G_s42", "D_G_s43", "D_G_2seed", "D_17_s42", "D_17_s43", "D_17_2seed", "D_4_cut7_s42", "X6_4_cut7"]}}
pairs = [("P_G", "P_4"), ("P_G", "X6_4_cut7"), ("P_G", "D_4_cut7_s42"), ("P_G", "D_G_2seed"), ("P_G", "D_G_s42"), ("P_G", "D_G_s43"), ("D_G_s43", "D_G_s42"),
         ("P_4", "D_4_cut7_s42"), ("P_G", "D_17_2seed"), ("D_17_s43", "D_17_s42"), ("D_G_2seed", "D_17_2seed"), ("P_4", "D_17_2seed"), ("P_G", "P_17_cmp30"), ("P_4", "P_17_cmp30"), ("P_G", "P_17_cmp30off_info")]
out["paired"] = {f"{a} - {b}": paired(S[a], S[b], common(a, b)) for a, b in pairs}
c26 = common("P_G", "P_17_cmp30"); out["sets_26"] = {k: setstats(S[k], c26) for k in ["P_G", "P_4", "P_17_cmp30", "P_17_cmp30off_info"]}
# per category (P_G vs P_4), point only
cat = {}
for l in open(R + "device-pixel8a/gemma73-a/judgments.haiku.jsonl"): r = json.loads(l); cat[r["queryId"]] = r["category"]
pc = collections.defaultdict(list); [pc[cat[q]].append(q) for q in common("P_G", "P_4", "D_G_2seed")]
out["per_category"] = {c: {"n": len(v), **{k: round(sum(S[k][q]["s"] for q in v) / sum(S[k][q]["r"] for q in v), 3) for k in ["P_G", "P_4", "D_G_2seed", "D_17_2seed"]}} for c, v in sorted(pc.items())}
def verdict1(p): lo, hi = p["d_raw_ci"]; return "A better" if lo > 0 else "B better" if hi < 0 else "not distinguishable"
out["readings"] = {k: verdict1(v) for k, v in out["paired"].items()}
for k in ["P_G - D_G_2seed", "P_4 - D_4_cut7_s42"]:
    p = out["paired"][k]; out["readings"][k + " parity"] = "within noise" if abs(p["d_raw"]) <= 0.03 and p["d_raw_ci"][0] >= -0.05 and p["d_raw_ci"][1] <= 0.05 else "outside parity rule"
band = out["paired"]["D_G_s43 - D_G_s42"]; pg = out["paired"]["P_G - D_G_2seed"]["d_raw"]
out["readings"]["P_G - D_G inside two-seed band"] = bool(band["d_raw_ci"][0] <= pg <= band["d_raw_ci"][1]) if True else None
js = json.dumps(out, indent=1); print(js)
if "--out" in sys.argv: open(sys.argv[sys.argv.index("--out") + 1], "w").write(js + "\n")
