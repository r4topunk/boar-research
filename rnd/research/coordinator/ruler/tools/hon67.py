#!/usr/bin/env python3
"""HON-7 WARN-TRANSFER + HON-6 TIER-PER100 (0 LLM, 0 judge). Criterion: ../HON67-criterion.md (sha in ../HON67-criterion.sha256).
Reuses tools/warncal_showanyway.py UNCHANGED (sha 8e162cea...): its definition blocks are exec'd verbatim; only the inputs differ.
Usage: python3 -I hon67.py -> ../HON7-WARN-TRANSFER-2026-10-21.json, ../HON6-TIER-PER100-2026-10-21.json (+ stdout)."""
import json, hashlib, os, random, collections
HERE = os.path.dirname(os.path.abspath(__file__)); RUL = os.path.dirname(HERE)
WC = f"{HERE}/warncal_showanyway.py"; WSHA = "8e162ceae8fd71919a8f9573ac3813636ca1beca44df51b9632e8ef4ca50cdc7"
src = open(WC).read(); assert hashlib.sha256(src.encode()).hexdigest() == WSHA, "warncal_showanyway.py changed"
CRIT = open(f"{RUL}/HON67-criterion.sha256").read().split()[0]
assert hashlib.sha256(open(f"{RUL}/HON67-criterion.md", "rb").read()).hexdigest() == CRIT
G = {"__file__": WC, "__name__": "warncal_defs"}
seg = lambda a, b: src[src.index(a):src.index(b)]
exec(src[:src.index("R = []")], G)                      # imports, labels, WARNSPEC/HEALTHGAP, setof, judg_lp, traces, bucket, row
exec(seg("def wilson", "LPR = [r for r"), G)              # wilson, cboot, sd, r3, cal, cal_full
exec(seg("def bstats", 'h1["by_bucket"] ='), G)
exec(seg("def rev(rows, nall)", "h2 = {"), G)             # rev, rev_full
row, cal_full, rev, rev_full, cboot, wilson, rd, r3, sd = (G[k] for k in ("row", "cal_full", "rev", "rev_full", "cboot", "wilson", "rd", "r3", "sd"))
ROOT = G["ROOT"]; A = G["A"]
ids_of = lambda f: [l.strip() for l in open(f) if l.strip()]
DETP = set(ids_of(f"{RUL}/ids/deterministic-pool.ids")); DETV = set(ids_of(f"{RUL}/ids/deterministic-v01.ids"))
dropped = collections.Counter()
def from_agg(tier, agg, trf):
    it = json.load(open(agg))["items"]; TR = G["traces"]([trf]); out = {}
    for i, x in it.items():
        if G["setof"](i) != "MAIN": dropped[f"{tier}-notmain"] += 1; continue
        if x.get("judgment") not in ("judged", "control") or x.get("corr") is None: dropped[tier] += 1; continue
        assert TR[i]["answer"]["text"] == x["text"], (tier, i)
        r = row("D", tier, i, TR[i], dict(corr=x["corr"], s=x["s"], sref=x["sref"])); r["weak"] = bool(TR[i]["answer"].get("weakSources")); out[i] = r
    return out
