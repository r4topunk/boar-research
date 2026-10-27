#!/usr/bin/env python3
"""CB17 per-item pack table (0 calls). python3 -I cb17_table.py  (criterion ../CB17-criterion.md)
Arms: CB = closed-book 1.7B (mini, arms/cb17), K0 / K1 = LP-SCREENS mini controls, K3 = LITEPACKS MacBook traces (K0-MacBook judgments reused on
byte-identical text, LITEPACKS rule). Haiku 5.5-low judge.v1-low rows for every arm; Opus judge.v1 rows (seed 7, frames of GEMMA-OPUS-MAIN) wherever the
identical (id, text) unit has them (ruler/tools/cv5_opus_pool.py). U = sum(s-1)/sum(r-1) (CV5), Q = sum s/sum r with declined := 0 (LITEPACKS).
Writes aggregates/pack_table_17b.{json,csv}."""
import json, sys, os, csv, hashlib, collections, numpy as np
R = "<workspace>/rnd/research/coordinator"; A = R + "/arms"; H = A + "/cb17"
sys.path.insert(0, R + "/ruler/tools"); import cv5_opus_pool as CP
sys.path.insert(0, A + "/null-cal/tools"); import labels as LB
crit = open(H + "/CB17-criterion.sha256").read().split()[0]
assert hashlib.sha256(open(H + "/CB17-criterion.md", "rb").read()).hexdigest() == crit
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ids = [x for x in open(A + "/lp-screens/main-97.ids").read().split() if x]; assert len(ids) == 97
CV5 = json.load(open(R + "/ruler/cv5-ladder/in/set.json"))["ids"]
V01 = [i for i in ids if not i.startswith("st-")]; CM = [i for i in ids if i.startswith("st-")]
TRF = {"CB": [H + "/traces/cb17-main-s42.traces.jsonl"], "K0": [A + "/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl"],
       "K1": [A + "/lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl"],
       "K3": [A + "/litepacks/traces/lp-K3-v01-s42.traces.jsonl", A + "/litepacks/traces/lp-K3-cm-s42.traces.jsonl"],
       "K0mb": [A + "/litepacks/traces/lp-K0-v01-s42.traces.jsonl", A + "/litepacks/traces/lp-K0-cm-s42.traces.jsonl"]}
TR = {a: {t["itemId"]: t for f in fs for t in rd(f)} for a, fs in TRF.items()}
QTXT = {(j := json.loads(l))["item"]["id"]: j["item"]["question"] for l in open(H + "/runs/req/cb17-main-s42.requests.jsonl")}
def sr(a, b): return {"s": (mr(a["boar"]) + mr(b["boar"])) / 2, "r": (mr(a["ref"]) + mr(b["ref"])) / 2, "corr": (a["boar"]["correctness"] + b["boar"]["correctness"]) / 2}
def load(paths):
    J = collections.defaultdict(dict)
    for p in paths:
        for r in rd(p):
            if r.get("ok") and not r.get("floorScored") and r["order"] not in J[r["queryId"]]: J[r["queryId"]][r["order"]] = r["mapped"]
    return {q: sr(v["boarA"], v["boarB"]) for q, v in J.items() if set(v) == {"boarA", "boarB"}}
U3 = ("v01", "qa-cooking-se", "qa-money-se")
HJ = {"CB": load([H + f"/judgments/cb17-main-s42-{u}.judgments.jsonl" for u in U3]),
      "K0": load([A + f"/lp-screens/control/judgments/lpctl-K0-main-s42-{u}.judgments.jsonl" for u in U3]),
      "K1": load([A + f"/lp-screens/control/judgments/lpctl-K1-main-s42-{u}.judgments.jsonl" for u in U3])}
lpj = lambda k: [A + f"/litepacks/judgments/lp-{k}-{x}-s42.judgments.jsonl" for x in ("v01", "cm-qa-cooking-se", "cm-qa-money-se")]
J3, J0mb = load(lpj("K3")), load(lpj("K0"))
HJ["K3"] = {i: (J0mb[i] if TR["K3"][i]["answer"]["text"] == TR["K0mb"][i]["answer"]["text"] else J3[i]) for i in ids}
for a in ("CB", "K0", "K1", "K3"): assert all(i in HJ[a] for i in ids), (a, [i for i in ids if i not in HJ[a]][:5])
FR = json.load(open(R + "/ruler/gemma-opus-main/in/set.json"))["frames"]
OPOOL = {}
for fr, (fa, fq) in FR.items(): OPOOL.update(CP.pool(fa, fq))
OJ = {a: {} for a in ("CB", "K0", "K1", "K3")}
for a in OJ:
    for i in ids:
        u = OPOOL.get(CP.key(i, TR[a][i]["answer"]["text"]))
        if u: OJ[a][i] = sr(u["boarA"], u["boarB"])
