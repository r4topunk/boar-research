"""REFVAR aggregate (0 LLM). Reads refvar judgments + existing v1 judgments + refs; writes refvar-results.json. Rules: ../REFVAR-criterion.md."""
import json, random, statistics as st, math, sys
R = "<workspace>/rnd/research/coordinator/ruler/refvar/"; A = "<workspace>/rnd/research/coordinator/arms/"
ids = [l.strip() for l in open(R + "refvar-20.ids") if l.strip()]
rd = lambda p: [json.loads(l) for l in open(p) if l.strip()]
def J(p):
    by = {}
    for r in rd(p):
        if r.get("ok") is True and r["queryId"] in ids: by.setdefault(r["queryId"], {})[r["order"]] = r["mapped"]
    m = lambda d: sum(d.values()) / 3
    return {q: (sum(m(x["boar"]) for x in v.values()) / 2, sum(m(x["ref"]) for x in v.values()) / 2) for q, v in by.items() if len(v) == 2}
TR = {"s17": A + "lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl", "s4b": A + "gemma4-e2b/vs4b/traces/gemma4-e2b-vs4b-K0-main-s42.traces.jsonl"}
dec = {s: {t["itemId"] for t in rd(p) if t.get("answer", {}).get("declined")} for s, p in TR.items()}
D = {}
for s in ["s17", "s4b"]:
    for ref in ["v1", "A", "B"]:
        D[(s, ref)] = J(R + f"judgments/refvar-{s}-ref{ref}.judgments.jsonl")
D[("s17", "v1old")] = J(A + "lp-screens/control/judgments/lpctl-K0-main-s42-v01.judgments.jsonl")
D[("s4b", "v1old")] = J(A + "gemma4-e2b/vs4b/judgments/gemma4-e2b-vs4b-K0-main-s42-v01.judgments.jsonl")
for s in ["s17", "s4b"]:
    D[(s, "AB")] = {i: ((D[(s, "A")][i][0] + D[(s, "B")][i][0]) / 2, (D[(s, "A")][i][1] + D[(s, "B")][i][1]) / 2) for i in ids if i in D[(s, "A")] and i in D[(s, "B")]}
for k in D: D[k] = {i: ((0.0 if i in dec[k[0]] else v[0]), v[1]) for i, v in D[k].items()}
common = [i for i in ids if all(i in D[k] for k in D if k[1] != "v1old")]  # primary set: every new judgment (v1old = test-retest only)
common_tr = [i for i in ids if all(i in D[k] for k in D)]
U = lambda d, I: sum(d[i][0] for i in I) / sum(d[i][1] for i in I)
UF = lambda d, I: sum(d[i][0] - 1 for i in I) / sum(d[i][1] - 1 for i in I)
rng = random.Random(11); BOOT = [[rng.choice(common) for _ in common] for _ in range(2000)]
rng2 = random.Random(11); BOOT_TR = [[rng2.choice(common_tr) for _ in common_tr] for _ in range(2000)]
def ci(f):
    v = sorted(f(I) for I in BOOT); return [round(v[49], 4), round(v[1949], 4)]
def ci_tr(f):
    v = sorted(f(I) for I in BOOT_TR); return [round(v[49], 4), round(v[1949], 4)]
def diff(a, b, s="s17", fn=U):
    if "v1old" in (a, b): return round(fn(D[(s, a)], common_tr) - fn(D[(s, b)], common_tr), 4), ci_tr(lambda I: fn(D[(s, a)], I) - fn(D[(s, b)], I))
    return round(fn(D[(s, a)], common) - fn(D[(s, b)], common), 4), ci(lambda I: fn(D[(s, a)], I) - fn(D[(s, b)], I))
def gap(ref, I=None): I = I or common; return U(D[("s4b", ref)], I) - U(D[("s17", ref)], I)
def gapdiff(a, b):
    if "v1old" in (a, b): return round(gap(a, common_tr) - gap(b, common_tr), 4), ci_tr(lambda I: gap(a, I) - gap(b, I))
    return round(gap(a) - gap(b), 4), ci(lambda I: gap(a, I) - gap(b, I))
out = {"n_common": len(common), "n_testretest": len(common_tr), "testretest_missing": [i for i in ids if i not in common_tr], "declined": {s: sorted(dec[s] & set(ids)) for s in dec}}
out["U"] = {f"{s}|{r}": {"U": round(U(D[(s, r)], common), 4), "ci": ci(lambda I: U(D[(s, r)], I)), "Ufloor": round(UF(D[(s, r)], common), 4),
                         "mean_sref": round(st.mean(D[(s, r)][i][1] for i in common), 3), "mean_s": round(st.mean(D[(s, r)][i][0] for i in common), 3)}
            for s in ["s17", "s4b"] for r in ["v1", "A", "B", "AB"]}
