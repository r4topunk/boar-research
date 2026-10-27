#!/usr/bin/env python3
"""X2B-RETEST report (0 LLM): default-mode metrics per arm vs the ON control, per X2B-RETEST-criterion.md. Writes aggregates/x2b-retest.json."""
import json, random, statistics as st, sys
A = "<workspace>/rnd/research/coordinator/arms"; X = A + "/x2b-retest"
sys.path.insert(0, A + "/null-cal/tools"); from labels import label
ids = open("<workspace>/rnd/research/coordinator/ruler/ids/stage1-pool.ids").read().split()
rd = lambda f: {json.loads(l)["itemId"]: json.loads(l) for l in open(f) if l.strip()}
CT = {**rd(A + "/lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl"), **rd(A + "/null-cal/control/traces/poolctl-K1-st180-s42.traces.jsonl")}
CA = json.load(open(A + "/null-cal/control/pool-K1.json"))["items"]
kept = lambda t: [(c.get("title"), c.get("section")) for c in (t.get("retrieval") or {}).get("kept", [])]
ctx = lambda t: (kept(t), t["timing"].get("promptTokens"))  # context proxy: kept sources + prompt tokens
cov = {i for i in ids if kept(CT[i])}
REAL = [i for i in ids if not i.startswith("st-")]; STI = [i for i in ids if i.startswith("st-")]
def U(xs, L): return sum(0 if L[i]["R"] else L[i]["s"] for i in xs) / sum(L[i]["sref"] for i in xs)
def boot(xs, LA, LC):
    r = random.Random(11); d = []
    for _ in range(2000):
        s = [r.choice(xs) for _ in xs]; d.append(U(s, LA) - U(s, LC))
    d.sort(); return [round(d[49], 4), round(d[1949], 4)]
LC = {i: label(CA[i]) for i in ids}
out = {"criterion_sha": open(X + "/X2B-RETEST-criterion.sha256").read().split()[0], "covered_on": len(cov), "arms": {}}
def summ(L, xs, T):
    pt = [T[i]["timing"].get("promptTokens") or 0 for i in xs]; rw = [T[i]["timing"].get("retrievalMs") or 0 for i in xs]
    return dict(n=len(xs), U_d=round(U(xs, L), 4), CEu=sum(L[i]["CEu"] for i in xs), R=sum(L[i]["R"] for i in xs),
                pt_mean=round(st.mean([p for p in pt if p > 0] or [0]), 1), ret_ms_mean=round(st.mean(rw), 1), ret_ms_p50=round(st.median(rw), 1))
out["arms"]["ON"] = {k: summ(LC, xs, CT) for k, xs in (("REAL", REAL), ("ST", STI), ("POOL", ids))}
for arm, name in (("x2boff", "OFF"), ("x2bv1orc", "V1orC")):
    T = rd(f"{X}/{arm}/traces/{arm}-K1-stage1-pool-s42.traces.jsonl")
    AG = json.load(open(f"{X}/{arm}/aggregates/{arm}-K1-stage1-pool-s42.json"))["items"]
    have = [i for i in ids if i in AG]; LA = {i: label(AG[i]) for i in have}
    r = {"missing": [i for i in ids if i not in AG], "errors": sum(bool(T[i].get("error")) for i in ids),
         "changed_answers": sum(T[i]["answer"]["text"] != CA[i]["text"] for i in ids),
         "changed_contexts": sum(ctx(T[i]) != ctx(CT[i]) for i in ids),
         "headpass_add_items": sum(any(c.startswith("headpass:add") for c in T[i]["route"].get("reasonCodes", [])) for i in ids),
         "retfloor_items": sum(any(c.startswith("retfloor:") for c in T[i]["route"].get("reasonCodes", [])) for i in ids)}
    for k, xs in (("REAL", REAL), ("ST", STI), ("POOL", ids), ("COV_REAL", [i for i in REAL if i in cov]), ("COV_POOL", [i for i in ids if i in cov])):
        xs = [i for i in xs if i in LA]
        a, c = summ(LA, xs, T), summ(LC, xs, CT)
        both = [i for i in xs if (T[i]["timing"].get("promptTokens") or 0) > 0 and (CT[i]["timing"].get("promptTokens") or 0) > 0]
        ptA = st.mean([T[i]["timing"]["promptTokens"] for i in both]) if both else 0; ptC = st.mean([CT[i]["timing"]["promptTokens"] for i in both]) if both else 0
        r[k] = dict(arm=a, on=c, dU=round(a["U_d"] - c["U_d"], 4), ci=boot(xs, LA, LC), dCEu=a["CEu"] - c["CEu"], dR=a["R"] - c["R"],
                    pt_live=[round(ptC, 1), round(ptA, 1), round((ptA - ptC) / ptC * 100, 1) if ptC else None], n_live=len(both))
    out["arms"][name] = r
json.dump(out, open(X + "/aggregates/x2b-retest.json", "w"), indent=1)
for name in ("OFF", "V1orC"):
    r = out["arms"][name]; print(f"== {name}: changed ans {r['changed_answers']} ctx {r['changed_contexts']} | headpass:add items {r['headpass_add_items']} retfloor items {r['retfloor_items']} | errors {r['errors']} missing {len(r['missing'])}")
    for k in ("REAL", "ST", "POOL", "COV_REAL", "COV_POOL"):
        x = r[k]; print(f"  {k:8s} n {x['arm']['n']:3d} U_d ON {x['on']['U_d']:.4f} arm {x['arm']['U_d']:.4f} d {x['dU']:+.4f} {x['ci']} | CEu {x['on']['CEu']}->{x['arm']['CEu']} R {x['on']['R']}->{x['arm']['R']} | ptok live {x['pt_live']} (n {x['n_live']}) | ret ms mean {x['on']['ret_ms_mean']}->{x['arm']['ret_ms_mean']} p50 {x['on']['ret_ms_p50']}->{x['arm']['ret_ms_p50']}")