assert all(i in OJ["CB"] for i in CV5), "CB Opus rows missing on the CV5 51"
S1 = {r["id"]: r["attempted"] for r in rd(H + "/judgments/cb17-main-s42.stage1.jsonl") if r.get("ok") and r["rep"] == 1}
FP = json.load(open(R + "/ruler/FACTPRESENT-2026-10-21.json"))["items"]; FN = json.load(open(R + "/ruler/RAG-FUNNEL-2026-10-21.json"))["items"]
IP = json.load(open(R + "/ruler/inpack-assignment.json"))["items"]
def flags(a, i):
    t = TR[a][i]["answer"]; tx = t["text"]; d = LB.is_decline(tx, t.get("declined"))
    return {"warned": tx.startswith(W), "declined": bool(d), "engine_declined": bool(t.get("declined"))}
U = lambda s, r: (s - 1).sum() / (r - 1).sum()
def Qf(a, J, ii): s = np.array([0.0 if TR[a][i]["answer"].get("declined") else J[a][i]["s"] for i in ii]); r = np.array([J[a][i]["r"] for i in ii]); return s.sum() / r.sum()
ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
def stats(J, arms, ii, pairs):
    n = len(ii); rng = np.random.default_rng(11); draws = [rng.integers(0, n, n) for _ in range(2000)]
    M = {a: (np.array([J[a][i]["s"] for i in ii]), np.array([J[a][i]["r"] for i in ii])) for a in arms}
    pt = {a: U(*M[a]) for a in arms}; bs = {a: np.array([U(M[a][0][d], M[a][1][d]) for d in draws]) for a in arms}
    out = {"n": n, "levels": {a: {"U": round(pt[a], 4), "U_ci": ci(bs[a]), "U_net": round((pt[a] - 0.058) / 0.942, 4), "Q": round(Qf(a, J, ii), 4),
                                  "CE": int(sum(J[a][i]["corr"] <= 1.5 and not flags(a, i)["declined"] for i in ii)),
                                  "warned": int(sum(flags(a, i)["warned"] for i in ii)), "declined": int(sum(flags(a, i)["declined"] for i in ii))} for a in arms}, "pairs": {}}
    for a, b in pairs:
        d = pt[a] - pt[b]; db = bs[a] - bs[b]; ds = [J[a][i]["s"] - J[b][i]["s"] for i in ii]
        out["pairs"][f"{a}-{b}"] = {"dU": round(d, 4), "dU_ci": ci(db), "win": sum(x > 0.25 for x in ds), "tie": sum(abs(x) <= 0.25 for x in ds), "loss": sum(x < -0.25 for x in ds),
                                     "changed_text": sum(TR[a][i]["answer"]["text"] != TR[b][i]["answer"]["text"] for i in ii)}
    return out
PAIRS = [("K0", "CB"), ("K1", "CB"), ("K3", "CB"), ("K1", "K0")]
res = {"criterion_sha256": crit, "judges": {"haiku": "Haiku 5.5-low judge.v1-low, N 4, both orders, seed 7", "opus": "Opus judge.v1, both orders, seed 7"},
       "hosts": {"CB": "mini", "K0": "mini", "K1": "mini", "K3": "MacBook (LITEPACKS)"}, "haiku": {}, "opus": {}, "splits": {}}
SETS = {"MAIN 97": ids, "v0.1 57": V01, "cooking+money 40": CM, "CV5 51": CV5}
for k, ii in SETS.items(): res["haiku"][k] = stats(HJ, ["CB", "K0", "K1", "K3"], ii, PAIRS)
for k, ii in SETS.items():
    arms = [a for a in ("CB", "K0", "K1", "K3") if all(i in OJ[a] for i in ii)]
    res["opus"][k] = stats(OJ, arms, ii, [p for p in PAIRS if p[0] in arms and p[1] in arms]) if "CB" in arms else {"coverage": {a: sum(i in OJ[a] for i in ii) for a in OJ}}
    res["opus"][k]["coverage"] = {a: sum(i in OJ[a] for i in ii) for a in OJ}
# D2S (report only): closed-book s := 1 (true zero on the U scale) when stage 1 says not attempted
if S1:
    for jn, J in (("haiku", HJ), ("opus", OJ)):
        for k in ("MAIN 97", "CV5 51"):
            ii = SETS[k]
            if not all(i in J["CB"] for i in ii): continue
            s = np.array([1.0 if S1.get(i) == "no" else J["CB"][i]["s"] for i in ii]); r = np.array([J["CB"][i]["r"] for i in ii])
            res[jn][k]["levels"]["CB"]["U_D2S"] = round(U(s, r), 4)
    res["stage1_not_attempted"] = sorted(i for i, v in S1.items() if v == "no")
# splits (Haiku on MAIN; Opus on the CV5 51 where K0/K1 rows cover)
def split(J, ii, key, arms=("CB", "K0", "K1")):
    g = collections.defaultdict(list)
    for i in ii: g[key(i)].append(i)
    return {str(v): stats(J, list(arms), sorted(x), [(a, "CB") for a in arms if a != "CB"]) for v, x in g.items() if v is not None and len(x) >= 5}
