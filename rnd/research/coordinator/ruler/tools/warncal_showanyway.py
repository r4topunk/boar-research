#!/usr/bin/env python3
"""HON-1 WARNCAL + HON-2 SHOWANYWAY-VALUE (0 LLM, 0 judge). Criterion: ../WARNCAL-SHOWANYWAY-criterion.md (sha256 d641551b...).
Usage: python3 -I warncal_showanyway.py  -> ../WARNCAL-2026-10-21.json, ../SHOWANYWAY-VALUE-2026-10-21.json (+ stdout)."""
import json, glob, math, random, re, sys, os, hashlib, collections
ROOT = "<workspace>"; A = f"{ROOT}/rnd/research/coordinator/arms"; OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f"{A}/null-cal/tools"); from labels import is_decline, W, MODEL_DECLINE  # noqa
CRIT = open(f"{OUT}/WARNCAL-SHOWANYWAY-criterion.sha256").read().split()[0]
assert hashlib.sha256(open(f"{OUT}/WARNCAL-SHOWANYWAY-criterion.md", "rb").read()).hexdigest() == CRIT
# WARNSPEC rule functions (warnspec.py, unchanged) and the HEALTHGAP v1.2 scan (as warnspec/tools/feats.py)
src = open(f"{A}/warnspec/tools/warnspec.py").read(); WS = {"re": re, "unicodedata": __import__("unicodedata")}
exec(src[src.index("NOT_A_MODEL ="):src.index("PUBLISHED =")], WS)
hsrc = open(f"{A}/healthgap/tools/healthgap_scan_v12.py", encoding="utf8").read().split("# ---------- data ----------")[0]
HG = {"__name__": "scan"}; _a = sys.argv; sys.argv = ["x", ROOT]; exec(hsrc, HG); sys.argv = _a
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
LP = f"{A}/litepacks"
V01 = [l.strip() for l in open(f"{LP}/data/v01-57.ids") if l.strip()]
CATV = {q["id"]: q["category"] for q in rd(f"{ROOT}/boar-eval/bench/v0.1/questions.public.jsonl")}
def setof(i):
    if i in V01 or i.startswith("st-qa-cooking-se") or i.startswith("st-qa-money-se"): return "MAIN"
    if i.startswith("st-boar-"): return "ST-cand"
    if i.startswith("st-qa-"): return "ST-SE"
    return None
