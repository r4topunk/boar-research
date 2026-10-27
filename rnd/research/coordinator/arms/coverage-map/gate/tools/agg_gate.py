#!/usr/bin/env python3
"""PRECISION-GATE aggregate (0 LLM). python3 -I tools/agg_gate.py   -> answers-gate.json, sanity.json
Rows: control = null-cal/control/pool-K1.json (judged K3-kit mini control); G = ARM-G (compose/screen: judged rows in screen/judge/G, control row where G's text equals the control's);
P1/P2 = this arm's traces: row = G's row if the answer text equals G's, else the control row if equal to the control's, else the arm's own Haiku judgment (gate/judge/<arm>).
Definitions as compose/screen/tools/agg_cmp.py (ratio-of-sums U, corr averaged over both orders, CE = not declined and corr <= 1.5, warned = text starts with the engine's warning line).
Paired dU: item bootstrap B 2000 seed 11. Fact present/absent = compose.json N10.gidf kept_list (stage K) / the other keyed items (calibration.json flag)."""
import json, sys, glob, random, os, collections
A = "<workspace>/rnd/research/coordinator/arms"; CM = A + "/coverage-map"; GD = CM + "/gate"; CMP = CM + "/compose"
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ids = open(A + "/lp-screens/main-97.ids").read().split()
ctl = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]; cal = json.load(open(GD + "/calibration.json")); flag = cal["flag"]
TR = {"G": {t["itemId"]: t for t in rd(CMP + "/screen/traces/cmp-G-K10-main-s42.traces.jsonl")}}
ARMS = [a for a in ("P1", "P2") if os.path.exists(f"{GD}/traces/gate-{a}-main-s42.traces.jsonl")]
for a in ARMS: TR[a] = {t["itemId"]: t for t in rd(f"{GD}/traces/gate-{a}-main-s42.traces.jsonl")}
def jby(JD):
    by = {}
    for f in sorted(glob.glob(JD + "/*.judgments.jsonl")):
        for r in rd(f):
            if r.get("ok") is True: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    return by
BY = {"G": jby(CMP + "/screen/judge/G")}
for a in ARMS: BY[a] = jby(f"{GD}/judge/{a}")
dim = lambda m, k: sum(m[k].values()) / 3
def jrow(by, i):
    ms = list(by[i].values())
    return dict(s=sum(dim(m, "boar") for m in ms) / 2, sref=sum(dim(m, "ref") for m in ms) / 2, corr=sum(m["boar"]["correctness"] for m in ms) / 2)
def mk(t, j, src):
    txt = t["answer"]["text"]; d = bool(t["answer"].get("declined"))
    return dict(j, text=txt, declined=d, warned=txt.startswith(W), CE=(not d and j["corr"] <= 1.5), judgment=src, outTok=t["timing"].get("outputTokens") or 0, totalMs=t["timing"].get("totalMs") or 0,
                weak=bool(t["answer"].get("weakSources")), nosrc=not t["retrieval"]["kept"], gated=any(c.startswith("rsgate:closed") or c == "dg:gate:no-evidence" for c in t["route"]["reasonCodes"]),
                modelgen=any(c.startswith("generate:user-model") for c in t["route"]["reasonCodes"]) and (t["timing"].get("outputTokens") or 0) > 0)
mini = {}
for f in glob.glob(A + "/litepacks/traces/mini/lp-K1-*-s42.mini.traces.jsonl"): mini.update({t["itemId"]: t for t in rd(f)})
crow = {i: dict(ctl[i], totalMs=mini[i]["timing"].get("totalMs") or 0, outTok=mini[i]["timing"].get("outputTokens") or 0, nosrc=not mini[i]["retrieval"]["kept"], gated=False,
                modelgen=any(c.startswith("generate:user-model") for c in mini[i]["route"]["reasonCodes"]) and (mini[i]["timing"].get("outputTokens") or 0) > 0) for i in ids}
rows = {"G": {}}; unjudged = {a: [] for a in ARMS}
for i in ids:
    t = TR["G"][i]; txt = t["answer"]["text"]; c = ctl[i]
    if txt != c["text"]:
        if i in BY["G"] and len(BY["G"][i]) == 2: j = jrow(BY["G"], i); src = "judged-G"
        else: raise SystemExit(f"ARM-G row missing for {i}")
    else: j = dict(s=c["s"], sref=c["sref"], corr=c["corr"]); src = "control-row"
    rows["G"][i] = mk(t, j, src)
