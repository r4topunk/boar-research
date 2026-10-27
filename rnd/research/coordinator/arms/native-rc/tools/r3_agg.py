#!/usr/bin/env python3
"""R3 aggregate, Claude-family half (0 LLM): RULER-SPEC-v1-r4 section 3 metrics with one reference family (F1 Claude) and one judge family (G1 Opus).
Per item i, arm X, generation g: m = mean of the three rubric scores per order, averaged over the two orders; u = 0 if z (refusal) else m(app) - 1;
r = m(ref) - 1 from X's own pairing; correct k: mean correctness over orders >= 4 and z = 0; confident error x: z = 0 and mean correctness <= 1.5;
win/tie/loss per item: judge-core combineOrders (both orders agree = verdict, else tie), z = loss. Generations: u, r, k, x averaged over the two seeds.
U_total = sum_H w u / sum_H w r (H = 71 non-anchor items, w = 0.5 health_safety); also weight 1, H u anchors (75), anchors alone, without the 7 location items,
coverage C/N/M (kept on every / no / some turn, seed 42 traces), U-ref / U-noref (numerator form), CR, CE (answered / over H), refusal rate, absolute means,
per family. Paired NATIVE - ENGINE with the common denominator rbar = (r_N + r_E) / 2. CI: B 2000, seed 11, items resampled, and within each item the two
orders and the two generations resampled (spec 3.7). Stage 1 (DECLINE2STAGE) not run (Haiku cap): these are judge.v1 + z numbers (spec 3.4 row (a)).
usage: python3 -I r3_agg.py -> aggregates/r3.json + table"""
import json, os, random, collections
A = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V = A + "/work/v04"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
Q = {r["id"]: r for r in rd(V + "/bench/questions.jsonl")}
LOC = {r["id"] for r in rd(V + "/native-items.jsonl") if r.get("context")}
IDS = list(Q); H = [i for i in IDS if not Q[i]["anchor"]]; ANCH = [i for i in IDS if Q[i]["anchor"]]
W = {i: Q[i]["weight"] for i in IDS}
mean = lambda xs: sum(xs) / len(xs)
def load(arm):
    G = {}
    for S in (42, 43):
        jf = f"{A}/judge/r3/{arm}-s{S}.opus.judgments.jsonl"; tf = f"{V}/traces/{arm}-s{S}.traces.jsonl"
        if not os.path.exists(jf): continue
        T = {t["itemId"]: t for t in rd(tf)}
        per = collections.defaultdict(dict)
        for r in rd(jf):
            if r.get("ok"): per[r["queryId"]][r["order"]] = r
        G[S] = {}
        for i in IDS:
            o = per.get(i, {})
            if len(o) < 2: continue
            z = bool(T[i]["ruler"].get("refusedZ"))
            orders = []
            for od in ("boarA", "boarB"):
                mp = o[od]["mapped"]; b, f = mp["boar"], mp["ref"]
                orders.append(dict(ma=mean([b["correctness"], b["completeness"], b["usefulness"]]), mr=mean([f["correctness"], f["completeness"], f["usefulness"]]),
                                   ca=b["correctness"], cr=f["correctness"], win=mp["winner"]))
            G[S][i] = dict(z=z, orders=orders, kept=T[i]["ruler"].get("kept"), keptTurns=T[i]["ruler"].get("keptTurns"))
    return G
def item_stats(e, orders=None):
    os_ = orders if orders is not None else e["orders"]
    ma = mean([o["ma"] for o in os_]); mr = mean([o["mr"] for o in os_]); ca = mean([o["ca"] for o in os_]); cr = mean([o["cr"] for o in os_])
    u = 0.0 if e["z"] else ma - 1; r = mr - 1
    k = float(ca >= 4 and not e["z"]); kref = float(cr >= 4); x = float(not e["z"] and ca <= 1.5)
    wins = {o["win"] for o in os_}
    wtl = "loss" if e["z"] else ({"boar": "win", "ref": "loss", "tie": "tie"}.get(next(iter(wins)), "tie") if len(wins) == 1 else "tie")
    return dict(u=u, r=r, k=k, kref=kref, x=x, ma=ma - 1, mr=mr - 1, wtl=wtl, z=float(e["z"]))
def per_item(G, rng=None):
    """per item: averaged over generations (resampled if rng), orders resampled if rng"""
    out = {}
    for i in IDS:
        gens = [S for S in G if i in G[S]]
        if not gens: continue
        if rng: gens = [rng.choice(gens) for _ in gens]
        ss = []
        for S in gens:
            e = G[S][i]; od = [rng.choice(e["orders"]) for _ in e["orders"]] if rng else None
            ss.append(item_stats(e, od))
        out[i] = {k: mean([s[k] for s in ss]) for k in ("u", "r", "k", "kref", "x", "ma", "mr", "z")}
        out[i]["wtl"] = collections.Counter(s["wtl"] for s in ss)
    return out
def ratio(P, S, w1=False, key="u"):
    S = [i for i in S if i in P]; num = sum((1 if w1 else W[i]) * P[i][key] for i in S); den = sum((1 if w1 else W[i]) * P[i]["r"] for i in S)
    return num / den if den else None
