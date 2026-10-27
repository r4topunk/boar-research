#!/usr/bin/env python3
"""COMPOSE answer screen: stage-0 sanity + changed sets (0 LLM). python3 -I sanity_cmp.py <S traces> <G traces> <out dir>
Control = arms/litepacks/traces/mini/lp-K1-{cm,v01}-s42.mini.traces.jsonl (same-host MINI-BASELINE K1 kit; not regenerated).
Writes <out>/sanity.json, <out>/changed.S.ids, <out>/changed.G.ids, <out>/changed.union.ids (changed = kept (title,section,source) sequence differs from the control AND answer text differs)."""
import json, sys, glob, collections, os
A = "<workspace>/rnd/research/coordinator/arms"; CMP = A + "/coverage-map/compose"
trS, trG, out = sys.argv[1:4]; os.makedirs(out, exist_ok=True)
ids = open(A + "/lp-screens/main-97.ids").read().split()
ld = lambda p: {json.loads(l)["itemId"]: json.loads(l) for l in open(p)}
ctl = {}
for f in glob.glob(A + "/litepacks/traces/mini/lp-K1-*-s42.mini.traces.jsonl"): ctl.update(ld(f))
rep = {"S": {json.loads(l)["id"]: json.loads(l) for l in open(CMP + "/replays/main.N10.stock.jsonl")},
       "G": {json.loads(l)["id"]: json.loads(l) for l in open(CMP + "/replays/main.N10.gidf.jsonl")}}
B0 = {json.loads(l)["id"]: json.loads(l) for l in open(A + "/retrieve-sweep/replay/B0.main.jsonl")}
def loop(txt):
    w = txt.split(); c = collections.Counter(tuple(w[i:i+6]) for i in range(len(w) - 5)); return any(v >= 3 for v in c.values())
def det(t): return (t["timing"].get("outputTokens") or 0) == 0 or not any(r.startswith("generate:user-model") for r in t["route"]["reasonCodes"])
seq = lambda t: [(c["title"], c.get("section"), c.get("source")) for c in t["retrieval"]["kept"]]
ttl = lambda t: [c["title"] for c in t["retrieval"]["kept"]]
R = {}
for arm, f in (("S", trS), ("G", trG)):
    T = ld(f); r = dict(rows=len(T), expected=len(ids), missing=[i for i in ids if i not in T], extra=[i for i in T if i not in ids])
    r["errors"] = [i for i in ids if i in T and T[i].get("error")]
    r["empty"] = [i for i in ids if i in T and not (T[i]["answer"]["text"] or "").strip()]
    r["loops"] = [i for i in ids if i in T and loop(T[i]["answer"]["text"] or "")]
    dets = [i for i in ids if det(ctl[i])]; r["det_items"] = len(dets)
    r["det_text_diff_ctl"] = [i for i in dets if T[i]["answer"]["text"] != ctl[i]["answer"]["text"]]
    r["det_not_det_in_arm"] = [i for i in dets if not det(T[i])]
    r["det_codes_only_diff_ctl"] = [i for i in dets if T[i]["answer"]["text"] == ctl[i]["answer"]["text"] and T[i]["route"]["reasonCodes"] != ctl[i]["route"]["reasonCodes"]]
    kd = [i for i in ids if seq(T[i]) != seq(ctl[i])]; td = [i for i in ids if T[i]["answer"]["text"] != ctl[i]["answer"]["text"]]
    chg = [i for i in kd if i in td]
    r["kept_differs_vs_ctl"] = len(kd); r["text_differs_vs_ctl"] = len(td); r["changed"] = len(chg)
    r["kept_differs_text_same"] = [i for i in kd if i not in td]; r["text_differs_kept_same"] = [i for i in td if i not in kd]
    r["text_same_kept_same"] = len(ids) - len(set(kd) | set(td)); r["changed_ids"] = chg
    rp = rep[arm]
    idn = [i for i in ids if ttl(T[i]) == [c["title"] for c in rp[i]["keptFull"]]]
    r["kept_identity_vs_replay"] = [len(idn), len(ids)]; r["kept_identity_share"] = round(len(idn) / len(ids), 3)
    nid = [i for i in ids if i not in idn]
    ms = [i for i in nid if collections.Counter(ttl(T[i])) == collections.Counter(c["title"] for c in rp[i]["keptFull"])]
    r["not_identical"] = nid; r["not_identical_order_only"] = ms
    r["not_identical_content"] = {i: dict(trace=ttl(T[i]), replay=[c["title"] for c in rp[i]["keptFull"]]) for i in nid if i not in ms}
    r["not_identical_trace_no_retrieval"] = [i for i in nid if not T[i]["retrieval"]["kept"]]
    r["ctl_run_vs_B0_replay_sequence_identity"] = sum(ttl(ctl[i]) == [c["title"] for c in B0[i]["keptFull"]] for i in ids)
    m = lambda D, xs, f: round(sum(f(D[i]) for i in xs) / len(xs), 2)
    r["mean_out_tok"] = m(T, ids, lambda t: t["timing"].get("outputTokens") or 0); r["mean_totalMs"] = m(T, ids, lambda t: t["timing"].get("totalMs") or 0)
    r["mean_retrievalMs"] = m(T, ids, lambda t: t["timing"].get("retrievalMs") or 0)
    r["mean_kept_chunks"] = m(T, ids, lambda t: len(t["retrieval"]["kept"])); r["ctl_mean_kept_chunks"] = m(ctl, ids, lambda t: len(t["retrieval"]["kept"]))
    r["ctl_mean_out_tok"] = m(ctl, ids, lambda t: t["timing"].get("outputTokens") or 0); r["ctl_mean_totalMs"] = m(ctl, ids, lambda t: t["timing"].get("totalMs") or 0)
    r["ctl_mean_retrievalMs"] = m(ctl, ids, lambda t: t["timing"].get("retrievalMs") or 0)
    r["kill"] = bool(r["missing"] or r["errors"] or r["empty"] or r["loops"] or r["det_text_diff_ctl"])
    R[arm] = r
    open(f"{out}/changed.{arm}.ids", "w").write("\n".join(chg) + "\n")
TS, TG = ld(trS), ld(trG)
R["S_vs_G_text_identical"] = sum(TS[i]["answer"]["text"] == TG[i]["answer"]["text"] for i in ids)
R["S_vs_G_kept_identical"] = sum(seq(TS[i]) == seq(TG[i]) for i in ids)
both = [i for i in R["S"]["changed_ids"] if i in R["G"]["changed_ids"]]
un = [i for i in ids if i in R["S"]["changed_ids"] or i in R["G"]["changed_ids"]]
R["both_changed"] = both; R["union_changed"] = un
open(f"{out}/changed.union.ids", "w").write("\n".join(un) + "\n")
json.dump(R, open(out + "/sanity.json", "w"), indent=1)
print(json.dumps({a: {k: v for k, v in R[a].items() if k not in ("changed_ids", "not_identical_content", "not_identical")} for a in ("S", "G")}, indent=0))
print({k: (len(v) if isinstance(v, list) else v) for k, v in R.items() if k not in ("S", "G")})
