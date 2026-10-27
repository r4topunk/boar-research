#!/usr/bin/env python3
"""HYBRID-READER (0 calls). Criterion HYBRID-criterion.md (sha 87060c26...). python3 -I hybrid.py <out.json>"""
import json, sys, random, collections
A = "<workspace>/rnd/research/coordinator/arms"; C = A.rsplit("/", 1)[0]
sys.path.insert(0, A + "/null-cal/tools"); from labels import label
sys.path.insert(0, C + "/ruler/tools"); import cv5_opus_pool as CP
K3 = ("correctness", "completeness", "usefulness")
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
rd = lambda f: {(t := json.loads(l))["itemId"]: t for l in open(f) if l.strip()}
def jr(p):
    J = collections.defaultdict(dict)
    for l in open(p):
        r = json.loads(l)
        if r.get("ok"): J[r["queryId"]][r["order"]] = r["mapped"]
    return {q: sum(v[o]["boar"][k] for o in v for k in K3) / sum(v[o]["ref"][k] for o in v for k in K3) for q, v in J.items() if set(v) == {"boarA", "boarB"}}
def feats(t):
    rel = []
    for e in t["events"]:
        if e.get("type") == "sources": rel = [s["relevance"] for s in e["sources"] if s.get("relevance") is not None]
    return dict(kept_n=len(t["retrieval"]["kept"]), maxrel=max(rel) if rel else 0.0)
AS = range(1, 9); BS = [0, 0.25, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9, 1.0]
rule = lambda f, a, b: f["kept_n"] >= a and f["maxrel"] >= b - 1e-9
# ---- fit on the 180
q17, b4, tr, tq = {}, {}, {}, {}
for p in PACKS:
    q17.update(jr(f"{A}/lite5/runs/180/lite5-180-on-{p}-s42.judgments.haiku55-low.jsonl"))
    b4.update(jr(f"{A}/headpass-st/gen-x2b/st-{p}-cut7-headpassx2b-s42.judgments.jsonl"))
    tr.update(rd(f"{A}/headpass-st/gen-x2b/st-{p}-cut7-headpassx2b-s42.traces.jsonl"))
    tq.update(rd(f"{A}/lite5/runs/180/lite5-180-on-{p}-s42.traces.jsonl"))
sid = sorted(q17); assert len(sid) == 180 and set(sid) == set(b4) == set(tr)
assert all(feats(tr[i]) == feats(tq[i]) for i in sid)
F180 = {i: feats(tr[i]) for i in sid}
m17 = sum(q17[i] for i in sid) / 180; m4 = sum(b4[i] for i in sid) / 180
grid180 = []
for a in AS:
    for b in BS:
        r = [i for i in sid if rule(F180[i], a, b)]
        hyb = sum(b4[i] if i in r else q17[i] for i in sid) / 180
        grid180.append(dict(a=a, b=b, share=round(len(r) / 180, 4), gain=round(hyb - m17, 4)))
ok = [g for g in grid180 if g["share"] <= 0.35]
P1 = sorted(ok, key=lambda g: (-g["gain"], g["share"], -g["a"], -g["b"]))[0]
# ---- MAIN 97
ids = sorted(x for x in open(f"{A}/lp-screens/main-97.ids").read().split() if x)
TQ = rd(f"{A}/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl"); TB = rd(f"{A}/gemma4-e2b/vs4b/traces/gemma4-e2b-vs4b-K0-main-s42.traces.jsonl")
assert all([k["title"] for k in TQ[i]["retrieval"]["kept"]] == [k["title"] for k in TB[i]["retrieval"]["kept"]] for i in ids)
FM = {i: feats(TQ[i]) for i in ids}
H = {"q": json.load(open(f"{A}/lp-screens/control/aggregates/lpctl-K0-main-s42.json"))["items"],
     "b": json.load(open(f"{A}/gemma4-e2b/vs4b/aggregates/gemma4-e2b-vs4b-K0-main-s42.json"))["items"]}
S = json.load(open(C + "/ruler/gemma-opus-main/in/set.json")); POOL = {}
for u, (fr, fq) in S["frames"].items(): POOL.update(CP.pool(fr, fq))
O = {}
for k, T in (("q", TQ), ("b", TB)):
    O[k] = {}
    for i in ids:
        t = T[i]["answer"]; key = CP.key(i, t["text"])
        if key in POOL:
            ms = [POOL[key]["boarA"], POOL[key]["boarB"]]; mean = lambda x: sum(x.values()) / 3
            O[k][i] = dict(s=sum(mean(m["boar"]) for m in ms) / 2, sref=sum(mean(m["ref"]) for m in ms) / 2,
                           corr=sum(m["boar"]["correctness"] for m in ms) / 2, text=t["text"], declined=bool(t.get("declined")))
B = 2000
def mk(J, routed, xs): return {i: J["b" if i in routed else "q"][i] for i in xs}
def U(rows, xs): return sum(0 if rows[i]["declined"] else rows[i]["s"] for i in xs) / sum(rows[i]["sref"] for i in xs)
def ci(f, pool):
    rnd = random.Random(11); b = sorted(f([rnd.choice(pool) for _ in pool]) for _ in range(B)); return [round(b[50], 4), round(b[1949], 4)]
