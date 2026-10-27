#!/usr/bin/env python3
"""STYLE-SEFIX aggregate (0 LLM): S = SEFIX-124 Succinct s42 (cached rows), D = SEFIX-124 Detailed s42 (cache + judge/*.judgments.jsonl). python3 -I tools/agg.py -> aggregates/style-sefix.json"""
import sys, json, random, statistics; sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/style-sefix/tools")
from common import *
cache = build_cache()
TS = ld(SF + "/ans-traces/sefix124-main-s42.traces.jsonl"); TD = ld(D + "/traces/style-sefix-D-s42.traces.jsonl")
NJ = jby(D + "/judge"); newn = 0
for i, by in NJ.items():
    if len(by) == 2:
        t = TD[i]["answer"]; row = jrow(NJ, i); row.update(declined=bool(t.get("declined")), warned=t["text"].startswith(W)); cache[(i, t["text"])] = row; newn += 1
def rows(T):
    R = {}
    for i in ids:
        t = T[i]["answer"]; c = cache[(i, t["text"])]
        R[i] = dict(c, declined=bool(t.get("declined")), warned=t["text"].startswith(W)); R[i]["CE"] = (not R[i]["declined"]) and R[i]["corr"] <= 1.5
    return R
S, Dr = rows(TS), rows(TD)
# cross-check S against answers-sefix124.json (s42 X rows)
X124 = json.load(open(SF + "/answers-sefix124.json"))["items"]["42"]
mism = [i for i in ids if any(abs((S[i][k] or 0) - (X124[i]["X"][k] or 0)) > 1e-9 for k in ("s", "sref", "corr"))]
CL = json.load(open(SF + "/chunklevel-124.json"))  # deviation: chunklevel.json has no "sefix F1F2F4" key; chunklevel-124.json is its superset (logged before judging)
CL = CL["per_item"]["sefix F1F2F4"]
dl = [i for i in ids if CL.get(i) and CL[i]["chunk"]]; nd = [i for i in ids if CL.get(i) and not CL[i]["chunk"]]
health = [i for i in ids if "-hlt-" in i or i.startswith("dng-")]
U = lambda R, xs: sum(0 if R[i]["declined"] else R[i]["s"] for i in xs) / sum(R[i]["sref"] for i in xs)
def boot(f, xs, B=2000):
    r = random.Random(11); v = sorted(f([r.choice(xs) for _ in xs]) for _ in range(B)); return [round(v[int(.025 * B)], 4), round(v[int(.975 * B) - 1], 4)]
p50 = lambda T, xs, k: statistics.median(T[i]["timing"].get(k) or 0 for i in xs)
def summ(R, T, xs):
    n = len(xs); ce = [i for i in xs if R[i]["CE"]]
    return dict(n=n, U=round(U(R, xs), 4), corr=round(sum(R[i]["corr"] for i in xs) / n, 3), CE=len(ce), CE_per100=round(100 * len(ce) / n, 1), CE_unwarned=sum(not R[i]["warned"] for i in ce),
                CE_unwarned_per100=round(100 * sum(not R[i]["warned"] for i in ce) / n, 1), warned=sum(R[i]["warned"] for i in xs), declined=sum(R[i]["declined"] for i in xs),
                out_tok_p50=p50(T, xs, "outputTokens"), ms_p50=p50(T, xs, "totalMs"))
def pair(xs):
    f = lambda s: U(Dr, s) - U(S, s)
    return dict(n=len(xs), dU=round(f(xs), 4), ci=boot(f, xs), better=sum(Dr[i]["s"] > S[i]["s"] for i in xs), tie=sum(Dr[i]["s"] == S[i]["s"] for i in xs), worse=sum(Dr[i]["s"] < S[i]["s"] for i in xs),
                dcorr=round(sum(Dr[i]["corr"] - S[i]["corr"] for i in xs) / len(xs), 3))