out["U_testretest_set"] = {f"{s}|{r}": round(U(D[(s, r)], common_tr), 4) for s in ["s17", "s4b"] for r in ["v1old", "v1", "A", "B", "AB"]}
out["dU"] = {}
for s in ["s17", "s4b"]:
    for a, b in [("A", "B"), ("AB", "v1"), ("A", "v1"), ("B", "v1"), ("v1", "v1old")]:
        d, c = diff(a, b, s); df, cf = diff(a, b, s, UF); out["dU"][f"{s}|{a}-{b}"] = {"dU": d, "ci": c, "dUfloor": df, "ci_floor": cf}
out["gap_4b_minus_17"] = {r: round(gap(r), 4) for r in ["v1", "A", "B", "AB"]}; out["gap_4b_minus_17_tr"] = {r: round(gap(r, common_tr), 4) for r in ["v1old", "v1"]}
out["gap_change"] = {f"{a}-{b}": gapdiff(a, b) for a, b in [("A", "B"), ("AB", "v1"), ("v1", "v1old")]}
# per-item ratio differences
for s in ["s17", "s4b"]:
    for a, b in [("A", "B"), ("v1", "v1old"), ("AB", "v1")]:
        I0 = common_tr if "v1old" in (a, b) else common
        d = [D[(s, a)][i][0] / D[(s, a)][i][1] - D[(s, b)][i][0] / D[(s, b)][i][1] for i in I0]
        m, sd = st.mean(d), st.stdev(d); h = 2.093 * sd / math.sqrt(len(d))
        out.setdefault("per_item", {})[f"{s}|{a}-{b}"] = {"mean": round(m, 4), "sd": round(sd, 4), "ci_t": [round(m - h, 4), round(m + h, 4)], "mean_abs": round(st.mean(abs(x) for x in d), 4)}
# lengths and sources
refs = {"v1": {r["id"]: r for r in rd("<workspace>/boar-eval/bench/v0.1/refs/refs.jsonl")}, "A": {r["id"]: r for r in rd(R + "refs/drawA.jsonl") if r.get("ok")}, "B": {r["id"]: r for r in rd(R + "refs/drawB.jsonl") if r.get("ok")}}
W = {k: {i: len(v[i]["answer"].split()) for i in ids if i in v} for k, v in refs.items()}
def q(xs): xs = sorted(xs); n = len(xs); return {"median": st.median(xs), "q1": xs[n // 4], "q3": xs[(3 * n) // 4], "min": xs[0], "max": xs[-1], "mean": round(st.mean(xs), 1)}
out["words"] = {k: q(list(v.values())) for k, v in W.items()}
def rank(x):
    o = sorted(range(len(x)), key=lambda k: x[k]); r = [0] * len(x)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and x[o[j + 1]] == x[o[i]]: j += 1
        for k in range(i, j + 1): r[o[k]] = (i + j) / 2
        i = j + 1
    return r
def spear(x, y):
    rx, ry = rank(x), rank(y); mx, my = st.mean(rx), st.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry)); den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)); return num / den if den else 0
pts = [(W[d][i], D[("s17", d)][i][1], D[("s17", d)][i][0] / D[("s17", d)][i][1]) for d in ["A", "B"] for i in common]
def spci(k):
    rr = random.Random(11); v = []
    for _ in range(2000):
        b = [rr.choice(pts) for _ in pts]; v.append(spear([p[0] for p in b], [p[k] for p in b]))
    v.sort(); return [round(v[49], 3), round(v[1949], 3)]
out["spearman_words"] = {"sref": [round(spear([p[0] for p in pts], [p[1] for p in pts]), 3), spci(1)], "ratio_s17": [round(spear([p[0] for p in pts], [p[2] for p in pts]), 3), spci(2)]}
dom = lambda u: u.split("/")[2].removeprefix("www.") if u.count("/") >= 2 else u
src = {}
for d in ["A", "B"]:
    rs = [refs[d][i] for i in ids if i in refs[d]]
    src[d] = {"urls_median": st.median(len({s["url"] for s in r["sources"]}) for r in rs), "dated_share": round(sum(1 for r in rs for s in r["sources"] if s.get("date") and "not shown" not in s["date"].lower()) / max(1, sum(len(r["sources"]) for r in rs)), 3),
              "searches_median": st.median(len(r["webSearches"]) for r in rs), "fetches_median": st.median(len(r["webFetches"]) for r in rs), "wall_s_median": round(st.median(r["wallMs"] for r in rs) / 1000, 1)}
jac = [len({dom(s["url"]) for s in refs["A"][i]["sources"]} & {dom(s["url"]) for s in refs["B"][i]["sources"]}) / max(1, len({dom(s["url"]) for s in refs["A"][i]["sources"]} | {dom(s["url"]) for s in refs["B"][i]["sources"]})) for i in ids if i in refs["A"] and i in refs["B"]]
src["domain_jaccard_AB_median"] = round(st.median(jac), 3); out["sources"] = src
out["items"] = {i: {"cat": refs["v1"][i]["category"], "words": {k: W[k].get(i) for k in W}, **{f"{s}|{r}": [round(x, 3) for x in D[(s, r)][i]] for s in ["s17", "s4b"] for r in ["v1old", "v1", "A", "B"] if i in D[(s, r)]}} for i in common}
json.dump(out, open(R + "refvar-results.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "items"}, indent=1))
