#!/usr/bin/env python3
"""HEADLINE-2x2 (NIGHT-criterion B). python3 -I b_agg.py plan|agg   (0 LLM here; judging is done by judge_b.sh / opus_b.sh)
Arm = SEFIX-124 on the adopted kit K13 (gidf + F1 + F2 + F4, F3 off), regenerated on the mini as b124-main-s{42,43} (b/traces). Control = K3 rows (s42 pool-K1 text / s43 ctlk1-main-s43), as agg_124.py.
Row cache = every judged row of agg_124.py (exec'd prefix: pool-K1, ARM-G, SEFIX-ALL, control s43, S124 Haiku rows) + b/judge/S<seed>.<X|C> (new Haiku rows). Key (id, answer text).
plan: writes b/judge/plan.json + ids files of the (seed, arm, id) units whose text has no judged row (divergence-first: a unit whose text equals the control's is judged once).
agg: delivered (chunk-level, replay of the adopted kit: chunklevel-124.json 'sefix F1F2F4') x correctness band (mean boar correctness >= 3.5), U/CE/CE-unwarned per cell, gap with item bootstrap (B 2000, Random(11))."""
import json, sys, glob, random, collections, hashlib, os
A = "<workspace>/rnd/research/coordinator/arms"; SF = A + "/coverage-map/sefix"; NB = A + "/night-1023"; B = NB + "/b"
exec(open(SF + "/ans-tools/agg_124.py").read().split("def build(s):")[0])   # cache, TR (old 124 X traces), ld, rd, jby, ids, src_of, pool, W, KEYS, put, ctl42
OLD_X = {s: TR[s]["X"] for s in (42, 43)}; CT = {s: TR[s]["C"] for s in (42, 43)}
NEW_X = {s: ld((SF + f"/ans-traces/sefix124-main-s{s}.traces.jsonl") if os.environ.get("B_DRY") else f"{B}/traces/b124-main-s{s}.traces.jsonl") for s in (42, 43)}
for s in (42, 43):   # b-judged rows into the cache
    for arm, T in (("X", NEW_X[s]), ("C", CT[s])):
        for i, by in jby(f"{B}/judge/S{s}.{arm}").items():
            if len(by) == 2:
                t = T[i]; row = jrow({i: by}, i); row.update(declined=bool(t["answer"].get("declined")), warned=t["answer"]["text"].startswith(W)); put(i, t["answer"]["text"], row)
mode = sys.argv[1]
txt = lambda D, i: D[i]["answer"]["text"]
mode_plan = mode == "plan"
if mode_plan:
    plan = {}; need = {}
    for s in (42, 43):
        for i in ids:
            for arm, D in (("X", NEW_X[s]), ("C", CT[s])):
                if arm == "C" and txt(NEW_X[s], i) == txt(CT[s], i) and (i, txt(NEW_X[s], i)) not in cache: continue   # judged once, as X
                if (i, txt(D, i)) not in cache: need.setdefault((s, arm), []).append(i)
    for (s, arm), v in need.items():
        os.makedirs(f"{B}/judge/S{s}.{arm}", exist_ok=True); open(f"{B}/judge/S{s}.{arm}/plan.ids", "w").write("\n".join(v) + "\n")
    plan = {f"{s}.{a}": v for (s, a), v in need.items()}; json.dump(plan, open(B + "/judge/plan.json", "w"), indent=1)
    print({k: (len(v), v) for k, v in plan.items()}, "calls", 2 * sum(len(v) for v in plan.values())); sys.exit(0)
# ---------------- agg
CL = json.load(open(SF + "/chunklevel-124.json"))["per_item"]; FLAG = {k: CL[k] for k in ("sefix F1F2F4", "B0 stock (retrieve-sweep)")}
RPX = {r["id"]: r for r in rd(SF + "/replays/main.F1F2F4.jsonl")}
KEYED = [i for i in ids if FLAG["sefix F1F2F4"].get(i) is not None]; V01 = [i for i in KEYED if src_of(i) == "v0.1"]; CMI = [i for i in KEYED if src_of(i) != "v0.1"]
assert len(KEYED) == 92 and len(V01) == 52 and len(CMI) == 40
dl = lambda i: bool(FLAG["sefix F1F2F4"][i]["chunk"])
S = {}; miss = []
for s in (42, 43):
    RX, RC = {}, {}
    for i in ids:
        for R, D, tag in ((RX, NEW_X[s], "X"), (RC, CT[s], "C")):
            row = cache.get((i, txt(D, i)))
            if row is None: miss.append((s, tag, i)); row = dict(s=0, sref=1, corr=0, declined=False, warned=False, MISSING=True)
            R[i] = dict(row, text=txt(D, i)); R[i]["declined"] = bool(D[i]["answer"].get("declined")); R[i]["warned"] = txt(D, i).startswith(W)
            R[i]["CE"] = (not R[i]["declined"]) and R[i]["corr"] <= 1.5
    S[s] = dict(X=RX, C=RC)