out = dict(criterion_sha=open(D + "/STYLE-SEFIX-criterion.sha256").read().split()[0], new_judged_ids=newn, S_rows_mismatch_vs_answers_sefix124=mism,
           text_identical=[i for i in ids if TS[i]["answer"]["text"] == TD[i]["answer"]["text"]],
           persona_sha_D=sorted({TD[i]["runtime"]["versions"].get("persona", "?") + ":" + TD[i]["runtime"]["versions"].get("persona.sha256", "?")[:8] for i in ids}),
           persona_sha_S=sorted({TS[i]["runtime"]["versions"].get("persona", "?") + ":" + TS[i]["runtime"]["versions"].get("persona.sha256", "?")[:8] for i in ids}),
           D_at_cap=sum((TD[i]["timing"].get("outputTokens") or 0) >= 1024 for i in ids), errors_D=sum(bool(TD[i].get("error")) for i in ids))
for nm, xs in (("overall", ids), ("delivered", dl), ("not_delivered", nd), ("health", health)):
    out[nm] = dict(S=summ(S, TS, xs), D=summ(Dr, TD, xs), paired=pair(xs))
f = lambda s: (U(Dr, [i for i in s if i in set(dl)]) - U(S, [i for i in s if i in set(dl)])) - (U(Dr, [i for i in s if i in set(nd)]) - U(S, [i for i in s if i in set(nd)]))
r = random.Random(11); v = []
for _ in range(2000):
    a = [r.choice(dl) for _ in dl]; b = [r.choice(nd) for _ in nd]; v.append((U(Dr, a) - U(S, a)) - (U(Dr, b) - U(S, b)))
v.sort(); out["interaction_dl_minus_nd"] = dict(d=round(out["delivered"]["paired"]["dU"] - out["not_delivered"]["paired"]["dU"], 4), ci=[round(v[50], 4), round(v[1949], 4)])
out["health_worse"] = [i for i in health if Dr[i]["s"] < S[i]["s"]]; out["health_worse_delivered"] = [i for i in out["health_worse"] if i in dl]
o, d_, n_ = out["overall"], out["delivered"], out["not_delivered"]
out["predictions"] = dict(P1=dict(pred="overall dU < 0, ~-0.04..-0.10", hit=o["paired"]["dU"] < 0, band=-0.10 <= o["paired"]["dU"] <= -0.04),
    P2=dict(pred="dU delivered > dU not delivered and <= 0", shrinks=d_["paired"]["dU"] > n_["paired"]["dU"], le0=d_["paired"]["dU"] <= 0),
    P3=dict(pred="CE/100 D > S in both splits", delivered=d_["D"]["CE_per100"] > d_["S"]["CE_per100"], not_delivered=n_["D"]["CE_per100"] > n_["S"]["CE_per100"]),
    P4=dict(pred="tok p50 >= 5x, ms p50 >= 2.5x", tok_ratio=round(o["D"]["out_tok_p50"] / max(1, o["S"]["out_tok_p50"]), 2), ms_ratio=round(o["D"]["ms_p50"] / max(1, o["S"]["ms_p50"]), 2)))
out["rule"] = dict(default_change=o["paired"]["dU"] >= 0 and o["D"]["CE_per100"] <= o["S"]["CE_per100"] and not out["health_worse"],
                   conditional_detailed_when_delivered=d_["paired"]["dU"] >= 0 and d_["paired"]["ci"][0] > -0.03 and d_["D"]["CE_per100"] <= d_["S"]["CE_per100"] and not out["health_worse_delivered"])
same = set(out["text_identical"])   # secondary, not in the criterion: text-differs items only (identical texts are forced ties)
out["secondary_text_differs"] = {nm: pair([i for i in xs if i not in same]) for nm, xs in (("overall", ids), ("delivered", dl), ("not_delivered", nd))}
out["secondary_text_differs_CE"] = {nm: dict(S=sum(S[i]["CE"] for i in xs if i not in same), D=sum(Dr[i]["CE"] for i in xs if i not in same)) for nm, xs in (("overall", ids), ("delivered", dl), ("not_delivered", nd))}
out["items"] = {i: dict(delivered=i in dl, keyed=i in dl or i in nd, S={k: S[i][k] for k in KEYS + ("CE",)}, D={k: Dr[i][k] for k in KEYS + ("CE",)}, tokS=TS[i]["timing"].get("outputTokens"), tokD=TD[i]["timing"].get("outputTokens")) for i in ids}
json.dump(out, open(D + "/aggregates/style-sefix.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "items"}, indent=1))