for a in ARMS:
    rows[a] = {}
    for i in ids:
        t = TR[a][i]; txt = t["answer"]["text"]; c = ctl[i]; g = rows["G"][i]
        if txt == g["text"]: j = {k: g[k] for k in ("s", "sref", "corr")}; src = "reused-G"
        elif txt == c["text"]: j = dict(s=c["s"], sref=c["sref"], corr=c["corr"]); src = "control-row"
        elif a == "P2" and "P1" in rows and i in rows["P1"] and rows["P1"][i]["text"] == txt and rows["P1"][i]["judgment"] in ("judged", "control-row"): r1 = rows["P1"][i]; j = {k: r1[k] for k in ("s", "sref", "corr")}; src = "reused-P1"
        elif i in BY[a] and len(BY[a][i]) == 2: j = jrow(BY[a], i); src = "judged"
        else: unjudged[a].append(i); continue
        rows[a][i] = mk(t, j, src)
def U(src, xs): return sum(0 if src[i]["declined"] else src[i]["s"] for i in xs) / sum(src[i]["sref"] for i in xs)
def summ(src, xs):
    nd = [i for i in xs if not src[i]["declined"]]; ce = [i for i in nd if src[i]["corr"] <= 1.5]
    return dict(n=len(xs), U=round(U(src, xs), 4), corr=round(sum(src[i]["corr"] for i in xs) / len(xs), 3), CE=len(ce), CE_unwarned=sum(1 for i in ce if not src[i]["warned"]),
                CE_unwarned_ui=sum(1 for i in ce if not src[i]["warned"] and not src[i].get("weak")), warned=sum(1 for i in xs if src[i]["warned"]), weak_flag=sum(1 for i in xs if src[i].get("weak")), declined=sum(1 for i in xs if src[i]["declined"]),
                closed_book=sum(1 for i in xs if src[i].get("modelgen") and src[i].get("nosrc")), totalMs=round(sum(src[i]["totalMs"] for i in xs) / len(xs), 0), outTok=round(sum(src[i]["outTok"] for i in xs) / len(xs), 2))
def boot(xs, f, B=2000):
    r = random.Random(11); v = []
    for _ in range(B): v.append(f([r.choice(xs) for _ in xs]))
    v.sort(); return [round(v[int(0.025 * B)], 4), round(v[int(0.975 * B) - 1], 4)]
def pair(srcA, srcB, xs):
    if not xs: return dict(n=0)
    f = lambda s: U(srcA, s) - U(srcB, s); g = lambda s: sum(srcA[i]["corr"] - srcB[i]["corr"] for i in s) / len(s)
    return dict(n=len(xs), d=round(f(xs), 4), ci=boot(xs, f), dcorr=round(g(xs), 4), dcorr_ci=boot(xs, g))
res = dict(n=len(ids), tau=cal["tau"], unjudged=unjudged, arms={})
cls = {"fact_present": [i for i in ids if flag[i] == "P"], "fact_absent": [i for i in ids if flag[i] == "A"], "unkeyed": [i for i in ids if flag[i] == "U"]}
res["control_all97"] = summ(crow, ids); res["G_all97"] = summ(rows["G"], ids)
for a in ARMS:
    R = rows[a]; x = {}
    if unjudged[a]: x["WARN_unjudged"] = unjudged[a]; res["arms"][a] = x; continue
    chg = [i for i in ids if R[i]["text"] != rows["G"][i]["text"]]
    x["changed_vs_G"] = chg; x["all97"] = summ(R, ids)
    x["vs_G_changed"] = dict(G=summ(rows["G"], chg) if chg else None, arm=summ(R, chg) if chg else None, **pair(R, rows["G"], chg))
    x["vs_G_all97"] = pair(R, rows["G"], ids)
    x["vs_control_all97"] = pair(R, crow, ids); x["G_vs_control_all97"] = pair(rows["G"], crow, ids)
    x["by_class"] = {k: dict(n=len(v), G=summ(rows["G"], v), arm=summ(R, v), changed=[i for i in v if i in chg], **{"vs_G": pair(R, rows["G"], v)}) for k, v in cls.items()}
    x["gated_items"] = [i for i in ids if R[i]["gated"]]
    fp = [i for i in cls["fact_present"] if R[i]["gated"]]; x["false_closed_book_fact_present"] = dict(n=len(fp), of=len(cls["fact_present"]), rate=round(len(fp) / len(cls["fact_present"]), 4), ids=fp)
    fa = [i for i in cls["fact_absent"] if R[i]["gated"]]; x["gated_fact_absent"] = dict(n=len(fa), of=len(cls["fact_absent"]), ids=fa)
    x["gated_items_detail"] = {i: dict(cls=flag[i], G_corr=rows["G"][i]["corr"], arm_corr=R[i]["corr"], G_s=round(rows["G"][i]["s"], 3), arm_s=round(R[i]["s"], 3), G_warned=rows["G"][i]["warned"], arm_warned=R[i]["warned"], judgment=R[i]["judgment"]) for i in x["gated_items"]}
    ce_up = x["all97"]["CE_unwarned"] > res["G_all97"]["CE_unwarned"]
    d = x["vs_G_changed"]; ok_u = d.get("n", 0) > 0 and d["d"] >= 0.02 and d["ci"][0] > -0.01
    passed = ok_u and not ce_up and x["false_closed_book_fact_present"]["rate"] <= 0.10
    e = x["vs_control_all97"]; lever = passed and e["d"] >= 0.02 and e["ci"][0] > -0.01
    x["rule"] = dict(dU_ge_0_02_ci_low_gt_minus_0_01=ok_u, CE_unwarned_not_up=not ce_up, false_closed_le_10pct=x["false_closed_book_fact_present"]["rate"] <= 0.10, PASS=passed,
                     vs_control_dU_ge_0_02_ci_low_gt_minus_0_01=(e["d"] >= 0.02 and e["ci"][0] > -0.01), LEVER_CANDIDATE=lever, verdict="LEVER-CANDIDATE" if lever else "PASS" if passed else "NO")
    res["arms"][a] = x
