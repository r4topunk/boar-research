#!/usr/bin/env python3
"""SHIP15B-PACKS + STYLE15B analysis (0 calls). Criteria ../SHIP15B-PACKS-criterion.md, ../STYLE15B-criterion.md (sha checked).
python3 -I ship15b_analyze.py <out.json>. Opus rows: ../opus/P.judgments.jsonl (new) + cv5-ladder L0 (C) + cv5_opus_pool reuse. Haiku rows: run_arm.sh
outputs (+ the K1 / K0 mini control rows for identical texts). D2S: ../stage1/stage1.jsonl (rep 1), Opus primary of SHIP15B only."""
import json, sys, os, collections, hashlib, numpy as np
A = "<workspace>/rnd/research/coordinator/arms/"; RU = A + "../ruler/"; S = A + "ship15b/"
sys.path.insert(0, RU + "tools"); import cv5_opus_pool as CP
for c in ("SHIP15B-PACKS", "STYLE15B"):
    assert hashlib.sha256(open(S + f"{c}-criterion.md", "rb").read()).hexdigest() == open(S + f"{c}-criterion.sha256").read().split()[0], c
ids = json.load(open(RU + "cv5-ladder/in/set.json"))["ids"]; assert len(ids) == 51
RUN = "K1-main-sub3e6183-s42"
TRF = {"C": A + "floor-anchors/traces/floor-anchors-K0-main-sub3e6183-s42.traces.jsonl",
       "P": A + f"ship15b-packs/traces/ship15b-packs-{RUN}.traces.jsonl",
       "D15": A + f"style15b-detailed/traces/style15b-detailed-{RUN}.traces.jsonl",
       "S17": A + "lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl",
       "D17": A + f"style17-detailed/traces/style17-detailed-{RUN}.traces.jsonl"}
TR = {k: {(j := json.loads(l)).get("itemId"): j for l in open(f)} for k, f in TRF.items()}
TX = {k: {q: TR[k][q]["answer"]["text"] for q in ids} for k in TR}
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
# ---- Haiku (arm rows first, then the run's own control for identical texts)
K1C = A + "lp-screens/control/judgments/lpctl-K1-main-s42-v01.judgments.jsonl"; K0C = A + "lp-screens/control/judgments/lpctl-K0-main-s42-v01.judgments.jsonl"
def hk(arm_files, ctl_file, ctl_tr, k):
    own = load(*arm_files); ctl = load(ctl_file); out = {}
    for q in ids:
        if q in own: out[q] = own[q]
        else:
            assert TX[k][q] == ctl_tr[q], (k, q); out[q] = ctl[q]
    return out
K1T = {q: TR["S17"][q]["answer"]["text"] for q in ids}
K0T = {(j := json.loads(l)).get("itemId"): j["answer"]["text"] for l in open(A + "lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl")}
H = {"C": hk([A + "floor-anchors/judgments/floor-anchors-K0-main-sub3e6183-s42-v01.judgments.jsonl"], K0C, K0T, "C"),
     "P": hk([A + f"ship15b-packs/judgments/ship15b-packs-{RUN}-v01.judgments.jsonl"], K1C, K1T, "P"),
     "D15": hk([A + f"style15b-detailed/judgments/style15b-detailed-{RUN}-v01.judgments.jsonl"], K1C, K1T, "D15"),
     "S17": hk([], K1C, K1T, "S17"),
     "D17": hk([A + f"style17-detailed/judgments/style17-detailed-{RUN}-v01.judgments.jsonl"], K1C, K1T, "D17")}
# ---- Opus
P_ = CP.pool("bd235bb9811f6d1ae88ba2d2ae3973e3572d75b6c451ee4cdd3a2e7644db48b1", "568b3ececd8afe5cad63a7f39bffe414e6dd45bcef9d03ef112faecad2981b18")
def opus(k, files):
    own = load(*files); out = {}; src = collections.Counter()
    for q in ids:
        uk = CP.key(q, TX[k][q])
        if uk in P_: out[q] = sr(P_[uk]["boarA"], P_[uk]["boarB"]); src["pool"] += 1
        elif q in own: out[q] = own[q]; src["new"] += 1
    return out, dict(src)
O = {}; OSRC = {}
O["C"], OSRC["C"] = opus("C", [RU + "cv5-ladder/out/L0_15B_closedbook.judgments.jsonl"])
O["P"], OSRC["P"] = opus("P", [S + "opus/P.judgments.jsonl"])
O["S17"], OSRC["S17"] = opus("S17", [])
# ---- D2S stage 1 (rep 1)
S1 = {}
if os.path.exists(S + "stage1/stage1.jsonl"):
    for l in open(S + "stage1/stage1.jsonl"):
        r = json.loads(l)
        if r.get("ok") and r["rep"] == 1: S1[r["key"]] = r["notAttempted"]
def d2s(k, J):
    out = {}
    for q in ids:
        x = dict(J[q]); na = S1.get(CP.key(q, TX[k][q]))
        if na is None: raise SystemExit(f"no stage-1 label {k} {q}")
        if na: x["s"] = 1.0
        x["na"] = na; out[q] = x
    return out