assert not miss, miss
def prow(a, b):
    ea = 0 if a["declined"] else a["s"]; eb = 0 if b["declined"] else b["s"]
    return dict(s=(ea + eb) / 2, sref=(a["sref"] + b["sref"]) / 2, corr=(a["corr"] + b["corr"]) / 2, declined=False, warned=a["warned"] and b["warned"], CE=None)
P = {k: {i: prow(S[42][k][i], S[43][k][i]) for i in ids} for k in ("X", "C")}
U = lambda R, xs: (sum(0 if R[i]["declined"] else R[i]["s"] for i in xs) / sum(R[i]["sref"] for i in xs)) if xs else None
def boot(xs, f, Bn=2000):
    r = random.Random(11); v = []
    for _ in range(Bn):
        x = f([r.choice(xs) for _ in xs])
        if x is not None: v.append(x)
    v.sort(); return [round(v[int(0.025 * len(v))], 4), round(v[int(0.975 * len(v)) - 1], 4)]
def cellstats(R, xs, pooled=False):
    nd = [i for i in xs if not R[i]["declined"]]
    d = dict(n=len(xs), U=round(U(R, xs), 4) if xs else None, corr=round(sum(R[i]["corr"] for i in xs) / len(xs), 3) if xs else None)
    if not pooled:
        ce = [i for i in nd if R[i]["corr"] <= 1.5]; d.update(CE=len(ce), CE_unwarned=sum(1 for i in ce if not R[i]["warned"]), declined=len(xs) - len(nd))
    return d
band = lambda R, i: R[i]["corr"] >= 3.5
def two_by_two(R, xs, flag, pooled=False):
    out = {}
    for dn, dv in (("delivered", True), ("not_delivered", False)):
        g = [i for i in xs if flag(i) == dv]
        out[dn] = dict(all=cellstats(R, g, pooled), band_ge35=cellstats(R, [i for i in g if band(R, i)], pooled), band_lt35=cellstats(R, [i for i in g if not band(R, i)], pooled))
        out[dn]["P_band_ge35"] = round(sum(1 for i in g if band(R, i)) / len(g), 3) if g else None
    d = [i for i in xs if flag(i)]; n = [i for i in xs if not flag(i)]
    gap = lambda sample: (U(R, [i for i in sample if flag(i)]) - U(R, [i for i in sample if not flag(i)])) if any(flag(i) for i in sample) and any(not flag(i) for i in sample) else None
    out["gap_U"] = dict(d=round(gap(xs), 4), ci=boot(xs, gap))
    return out
def band_gap(R, xs, flag):
    def f(sm):
        a = [i for i in sm if flag(i)]; b = [i for i in sm if not flag(i)]
        return (sum(band(R, i) for i in a) / len(a) - sum(band(R, i) for i in b) / len(b)) if a and b else None
    return dict(d=round(f(xs), 4), ci=boot(xs, f))
def pair(Ra, Rb, xs):
    f = lambda sm: U(Ra, sm) - U(Rb, sm); g = lambda sm: sum(Ra[i]["corr"] - Rb[i]["corr"] for i in sm) / len(sm)
    return dict(n=len(xs), d=round(f(xs), 4), ci=boot(xs, f), dcorr=round(g(xs), 4), dcorr_ci=boot(xs, g))
