#!/usr/bin/env python3
"""FEWSHOT-READ / SAMPLE2-GATE reading (0 LLM). Usage: python3 -I report.py <fewshot-read|sample2-gate>  -> aggregates/<arm>.report.json + stdout.
Metrics as frozen in the two criteria: dU (agg_run vs_control), CE-unwarned / R / decline (null-cal/tools/labels.py), [n] share on shown LLM
answers, prompt / generated tokens, wall, RD-1 conversion on the 7 K0 FACTPRESENT-present pool ids."""
import json, sys, re, statistics as st, importlib.util
A = "<workspace>/rnd/research/coordinator/arms"; arm = sys.argv[1]
sp = importlib.util.spec_from_file_location("lab", f"{A}/null-cal/tools/labels.py"); lab = importlib.util.module_from_spec(sp); sp.loader.exec_module(lab)
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
IDS = [x for x in open(f"{A}/../ruler/ids/stage1-pool.ids").read().split() if x]
RUN = {"fewshot-read": "fewshot-read-K0-stage1-pool-s42", "sample2-gate": "sample2-gate-K0-stage1-pool-s42s43"}[arm]
ag = json.load(open(f"{A}/{arm}/aggregates/{RUN}.json")); ctl = json.load(open(f"{A}/null-cal/control/pool-K0.json"))["items"]
TR = {t["itemId"]: t for t in rd(f"{A}/{arm}/traces/{RUN}.traces.jsonl")}
CT = {}
for f in (f"{A}/lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl", f"{A}/null-cal/control/traces/poolctl-K0-st180-s42.traces.jsonl"):
    for t in rd(f): CT[t["itemId"]] = t
fp = json.load(open(f"{A}/../ruler/FACTPRESENT-2026-10-21.json"))["items"]
present = [i for i in IDS if fp[i]["K0"]["present"]]
L = {i: lab.label(ag["items"][i]) for i in IDS}; LC = {i: lab.label(ctl[i]) for i in IDS}
cnt = lambda LL, k: sum(1 for i in IDS if LL[i][k])
def cite(LL, T):
    sh = [i for i in IDS if LL[i]["shown"] and (T[i]["timing"].get("outputTokens") or 0) > 0]
    return [sum(1 for i in sh if re.search(r"\[\d+\]", T[i]["answer"]["text"])), len(sh)]
pq = lambda xs: dict(n=len(xs), p50=st.median(xs) if xs else None, p90=sorted(xs)[int(0.9 * (len(xs) - 1))] if xs else None, sum=sum(xs))
pt_a = {i: TR[i]["timing"].get("promptTokens") or 0 for i in IDS}; pt_c = {i: CT[i]["timing"].get("promptTokens") or 0 for i in IDS}
fired = [i for i in IDS if pt_a[i] != pt_c[i]]
out_a = sum(TR[i]["timing"].get("outputTokens") or 0 for i in IDS); out_c = sum(CT[i]["timing"].get("outputTokens") or 0 for i in IDS)
tot = lambda T: [T[i]["timing"].get("totalMs") or 0 for i in IDS]
rep = dict(arm=arm, n=len(IDS), vs_control=ag["vs_control"], U=[ag["summary"]["U"], None],
           CEu=[cnt(L, "CEu"), cnt(LC, "CEu")], CE=[cnt(L, "CE"), cnt(LC, "CE")], R=[cnt(L, "R"), cnt(LC, "R")], decline=[cnt(L, "decline"), cnt(LC, "decline")],
           warned=[cnt(L, "warned"), cnt(LC, "warned")], cite_shown_llm=[cite(L, TR), cite(LC, CT)],
           prompt_tokens=dict(fired_items=len(fired), arm=pq([pt_a[i] for i in fired]), control=pq([pt_c[i] for i in fired]), delta=pq([pt_a[i] - pt_c[i] for i in fired])),
           output_tokens=[out_a, out_c], totalMs_p50=[st.median(tot(TR)), st.median(tot(CT))], totalMs_sum=[sum(tot(TR)), sum(tot(CT))],
           rd1=dict(ids=present, arm=[sum(ag["items"][i]["corr"] >= 4 for i in present), len(present)], control=[sum(ctl[i]["corr"] >= 4 for i in present), len(present)],
                    per_item={i: [ctl[i]["corr"], ag["items"][i]["corr"]] for i in present}),
           changed=[dict(id=i, corr=[ctl[i]["corr"], ag["items"][i]["corr"]], u=[round(ctl[i]["s"] / ctl[i]["sref"], 3) if not ctl[i]["declined"] else 0, round(ag["items"][i]["s"] / ag["items"][i]["sref"], 3) if not ag["items"][i]["declined"] else 0],
                         CEu=[LC[i]["CEu"], L[i]["CEu"]], R=[LC[i]["R"], L[i]["R"]]) for i in IDS if ag["items"][i]["text"] != ctl[i]["text"]])