U = lambda s, r: (s - 1).sum() / (r - 1).sum(); RAW = lambda s, r: s.sum() / r.sum()
ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
rng = np.random.default_rng(11); n = len(ids); draws = [rng.integers(0, n, n) for _ in range(2000)]
def dec(k, q, J): return bool(TR[k][q]["answer"].get("declined")) or bool(J[q].get("na"))
def lv(k, J, sel=ids):
    s = np.array([J[q]["s"] for q in sel]); r = np.array([J[q]["r"] for q in sel]); m = len(sel)
    sh = [q for q in sel if not dec(k, q, J)]
    return {"n": m, "U": round(U(s, r), 4), "U_ci": ci([U(s[ii], r[ii]) for ii in draws]) if m == n else None, "U_raw": round(RAW(s, r), 4), "U_net": round((U(s, r) - 0.058) / 0.942, 4),
            "win_rate": round(float((s > r).mean()), 4), "correct_shown_per100": round(100 * sum(J[q]["corr"] >= 4 for q in sh) / m, 2),
            "ce_shown_per100": round(100 * sum(J[q]["corr"] <= 1.5 for q in sh) / m, 2), "declined": sum(dec(k, q, J) for q in sel)}
def pair(a, Ja, b, Jb):
    sa, ra = np.array([Ja[q]["s"] for q in ids]), np.array([Ja[q]["r"] for q in ids]); sb, rb = np.array([Jb[q]["s"] for q in ids]), np.array([Jb[q]["r"] for q in ids])
    d = U(sa, ra) - U(sb, rb); db = np.array([U(sa[ii], ra[ii]) - U(sb[ii], rb[ii]) for ii in draws])
    ce = lambda k, J: np.array([float(not dec(k, q, J) and J[q]["corr"] <= 1.5) for q in ids])
    dce = 100 * (ce(a, Ja).mean() - ce(b, Jb).mean()); dceb = [100 * (ce(a, Ja)[ii].mean() - ce(b, Jb)[ii].mean()) for ii in draws]
    return {"dU": round(d, 4), "dU_ci": ci(db), "dU_raw": round(RAW(sa, ra) - RAW(sb, rb), 4), "better_worse": [int((sa > sb).sum()), int((sa < sb).sum())],
            "d_ce_shown_per100": round(dce, 2), "d_ce_ci": ci(dceb), "changed_text": sum(TX[a][q] != TX[b][q] for q in ids)}
def cost(k):
    t = [TR[k][q]["timing"] for q in ids]; ot = np.array([x.get("outputTokens") or 0 for x in t]); w = np.array([x.get("totalMs") or 0 for x in t]) / 1000
    gen = ot > 0; cap = 1024 if k in ("D15", "D17") else 512
    return {"out_tokens_p50": float(np.median(ot)), "out_tokens_mean": round(float(ot.mean()), 1), "out_tokens_p50_generated": float(np.median(ot[gen])) if gen.any() else 0,
            "generated_rows": int(gen.sum()), "at_cap": int((ot >= cap - 1).sum()), "wall_p50_s": round(float(np.median(w)), 2), "wall_sum_s": round(float(w.sum()), 1),
            "words_p50": float(np.median([len(TX[k][q].split()) for q in ids])), "kept_sources_items": sum(bool(TR[k][q]["retrieval"]["kept"]) for q in ids),
            "persona": TR[k][ids[0]]["runtime"]["versions"].get("persona"), "model_sha": TR[k][ids[0]]["runtime"]["versions"]["model.sha256"][:8], "host": TR[k][ids[0]]["runtime"]["host"]}
out = {"ids": n, "cost": {k: cost(k) for k in TR}, "opus_sources": OSRC}
# SHIP15B
ship = {}
if len(O["P"]) == n and len(O["C"]) == n:
    OP, OC = d2s("P", O["P"]), d2s("C", O["C"])
    ship["opus_d2s"] = {"P": lv("P", OP), "C": lv("C", OC), "P-C": pair("P", OP, "C", OC)}
    ship["opus_v1"] = {"P": lv("P", O["P"]), "C": lv("C", O["C"]), "P-C": pair("P", O["P"], "C", O["C"])}
    pc = ship["opus_d2s"]["P-C"]
    ship["verdict"] = "FAIL-HARM" if pc["d_ce_shown_per100"] >= 3 else ("PASS" if pc["dU"] >= 0.03 and pc["dU_ci"][0] > 0 else "NO-GAIN")
    ship["d2s_not_attempted"] = {"P": sum(OP[q]["na"] for q in ids), "C": sum(OC[q]["na"] for q in ids)}
ship["haiku"] = {"P": lv("P", H["P"]), "C": lv("C", H["C"]), "P-C": pair("P", H["P"], "C", H["C"]), "S17": lv("S17", H["S17"])}
ship["S17_opus_pool_coverage"] = len(O["S17"])
if len(O["S17"]) == n: ship["S17_opus"] = lv("S17", O["S17"])
out["ship15b"] = ship
# STYLE15B (Haiku)
st = {}
for m, s_, d_ in (("1.5B", "P", "D15"), ("1.7B", "S17", "D17")):
    pr = pair(s_, H[s_], d_, H[d_]); v = "NONINFERIOR" if pr["dU_ci"][0] >= -0.02 else ("NOT-WORSE (point)" if pr["dU"] >= -0.02 else "WORSE")
    st[m] = {"S": lv(s_, H[s_]), "D": lv(d_, H[d_]), "S-D": pr, "verdict": v}
out["style15b"] = st
js = json.dumps(out, indent=1); open(sys.argv[1], "w").write(js + "\n"); print(js)