# sanity (stage-0): rows, errors, empty, loops, deterministic items identical to ARM-G
def loop(txt):
    w = txt.split(); c = collections.Counter(tuple(w[i:i + 6]) for i in range(len(w) - 5)); return any(v >= 3 for v in c.values())
det = lambda t: (t["timing"].get("outputTokens") or 0) == 0 or not any(r.startswith("generate:user-model") for r in t["route"]["reasonCodes"])
san = {}
for a in ARMS:
    T = TR[a]; G = TR["G"]
    dets = [i for i in ids if det(G[i])]
    san[a] = dict(rows=len(T), missing=[i for i in ids if i not in T], errors=[i for i in ids if i in T and T[i].get("error")], empty=[i for i in ids if i in T and not (T[i]["answer"]["text"] or "").strip()],
                  loops=[i for i in ids if i in T and loop(T[i]["answer"]["text"] or "")], det_items=len(dets), det_text_diff_vs_G=[i for i in dets if T[i]["answer"]["text"] != G[i]["answer"]["text"]],
                  text_identical_to_G=sum(T[i]["answer"]["text"] == G[i]["answer"]["text"] for i in ids), kept_identical_to_G=sum([(c["title"], c.get("section")) for c in T[i]["retrieval"]["kept"]] == [(c["title"], c.get("section")) for c in G[i]["retrieval"]["kept"]] for i in ids),
                  closed_book=sum(1 for i in ids if rows[a].get(i, {}).get("modelgen") and rows[a].get(i, {}).get("nosrc")), G_closed_book=sum(1 for i in ids if rows["G"][i]["modelgen"] and rows["G"][i]["nosrc"]),
                  mean_totalMs=round(sum(T[i]["timing"].get("totalMs") or 0 for i in ids) / len(ids), 0), G_mean_totalMs=round(sum(G[i]["timing"].get("totalMs") or 0 for i in ids) / len(ids), 0))
    sel = [T[i].get("retrieval", {}).get("dg") for i in ids if T[i].get("retrieval", {}).get("dg")]
    if sel:
        ms = [d["select"]["ms"] for d in sel if d and d.get("select") and d["select"].get("ms")]
        san[a]["select_calls"] = len(ms); san[a]["select_ms_mean"] = round(sum(ms) / len(ms), 0) if ms else None
        san[a]["no_evidence"] = sum(1 for d in sel if d.get("select", {}).get("noEvidence")); san[a]["unmapped"] = sum(1 for d in sel if d.get("select", {}).get("unmapped")); san[a]["no_sentences"] = sum(1 for d in sel if d.get("select", {}).get("noSentences"))
    san[a]["kill"] = bool(san[a]["missing"] or san[a]["errors"] or san[a]["empty"] or san[a]["loops"] or san[a]["det_text_diff_vs_G"])
res["sanity"] = san
res["rows"] = {a: {i: {k: v for k, v in r.items() if k != "text"} for i, r in rows[a].items()} for a in rows}
res["texts"] = {a: {i: rows[a][i]["text"] for i in (res["arms"].get(a, {}).get("changed_vs_G") or [])} for a in ARMS}
res["texts"]["G"] = {i: rows["G"][i]["text"] for a in ARMS for i in (res["arms"].get(a, {}).get("changed_vs_G") or [])}
json.dump(res, open(GD + "/answers-gate.json", "w"), indent=1, ensure_ascii=False)
json.dump(san, open(GD + "/sanity.json", "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k not in ("rows", "texts")}, indent=0, ensure_ascii=False)[:7000])
