#!/usr/bin/env python3
"""NULLCAL measurement report (0 LLM). Usage: python3 -I null_report.py <candidate agg.json> <MINI control agg.json> <screen-K.json> <control traces.jsonl> [--json out]
Both aggregates come from lp-screens/tools/agg_run.py (candidate judged only where the text differs from the control). Definitions are frozen in NULLCAL-criterion.md:
  live(i)      = the CONTROL trace generated tokens (timing.outputTokens > 0); no-LLM items (routing refusals, calculator/facts layers, detector) are dead
  CEu(x)       = x.CE and not x.warned      (CE in the product default: warned memory answers are refused, so they are not shown)
  fixed_v1     = problems CE in control and not CE in candidate                (screen_gate.py definition, 23 items on K0)
  fixed_reach  = same, restricted to live problems                              (reachable denominator)
  fixed_u      = live problems with CEu in control and not CEu in candidate     (default-mode fixes)
  new_CEu      = live items (problems + sentinels) not CEu in control and CEu in candidate (default-mode regressions)
  sent_worse_v1 / sent_worse_live = screen_gate.py sentinel rule over all 10 / over the live sentinels only"""
import json, sys
c, k, sc = (json.load(open(p)) for p in sys.argv[1:4]); C, K = c["items"], k["items"]
live = {}
for l in open(sys.argv[4]):
    t = json.loads(l); live[t["itemId"]] = (t["timing"].get("outputTokens") or 0) > 0
P, S = sc["problems"], sc["sentinels"]
CEu = lambda x: bool(x["CE"] and not x["warned"])
def worse(i):
    why = []
    if C[i]["corr"] <= K[i]["corr"] - 1.0: why.append(f"corr {K[i]['corr']}->{C[i]['corr']}")
    if C[i]["declined"] and not K[i]["declined"]: why.append("newly declined")
    if C[i]["refusal_like"] and not K[i]["refusal_like"]: why.append("newly refusal-like")
    if C[i]["CE"] and not K[i]["CE"]: why.append("newly CE")
    return why
ctl_ce = [i for i in P if K[i]["CE"]]; reach = [i for i in ctl_ce if live[i]]
fixed_v1 = [i for i in ctl_ce if not C[i]["CE"]]; fixed_reach = [i for i in reach if not C[i]["CE"]]
ctl_ceu_live = [i for i in P if live[i] and CEu(K[i])]; fixed_u = [i for i in ctl_ceu_live if not CEu(C[i])]
ids = P + S; new_ceu = [i for i in ids if live[i] and not CEu(K[i]) and CEu(C[i])]
sw = {i: worse(i) for i in S if worse(i)}; swl = {i: w for i, w in sw.items() if live[i]}
out = dict(problems=len(P), control_ce=len(ctl_ce), reachable_ce=len(reach), control_ceu_live_problems=len(ctl_ceu_live),
           fixed_v1=fixed_v1, fixed_reach=fixed_reach, fixed_u=fixed_u, new_CEu=new_ceu,
           ceu_count_control_live=sum(live[i] and CEu(K[i]) for i in ids), ceu_count_candidate_live=sum(live[i] and CEu(C[i]) for i in ids),
           sentinels=len(S), live_sentinels=sum(live[i] for i in S), sentinels_worse_v1=sw, sentinels_worse_live=swl,
           changed_live=sum(live[i] and C[i]["text"] != K[i]["text"] for i in ids), live_items=sum(live[i] for i in ids),
           dead_changed=sum((not live[i]) and C[i]["text"] != K[i]["text"] for i in ids))
print(json.dumps(out, indent=1))
if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