fpk = lambda i: (FP.get(i, {}).get("K1") or {}).get("present")
ipk = lambda i: IP.get(i, {}).get("side")
res["splits"]["haiku MAIN 97: fact present in K1 context"] = split(HJ, [i for i in ids if fpk(i) is not None], fpk)
res["splits"]["haiku MAIN 97: in-pack"] = split(HJ, ids, ipk)
fnk = lambda i: (FN.get(i, {}).get("K1") or {}).get("vstage") or (FN.get(i, {}).get("K1") or {}).get("stage")
res["splits"]["haiku MAIN 97: RAG-FUNNEL K1 stage"] = split(HJ, [i for i in ids if fnk(i)], fnk)
res["splits"]["opus v0.1 57: fact present in K1 context (K0 only; K1 Opus rows incomplete)"] = split(OJ, [i for i in V01 if fpk(i) is not None], fpk, ("CB", "K0"))
res["splits"]["opus v0.1 57: in-pack (K0 only)"] = split(OJ, V01, ipk, ("CB", "K0"))
if all(all(i in OJ[a] for i in CV5) for a in ("K0", "K1")):
    res["splits"]["opus CV5 51: fact present in K1 context"] = split(OJ, [i for i in CV5 if fpk(i) is not None], fpk)
    res["splits"]["opus CV5 51: in-pack"] = split(OJ, CV5, ipk)
# sensitivity (report only, LITEPACKS/LP-SCREENS rule): CB rows whose text is byte-identical to the paired arm's text reuse that arm's judgment
same = lambda a, i: TR[a][i]["answer"]["text"] == TR["CB"][i]["answer"]["text"]
sens = {}
for jn, J in (("haiku", HJ), ("opus", OJ)):
    for k, ii in SETS.items():
        for a in ("K0", "K1"):
            if not all(i in J[a] and i in J["CB"] for i in ii): continue
            JJ = {"CB": {i: (J[a][i] if same(a, i) else J["CB"][i]) for i in ii}, a: J[a]}
            st_ = stats(JJ, ["CB", a], ii, [(a, "CB")])
            idn = [i for i in ii if same(a, i)]
            sens[f"{jn} {k} {a}-CB"] = {"identical_texts": len(idn), "dU_reuse": st_["pairs"][f"{a}-CB"]["dU"], "dU_reuse_ci": st_["pairs"][f"{a}-CB"]["dU_ci"],
                                        "wtl_reuse": [st_["pairs"][f"{a}-CB"][x] for x in ("win", "tie", "loss")],
                                        "retest_mean_abs_ds_identical": round(float(np.mean([abs(J[a][i]["s"] - J["CB"][i]["s"]) for i in idn])), 3) if idn else None,
                                        "retest_U_gap_identical": round(float(U(np.array([J[a][i]["s"] for i in idn]), np.array([J[a][i]["r"] for i in idn])) - U(np.array([J["CB"][i]["s"] for i in idn]), np.array([J["CB"][i]["r"] for i in idn]))), 4) if idn else None}
res["sensitivity_identical_text_reuse"] = sens
# rows
rows = []
r2 = lambda x: None if x is None else round(x, 3)
for i in ids:
    st = lambda a, J: r2(J[a][i]["s"]) if i in J[a] else None
    f = {a: flags(a, i) for a in ("CB", "K0", "K1", "K3")}
    fk = FN.get(i, {}).get("K1") or {}
    row = {"id": i, "set": "v0.1" if i in V01 else ("cooking-se" if "cooking" in i else "money-se"), "cv5_51": i in CV5,
           "tag": IP.get(i, {}).get("tag"), "in_pack": IP.get(i, {}).get("side"), "fact_present_K1": fpk(i), "funnel_stage_K1": fk.get("vstage") or fk.get("stage"),
           "ref_haiku": r2(HJ["K0"][i]["r"]),
           **{f"haiku_{a}": st(a, HJ) for a in ("CB", "K0", "K1", "K3")}, **{f"opus_{a}": st(a, OJ) for a in ("CB", "K0", "K1", "K3")},
           "d_haiku_K1_CB": r2(HJ["K1"][i]["s"] - HJ["CB"][i]["s"]), "d_haiku_K0_CB": r2(HJ["K0"][i]["s"] - HJ["CB"][i]["s"]),
           "d_opus_K1_CB": r2(OJ["K1"][i]["s"] - OJ["CB"][i]["s"]) if i in OJ["K1"] and i in OJ["CB"] else None,
           "d_opus_K0_CB": r2(OJ["K0"][i]["s"] - OJ["CB"][i]["s"]) if i in OJ["K0"] and i in OJ["CB"] else None,
           **{f"warned_{a}": f[a]["warned"] for a in ("CB", "K0", "K1", "K3")}, **{f"declined_{a}": f[a]["declined"] for a in ("CB", "K0", "K1", "K3")},
           "cb_stage1_attempted": S1.get(i)}
    rows.append(row)
res["rows"] = rows
os.makedirs(H + "/aggregates", exist_ok=True)
json.dump(res, open(H + "/aggregates/pack_table_17b.json", "w"), indent=1)
with open(H + "/aggregates/pack_table_17b.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1)[:12000])
