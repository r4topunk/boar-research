#!/usr/bin/env python3
"""DEVICE-FINAL M1 aggregate (0 LLM): LabRat 7788924a on the Pixel 8a, ruler v0.4, seeds 42/43/44 (whatever is judged), two judge families as RULER-FINAL
(native-rc/tools/rf_agg.py metric code reused verbatim: U-total H with health weight 0.5, win-rate, CR, CE, refusals, FACT-AVAIL split, bootstrap B 2000 seed 11).
Adds: pooled seeds (per item, both orders of every judged seed), min over families per draw, paired phone - desktop twin (RULER-FINAL b4ef94f3 s42) per family.
usage: python3 -I m1_agg.py -> aggregates/m1.json + table"""

import json, os, random, collections
DF = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = os.path.dirname(DF) + "/native-rc"; V = A + "/work/v04"; RU = os.path.dirname(os.path.dirname(A)) + "/ruler"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
Q = {r["id"]: r for r in rd(V + "/bench/questions.jsonl")}; IDS = list(Q)
H = [i for i in IDS if not Q[i]["anchor"]]; W = {i: Q[i]["weight"] for i in IDS}
FA = {i: v["label"] for i, v in json.load(open(RU + "/factavail/out/factavail-items.json"))["items"].items()}
mean = lambda xs: sum(xs) / len(xs)
def load(jf, tf):
    T = {t["itemId"]: t for t in rd(tf)}; per = collections.defaultdict(dict)
    for r in rd(jf):
        if r.get("ok"): per[r["queryId"]][r["order"]] = r["mapped"]
    out = {}
    for i in IDS:
        if len(per.get(i, {})) < 2: continue
        os_ = [dict(ma=mean([m["boar"][k] for k in ("correctness", "completeness", "usefulness")]), mr=mean([m["ref"][k] for k in ("correctness", "completeness", "usefulness")]),
                    ca=m["boar"]["correctness"], cr=m["ref"]["correctness"], win=m["winner"]) for m in per[i].values()]
        out[i] = dict(z=bool(T[i]["ruler"].get("refusedZ")), orders=os_, kept=T[i]["ruler"].get("kept"))
    return out
def st(e, rnd=None):
    os_ = [rnd.choice(e["orders"]) for _ in e["orders"]] if rnd else e["orders"]
    ma, mr, ca, cr = (mean([o[k] for o in os_]) for k in ("ma", "mr", "ca", "cr"))
    wins = {o["win"] for o in os_}
    wtl = "loss" if e["z"] else ({"boar": "win", "ref": "loss", "tie": "tie"}.get(next(iter(wins)), "tie") if len(wins) == 1 else "tie")
    return dict(u=0.0 if e["z"] else ma - 1, r=mr - 1, k=float(ca >= 4 and not e["z"]), kref=float(cr >= 4), x=float(not e["z"] and ca <= 1.5), wtl=wtl, z=e["z"], ma=ma - 1, mr=mr - 1)
def U(P, S, w1=False):
    S = [i for i in S if i in P]; d = sum((1 if w1 else W[i]) * P[i]["r"] for i in S)
    return sum((1 if w1 else W[i]) * P[i]["u"] for i in S) / d if d else None
def metrics(G):
    P = {i: st(e) for i, e in G.items()}; h = [i for i in H if i in P]
    wtl = collections.Counter(P[i]["wtl"] for i in h); ans = [i for i in h if not P[i]["z"]]
    strata = {lab: [i for i in h if FA.get(i) == lab] for lab in ("AVAILABLE", "PARTIAL", "NONE")}
    return dict(n=len(h), U_total=U(P, h), U_total_w1=U(P, h, True), U_H_anchors=U(P, [i for i in IDS if i in P]),
                win_rate=wtl["win"] / len(h), win_tie_rate=(wtl["win"] + wtl["tie"] / 2) / len(h), wtl=dict(wtl),
                CR=sum(W[i] * P[i]["k"] for i in h) / max(1e-9, sum(W[i] * P[i]["kref"] for i in h)), correct_per_100=100 * mean([P[i]["k"] for i in h]),
                CE_answered=sum(P[i]["x"] for i in ans) / max(1, len(ans)), CE_over_H=mean([P[i]["x"] for i in h]), refusals_items_H=sum(P[i]["z"] for i in h),
                coverage=mean([bool(G[i]["kept"]) for i in h]), abs_app=sum(W[i] * P[i]["ma"] for i in h) / sum(W[i] for i in h), abs_ref=sum(W[i] * P[i]["mr"] for i in h) / sum(W[i] for i in h),
                factavail={lab: dict(n=len(v), U=U(P, v)) for lab, v in strata.items()}), P
def boot(fn, B=2000):
    rnd = random.Random(11); vals = []
    for _ in range(B):
        its = [rnd.choice(IDS) for _ in IDS]; v = fn(its, rnd)
        if v is not None: vals.append(v)
    vals.sort(); return [round(vals[int(.025 * len(vals))], 3), round(vals[int(.975 * len(vals)) - 1], 3)]
