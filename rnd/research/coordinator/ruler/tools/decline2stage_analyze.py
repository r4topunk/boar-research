#!/usr/bin/env python3
"""DECLINE2STAGE analysis (0 calls). Criterion ../DECLINE2STAGE-criterion.md (sha checked). python3 -I decline2stage_analyze.py <out.json>
Bars (a)(b)(c), retest, and (d) the CV5 v0.1 51 ladder (cv5_ladder.py loaders exec'd unchanged up to its output block) with s := 1 (U contribution 0)
for detected not-attempted answers: stage-1 rep-1 label on identical (id, text), else labels.is_decline stand-in."""
import json, sys, os, hashlib, collections, copy
R0 = "<workspace>/rnd/research/coordinator"; RU = R0 + "/ruler/"; D = RU + "decline2stage/"
CRIT = open(RU + "DECLINE2STAGE-criterion.sha256").read().split()[0]
assert hashlib.sha256(open(RU + "DECLINE2STAGE-criterion.md", "rb").read()).hexdigest() == CRIT
sys.path.insert(0, R0 + "/arms/null-cal/tools"); from labels import is_decline, ENGINE_DECLINE  # noqa
sha = lambda t: hashlib.sha256(t.encode()).hexdigest()
U_ = {(u := json.loads(l))["key"]: u for l in open(D + "in/units.jsonl")}
S1 = [json.loads(l) for l in open(D + "out/stage1.jsonl")]
assert all(r["ok"] and r["requestedModel"] == "claude-haiku-5-5" for r in S1) and len(open(D + "out/calls.log").read().split("\n")) - 1 == len(S1) == 258
lab = {r["key"]: r["notAttempted"] for r in S1 if r["rep"] == 1}; assert len(lab) == 238
out = {"criterion_sha256": CRIT, "script_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest(), "calls": len(S1)}
# (a)
a = {v: sum(lab[k] for k, u in U_.items() if u["set"] == f"FLOOR-{v}") for v in "abc"}
out["a"] = {"per_variant_of_30": a, "recall_90": round(sum(a.values()) / 90, 4), "recall_c": round(a["c"] / 30, 4)}
out["a"]["pass"] = sum(a.values()) >= 86 and a["c"] >= 27
# (b)
def bset(s, cap):
    els = [k for k, u in U_.items() if u["set"] == s and u["ref_corr"] >= 3]; hits = [k for k in els if lab[k]]
    allna = [k for k, u in U_.items() if u["set"] == s and lab[k]]
    return {"n_ref_ge3": len(els), "false_not_attempted": len(hits), "cap": cap, "pass": len(hits) <= cap,
            "hits": [dict(id=U_[k]["id"], opus_corr=U_[k]["opus_corr"], haiku_corr=U_[k]["haiku_corr"], engine_refusal_string=bool(ENGINE_DECLINE.search(U_[k]["text"])),
                          labels_is_decline=is_decline(U_[k]["text"], False), text_head=U_[k]["text"][:90]) for k in hits],
            "all_not_attempted": len(allna), "all_not_attempted_labels_is_decline": sum(is_decline(U_[k]["text"], False) for k in allna),
            "labels_is_decline_total": sum(is_decline(u["text"], False) for u in U_.values() if u["set"] == s),
            "ref_src": dict(collections.Counter(U_[k]["ref_src"] for k in els))}
out["b"] = {"MAIN": bset("MAIN", 1), "WARN": bset("WARN", 3)}; out["b"]["pass"] = out["b"]["MAIN"]["pass"] and out["b"]["WARN"]["pass"]
# post hoc sensitivity (no rule): hits that are not the engine's fixed refusal strings (which the spec §3.1 z override already zeroes)
out["b_posthoc_non_engine_hits"] = {s: sum(not h["engine_refusal_string"] for h in out["b"][s]["hits"]) for s in ("MAIN", "WARN")}
# (c) CE flips on non-declines: score/CE unchanged for every attempted unit (MAIN, WARN), by construction
flips = 0
for k, u in U_.items():
    if u["set"] in ("MAIN", "WARN") and not lab[k]:
        c_v1 = u["haiku_corr"] <= 1.5; c_d2s = u["haiku_corr"] <= 1.5; flips += c_v1 != c_d2s
assert flips == 0; out["c"] = {"ce_flips_non_declines": flips, "pass": True}
# retest
rt = {r["key"]: r["notAttempted"] for r in S1 if r["rep"] == 2}
out["retest"] = {"n": len(rt), "agree": sum(rt[k] == lab[k] for k in rt), "disagree_keys": [k for k in rt if rt[k] != lab[k]]}
# (d) ladder
T_ = "<workspace>/rnd/research/coordinator/ruler/tools/cv5_ladder.py"; src = open(T_).read()
G = {"__file__": T_, "__name__": "d2s"}; exec(src[:src.index('out = {"criterion_sha256"')], G)
ids, L, T, O, H, block = G["ids"], G["L"], G["T"], G["O"], G["H"], G["block"]
s1 = {(u["id"], u["text_sha256"]): lab[k] for k, u in U_.items()}
det, src_ = {}, collections.Counter()
for k in L:
    det[k] = {}
    for q in ids:
        t = T[k][q]; key = (q, sha(t))
        if key in s1: det[k][q] = s1[key]; src_[(k, "stage1")] += 1
        else: det[k][q] = is_decline(t, False); src_[(k, "labels_stand_in")] += 1
def zero(S):
    Z = copy.deepcopy(S)
    for k in L:
        for q in ids:
            if det[k][q]: Z[k][q]["s"] = 1.0
    return Z
d = {"detection_source": {f"{k}|{s}": n for (k, s), n in sorted(src_.items())}, "detected": {k: [q for q in ids if det[k][q]] for k in L}}
for name, S in (("opus", O), ("haiku_same_frame", H)):
    b0, b1 = block(S), block(zero(S))
    d[name] = {"levels": {k: {"U_v1": b0["levels"][k]["U"], "U_v1_ci": b0["levels"][k]["U_ci"], "U_net_D0.058": b0["levels"][k]["U_net"],
                              "U_d2s": b1["levels"][k]["U"], "U_d2s_ci": b1["levels"][k]["U_ci"], "correction": round(b1["levels"][k]["U"] - b0["levels"][k]["U"], 4)} for k in L},
               "pairs": {p: {"dU_v1": b0["pairs"][p]["dU"], "dU_v1_ci": b0["pairs"][p]["dU_ci"], "dU_net": b0["pairs"][p]["dU_net"], "dU_d2s": b1["pairs"][p]["dU"],
                             "dU_d2s_ci": b1["pairs"][p]["dU_ci"], "sep_v1": b0["pairs"][p]["separable"], "sep_d2s": b1["pairs"][p]["separable"]} for p in b0["pairs"]}}
out["d"] = d
out["verdict"] = "PASS" if (out["a"]["pass"] and out["b"]["pass"] and out["c"]["pass"]) else "FAIL"
js = json.dumps(out, indent=1); open(sys.argv[1], "w").write(js + "\n"); print(js)
