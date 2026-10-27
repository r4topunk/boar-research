#!/usr/bin/env python3
"""RULER-FINAL aggregate (0 LLM): BoarLite b4ef94f3 on v0.4, ONE seed (42), two judge families: G1 = Opus judge.v1 vs the Claude refs (b27eac37),
G2 = Codex judge.v1-codex vs the Codex refs (047cb199). Spec RULER-SPEC-v1-r4 section 3 with one reference family per judge family (the card's
"one reference family" rows): u = 0 if z else m(app) - 1, r = m(ref) - 1 from the same pairing, m = mean of the 3 rubric scores averaged over both orders.
U_total over H (71, health weight 0.5); weight 1; H u anchors; win-rate (combineOrders: agreement = verdict, else tie; z = loss) W/|H| and (W + T/2)/|H|;
correct-rate ratio; CE; refusals (fixed text); AVAILABLE / PARTIAL / NONE split (FACT-AVAIL primary label, A-union packs, all installed in this kit;
ids only are read); min over families computed per bootstrap draw. Paired vs the 10-24 afternoon NATIVE-RC f1023b93 seed 42 (G1 only: f1023b93 has no
Codex judgments), common denominator. CI: B 2000, seed 11, items resampled, and the two orders within each item.
usage: python3 -I rf_agg.py -> aggregates/rf.json + table"""
import json, os, random, collections
A = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); V = A + "/work/v04"; RU = os.path.dirname(os.path.dirname(A)) + "/ruler"
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
J = A + "/judge/rf"; TR = V + "/traces/lite-s42.traces.jsonl"
FAM = {}
if os.path.exists(f"{J}/lite-s42.opus.judgments.jsonl"): FAM["G1 Claude (Opus vs Claude refs)"] = load(f"{J}/lite-s42.opus.judgments.jsonl", TR)
if os.path.exists(f"{J}/lite-s42.codex.judgments.jsonl"): FAM["G2 Codex (gpt-5.6-sol vs Codex refs)"] = load(f"{J}/lite-s42.codex.judgments.jsonl", TR)
res = dict(families={}); Hs = set(H)
for k, G in FAM.items():
    m, P = metrics(G); m["CI_U_total"] = boot(lambda its, rnd: ratio_draw(G, its, rnd, Hs)); m["CI_U_total_w1"] = boot(lambda its, rnd: (lambda P2: U(P2, [i for i in its if i in Hs], True))({i: st(G[i], rnd) for i in set(its) if i in G}))
    m["complete"] = len(G) == len(IDS); res["families"][k] = m
if len(FAM) == 2:
    g1, g2 = list(FAM.values())
    res["min_over_families"] = dict(point=min(v["U_total"] for v in res["families"].values()),
                                    ci=boot(lambda its, rnd: min(ratio_draw(g1, its, rnd, Hs) or 0, ratio_draw(g2, its, rnd, Hs) or 0)))
# paired vs NATIVE-RC f1023b93 seed 42, G1
NF = A + "/judge/r3/native-s42.opus.judgments.jsonl"
if FAM and os.path.exists(NF):
    GN = load(NF, V + "/traces/native-s42.traces.jsonl"); GL = FAM["G1 Claude (Opus vs Claude refs)"]
    def pd(its, rnd):
        num = den = 0.0
        for i in its:
            if i in Hs and i in GN and i in GL:
                a, b = st(GL[i], rnd), st(GN[i], rnd); num += W[i] * (a["u"] - b["u"]); den += W[i] * (a["r"] + b["r"]) / 2
        return num / den if den else None
    PN = {i: st(e) for i, e in GN.items()}; PL = {i: st(e) for i, e in GL.items()}
    res["paired_vs_f1023b93_s42_G1"] = dict(f1023b93_U_s42=U(PN, H), lite_U=U(PL, H), delta=pd(IDS, None), ci=boot(pd),
                                           better=sum(PL[i]["u"] > PN[i]["u"] for i in H if i in PL and i in PN), worse=sum(PL[i]["u"] < PN[i]["u"] for i in H if i in PL and i in PN))
res["notes"] = "ONE seed (42, addendum); one reference family per judge family; stage 1 not run; no errata; desktop twin (harness-lite conv, port nh), not the APK"
json.dump(res, open(A + "/aggregates/rf.json", "w"), indent=1)
for k, m in res["families"].items():
    print(f"{k}: n {m['n']} U {m['U_total']:.3f} {m['CI_U_total']} w1 {m['U_total_w1']:.3f} H+a {m['U_H_anchors']:.3f} win {m['win_rate']:.3f} (W+T/2 {m['win_tie_rate']:.3f}) wtl {m['wtl']} "
          f"CR {m['CR']:.3f} CE {m['CE_answered']:.3f} refusals {m['refusals_items_H']} cov {m['coverage']:.2f} abs {m['abs_app']:.2f}/{m['abs_ref']:.2f} FA {{{', '.join(f'{a}: n{b['n']} {b['U']:.3f}' for a, b in m['factavail'].items() if b['U'] is not None)}}} complete {m['complete']}")
for k in ("min_over_families", "paired_vs_f1023b93_s42_G1"):
    if k in res: print(k, res[k])
