#!/usr/bin/env python3
"""DG stage-0 sanity (0 LLM). Usage: python3 -I sanity_dg.py <candidate.traces.jsonl> <ids file> <out.json>
Baselines: B_ctl = arms/null-cal/control/pool-K1.json item texts (merged mini K1 control: the judged control), B_mini = arms/litepacks/traces/mini lp-K1-{cm,v01}-s42.mini.traces.jsonl (+ lpctl traces for timing/reasonCodes)."""
import json, sys, glob, collections
A = "<workspace>/rnd/research/coordinator/arms"
tr, idsf, out = sys.argv[1:4]
ids = open(idsf).read().split()
def ld(p): return {json.loads(l)["itemId"]: json.loads(l) for l in open(p)}
T = ld(tr)
ctl = {}
for f in (f"{A}/lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl", f"{A}/null-cal/control/traces/poolctl-K1-st180-s42.traces.jsonl"): ctl.update(ld(f))
ctlj = json.load(open(f"{A}/null-cal/control/pool-K1.json"))["items"]
mini = {}
for f in glob.glob(f"{A}/litepacks/traces/mini/lp-K1-*-s42.mini.traces.jsonl"): mini.update(ld(f))
def loop(txt):
    w = txt.split(); c = collections.Counter(tuple(w[i:i+6]) for i in range(len(w) - 5)); return any(v >= 3 for v in c.values())
def det(t): return (t["timing"].get("outputTokens") or 0) == 0 or not any(r.startswith("generate:user-model") for r in t["route"]["reasonCodes"])
r = dict(file=tr, rows=len(T), expected=len(ids), missing=[i for i in ids if i not in T], extra=[i for i in T if i not in ids])
ids = [i for i in ids if i in T]
r["errors"] = [i for i in ids if T[i].get("error")]
r["empty"] = [i for i in ids if not (T[i]["answer"]["text"] or "").strip()]
r["loops"] = [i for i in ids if loop(T[i]["answer"]["text"] or "")]
r["det_items"] = [i for i in ids if det(ctl[i])]
r["det_diff_ctl"] = [i for i in r["det_items"] if T[i]["answer"]["text"] != ctl[i]["answer"]["text"] or T[i]["route"]["reasonCodes"] != ctl[i]["route"]["reasonCodes"]]
live = [i for i in ids if not det(ctl[i])]
r["live"] = len(live)
r["changed_vs_ctl_all"] = sum(T[i]["answer"]["text"] != ctlj[i]["text"] for i in ids)
r["changed_vs_ctl_live"] = sum(T[i]["answer"]["text"] != ctlj[i]["text"] for i in live)
mm = [i for i in ids if i in mini]
r["changed_vs_mini_baseline"] = sum(T[i]["answer"]["text"] != mini[i]["answer"]["text"] for i in mm); r["n_mini_baseline"] = len(mm)
r["ctl_vs_mini_text_differs"] = [i for i in mm if ctlj[i]["text"] != mini[i]["answer"]["text"]]
dgs = {i: (T[i]["retrieval"].get("dg") or {}).get("select") for i in ids}
r["dg_rows"] = sum(1 for v in dgs.values() if v)
r["no_evidence"] = sum(1 for i in ids if "dg:no-evidence" in T[i]["route"]["reasonCodes"])
r["selected_in_dropped"] = sum(1 for v in dgs.values() if v and v.get("inDropped"))
r["selected_in_kept"] = sum(1 for v in dgs.values() if v and v.get("inKept"))
r["select_ms_mean_on_dg_rows"] = round(sum(v["ms"] for v in dgs.values() if v) / max(1, r["dg_rows"]), 1)
m = lambda D, xs, f: round(sum(f(D[i]) for i in xs) / len(xs), 2)
for nm, D in (("cand", T), ("ctl", ctl)):
    r[f"mean_out_tok_{nm}_all"] = m(D, ids, lambda t: t["timing"].get("outputTokens") or 0)
    r[f"mean_totalMs_{nm}_all"] = m(D, ids, lambda t: t["timing"].get("totalMs") or 0)
    r[f"mean_out_tok_{nm}_live"] = m(D, live, lambda t: t["timing"].get("outputTokens") or 0)
    r[f"mean_totalMs_{nm}_live"] = m(D, live, lambda t: t["timing"].get("totalMs") or 0)
r["totalMs_ratio_all"] = round(r["mean_totalMs_cand_all"] / r["mean_totalMs_ctl_all"], 3); r["totalMs_ratio_live"] = round(r["mean_totalMs_cand_live"] / r["mean_totalMs_ctl_live"], 3)
r["empty_or_loop_share"] = round(len(set(r["empty"]) | set(r["loops"])) / len(ids), 3)
r["kill"] = bool(r["missing"] or r["errors"] or r["det_diff_ctl"] or r["empty_or_loop_share"] > 0.05 or r["totalMs_ratio_all"] > 4)
json.dump(r, open(out, "w"), indent=1)
print(json.dumps({k: v for k, v in r.items() if k != "file"}, indent=0))
