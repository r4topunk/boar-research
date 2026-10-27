#!/usr/bin/env python3
"""GATE v2 stage-1 screen (0 LLM). Usage: python3 -I screen_gate_v2.py <candidate agg.json> <pool control json (null-cal/control/pool-K.json)> <screen2-K.json> [--json out] [--metrics]
Spec and calibration: arms/null-cal/GATE-V2.md. screen_gate.py (v1) is untouched and stays for frozen verdicts.
Corrected labels (labels.py): decline / warned / CE / CEu (= CE and not warned) / R (= decline or warned = default-mode refused) / shown.
Screen = PROBLEMS (live items that are CE-unwarned in the mini control) + SENTINELS (20 live items the default product shows, not CE).
Metrics (candidate vs control, on the screen items):
  fixed_u     = problems that are not CE-unwarned in the candidate          (primary; of which by_refusal = the candidate refuses them)
  new_CEu     = live items (problems + sentinels) not CE-unwarned in the control that are CE-unwarned in the candidate
  net         = |fixed_u| - |new_CEu|
  false_ref   = sentinels (control shown, judge-correct corr >= 3.0) that the candidate refuses (declined or warned)   [default-mode false refusals]
  sent_worse  = sentinels the candidate still shows whose correctness fell >= 1.0 or that became CE                      [quality loss]
  U_cov       = U on the covered items (control shown: problems and sentinels): sum s / sum sref with s := 0 when the candidate refuses; delta vs control
GO iff net >= BAR_NET and |false_ref| <= MAX_FALSE_REF and U_cov delta >= MIN_UCOV_DELTA   (parameters per pack set, calibrated on the null runs, see GATE-V2.md).
sent_worse is REPORTED, not gated: under the nulls 1-7 of 20 sentinels read "worse" by sampling alone (sentinels are selected at the top of the correctness scale)."""
import json, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from labels import label
# Calibrated 2026-10-20 from the 4 null runs on these screens (arms/null-cal/arms/*): BAR_NET = max null net + 2; MAX_FALSE_REF = max null false refusals + 1;
# MIN_UCOV_DELTA = min null U_cov delta - 0.02 (rounded outward). See GATE-V2.md.
PARAMS = {"K0": dict(BAR_NET=10, MAX_FALSE_REF=2, MIN_UCOV_DELTA=-0.059), "K1": dict(BAR_NET=9, MAX_FALSE_REF=4, MIN_UCOV_DELTA=-0.071)}
def metrics(C, K, sc):
    P, S = sc["problems"], sc["sentinels"]; assert all(i in C and i in K for i in P + S), "aggregates do not cover the screen"
    LC = {i: label(C[i]) for i in P + S}; LK = {i: label(K[i]) for i in P + S}; live = {i: K[i]["live"] for i in P + S}
    assert all(LK[i]["CEu"] and live[i] for i in P), "control no longer matches the screen (problems must be live CE-unwarned)"
    fixed = [i for i in P if not LC[i]["CEu"]]; by_ref = [i for i in fixed if LC[i]["R"]]
    new = [i for i in P + S if live[i] and not LK[i]["CEu"] and LC[i]["CEu"]]
    fr = [i for i in S if LK[i]["shown"] and LK[i]["corr"] >= 3.0 and LC[i]["R"]]
    sw = {i: (f"corr {LK[i]['corr']}->{LC[i]['corr']}" if LC[i]["corr"] <= LK[i]["corr"] - 1.0 else "newly CE") for i in S
          if not LC[i]["R"] and (LC[i]["corr"] <= LK[i]["corr"] - 1.0 or (LC[i]["CE"] and not LK[i]["CE"]))}
    cov = [i for i in P + S if LK[i]["shown"]]; sref = lambda xs: sum(LK[i]["sref"] for i in xs)
    u = lambda xs, L: sum(0 if L[i]["R"] else L[i]["s"] for i in xs) / sref(xs)
    rnd = random.Random(11); d = []
    for _ in range(2000):
        s = [rnd.choice(cov) for _ in cov]; d.append(u(s, LC) - u(s, LK))
    d.sort()
    return dict(problems=len(P), sentinels=len(S), fixed_u=fixed, fixed_by_refusal=by_ref, new_CEu=new, net=len(fixed) - len(new), false_ref=fr, sent_worse=sw,
                U_cov_ctl=round(u(cov, LK), 4), U_cov_cand=round(u(cov, LC), 4), U_cov_delta=round(u(cov, LC) - u(cov, LK), 4), U_cov_ci=[round(d[50], 4), round(d[1949], 4)], covered=len(cov),
                ceu_ctl=sum(LK[i]["CEu"] for i in P + S), ceu_cand=sum(LC[i]["CEu"] for i in P + S), declines_ctl=sum(LK[i]["decline"] for i in P + S),
                declines_cand=sum(LC[i]["decline"] for i in P + S), warned_ctl=sum(LK[i]["warned"] for i in P + S), warned_cand=sum(LC[i]["warned"] for i in P + S),
                changed=sum(C[i]["text"] != K[i]["text"] for i in P + S), dead_changed=sum((not live[i]) and C[i]["text"] != K[i]["text"] for i in P + S))
def verdict(m, K):
    p = PARAMS[K]
    return "GO" if m["net"] >= p["BAR_NET"] and len(m["false_ref"]) <= p["MAX_FALSE_REF"] and m["U_cov_delta"] >= p["MIN_UCOV_DELTA"] else "NO-GO"
if __name__ == "__main__":
    c, k, sc = (json.load(open(p)) for p in sys.argv[1:4]); m = metrics(c["items"], k["items"], sc); K = sc["pack_set"]; P_ = PARAMS[K]; m["params"] = P_; m["verdict"] = verdict(m, K)
    print(f"screen2 {sc['pack_set']}: problems {m['problems']} | fixed_u {len(m['fixed_u'])} (by refusal {len(m['fixed_by_refusal'])}) | new CEu {len(m['new_CEu'])} | net {m['net']} (bar {P_['BAR_NET']}) | "
          f"false refusals {len(m['false_ref'])}/{m['sentinels']} (max {P_['MAX_FALSE_REF']}) | sentinels worse {len(m['sent_worse'])} (report only) | "
          f"U_cov {m['U_cov_delta']:+.4f} {m['U_cov_ci']} (min {P_['MIN_UCOV_DELTA']}) | changed {m['changed']} | dead changed {m['dead_changed']} -> {m['verdict']}")
    if "--json" in sys.argv: json.dump(m, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