def judg_lp(arm):
    by = {}
    for f in sorted(glob.glob(f"{LP}/judgments/lp-{arm}-*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    out = {}
    for q, v in by.items():
        if len(v) != 2: continue
        ms = list(v.values()); mean = lambda d: sum(d.values()) / 3
        out[q] = dict(s=sum(mean(m["boar"]) for m in ms) / 2, sref=sum(mean(m["ref"]) for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2)
    return out
def traces(files):
    out = {}
    for f in files:
        if "smoke" in f: continue
        for t in rd(f): out[t["itemId"]] = t
    return out
def done_ev(t):
    d = [e for e in t.get("events", []) if e.get("type") == "done"]; return d[-1] if d else {}
def bucket(t, warned, dec, kept, ot):
    rc = t["route"]["reasonCodes"]
    if dec: return "decline"
    if warned:
        if "grounding:compact-decline-released-no-source" in rc: return "W:no-source"
        if "grounding:compact-decline-released-all-citations-removed" in rc: return "W:all-citations-removed"
        if "grounding:compact-decline-released-uncited-with-sources" in rc: return "W:uncited-with-sources"
        return "W:other"
    if ot == 0: return "U:deterministic"
    if not kept: return "U:no-kept(banner)"
    if "grounding:no-good-source" in rc or "grounding:uncited-warning" in rc: return "U:kept-weak"
    return "U:grounded"
dropped = collections.Counter()
def row(src, arm, i, t, j):
    tx = t["answer"]["text"]; dec = is_decline(tx, t["answer"]["declined"]); w = tx.startswith(W)
    kept = t["retrieval"]["kept"]; ot = t["timing"].get("outputTokens") or 0; c = j["corr"]
    d = done_ev(t); rec = d.get("receipt") or {}; rc = t["route"]["reasonCodes"]
    p = next((float(x.split("=")[1]) for x in rc if x.startswith("detector:p=")), None)
    wr = {"model": "x", "codes": rc, "modelId": rec.get("modelId"), "outcome": t["route"].get("outcome"), "text": d.get("finalText") or tx, "cited": d.get("cited") or [],
          "kept": [(k.get("title"), k.get("source")) for k in kept], "p": p, "q": t["question"], "lexSafety": False,
          "hgScan": (HG["classify"](t["question"], []) or {}).get("cls")}
    hr = WS["health_reasons"](wr)
    tier = None
    if hr:
        if not kept: tier = "no-source"
        else:
            unc, n, first = WS["coverage"](wr)
            tier = "beyond-source" if (not wr["cited"] or n == 0 or not first or (n - len(unc)) * 2 < n) else "sourced"
    hidden = dec or w or (ot > 0 and not kept)
    return dict(src=src, arm=arm, id=i, set=setof(i), cat=CATV.get(i) or re.match(r"st-(.*)-\d+$", i).group(1), q=t["question"], dec=dec, w=w, ot=ot, kept=len(kept),
                corr=c, s=j["s"], sref=j["sref"], CE=(not dec) and c <= 1.5, correct=(not dec) and c >= 4, bucket=bucket(t, w, dec, bool(kept), ot),
                hidden=hidden, revealable=hidden and ot > 0, abstention=(not dec) and bool(MODEL_DECLINE.search(tx[len(W):] if w else tx)) and len(tx) < 300 + len(W),
                health=bool(hr), health_reasons=hr, tier=tier, text200=tx[:200])
R = []
J0 = judg_lp("K0")
TR0 = traces(sorted(glob.glob(f"{LP}/traces/lp-K0-*-s42.traces.jsonl")))
for arm in ["K0", "K1", "K3"]:
    TR = traces(sorted(glob.glob(f"{LP}/traces/lp-{arm}-*-s42.traces.jsonl"))); Ja = judg_lp(arm)
    for i, t in TR.items():
        if setof(i) is None: continue
        j = J0.get(i) if t["answer"]["text"] == TR0[i]["answer"]["text"] else Ja.get(i)
        if not j: dropped[f"LP-{arm}"] += 1; continue
        R.append(row("LP", arm, i, t, j))
for arm in ["K0", "K1"]:
    P = json.load(open(f"{A}/null-cal/control/pool-{arm}.json"))["items"]
    TR = traces([f"{A}/lp-screens/control/traces/lpctl-{arm}-main-s42.traces.jsonl", f"{A}/null-cal/control/traces/poolctl-{arm}-st180-s42.traces.jsonl"])
    for i, it in P.items():
        if setof(i) is None or i not in TR: dropped[f"MINI-{arm}-noset"] += 1; continue
        if it.get("judgment") != "judged" or it.get("corr") is None: dropped[f"MINI-{arm}"] += 1; continue
        assert TR[i]["answer"]["text"] == it["text"], i
        R.append(row("MINI", arm, i, TR[i], dict(corr=it["corr"], s=it["s"], sref=it["sref"])))
def wilson(k, n, z=1.96):
    if n == 0: return None
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]
def cboot(rows, fn, B=2000, seed=11):
    by = collections.defaultdict(list)
    for r in rows: by[r["id"]].append(r)
    ids = sorted(by); rnd = random.Random(seed); xs = []
    for _ in range(B):
        s = [x for _ in ids for x in by[ids[rnd.randrange(len(ids))]]]; v = fn(s)
        if v is not None: xs.append(v)
    xs.sort(); return [round(xs[int(0.025 * len(xs))], 3), round(xs[int(0.975 * len(xs)) - 1], 3)] if xs else None
sd = lambda a, b: (a / b) if b else None
r3 = lambda v: round(v, 3) if isinstance(v, float) else v
# ---------------- HON-1 ----------------
def cal(rows, flag=lambda r: r["w"]):
    a = [r for r in rows if not r["dec"]]; w = [r for r in a if flag(r)]; u = [r for r in a if not flag(r)]
    ce = sum(r["CE"] for r in a); cw = sum(r["CE"] for r in w); cu = sum(r["CE"] for r in u)
    kw = sum(r["correct"] for r in w); ku = sum(r["correct"] for r in u)
    return dict(n=len(a), warned=len(w), unwarned=len(u), ce=ce, ce_w=cw, ce_u=cu, correct_w=kw, correct_u=ku,
                precision=sd(cw, len(w)), recall=sd(cw, ce), p_ce_u=sd(cu, len(u)), p_corr_w=sd(kw, len(w)), p_corr_u=sd(ku, len(u)),
                ratio=sd(sd(cw, len(w)) or 0, sd(cu, len(u))) if cu else None, correct_hidden_share=sd(kw, kw + ku))
def cal_full(rows, boot=False, flag=lambda r: r["w"]):
    m = cal(rows, flag); out = {k: r3(v) for k, v in m.items()}
    out["wilson"] = dict(precision=wilson(m["ce_w"], m["warned"]), recall=wilson(m["ce_w"], m["ce"]), p_ce_u=wilson(m["ce_u"], m["unwarned"]),
                         p_corr_w=wilson(m["correct_w"], m["warned"]), p_corr_u=wilson(m["correct_u"], m["unwarned"]))
    if boot:
        out["cluster_ci"] = {k: cboot(rows, lambda s, k=k: cal(s, flag)[k]) for k in ("precision", "recall", "p_ce_u", "p_corr_w", "p_corr_u", "ratio")}
    return out
LPR = [r for r in R if r["src"] == "LP"]; MIN = [r for r in R if r["src"] == "MINI"]
h1 = {"criterion_sha256": CRIT, "rows": {"LP": len(LPR), "MINI": len(MIN)}, "dropped_no_judgment": dict(dropped)}
h1["primary_LP_pooled"] = cal_full(LPR, boot=True)
h1["MINI_pooled"] = cal_full(MIN, boot=True)
h1["ALL_pooled"] = cal_full(R, boot=True)
h1["by_set_LP"] = {s: cal_full([r for r in LPR if r["set"] == s], boot=True) for s in ("MAIN", "ST-cand", "ST-SE")}
h1["by_set_LP"]["ST-180"] = cal_full([r for r in LPR if r["set"] != "MAIN"], boot=True)
h1["by_arm_set"] = {f"{src}-{a}-{s}": cal_full([r for r in R if r["src"] == src and r["arm"] == a and r["set"] == s])
                    for src, arms in (("LP", ("K0", "K1", "K3")), ("MINI", ("K0", "K1"))) for a in arms for s in ("MAIN", "ST-cand", "ST-SE")}
h1["LLM_only_LP"] = cal_full([r for r in LPR if r["ot"] > 0], boot=True)
h1["refuse_signal_LP"] = cal_full(LPR, boot=True, flag=lambda r: r["w"] or (r["ot"] > 0 and r["kept"] == 0))
def bstats(rows):
    a = [r for r in rows if not r["dec"]]; n = len(a); ce = sum(r["CE"] for r in a); k = sum(r["correct"] for r in a)
    return dict(n=n, ce=ce, p_ce=r3(sd(ce, n)), p_ce_ci=wilson(ce, n), correct=k, p_corr=r3(sd(k, n)), p_corr_ci=wilson(k, n), corr_mean=r3(sd(sum(r["corr"] for r in a), n)))
h1["by_bucket"] = {src: {b: bstats([r for r in R if r["src"] == src and r["bucket"] == b]) for b in sorted({r["bucket"] for r in R})} for src in ("LP", "MINI")}
h1["by_bucket_set_LP"] = {f"{b}|{s}": bstats([r for r in LPR if r["bucket"] == b and r["set"] == s]) for b in sorted({r["bucket"] for r in LPR}) for s in ("MAIN", "ST-cand", "ST-SE")}
pp = h1["primary_LP_pooled"]
kill = pp["cluster_ci"]["precision"][1] < 0.40 or pp["cluster_ci"]["recall"][1] < 0.50
h1["kill_literal"] = dict(rule="KILL iff precision CI-high < 0.40 OR recall CI-high < 0.50 (LP pooled, cluster bootstrap)", precision=pp["precision"], precision_ci=pp["cluster_ci"]["precision"],
                         recall=pp["recall"], recall_ci=pp["cluster_ci"]["recall"], verdict="KILL" if kill else "NOT KILLED",
                         point_below_thresholds=(pp["precision"] < 0.40 or pp["recall"] < 0.50))
h1["statement_support"] = dict(ratio=pp["ratio"], ratio_ci=pp["cluster_ci"]["ratio"], recall=pp["recall"], supported=(pp["ratio"] or 0) >= 2 and pp["recall"] >= 0.60)
# CE-OPUS 47 sensitivity: same items, Haiku vs Opus CE label, warned split
C = f"{A}/ce-opus-check"; ctl = json.load(open(f"{A}/lp-screens/control/aggregates/lpctl-K0-screen-s42.json"))["items"]
gr = json.load(open(f"{A}/greedy/aggregates/greedy-K0-screen-s42.json"))["items"]; op = []
for tag, srcd in (("ctl", ctl), ("greedy", gr)):
    by = {}
    for f in glob.glob(f"{C}/out/{tag}-*.judgments.jsonl"):
        for l in open(f):
            x = json.loads(l)
            if x.get("ok"): by.setdefault(x["queryId"], {})[x["order"]] = x["mapped"]["boar"]["correctness"]
    for i, v in by.items():
        if len(v) != 2: continue
        it = srcd[i]; oc = sum(v.values()) / 2; d = is_decline(it["text"], it["declined"])
        op.append(dict(id=i, w=it["text"].startswith(W), dec=d, hCE=(not d) and it["corr"] <= 1.5, oCE=(not d) and oc <= 1.5))
def ceo(lbl):
    a = [x for x in op if not x["dec"]]; w = [x for x in a if x["w"]]; ce = [x for x in a if x[lbl]]
    return dict(n=len(a), warned=len(w), ce=len(ce), ce_w=sum(x[lbl] for x in w), precision=r3(sd(sum(x[lbl] for x in w), len(w))), recall=r3(sd(sum(x[lbl] for x in w), len(ce))))
h1["ceopus_47_sensitivity"] = dict(note="47 answers selected on Haiku CE (control half) + greedy changed; not representative, direction only", haiku=ceo("hCE"), opus=ceo("oCE"))
# hedge sensitivity (report only): same id, warned body vs an unwarned answer whose first 100 body chars are identical (judge sees the warning line)
by = collections.defaultdict(list)
for r in R: by[r["id"]].append(r)
hp = []
for i, rs in by.items():
    for a in rs:
        for b in rs:
            if a["w"] and not b["w"] and not b["dec"]:
                ba = a["text200"][len(W):].strip()[:100]; bb = b["text200"].strip()[:100]
                if len(ba) >= 60 and ba == bb: hp.append(dict(id=i, warned=f'{a["src"]}-{a["arm"]}', corr_w=a["corr"], unwarned=f'{b["src"]}-{b["arm"]}', corr_u=b["corr"]))
dd = [x["corr_w"] - x["corr_u"] for x in hp]
h1["hedge_pairs"] = dict(note="prefix-matched pairs (first 100 body chars), not byte-identical; pairs share items, not independent", pairs=len(hp), items=len({x["id"] for x in hp}),
                         mean_corr_warned_minus_unwarned=r3(sum(dd) / len(dd)) if dd else None, ce_w=sum(x["corr_w"] <= 1.5 for x in hp), ce_u=sum(x["corr_u"] <= 1.5 for x in hp), rows=hp)
# ---------------- HON-2 ----------------
def rev(rows, nall):
    hid = [r for r in rows if r["hidden"]]; rv = [r for r in hid if r["revealable"]]
    k = sum(r["correct"] for r in rv); ce = sum(r["CE"] for r in rv); mid = len(rv) - k - ce
    sref_all = sum(r["sref"] for r in nall) or 1
    return dict(items=len(nall), hidden=len(hid), no_text_declines=len(hid) - len(rv), revealable=len(rv), correct=k, ce=ce, mid=mid,
                abstentions=sum(r["abstention"] for r in rv), ratio=sd(k, ce), net_per100=sd(100 * (k - ce), len(rv)), correct_per100=sd(100 * k, len(rv)), ce_per100=sd(100 * ce, len(rv)),
                dU_all_vs_none=sum(r["s"] for r in rv) / sref_all, dU_floor_adj=sum(r["s"] - 1 for r in rv) / (sum(r["sref"] - 1 for r in nall) or 1), U_hidden_only=sd(sum(r["s"] for r in rv), sum(r["sref"] for r in rv)),
                U_shown_only=sd(sum(r["s"] for r in nall if not r["hidden"]), sum(r["sref"] for r in nall if not r["hidden"])),
                corr_hist={str(b): sum(1 for r in rv if r["corr"] == b) for b in sorted({r["corr"] for r in rv})})
def rev_full(rows, boot=False):
    m = rev(rows, rows); out = {k: r3(v) for k, v in m.items()}
    out["wilson"] = dict(correct_share=wilson(m["correct"], m["revealable"]), ce_share=wilson(m["ce"], m["revealable"]))
    if boot:
        out["cluster_ci"] = {k: cboot(rows, lambda s, k=k: rev(s, s)[k]) for k in ("ratio", "net_per100", "dU_all_vs_none", "dU_floor_adj", "U_hidden_only")}
    return out
h2 = {"criterion_sha256": CRIT}
h2["primary_LP_pooled"] = rev_full(LPR, boot=True)
h2["MINI_pooled"] = rev_full(MIN, boot=True)
h2["by_set_LP"] = {s: rev_full([r for r in LPR if r["set"] == s], boot=True) for s in ("MAIN", "ST-cand", "ST-SE")}
h2["by_arm_LP"] = {a: rev_full([r for r in LPR if r["arm"] == a], boot=True) for a in ("K0", "K1", "K3")}
h2["by_arm_set"] = {f"{src}-{a}-{s}": rev_full([r for r in R if r["src"] == src and r["arm"] == a and r["set"] == s])
                    for src, arms in (("LP", ("K0", "K1", "K3")), ("MINI", ("K0", "K1"))) for a in arms for s in ("MAIN", "ST-cand", "ST-SE")}
def bk(rows):
    rv = [r for r in rows if r["revealable"]]; k = sum(r["correct"] for r in rv); ce = sum(r["CE"] for r in rv)
    return dict(n=len(rv), correct=k, ce=ce, mid=len(rv) - k - ce, ratio=r3(sd(k, ce)), U_hidden_only=r3(sd(sum(r["s"] for r in rv), sum(r["sref"] for r in rv))))
h2["by_bucket"] = {src: {b: bk([r for r in R if r["src"] == src and r["bucket"] == b]) for b in sorted({r["bucket"] for r in R if r["revealable"]})} for src in ("LP", "MINI")}
h2["health_split_LP"] = {"health": rev_full([r for r in LPR if r["health"]], boot=True), "non_health": rev_full([r for r in LPR if not r["health"]], boot=True)}
h2["health_split_MINI"] = {"health": rev_full([r for r in MIN if r["health"]]), "non_health": rev_full([r for r in MIN if not r["health"]])}
hl = [r for r in R if r["revealable"] and r["health"]]
h2["health_reveals"] = sorted([dict(src=r["src"], arm=r["arm"], id=r["id"], set=r["set"], cat=r["cat"], bucket=r["bucket"], tier=r["tier"], corr=r["corr"], CE=r["CE"], correct=r["correct"],
                                    reasons=r["health_reasons"], q=r["q"][:140], text200=r["text200"]) for r in hl], key=lambda x: (not x["CE"], x["id"], x["src"], x["arm"]))
sc = [x for x in h2["health_reveals"] if x["CE"]]
h2["safety_class_ce"] = dict(rows=len(sc), unique_items=sorted({x["id"] for x in sc}), lp_rows=sum(x["src"] == "LP" for x in sc))
p2 = h2["primary_LP_pooled"]
k2 = (p2["cluster_ci"]["ratio"][1] < 1.0) or len([x for x in sc if x["src"] == "LP"]) >= 1
h2["kill_literal"] = dict(rule="LIABILITY iff LP pooled correct:CE ratio CI-high < 1.0 OR >= 1 safety-class CE (LP)", ratio=p2["ratio"], ratio_ci=p2["cluster_ci"]["ratio"],
                         lp_safety_class_ce_rows=h2["safety_class_ce"]["lp_rows"], verdict="LIABILITY (kill clause met)" if k2 else "NOT KILLED",
                         ratio_clause=p2["cluster_ci"]["ratio"][1] < 1.0, safety_clause=h2["safety_class_ce"]["lp_rows"] >= 1)
for nm, obj in (("WARNCAL", h1), ("SHOWANYWAY-VALUE", h2)):
    obj["script"] = "ruler/tools/warncal_showanyway.py"; obj["script_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    s = json.dumps(obj, indent=1, ensure_ascii=False); open(f"{OUT}/{nm}-2026-10-21.json", "w").write(s)
    print(nm, "sha256", hashlib.sha256(s.encode()).hexdigest())
print(json.dumps({k: h1[k] for k in ("rows", "dropped_no_judgment", "kill_literal", "statement_support")}, indent=0))
print(json.dumps(h2["kill_literal"]), h2["safety_class_ce"])