uc = sum(0 if ctl[i]["declined"] else ctl[i]["s"] for i in IDS) / sum(ctl[i]["sref"] for i in IDS); rep["U"][1] = uc
c = [x for x in rep["changed"]]
rep["changed_summary"] = dict(n=len(c), up=sum(x["u"][1] > x["u"][0] for x in c), down=sum(x["u"][1] < x["u"][0] for x in c),
                              CEu_fixed=sum(x["CEu"][0] and not x["CEu"][1] for x in c), CEu_new=sum(x["CEu"][1] and not x["CEu"][0] for x in c),
                              R_new=sum(x["R"][1] and not x["R"][0] for x in c), R_gone=sum(x["R"][0] and not x["R"][1] for x in c))
if arm == "sample2-gate":
    G = rd(f"{A}/sample2-gate/gate/s2g.outputs.jsonl"); S = {t["itemId"]: t for t in rd(f"{A}/sample2-gate/traces/s2g-K0-stage1-pool-s43dump.traces.jsonl")}
    sel = json.load(open(f"{A}/sample2-gate/gate/selection.json"))
    rep["sample2"] = dict(eligible=sum("p42" in v for v in sel.values()), picked_s43=sum(v["pick"] == "s43" for v in sel.values()),
                          s43_text_differs=sum(S[i]["answer"]["text"] != CT[i]["answer"]["text"] for i in IDS),
                          decode_tokens=dict(s42=out_c, s43=sum(S[i]["timing"].get("outputTokens") or 0 for i in IDS)),
                          gate_calls=len(G), gate_prompt_tokens=pq([g["prompt_n"] for g in G]), gate_prompt_ms=pq([round(g["prompt_ms"]) for g in G]),
                          gen_totalMs_sum=dict(s42=sum(tot(CT)), s43=sum(S[i]["timing"].get("totalMs") or 0 for i in IDS)))
json.dump(rep, open(f"{A}/{arm}/aggregates/{arm}.report.json", "w"), indent=1)
v = rep["vs_control"]["deltas"]["U"]
print(f"{arm}: U {rep['U'][0]:.4f} vs {rep['U'][1]:.4f} dU {v['d']:+.4f} CI {v['ci']} | CEu {rep['CEu']} R {rep['R']} decline {rep['decline']} warned {rep['warned']} cite {rep['cite_shown_llm']}")
print(f" changed {rep['changed_summary']} | prompt tok fired {rep['prompt_tokens']['fired_items']} delta {rep['prompt_tokens']['delta']} | out tok {rep['output_tokens']} | totalMs p50 {rep['totalMs_p50']}")
print(f" RD-1 present n {len(present)}: control {rep['rd1']['control']} arm {rep['rd1']['arm']} {rep['rd1']['per_item']}")
if "sample2" in rep: print(" sample2", json.dumps(rep["sample2"]))