def ratio_draw(G, its, rnd, sub):
    P = {}; num = den = 0.0
    for i in its:
        if i in sub and i in G: s = st(G[i], rnd); num += W[i] * s["u"]; den += W[i] * s["r"]
    return num / den if den else None

J = DF + "/judge"; FAMS = {"opus": "G1 Claude (Opus vs Claude refs)", "codex": "G2 Codex (gpt-5.6-sol vs Codex refs)"}
def ok(jf):
    return os.path.exists(jf) and sum(1 for r in rd(jf) if r.get("ok")) >= 2 * len(IDS)
res = dict(per_seed={}, pooled={}, paired_vs_desktop_s42={}); G = collections.defaultdict(dict)
for s in ("42", "43", "44"):
    for f, name in FAMS.items():
        jf = f"{J}/dev-s{s}.{f}.judgments.jsonl"
        if ok(jf):
            G[f][s] = load(jf, f"{DF}/traces/dev-s{s}.traces.jsonl"); m, P = metrics(G[f][s])
            m["CI_U_total"] = boot(lambda its, rnd, g=G[f][s]: ratio_draw(g, its, rnd, set(H))); res["per_seed"][f"{name} s{s}"] = m
def pool(seeds):
    out = {}
    for i in IDS:
        es = [seeds[s][i] for s in seeds if i in seeds[s]]
        if es: out[i] = dict(z=any(e["z"] for e in es) and all(e["z"] for e in es), orders=[o for e in es for o in e["orders"]], kept=all(e["kept"] for e in es))
    return out
PO = {}
for f, name in FAMS.items():
    if len(G[f]) >= 2:
        PO[f] = pool(G[f]); m, _ = metrics(PO[f]); m["CI_U_total"] = boot(lambda its, rnd, g=PO[f]: ratio_draw(g, its, rnd, set(H))); m["seeds"] = sorted(G[f])
        m["seed_mean_U"] = mean([res["per_seed"][f"{name} s{s}"]["U_total"] for s in G[f]]); res["pooled"][name] = m
if all(G[f].get("42") for f in FAMS):
    g1, g2 = G["opus"]["42"], G["codex"]["42"]
    res["min_over_families_s42"] = dict(point=min(res["per_seed"][f"{n} s42"]["U_total"] for n in FAMS.values()),
                                        ci=boot(lambda its, rnd: min(ratio_draw(g1, its, rnd, set(H)) or 0, ratio_draw(g2, its, rnd, set(H)) or 0)))
RF = A + "/judge/rf"; RT = V + "/traces/lite-s42.traces.jsonl"; Hs = set(H)
for f, name in FAMS.items():
    df = f"{RF}/lite-s42.{f}.judgments.jsonl"
    if G[f].get("42") and os.path.exists(df):
        GD = load(df, RT); GP = G[f]["42"]
        def pd(its, rnd, GD=GD, GP=GP):
            num = den = 0.0
            for i in its:
                if i in Hs and i in GD and i in GP:
                    a, b = st(GP[i], rnd), st(GD[i], rnd); num += W[i] * (a["u"] - b["u"]); den += W[i] * (a["r"] + b["r"]) / 2
            return num / den if den else None
        PD = {i: st(e) for i, e in GD.items()}; PP = {i: st(e) for i, e in GP.items()}
        res["paired_vs_desktop_s42"][name] = dict(desktop_U=U(PD, H), phone_U=U(PP, H), delta=pd(IDS, None), ci=boot(pd),
            better=sum(PP[i]["u"] > PD[i]["u"] for i in H if i in PP and i in PD), worse=sum(PP[i]["u"] < PD[i]["u"] for i in H if i in PP and i in PD))
res["notes"] = "phone = LabRat 7788924a APK path (device eval runner + follow-up history patch), Pixel 8a; desktop twin = RULER-FINAL b4ef94f3 harness-lite; engines differ by the Rat persona line; one reference family per judge family; stage 1 not run; no errata"
json.dump(res, open(DF + "/aggregates/m1.json", "w"), indent=1)
for k, m in list(res["per_seed"].items()) + [("POOLED " + k, v) for k, v in res["pooled"].items()]:
    print(f"{k}: n {m['n']} U {m['U_total']:.3f} {m['CI_U_total']} win {m['win_rate']:.3f} (W+T/2 {m['win_tie_rate']:.3f}) CR {m['CR']:.3f} CE {m['CE_answered']:.3f} refusals {m['refusals_items_H']} cov {m['coverage']:.2f} abs {m['abs_app']:.2f}/{m['abs_ref']:.2f}" + (f" seeds {m['seeds']} seed-mean {m['seed_mean_U']:.3f}" if 'seeds' in m else ""))
for k in ("min_over_families_s42", "paired_vs_desktop_s42"):
    if res.get(k): print(k, json.dumps(res[k]))