def jfile(f):
    by = {}
    for r in rd(f):
        if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    out = {}
    for q, v in by.items():
        if len(v) != 2: continue
        ms = list(v.values()); mean = lambda d: sum(d.values()) / 3
        out[q] = dict(s=sum(mean(m["boar"]) for m in ms) / 2, sref=sum(mean(m["ref"]) for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2)
    return out
def from_judg(tier, J, TR, src="D"):
    out = {}
    for i, t in TR.items():
        if G["setof"](i) != "MAIN": continue
        if i not in J: dropped[tier] += 1; continue
        r = row(src, tier, i, t, J[i]); r["weak"] = bool(t["answer"].get("weakSources")); out[i] = r
    return out
CO = f"{A}/lp-screens/control"; GE = f"{A}/gemma4-e2b"
D = {"4B": from_agg("4B", f"{GE}/vs4b/aggregates/gemma4-e2b-vs4b-K0-main-s42.json", f"{GE}/vs4b/traces/gemma4-e2b-vs4b-K0-main-s42.traces.jsonl"),
     "Gemma": from_agg("Gemma", f"{GE}/stage2/aggregates/gemma4-e2b-eng-K0-main-s42.json", f"{GE}/stage2/traces/gemma4-e2b-eng-K0-main-s42.traces.jsonl"),
     "1.7B": from_agg("1.7B", f"{CO}/aggregates/lpctl-K0-main-s42.json", f"{CO}/traces/lpctl-K0-main-s42.traces.jsonl")}
LP = G["LP"]; J0 = G["judg_lp"]("K0"); TR0 = G["traces"](sorted(__import__("glob").glob(f"{LP}/traces/lp-K0-*-s42.traces.jsonl")))
D["1.7B-LP"] = from_judg("1.7B-LP", J0, TR0)
PH = f"{ROOT}/boar-eval/runs/device-pixel8a"
def phone(run, tier):
    TR = G["traces"]([f"{PH}/{run}/traces.jsonl"]); return from_judg(tier, jfile(f"{PH}/{run}/judgments.haiku.jsonl"), TR, src="PH")
P = {"4B": phone("final-cut7-v01", "4B-px"), "Gemma": phone("gemma73-a", "Gemma-px"), "1.7B": phone("cmp30off-q17", "1.7B-px26")}
FLAG = {"D": lambda r: r["w"], "PH": lambda r: r["w"] or (r["ot"] > 0 and (r["kept"] == 0 or r["weak"]))}
HID = {"D": lambda r: r["hidden"], "PH": lambda r: r["dec"] or FLAG["PH"](r)}
def splits(rows, det):
    return {"all": rows, "deterministic": [r for r in rows if r["id"] in det], "divergent": [r for r in rows if r["id"] not in det]}
# ---------------- HON-7 ----------------
def h7(rows, srck):
    fl = FLAG[srck]; o = {"warn": cal_full(rows, boot=True, flag=fl)}
    o["refuse_signal"] = cal_full(rows, boot=True, flag=lambda r: fl(r) or (r["ot"] > 0 and r["kept"] == 0))
    rr = [dict(r, hidden=HID[srck](r), revealable=HID[srck](r) and r["ot"] > 0) for r in rows]
    rv = rev(rr, rr); o["reveal"] = {k: r3(rv[k]) for k in ("hidden", "revealable", "correct", "ce", "mid", "ratio", "correct_per100", "ce_per100")}
    o["reveal"]["ratio_ci"] = cboot(rr, lambda s: rev(s, s)["ratio"])
    hl = [r for r in rr if r["revealable"] and r["health"]]
    o["health_reveals"] = dict(n=len(hl), ce=sum(r["CE"] for r in hl), correct=sum(r["correct"] for r in hl), ce_ids=sorted(r["id"] for r in hl if r["CE"]))
    w = o["warn"]; pc = w["precision"] or 0; rc = w["recall"] or 0; pw = w["p_corr_w"] or 0; ci = w["cluster_ci"]["precision"]
    holds = pc >= 0.30 and rc >= 0.55 and pw <= 0.10; kill = (ci[1] < 0.30) or rc < 0.50 or pw > 0.15
    o["verdict"] = "HOLDS" if holds else ("KILL" if kill else "INDETERMINATE")
    o["checks"] = dict(precision_ge_030=pc >= 0.30, recall_ge_055=rc >= 0.55, pcorrw_le_010=pw <= 0.10, prec_cihigh_lt_030=ci[1] < 0.30, recall_lt_050=rc < 0.50, pcorrw_gt_015=pw > 0.15)
    return o
H7 = {"criterion_sha256": CRIT, "reused_script_sha256": WSHA, "dropped_no_judgment": None, "desktop": {}, "pixel": {}}
for t in ("4B", "Gemma", "1.7B", "1.7B-LP"):
    rows = list(D[t].values()); H7["desktop"][t] = {"n_items": len(rows), **{k: h7(v, "D") for k, v in splits(rows, DETP).items() if k != "deterministic"}}
    H7["desktop"][t]["deterministic_n"] = len(splits(rows, DETP)["deterministic"])
for t in ("4B", "Gemma", "1.7B"):
    rows = list(P[t].values()); H7["pixel"][t] = {"n_items": len(rows), "all": h7(rows, "PH")}
    if t == "1.7B": H7["pixel"][t]["line_only"] = cal_full(rows, boot=True, flag=FLAG["D"])
# ---------------- HON-6 ----------------
def per100(rows, mode, hid):
    n = len(rows); sh = [r for r in rows if not r["dec"]] if mode == "show" else [r for r in rows if not hid(r)]
    k = sum(r["correct"] for r in sh); ce = sum(r["CE"] for r in sh); sref = sum(r["sref"] for r in rows) or 1; fref = sum(r["sref"] - 1 for r in rows) or 1
    return dict(n=n, correct=100 * k / n, ce=100 * ce / n, partial=100 * (len(sh) - k - ce) / n, hidden=100 * (n - len(sh)) / n,
                U=sum(r["s"] for r in sh) / sref, U_fa=sum(r["s"] - 1 for r in sh) / fref)
KEYS = ("correct", "ce", "partial", "hidden", "U", "U_fa")
def pboot(a, b, mode, hid, ids, B=2000, seed=11):
    rnd = random.Random(seed); xs = {k: [] for k in KEYS}
    for _ in range(B):
        s = [ids[rnd.randrange(len(ids))] for _ in ids]; pa = per100([a[i] for i in s], mode, hid); pb = per100([b[i] for i in s], mode, hid)
        for k in KEYS: xs[k].append(pa[k] - pb[k])
    ci = lambda v: [round(sorted(v)[int(0.025 * B)], 3), round(sorted(v)[int(0.975 * B) - 1], 3)]
    return {k: ci(v) for k, v in xs.items()}
def table(T, srck, det, tiers, pairs, ids=None):
    hid = HID[srck]; common = sorted(set.intersection(*[set(T[t]) for t in tiers]) if ids is None else ids)
    out = {"ids": len(common), "splits": {}}
    for sp, sel in (("all", common), ("deterministic", [i for i in common if i in det]), ("divergent", [i for i in common if i not in det])):
        if not sel: continue
        o = {"n": len(sel), "tiers": {}, "paired": {}}
        for t in tiers:
            o["tiers"][t] = {m: {k: r3(v) for k, v in per100([T[t][i] for i in sel], m, hid).items()} for m in ("show", "refuse")}
        for a, b in pairs:
            o["paired"][f"{a} - {b}"] = {m: {"point": {k: r3(o["tiers"][a][m][k] - o["tiers"][b][m][k]) for k in KEYS}, "ci": pboot(T[a], T[b], m, hid, sel)} for m in ("show", "refuse")}
        out["splits"][sp] = o
    return out
PAIRS = [("4B", "1.7B"), ("4B", "Gemma"), ("Gemma", "1.7B")]
H6 = {"criterion_sha256": CRIT, "reused_script_sha256": WSHA}
H6["desktop_primary"] = table(D, "D", DETP, ("4B", "Gemma", "1.7B"), PAIRS)
DL = {"4B": D["4B"], "Gemma": D["Gemma"], "1.7B": D["1.7B-LP"]}
H6["desktop_17B_LP_replication"] = table(DL, "D", DETP, ("4B", "Gemma", "1.7B"), PAIRS)
H6["pixel57_4B_Gemma"] = table(P, "PH", DETV, ("4B", "Gemma"), [("4B", "Gemma")])
H6["pixel26_with_17B"] = table(P, "PH", DETV, ("4B", "Gemma", "1.7B"), PAIRS)
sp = json.load(open(f"{RUL}/SPEED-PRECHECK-2026-10-21.json"))
H6["p50_complete_s"] = {r["tier"]: dict(run=r["run"], S1_answered=r["sets"]["S1_answered"]["complete_p50"], S3_all=r["sets"]["S3_all"]["complete_p50"], S2_model_path=r["sets"]["S2_answered_no_det_ids"]["complete_p50"])
                        for r in sp["runs"] if r.get("primary")}
H6["p50_source"] = dict(file="ruler/SPEED-PRECHECK-2026-10-21.json", sha256=hashlib.sha256(open(f"{RUL}/SPEED-PRECHECK-2026-10-21.json", "rb").read()).hexdigest())
def decide(o, a="4B", b="1.7B"):
    pr = o["paired"][f"{a} - {b}"]; dce = pr["refuse"]["point"]["ce"]; dce_ci = pr["refuse"]["ci"]["ce"]; dk = pr["refuse"]["point"]["correct"]
    sa = pr["show"]["point"]; dom_show = sa["correct"] >= 0 and sa["ce"] <= 3
    sup = dce >= 3 and dce_ci[0] > 0 and dk <= 5 and dom_show
    kill = dce < 3 and (dce_ci[0] <= 0) and dk >= 5
    return dict(pair=f"{a} - {b}", dCE_refuse=dce, dCE_refuse_ci=dce_ci, dK_refuse=dk, dK_refuse_ci=pr["refuse"]["ci"]["correct"], show_dK=sa["correct"], show_dCE=sa["ce"],
                show_dominates=dom_show, verdict="STATEMENT SUPPORTED" if sup else ("KILL: 4B DOMINATES" if kill else "MIXED"))
oa = H6["desktop_primary"]["splits"]["all"]
H6["decision"] = decide(oa); H6["decision_divergent_report"] = decide(H6["desktop_primary"]["splits"]["divergent"])
H6["decision_LP_replication"] = decide(H6["desktop_17B_LP_replication"]["splits"]["all"])
H6["pairwise_gemma"] = {"Gemma - 1.7B": decide(oa, "Gemma", "1.7B"), "4B - Gemma": decide(oa, "4B", "Gemma")}
H7["dropped_no_judgment"] = H6["dropped_no_judgment"] = dict(dropped)
for nm, obj in (("HON7-WARN-TRANSFER", H7), ("HON6-TIER-PER100", H6)):
    obj["script"] = "ruler/tools/hon67.py"; obj["script_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    s = json.dumps(obj, indent=1, ensure_ascii=False); open(f"{RUL}/{nm}-2026-10-21.json", "w").write(s)
    print(nm, "sha256", hashlib.sha256(s.encode()).hexdigest())
