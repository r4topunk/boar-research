# PARA135 set B aggregation (0 LLM; definitions of ship15b/tools/ship15b_analyze.py). python3 -I tools/agg_b.py  (run from arms/para135)
import json, sys, os, collections, hashlib, numpy as np
A = "<workspace>/rnd/research/coordinator/arms/"; D = A + "para135/"
sys.path.insert(0, D + "tools"); from para import paragraphs
assert hashlib.sha256(open(D + "PARA135-criterion.md", "rb").read()).hexdigest() == open(D + "PARA135-criterion.sha256").read().split()[0]
ids = open(A + "native-parity/cv5-51.ids").read().split(); assert len(ids) == 51
TRF = {"p1": D + "gen/p135-b-p1-s42/traces.jsonl", "p3": D + "gen/p135-b-p3-s42/traces.jsonl", "p5": D + "gen/p135-b-p5-s42/traces.jsonl",
       "D17": A + "style17-detailed/traces/style17-detailed-K1-main-sub3e6183-s42.traces.jsonl", "S17": A + "lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl"}
TR = {k: {(j := json.loads(l)).get("itemId"): j for l in open(f)} for k, f in TRF.items()}
TX = {k: {q: TR[k][q]["answer"]["text"] or "" for q in ids} for k in TR}
K = ("correctness", "completeness", "usefulness"); mr = lambda d: sum(d[k] for k in K) / 3
def sr(a, b): return {"s": (mr(a["boar"]) + mr(b["boar"])) / 2, "r": (mr(a["ref"]) + mr(b["ref"])) / 2, "corr": (a["boar"]["correctness"] + b["boar"]["correctness"]) / 2}
def load(*paths):
    J = collections.defaultdict(dict)
    for p in paths:
        if not os.path.exists(p): continue
        for l in open(p):
            r = json.loads(l)
            if r.get("ok") and not r.get("floorScored") and r["order"] not in J[r["queryId"]]: J[r["queryId"]][r["order"]] = r["mapped"]
    return {q: sr(v["boarA"], v["boarB"]) for q, v in J.items() if set(v) == {"boarA", "boarB"}}
K1C = load(A + "lp-screens/control/judgments/lpctl-K1-main-s42-v01.judgments.jsonl")
def hk(files, k):
    own = load(*files); out = {}
    for q in ids:
        if q in own: out[q] = own[q]
        else: assert TX[k][q] == TX["S17"][q], (k, q); out[q] = K1C[q]
    return out
H = {k: hk([D + f"judge/b/p135-b-{k}-s42-v01.judgments.jsonl"], k) for k in ("p1", "p3", "p5")}
H["D17"] = hk([A + "style17-detailed/judgments/style17-detailed-K1-main-sub3e6183-s42-v01.judgments.jsonl"], "D17"); H["S17"] = hk([], "S17")
U = lambda s, r: (s - 1).sum() / (r - 1).sum(); RAW = lambda s, r: s.sum() / r.sum()
ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
rng = np.random.default_rng(11); n = len(ids); draws = [rng.integers(0, n, n) for _ in range(2000)]
dec = lambda k, q: bool(TR[k][q]["answer"].get("declined"))
def lv(k):
    J = H[k]; s = np.array([J[q]["s"] for q in ids]); r = np.array([J[q]["r"] for q in ids]); sh = [q for q in ids if not dec(k, q)]
    return {"U": round(U(s, r), 4), "U_ci": ci([U(s[ii], r[ii]) for ii in draws]), "U_raw": round(RAW(s, r), 4), "win_rate": round(float((s > r).mean()), 4),
            "correct_shown_per100": round(100 * sum(J[q]["corr"] >= 4 for q in sh) / n, 2), "ce_per100": round(100 * sum(J[q]["corr"] <= 1.5 for q in sh) / n, 2), "declined": n - len(sh)}
def pair(a, b):
    sa, ra = np.array([H[a][q]["s"] for q in ids]), np.array([H[a][q]["r"] for q in ids]); sb, rb = np.array([H[b][q]["s"] for q in ids]), np.array([H[b][q]["r"] for q in ids])
    return {"dU": round(U(sa, ra) - U(sb, rb), 4), "dU_ci": ci([U(sa[ii], ra[ii]) - U(sb[ii], rb[ii]) for ii in draws]),
            "better_tie_worse": [int((sa > sb).sum()), int((sa == sb).sum()), int((sa < sb).sum())], "changed_text": sum(TX[a][q] != TX[b][q] for q in ids)}
def cost(k, cap):
    t = [TR[k][q]["timing"] for q in ids]; ot = np.array([x.get("outputTokens") or 0 for x in t]); w = np.array([x.get("totalMs") or 0 for x in t])
    np_ = [len(paragraphs(TX[k][q])[1]) for q in ids]; N = {"p1": 1, "p3": 3, "p5": 5}.get(k)
    return {"out_tokens_p50": float(np.median(ot)), "out_tokens_mean": round(float(ot.mean()), 1), "at_cap": int((ot >= cap - 1).sum()), "ms_p50": round(float(np.median(w))),
            "words_p50": float(np.median([len(TX[k][q].split()) for q in ids])), "paras_p50": float(np.median(np_)), "paras_hist": dict(sorted(collections.Counter(np_).items())),
            "compliance": (sum(x == N for x in np_) if N else None), "compliance_pm1": (sum(abs(x - N) <= 1 for x in np_) if N else None),
            "banner": sum(bool(paragraphs(TX[k][q])[0]) for q in ids), "kept_items": sum(bool(TR[k][q]["retrieval"]["kept"]) for q in ids),
            "persona_sha": TR[k][ids[0]]["runtime"]["versions"].get("persona.sha256", "")[:8]}
caps = {"p1": 1024, "p3": 1024, "p5": 1024, "D17": 1024, "S17": 512}
out = {"n": n, "arms": {k: {**lv(k), **cost(k, caps[k])} for k in ("p1", "p3", "p5", "D17", "S17")},
       "vs_p1": {k: pair(k, "p1") for k in ("p3", "p5", "D17", "S17")}, "p5_vs_p3": pair("p5", "p3"),
       "reused_rows": {k: sum(1 for q in ids if q not in load(D + f"judge/b/p135-b-{k}-s42-v01.judgments.jsonl")) for k in ("p1", "p3", "p5")}}
json.dump(out, open(D + "aggregates/setB.json", "w"), indent=1); print(json.dumps(out, indent=1))
