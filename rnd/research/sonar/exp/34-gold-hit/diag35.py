"""exp-35 diagnosis (Sonar): rv2 R vs A on v0.1 EN: concentration, seed agreement, answer style, displaced kit passages,
and R's context vs Anvil's Q450 context on the same items. Dev only."""
import json, re, statistics as st, collections
K = "<workspace>/boar-eval/runs/kiln/"; O = "<workspace>/rnd/research/anvil/exp/oracle/"
ids = open("<workspace>/rnd/research/anvil/exp/outofkit/v01-en-ids.txt").read().strip().split(",")
def judg(f):
    d = collections.defaultdict(list)
    for l in open(f):
        r = json.loads(l)
        if r.get("ok"): d[r["queryId"]].append((st.mean(r["mapped"]["boar"].values()), st.mean(r["mapped"]["ref"].values())))
    return {k: (st.mean(x for x, _ in v), st.mean(y for _, y in v)) for k, v in d.items()}
J = {"A42": judg(K + "bigpack-l1/bigpack-A-s42.v01.judgments.jsonl"), "A43": judg(K + "rv2-l1/rv2l1-A-s43.v01.judgments.jsonl"),
     "R42": judg(K + "rv2-l1/rv2l1-R-s42.v01.judgments.jsonl"), "R43": judg(K + "rv2-l1/rv2l1-R-s43.v01.judgments.jsonl"),
     "Q": judg(O + "runs/qwen3-4b-Q450.judgments.jsonl"), "E44": judg("<workspace>/boar-eval/runs/and-qwen-s44/and-qwen-s44.judgments.jsonl")}
def tr(f): return {json.loads(l)["itemId"]: json.loads(l) for l in open(f)}
T = {"A42": tr(K + "bigpack-l1/bigpack-A-s42.traces.jsonl"), "A43": tr(K + "rv2-l1/rv2l1-A-s43.traces.jsonl"),
     "R42": tr(K + "rv2-l1/rv2l1-R-s42.traces.jsonl"), "R43": tr(K + "rv2-l1/rv2l1-R-s43.traces.jsonl")}
Qc = {json.loads(l)["id"]: json.loads(l)["passages"] for l in open(O + "ctx-Q450.jsonl")}
common = [i for i in ids if all(i in J[k] for k in ("A42", "A43", "R42", "R43"))]
A = {i: (J["A42"][i][0] + J["A43"][i][0]) / 2 for i in common}; R = {i: (J["R42"][i][0] + J["R43"][i][0]) / 2 for i in common}
ref = sum((J["A42"][i][1] + J["A43"][i][1]) / 2 for i in common)
d = {i: R[i] - A[i] for i in common}
tot = sum(d.values())
print(f"items {len(common)}; sum delta {tot:+.2f} rubric pts = {tot/ref:+.4f} ratio")
srt = sorted(common, key=lambda i: d[i])
for k in (1, 3, 5): print(f"  worst {k}: {sum(d[i] for i in srt[:k]):+.2f}; without them the delta would be {(tot - sum(d[i] for i in srt[:k]))/ref:+.4f}")
print(f"  items worse by >=0.5: {sum(d[i] <= -0.5 for i in common)}, better by >=0.5: {sum(d[i] >= 0.5 for i in common)}")
# seed agreement
dd42 = {i: J["R42"][i][0] - J["A42"][i][0] for i in common}; dd43 = {i: J["R43"][i][0] - J["A43"][i][0] for i in common}
big = [i for i in common if abs(d[i]) >= 0.5]
print(f"seed agreement on |d|>=0.5 items: same sign {sum((dd42[i] > 0) == (dd43[i] > 0) and dd42[i] != 0 and dd43[i] != 0 for i in big)}/{len(big)}")
for i in srt[:6]: print(f"   {i}: s42 {dd42[i]:+.2f}  s43 {dd43[i]:+.2f}")
# style
def ctx(r):
    ev = [e for e in r["events"] if e.get("type") == "sources" and any(x.get("text") for x in e.get("sources", []))]
    return ev[-1]["sources"] if ev else []
def style(arm):
    w, cites, warn, none_ctx, decl = [], 0, 0, 0, 0
    for s in ("42", "43"):
        for i in common:
            r = T[arm + s][i]; a = (r.get("answer") or {}).get("text", "") if isinstance(r.get("answer"), dict) else ""
            w.append(len(a.split())); cites += bool(re.search(r"\[\d+\]", a))
            rc = r["route"]["reasonCodes"]; warn += any("uncited" in c for c in rc); none_ctx += not ctx(r)
            decl += bool(re.search(r"(?i)\b(couldn't find|could not find|don't have (enough )?information|not (in|from) the (sources|context)|sources don't)", a))
    n = 2 * len(common)
    return f"{arm}: mean answer words {st.mean(w):.0f}; answers with [n] citations {cites}/{n}; uncited warning/preface {warn}/{n}; no context {none_ctx}/{n}; decline-ish {decl}/{n}"
print(style("A")); print(style("R"))
# displaced kit passages: A had Wikivoyage/crypto/other kit passages that R lost
W = lambda s: re.findall(r"\w+", s.lower())
def g4(s): w = W(s); return {tuple(w[k:k + 4]) for k in range(len(w) - 3)}
disp = []
for i in common:
    a = [x for x in ctx(T["A42"][i]) if not (x.get("source") or "").startswith("Wikipedia")]
    rg = g4(" ".join((x.get("text") or "") for x in ctx(T["R42"][i])))
    lost = [x for x in a if len(g4(x.get("text") or "") & rg) / max(1, len(g4(x.get("text") or ""))) < 0.3]
    if lost: disp.append(i)
print(f"items where R dropped >=1 of A's kit passages (s42): {len(disp)}, sum delta there {sum(d[i] for i in disp):+.2f}; elsewhere {sum(d[i] for i in common if i not in disp):+.2f}")
# R vs Q450 context overlap and judged
def cov(ps, rg): return max((len(g4(p["text"]) & rg) / max(1, len(g4(p["text"]))) for p in ps), default=0)
qo = {i: cov(Qc.get(i, []), g4(" ".join((x.get("text") or "") for x in ctx(T["R42"][i])))) for i in common}
hi = [i for i in common if qo[i] >= 0.5]; lo_ = [i for i in common if qo[i] < 0.2]
print(f"R context holds a Q450 passage (>=50% 4-grams) on {len(hi)} items; <20% on {len(lo_)}")
qd = {i: J["Q"][i][0] - J["E44"][i][0] for i in common if i in J["Q"] and i in J["E44"]}
for name, S in (("R has a Q450 passage", hi), ("R lacks Q450 passages", lo_)):
    S = [i for i in S if i in qd]
    print(f"  {name}: n={len(S)}  R-A sum {sum(d[i] for i in S):+.2f}   Q450-engine(s44) sum {sum(qd[i] for i in S):+.2f}")
json.dump({"delta": d, "s42": dd42, "s43": dd43, "q450_overlap": qo, "displaced": disp}, open("diag35.json", "w"), indent=0)
