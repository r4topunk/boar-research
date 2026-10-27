#!/usr/bin/env python3
"""A1-RC1-SHIPPED-U analysis (0 calls). Criterion ../A1-criterion.md. python3 -I a1_analyze.py <rows.jsonl> <rc1 judgments.jsonl> <out.json>
CV5 rungs: Opus judge.v1 rows loaded exactly as ruler/tools/cv5_ladder.py (new rows in ruler/cv5-ladder/out + reused units via cv5_opus_pool).
RC1: Opus judge.v1 rows, both orders, ok; floor-scored rows (errored traces, judge.mjs --floor-errored) kept at 1/1/1.
s, r = mean of the 3 dimensions averaged over both orders; U = sum(s-1)/sum(r-1); raw = sum(s)/sum(r); U_net = (U-0.058)/0.942;
U_D2S = U with s := 1 for detected non-answers (labels.is_decline stand-in, 0 Haiku; as DECLINE2STAGE (d)).
Item-cluster bootstrap B 2000, numpy default_rng(11), 2.5/97.5 pct, pairs on the same draws (as cv5_ladder.py).
Per 100: correct = not decline and corr >= 4; CE = not decline and corr <= 1.5; decline = is_decline; partial = the rest.
Win/tie/loss vs the reference: mapped.winner boar in both orders = win, ref in both = loss, else tie (judge-core rule)."""
import json, sys, os, collections, hashlib, statistics, numpy as np
C = "<workspace>/rnd/research/coordinator/"; A = C + "arms/"; W = C + "ruler/cv5-ladder/"
sys.path.insert(0, C + "ruler/tools"); import cv5_opus_pool as CP
sys.path.insert(0, A + "null-cal/tools"); from labels import is_decline
rows_f, jf, outf = sys.argv[1:4]
crit = open(A + "rc1-pixel/A1-criterion.sha256").read().split()[0]
assert hashlib.sha256(open(A + "rc1-pixel/A1-criterion.md", "rb").read()).hexdigest() == crit, "criterion sha mismatch"
K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
def sr(a, b): return {"s": (mr(a["boar"]) + mr(b["boar"])) / 2, "r": (mr(a["ref"]) + mr(b["ref"])) / 2,
                      "corr": (a["boar"]["correctness"] + b["boar"]["correctness"]) / 2, "wins": [a["winner"], b["winner"]]}
S_ = json.load(open(W + "in/set.json")); ids = S_["ids"]; RUNGS = S_["rungs"]
T = {k: {(j := json.loads(l)).get("itemId") or j.get("queryId"): j["answer"]["text"] for l in open(p)} for k, p in RUNGS.items()}
OP = {}
for k in RUNGS:
    by = collections.defaultdict(dict)
    for l in open(W + f"out/{k}.judgments.jsonl"):
        r = json.loads(l)
        if r.get("ok") and not r.get("floorScored"): by[r["queryId"]].setdefault(r["order"], r["mapped"])
    for q, v in by.items():
        if set(v) == {"boarA", "boarB"}: OP[CP.key(q, T[k][q])] = sr(v["boarA"], v["boarB"])
P = CP.pool("bd235bb9811f6d1ae88ba2d2ae3973e3572d75b6c451ee4cdd3a2e7644db48b1", "568b3ececd8afe5cad63a7f39bffe414e6dd45bcef9d03ef112faecad2981b18",
            exclude_prefix=W)
for uk, u in S_["units"].items():
    if u["reuse"]: OP.setdefault(uk, sr(P[uk]["boarA"], P[uk]["boarB"]))
O = {k: {q: dict(OP[CP.key(q, T[k][q])], text=T[k][q]) for q in ids} for k in RUNGS}
# ---- RC1
RW = {(r := json.loads(l))["queryId"]: r for l in open(rows_f)}
by = collections.defaultdict(dict); n_calls = 0; floor = set()
for l in open(jf):
    r = json.loads(l)
    if not r.get("floorScored"): n_calls += 1
    if r.get("ok"):
        by[r["queryId"]].setdefault(r["order"], r["mapped"])
        if r.get("floorScored"): floor.add(r["queryId"])
assert all(set(by[q]) == {"boarA", "boarB"} for q in ids), [q for q in ids if set(by[q]) != {"boarA", "boarB"}]
O["RC1_15B_shipped"] = {q: dict(sr(by[q]["boarA"], by[q]["boarB"]), text=(RW.get(q) or {}).get("answer") or "") for q in ids}
L = ["RC1_15B_shipped", "L0_15B_closedbook", "L1_17B_K0_s42", "L2_GemmaE2B_desk_s42", "L3_4B_phone_cut7"]
for k in L:
    for q in ids: O[k][q]["dec"] = is_decline(O[k][q]["text"], False)
U = lambda s, r: (s - 1).sum() / (r - 1).sum(); RAW = lambda s, r: s.sum() / r.sum(); NET = lambda u: (u - 0.058) / 0.942
ci = lambda x: [round(float(v), 4) for v in np.percentile(x, [2.5, 97.5])]
n = len(ids); rng = np.random.default_rng(11); draws = [rng.integers(0, n, n) for _ in range(2000)]
def arrs(k, d2s=False):
    s = np.array([1.0 if (d2s and O[k][q]["dec"]) else O[k][q]["s"] for q in ids]); r = np.array([O[k][q]["r"] for q in ids]); return s, r
def wtl(k):
    w = [all(x == "boar" for x in O[k][q]["wins"]) for q in ids]; lo = [all(x == "ref" for x in O[k][q]["wins"]) for q in ids]
    return np.array(w, float), np.array(lo, float)