SETS = {"MAIN97 (92 keyed)": KEYED, "v0.1 52": V01, "cm 40": CMI}
res = dict(sanity={}, sets={}, arm_vs_control={}, parity={}, sensitivity={}, control_2x2={}, unkeyed_5=[i for i in ids if i not in KEYED])
# sanity + regen identity
loop = lambda t: any(v >= 3 for v in collections.Counter(tuple(t.split()[k:k + 6]) for k in range(max(0, len(t.split()) - 5))).values())
det = lambda t: (t["timing"].get("outputTokens") or 0) == 0 or not any(r.startswith("generate:user-model") for r in t["route"]["reasonCodes"])
for s in (42, 43):
    X, C = NEW_X[s], CT[s]; dets = [i for i in ids if det(C[i])]
    res["sanity"][s] = dict(rows=len(X), missing=[i for i in ids if i not in X], errors=[i for i in ids if X[i].get("error")], empty=[i for i in ids if not txt(X, i).strip()], loops=[i for i in ids if loop(txt(X, i))],
        identical_to_old_sefix124_run=sum(txt(X, i) == txt(OLD_X[s], i) for i in ids), det_items_in_control=len(dets), det_identical_to_control=sum(txt(X, i) == txt(C, i) for i in dets), det_not_identical=[i for i in dets if txt(X, i) != txt(C, i)],
        text_differs_vs_control=sum(txt(X, i) != txt(C, i) for i in ids), kept_titles_eq_replay=sum([c["title"] for c in X[i]["retrieval"]["kept"]] == [c["title"] for c in RPX[i]["keptFull"]] for i in ids if i in RPX))
    res["parity"][s] = [i for i in KEYED if [c["title"] for c in NEW_X[s][i]["retrieval"]["kept"]] == [c["title"] for c in RPX[i]["keptFull"]]]
for nm, xs in SETS.items():
    r = {}
    for s in (42, 43):
        r[f"s{s}"] = two_by_two(S[s]["X"], xs, dl); r[f"s{s}"]["band_gap"] = band_gap(S[s]["X"], xs, dl)
    r["pooled"] = two_by_two(P["X"], xs, dl, True); r["pooled"]["band_gap"] = band_gap(P["X"], xs, dl)
    # arm vs control inside delivered / non-delivered
    r["dU_vs_control"] = {f"s{s}": {k: pair(S[s]["X"], S[s]["C"], [i for i in xs if dl(i) == v]) for k, v in (("delivered", True), ("not_delivered", False))} for s in (42, 43)}
    r["dU_vs_control"]["pooled"] = {k: pair(P["X"], P["C"], [i for i in xs if dl(i) == v]) for k, v in (("delivered", True), ("not_delivered", False))}
    res["sets"][nm] = r
res["arm_vs_control"] = {f"s{s}": pair(S[s]["X"], S[s]["C"], ids) for s in (42, 43)}; res["arm_vs_control"]["pooled"] = pair(P["X"], P["C"], ids)
res["arm_vs_control"]["all97_summ"] = {f"s{s}": dict(C=cellstats(S[s]["C"], ids), X=cellstats(S[s]["X"], ids)) for s in (42, 43)}
# sensitivity: live-title parity subset; control kit's own delivered flag (B0 replay) on the control rows
for s in (42, 43):
    par = res["parity"][s]; res["sensitivity"][f"parity_s{s}"] = dict(n=len(par), **{k: v for k, v in two_by_two(S[s]["X"], par, dl).items() if k == "gap_U"}, delivered_n=sum(dl(i) for i in par))
    cf = lambda i: bool(FLAG["B0 stock (retrieve-sweep)"][i]["chunk"]) if FLAG["B0 stock (retrieve-sweep)"].get(i) else False
    res["control_2x2"][f"s{s}"] = dict(delivered_n=sum(cf(i) for i in KEYED), **{k: v for k, v in two_by_two(S[s]["C"], KEYED, cf).items() if k in ("gap_U", "delivered", "not_delivered")})
# rule
rule = {f"s{s}": (lambda g: dict(gap=g["d"], ci_low=g["ci"][0], ok=(g["d"] >= 0.3 and g["ci"][0] > 0)))(res["sets"]["MAIN97 (92 keyed)"][f"s{s}"]["gap_U"]) for s in (42, 43)}
rule["PUBLISHABLE"] = all(rule[f"s{s}"]["ok"] for s in (42, 43)); res["rule"] = rule
res["miss"] = miss
json.dump(res, open(NB + "/b-table.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(dict(sanity=res["sanity"], rule=rule, arm_vs_control=res["arm_vs_control"]["pooled"], gaps={nm: {k: v["gap_U"] for k, v in r.items() if k.startswith(("s", "pooled")) and isinstance(v, dict) and "gap_U" in v} for nm, r in res["sets"].items()}), indent=1))