def metrics(G):
    P = per_item(G)
    S42 = G.get(42, {})
    C = [i for i in H if i in S42 and all(S42[i]["keptTurns"] or [S42[i]["kept"]])]
    N = [i for i in H if i in S42 and not any(S42[i]["keptTurns"] or [S42[i]["kept"]])]
    M = [i for i in H if i in S42 and i not in C and i not in N]
    den = sum(W[i] * P[i]["r"] for i in H if i in P)
    ans = [i for i in H if i in P and P[i]["z"] < 1]
    wtl = collections.Counter(); [wtl.update(P[i]["wtl"]) for i in H if i in P]
    fam = collections.defaultdict(list); [fam[Q[i]["family"]].append(i) for i in H]
    return dict(n_items=len([i for i in H if i in P]), gens=sorted(G), U_total=ratio(P, H), U_total_w1=ratio(P, H, True), U_H_anchors=ratio(P, IDS), U_anchors=ratio(P, ANCH),
                U_without_location=ratio(P, [i for i in H if i not in LOC]), coverage=dict(c=len(C) / len(H), C=len(C), N=len(N), M=len(M),
                c_w=sum(W[i] for i in C) / sum(W[i] for i in H)),
                U_decomp_numerator=dict(C=sum(W[i] * P[i]["u"] for i in C) / den, N=sum(W[i] * P[i]["u"] for i in N) / den, M=sum(W[i] * P[i]["u"] for i in M) / den),
                U_ref=ratio(P, C), U_noref=ratio(P, N), CR=sum(W[i] * P[i]["k"] for i in H if i in P) / max(1e-9, sum(W[i] * P[i]["kref"] for i in H if i in P)),
                correct_per_100=100 * mean([P[i]["k"] for i in H if i in P]), CE_answered=sum(P[i]["x"] for i in ans) / max(1, len(ans)), CE_over_H=mean([P[i]["x"] for i in H if i in P]),
                answered=len(ans), refusal_rate=mean([P[i]["z"] for i in H if i in P]), abs_mean_app=sum(W[i] * P[i]["ma"] for i in H if i in P) / sum(W[i] for i in H if i in P),
                abs_mean_ref=sum(W[i] * P[i]["mr"] for i in H if i in P) / sum(W[i] for i in H if i in P), mean_ref_mass=den / sum(W[i] for i in H if i in P),
                items_r0=sum(P[i]["r"] == 0 for i in H if i in P), wtl={k: round(v, 1) for k, v in wtl.items()},
                per_family={f: dict(n=len(v), U=ratio(P, v)) for f, v in sorted(fam.items())}), P
def ci(f, B=2000):
    rnd = random.Random(11); vals = []
    for _ in range(B):
        items = [rnd.choice(IDS) for _ in IDS]; v = f(items, rnd)
        if v is not None: vals.append(v)
    vals.sort(); return [round(vals[int(.025 * len(vals))], 3), round(vals[int(.975 * len(vals)) - 1], 3)]
def boot_ratio(G, sub, w1=False):
    def f(items, rnd):
        P = per_item(G, rnd); its = [i for i in items if i in sub and i in P]
        num = sum((1 if w1 else W[i]) * P[i]["u"] for i in its); den = sum((1 if w1 else W[i]) * P[i]["r"] for i in its)
        return num / den if den else None
    return ci(f)
res = {}; GS = {}
for arm in ("native", "engine"):
    G = load(arm)
    if not G: continue
    GS[arm] = G; m, P = metrics(G)
    m["CI_U_total"] = boot_ratio(G, set(H)); m["CI_U_total_w1"] = boot_ratio(G, set(H), True); m["CI_U_H_anchors"] = boot_ratio(G, set(IDS))
    res[arm] = m
if len(GS) == 2:
    def paired(items, rnd):
        PN, PE = per_item(GS["native"], rnd), per_item(GS["engine"], rnd)
        its = [i for i in items if i in H and i in PN and i in PE]
        den = sum(W[i] * (PN[i]["r"] + PE[i]["r"]) / 2 for i in its)
        return sum(W[i] * (PN[i]["u"] - PE[i]["u"]) for i in its) / den if den else None
    PN, PE = per_item(GS["native"]), per_item(GS["engine"])
    res["paired_native_minus_engine"] = dict(delta=paired([i for i in IDS], None), ci=ci(paired),
                                             better=sum(PN[i]["u"] > PE[i]["u"] for i in H if i in PN and i in PE), worse=sum(PN[i]["u"] < PE[i]["u"] for i in H if i in PN and i in PE))
res["notes"] = "Claude half only (F1 refs, G1 Opus); stage 1 not run (judge.v1 + z); no errata (contested-point pass needs the Codex refs); one judge pass; H = 71, w health 0.5"
json.dump(res, open(A + "/aggregates/r3.json", "w"), indent=1, default=str)
for arm in ("native", "engine"):
    if arm in res:
        m = res[arm]; print(f"{arm}: gens {m['gens']} n {m['n_items']} U_total {m['U_total']:.3f} {m['CI_U_total']} w1 {m['U_total_w1']:.3f} H+anch {m['U_H_anchors']:.3f} cov {m['coverage']['c']:.2f} "
                            f"U_ref {m['U_ref']} U_noref {m['U_noref']} CR {m['CR']:.3f} CE_ans {m['CE_answered']:.3f} CE_H {m['CE_over_H']:.3f} refusal {m['refusal_rate']:.3f} wtl {m['wtl']} no-loc {m['U_without_location']:.3f}")
if "paired_native_minus_engine" in res: print("paired", res["paired_native_minus_engine"])
