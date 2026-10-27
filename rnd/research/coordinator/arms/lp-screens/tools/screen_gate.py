#!/usr/bin/env python3
"""LP-SCREENS stage-1 gate (GRILL-2026-10-20 Q6; 0 LLM). Usage: python3 -I screen_gate.py <candidate agg.json> <MINI control agg.json> <screen-K.json> [--json out]
Both aggregates come from tools/agg_run.py on the same screen (the control is the MINI control, never the MacBook LITEPACKS traces).
  problems           = the screen's problem ids (CE in the MacBook LITEPACKS arm when the screen was frozen; 27 for K0 and K1)
  fixed              = problem ids that are CE in the mini control and not CE in the candidate
  still_CE           = problem ids that are CE in the candidate
  sentinel worse     = sentinel ids where the candidate's correctness is >= 1.0 point lower than the control's, or is newly declined / refusal-like, or is newly CE
GO iff fixed >= ceil(0.22 * problems) AND sentinels worse <= 1 (frozen stage-1 gate)."""
import json, sys, math
c, k, sc = (json.load(open(p)) for p in sys.argv[1:4]); C, K = c["items"], k["items"]
P, S = sc["problems"], sc["sentinels"]
assert all(i in C and i in K for i in P + S), "aggregates do not cover the screen"
ctlce = [i for i in P if K[i]["CE"]]
fixed = [i for i in ctlce if not C[i]["CE"]]; still = [i for i in P if C[i]["CE"]]; newly_ce_problem = [i for i in P if C[i]["CE"] and not K[i]["CE"]]
worse = []
for i in S:
    why = []
    # >= 1.0 point: Haiku re-judging identical text changes correctness on 13/37 items (setup noise check), so smaller drops are judge noise.
    if C[i]["corr"] <= K[i]["corr"] - 1.0: why.append(f"corr {K[i]['corr']}->{C[i]['corr']}")
    if C[i]["declined"] and not K[i]["declined"]: why.append("newly declined")
    if C[i]["refusal_like"] and not K[i]["refusal_like"]: why.append("newly refusal-like")
    if C[i]["CE"] and not K[i]["CE"]: why.append("newly CE")
    if why: worse.append((i, why))
need = math.ceil(0.22 * len(P)); go = len(fixed) >= need and len(worse) <= 1
out = dict(pack_set=sc["pack_set"], problems=len(P), control_ce_on_problems=len(ctlce), fixed=fixed, still_ce=still, problems_newly_ce=newly_ce_problem,
           sentinels=len(S), sentinels_worse={i: w for i, w in worse}, need_fixed=need, verdict="GO" if go else "NO-GO",
           changed_answers=sum(C[i]["text"] != K[i]["text"] for i in P + S))
print(f"screen {sc['pack_set']}: problems {len(P)} (CE in mini control {len(ctlce)}) | fixed {len(fixed)} (need >= {need}) | still CE {len(still)} | "
      f"sentinels worse {len(worse)}/{len(S)} (max 1) | changed answers {out['changed_answers']}/{len(P) + len(S)} -> {out['verdict']}")
for i in fixed: print("  fixed", i, K[i]["corr"], "->", C[i]["corr"])
for i, w in worse: print("  sentinel worse", i, "; ".join(w))
if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