def evaluate(J, routed, xs):
    hy, q, b = mk(J, routed, xs), {i: J["q"][i] for i in xs}, {i: J["b"][i] for i in xs}
    f = lambda s: U(hy, s) - U(q, s); g = lambda s: U(b, s) - U(q, s)
    rnd = random.Random(11); caps = []; le0 = 0
    for _ in range(B):
        s = [rnd.choice(xs) for _ in xs]; d = g(s)
        if d <= 0: le0 += 1; continue
        caps.append(f(s) / d)
    caps.sort(); n = len(caps)
    ceu = lambda rows: sum(label(rows[i])["CEu"] for i in xs)
    sh = sum(i in routed for i in xs) / len(xs)
    return dict(n=len(xs), routed=sum(i in routed for i in xs), share=round(sh, 4), U_17=round(U(q, xs), 4), U_hyb=round(U(hy, xs), 4), U_4B=round(U(b, xs), 4),
                dU=round(f(xs), 4), dU_ci=ci(f, xs), dU_all4B=round(g(xs), 4), dU_all4B_ci=ci(g, xs),
                captured=round(f(xs) / g(xs), 3) if g(xs) > 0 else None, captured_ci=[round(caps[int(.025 * n)], 3), round(caps[int(.975 * n) - 1], 3)] if n > 40 else None, cap_den_le0=le0,
                CEu=dict(q17=ceu(q), hyb=ceu(hy), b4=ceu(b)),
                p50_proj_19_4=round(sh * 19.4 + (1 - sh) * 4.2, 2), p50_proj_25=round(sh * 25 + (1 - sh) * 4.2, 2))
def routed_by(a, b): return {i for i in ids if rule(FM[i], a, b)}
def both_cov(): return [i for i in ids if i in O["q"] and i in O["b"]]
res = dict(criterion_sha256=open(A + "/hybrid-reader/HYBRID-criterion.sha256").read().split()[0],
           fit180=dict(mean_17=round(m17, 4), mean_4B=round(m4, 4), P1=P1, grid=grid180),
           main_features=dict(kept_n=dict(collections.Counter(FM[i]["kept_n"] for i in ids)), opus_cov=dict(q17=len(O["q"]), b4=len(O["b"]), both=len(both_cov()))))
r1 = routed_by(P1["a"], P1["b"]); res["P1"] = dict(rule=P1, haiku=evaluate(H, r1, ids), opus_both=evaluate(O, r1, both_cov()), routed_ids=sorted(r1))
p2a = P1["a"] if 0 < len(r1) <= 0.35 * 97 else next((a for a in AS if 0 < len(routed_by(a, P1["b"])) <= 0.35 * 97), None)
if p2a is not None:
    r2 = routed_by(p2a, P1["b"]); res["P2"] = dict(a=p2a, b=P1["b"], haiku=evaluate(H, r2, ids), opus_both=evaluate(O, r2, both_cov()), routed_ids=sorted(r2))
res["grid_main_report_only"] = [dict(a=a, b=b, **{k: v for k, v in evaluate(H, routed_by(a, b), ids).items() if k in ("routed", "share", "dU", "dU_ci", "captured", "p50_proj_19_4")})
                                for a in range(1, 5) for b in BS if routed_by(a, b)]
gain = sorted(ids, key=lambda i: -((0 if H["b"][i]["declined"] else H["b"][i]["s"]) - (0 if H["q"][i]["declined"] else H["q"][i]["s"])))
ro = set(gain[:int(0.35 * 97)]); ro = {i for i in ro if (0 if H["b"][i]["declined"] else H["b"][i]["s"]) > (0 if H["q"][i]["declined"] else H["q"][i]["s"])}
res["oracle_main_share_le_0_35"] = {k: v for k, v in evaluate(H, ro, ids).items() if k in ("routed", "share", "dU", "dU_ci", "captured")}
ro2 = set(gain[:int(0.276 * 97)]); ro2 = {i for i in ro2 if i in ro}
res["oracle_main_share_le_0_276"] = {k: v for k, v in evaluate(H, ro2, ids).items() if k in ("routed", "share", "dU", "dU_ci", "captured")}
# per-stage
FUN = json.load(open(C + "/ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
ps = collections.defaultdict(lambda: collections.Counter()); pg = collections.defaultdict(list)
for i in ids:
    st = FUN[i]["K0"]["stage"] if i in FUN else "unkeyed"; st3 = FUN[i]["K3"]["stage"] if i in FUN else "unkeyed"
    for rs, lab in ((r1, "P1"), (res.get("P2", {}).get("routed_ids", []), "P2")):
        ps[f"{lab}:K0:{st}"]["routed" if i in rs else "not"] += 1
        ps[f"{lab}:K3:{st3}"]["routed" if i in rs else "not"] += 1
    d = (0 if H["b"][i]["declined"] else H["b"][i]["s"]) - (0 if H["q"][i]["declined"] else H["q"][i]["s"])
    pg[f"K0:{st}"].append(d); pg[f"kept_n:{FM[i]['kept_n']}"].append(d)
res["per_stage_counts"] = {k: dict(v) for k, v in sorted(ps.items())}
res["per_stage_mean_s_gain_4B_minus_17"] = {k: dict(n=len(v), mean=round(sum(v) / len(v), 3)) for k, v in sorted(pg.items())}
P = res["P1"]["haiku"]
res["verdict"] = "PASS" if (P["dU"] >= 0.03 and P["dU_ci"][0] > 0 and P["share"] <= 0.35 and P["p50_proj_19_4"] <= 8.4) else \
    ("KILL (P2 LEAD)" if "P2" in res and res["P2"]["haiku"]["dU"] >= 0.03 and res["P2"]["haiku"]["dU_ci"][0] > 0 and res["P2"]["haiku"]["share"] <= 0.35 else "KILL")
json.dump(res, open(sys.argv[1], "w"), indent=1)
print(json.dumps({k: res[k] for k in ("verdict", "P1", "P2") if k in res}, indent=1)[:6000])
print(json.dumps(res["fit180"]["P1"]), res["main_features"], res["oracle_main_share_le_0_35"], res["oracle_main_share_le_0_276"])