def cls(k):
    c = {"correct": [], "CE": [], "decline": [], "partial": []}
    for q in ids:
        x = O[k][q]; lab = "decline" if x["dec"] else "correct" if x["corr"] >= 4 else "CE" if x["corr"] <= 1.5 else "partial"
        for kk in c: c[kk].append(1.0 if kk == lab else 0.0)
    return {kk: np.array(v) for kk, v in c.items()}
lv, BS = {}, {}
for k in L:
    s, r = arrs(k); s2, _ = arrs(k, True); w, lo = wtl(k); c = cls(k)
    bu = np.array([U(s[ii], r[ii]) for ii in draws]); b2 = np.array([U(s2[ii], r[ii]) for ii in draws]); bw = np.array([w[ii].mean() for ii in draws])
    BS[k] = {"U": bu, "D2S": b2, **{kk: np.array([v[ii].mean() * 100 for ii in draws]) for kk, v in c.items()}}
    lv[k] = {"U": round(U(s, r), 4), "U_ci": ci(bu), "raw": round(RAW(s, r), 4), "raw_ci": ci(np.array([RAW(s[ii], r[ii]) for ii in draws])),
             "U_net": round(NET(U(s, r)), 4), "U_D2S": round(U(s2, r), 4), "U_D2S_ci": ci(b2),
             "win": int(w.sum()), "loss": int(lo.sum()), "tie": int(n - w.sum() - lo.sum()), "win_rate": round(w.mean(), 4), "win_rate_ci": ci(bw),
             "per100": {kk: round(v.mean() * 100, 1) for kk, v in c.items()}, "per100_ci": {kk: ci(BS[k][kk]) for kk in c}}
def pair(a, b):
    d = lv[a]["U"] - lv[b]["U"]; db = BS[a]["U"] - BS[b]["U"]; d2 = lv[a]["U_D2S"] - lv[b]["U_D2S"]; db2 = BS[a]["D2S"] - BS[b]["D2S"]
    return {"dU": round(d, 4), "dU_ci": ci(db), "dU_D2S": round(d2, 4), "dU_D2S_ci": ci(db2),
            "better_worse": [int(sum(O[a][q]["s"] > O[b][q]["s"] for q in ids)), int(sum(O[a][q]["s"] < O[b][q]["s"] for q in ids))],
            "d_per100": {kk: [round(float((BS[a][kk] - BS[b][kk]).mean()), 1), ci(BS[a][kk] - BS[b][kk])] for kk in ("correct", "CE", "decline")}}
PR = {"1.7B-RC1": pair("L1_17B_K0_s42", "RC1_15B_shipped"), "RC1-1.5Bclosed": pair("RC1_15B_shipped", "L0_15B_closedbook"),
      "4B-RC1": pair("L3_4B_phone_cut7", "RC1_15B_shipped"), "Gemma-RC1": pair("L2_GemmaE2B_desk_s42", "RC1_15B_shipped")}
# ---- run readout
rr = [RW.get(q) for q in ids]; got = [r for r in rr if r]
answered = sum(1 for r in got if r.get("outcome") == "success" and (r.get("answer") or "").strip())
ret = sum(1 for r in got if r.get("retrievalUsed")); tl = sorted(r["totalLatencyMs"] / 1000 for r in got if isinstance(r.get("totalLatencyMs"), (int, float)))
tok = [r.get("tokensGenerated") or 0 for r in got]
run = {"rows": len(got), "answered": answered, "outcomes": dict(collections.Counter(r.get("outcome") for r in got)), "retrievalUsed": ret,
       "retrieval_ids": [r["queryId"] for r in got if r.get("retrievalUsed")], "answer_s_p50": round(statistics.median(tl), 1) if tl else None,
       "tokens_p50": statistics.median(tok) if tok else None, "hit_1024": sum(1 for t in tok if t >= 1024), "floor_scored": sorted(floor),
       "declines_detected": [q for q in ids if O["RC1_15B_shipped"][q]["dec"]], "opus_calls_in_file": n_calls,
       "personality": sorted({str(r.get("personalityId")) for r in got}), "maxTokens": sorted({str(r.get("maxTokens")) for r in got}),
       "models": sorted({str(r.get("modelId")) for r in got}), "appVersion": sorted({str(r.get("appVersion")) for r in got})}
# ---- frozen rules (A1-criterion.md)
u = lv["RC1_15B_shipped"]["U"]; p = PR["1.7B-RC1"]
SUMM = json.load(open(os.path.join(os.path.dirname(rows_f), "summary.json"))); lmk = SUMM.get("lmk_lines") or 0; run["lmk_lines"] = lmk
fl = {"partial": bool(answered < 45 or lmk > 0), "proxy_holds": bool(abs(u - 0.261) <= 0.05), "below_engine_point": bool(p["dU"] >= 0.05),
      "below_engine": bool(p["dU"] >= 0.05 and p["dU_ci"][0] > 0), "retrieval_le5": bool(ret <= 5), "kb_assisted": bool(ret > 10),
      "proxy_holds_D2S": bool(abs(lv["RC1_15B_shipped"]["U_D2S"] - 0.258) <= 0.05), "below_engine_D2S": bool(p["dU_D2S"] >= 0.05 and p["dU_D2S_ci"][0] > 0)}
fl["verdict"] = "PARTIAL" if fl["partial"] else ("SUPPORTED" if fl["proxy_holds"] and fl["below_engine"] and fl["retrieval_le5"] else
                                                  "KILLED" if not fl["proxy_holds"] else "MIXED")
out = {"criterion_sha256": crit, "n": n, "run": run, "levels": lv, "pairs": PR, "rules": fl}
js = json.dumps(out, indent=1); open(outf, "w").write(js + "\n"); print(js)
