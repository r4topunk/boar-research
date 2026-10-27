#!/usr/bin/env python3
"""CITEFIX step 3 (0 LLM): GATE v2 line of a candidate run with its changed rows set to the gate's best case.
Usage: python3 -I bound_gate.py <candidate agg.json> <pool control json> <screen2-K.json> <changed ids comma list or ''> [--json out]
Best case per changed row: text = the answer without the warning line (shown), declined False, corr 5.0, s 5.0 (not CE).
With no changed rows this is the original gate line (reproduction check)."""
import json, sys, os, copy
NC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../null-cal/tools"); sys.path.insert(0, NC)
from screen_gate_v2 import metrics, verdict, PARAMS
W = "Not found in this phone's offline library. From the model's memory, may be wrong:"
c, k, sc = (json.load(open(p)) for p in sys.argv[1:4]); ch = [i for i in sys.argv[4].split(",") if i]
C = copy.deepcopy(c["items"])
for i in ch:
    x = C[i]; t = x["text"]; x["text"] = (t[len(W):].lstrip("\n") if t.startswith(W) else t) or "(best case)"; x["declined"] = False; x["corr"] = 5.0; x["s"] = 5.0
m = metrics(C, k["items"], sc); K = sc["pack_set"]; P_ = PARAMS[K]; m["verdict"] = verdict(m, K); m["bound_rows"] = ch
print(f"{'BOUND ' if ch else ''}screen2 {K}: problems {m['problems']} | fixed_u {len(m['fixed_u'])} (by refusal {len(m['fixed_by_refusal'])}) | new CEu {len(m['new_CEu'])} | net {m['net']} (bar {P_['BAR_NET']}) | "
      f"false refusals {len(m['false_ref'])}/{m['sentinels']} (max {P_['MAX_FALSE_REF']}) | sentinels worse {len(m['sent_worse'])} (report only) | "
      f"U_cov {m['U_cov_delta']:+.4f} {m['U_cov_ci']} (min {P_['MIN_UCOV_DELTA']}) | changed {m['changed']} | dead changed {m['dead_changed']} -> {m['verdict']}")
if "--json" in sys.argv: json.dump(m, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
