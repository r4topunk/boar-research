#!/usr/bin/env python3
"""F1b answer screen stage-0 sanity + changed sets (0 LLM). python3 -I sanity_f1b.py   -> ans-judge/sanity.json, ans-judge/changed.F.ids
Arm = ans-traces/f1b-main-s42.traces.jsonl; ARM-G = compose/screen/traces/cmp-G-K10-main-s42.traces.jsonl; control = litepacks mini K1 traces (same host).
changed vs G = kept (title,section,source) sequence differs AND answer text differs. Kept identity vs the F1b replay (sefix/replays/main.v3-extra.jsonl keptFull titles)."""
import json, glob, collections, os
A = "<workspace>/rnd/research/coordinator/arms"; CM = A + "/coverage-map"; SF = CM + "/sefix"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
ld = lambda p: {json.loads(l)["itemId"]: json.loads(l) for l in open(p)}
ids = open(A + "/lp-screens/main-97.ids").read().split()
T = ld(SF + "/ans-traces/f1b-main-s42.traces.jsonl"); G = ld(CM + "/compose/screen/traces/cmp-G-K10-main-s42.traces.jsonl")
ctl = {}
for f in glob.glob(A + "/litepacks/traces/mini/lp-K1-*-s42.mini.traces.jsonl"): ctl.update(ld(f))
rp = {r["id"]: r for r in rd(SF + "/replays/main.v3-extra.jsonl")}
def loop(txt):
    w = txt.split(); c = collections.Counter(tuple(w[i:i+6]) for i in range(len(w) - 5)); return any(v >= 3 for v in c.values())
det = lambda t: (t["timing"].get("outputTokens") or 0) == 0 or not any(r.startswith("generate:user-model") for r in t["route"]["reasonCodes"])
seq = lambda t: [(c["title"], c.get("section"), c.get("source")) for c in t["retrieval"]["kept"]]
ttl = lambda t: [c["title"] for c in t["retrieval"]["kept"]]
r = dict(rows=len(T), expected=len(ids), missing=[i for i in ids if i not in T], extra=[i for i in T if i not in ids])
r["errors"] = [i for i in ids if i in T and T[i].get("error")]
r["empty"] = [i for i in ids if i in T and not (T[i]["answer"]["text"] or "").strip()]
r["loops"] = [i for i in ids if i in T and loop(T[i]["answer"]["text"] or "")]
dets = [i for i in ids if det(G[i])]; r["det_items_in_G"] = len(dets)
r["det_text_diff_G"] = [i for i in dets if T[i]["answer"]["text"] != G[i]["answer"]["text"]]
r["det_not_det_in_arm"] = [i for i in dets if not det(T[i])]
r["det_text_byte_identical_to_G"] = sum(T[i]["answer"]["text"] == G[i]["answer"]["text"] for i in dets)
kd = [i for i in ids if seq(T[i]) != seq(G[i])]; td = [i for i in ids if T[i]["answer"]["text"] != G[i]["answer"]["text"]]
chg = [i for i in kd if i in td]
r.update(kept_differs_vs_G=len(kd), text_differs_vs_G=len(td), changed_vs_G=len(chg), kept_differs_text_same=[i for i in kd if i not in td], text_differs_kept_same=[i for i in td if i not in kd], changed_ids=chg)
kc = [i for i in ids if seq(T[i]) != seq(ctl[i]) and T[i]["answer"]["text"] != ctl[i]["answer"]["text"]]; r["changed_vs_ctl"] = len(kc)
idn = [i for i in ids if ttl(T[i]) == [c["title"] for c in rp[i]["keptFull"]]]
r["kept_identity_vs_replay"] = [len(idn), len(ids)]; r["kept_identity_share"] = round(len(idn) / len(ids), 3)
nid = [i for i in ids if i not in idn]
ms = [i for i in nid if collections.Counter(ttl(T[i])) == collections.Counter(c["title"] for c in rp[i]["keptFull"])]
r["not_identical"] = nid; r["not_identical_order_only"] = ms
r["not_identical_content"] = {i: dict(trace=ttl(T[i]), replay=[c["title"] for c in rp[i]["keptFull"]]) for i in nid if i not in ms}
r["not_identical_trace_no_retrieval"] = [i for i in nid if not T[i]["retrieval"]["kept"]]
r["not_identical_trace_has_fewer_than_replay"] = [i for i in nid if i not in ms and len(ttl(T[i])) < len(rp[i]["keptFull"])]
r["not_identical_trace_has_more_than_replay"] = [i for i in nid if i not in ms and len(ttl(T[i])) > len(rp[i]["keptFull"])]
m = lambda D, f: round(sum(f(D[i]) for i in ids) / len(ids), 2)
r["mean_out_tok"] = m(T, lambda t: t["timing"].get("outputTokens") or 0); r["G_mean_out_tok"] = m(G, lambda t: t["timing"].get("outputTokens") or 0)
r["mean_totalMs"] = m(T, lambda t: t["timing"].get("totalMs") or 0); r["G_mean_totalMs"] = m(G, lambda t: t["timing"].get("totalMs") or 0)
r["mean_retrievalMs"] = m(T, lambda t: t["timing"].get("retrievalMs") or 0); r["G_mean_retrievalMs"] = m(G, lambda t: t["timing"].get("retrievalMs") or 0)
r["mean_kept_chunks"] = m(T, lambda t: len(t["retrieval"]["kept"])); r["G_mean_kept_chunks"] = m(G, lambda t: len(t["retrieval"]["kept"]))
r["kill"] = bool(r["missing"] or r["errors"] or r["empty"] or r["loops"] or r["det_text_diff_G"])
os.makedirs(SF + "/ans-judge", exist_ok=True)
open(SF + "/ans-judge/changed.F.ids", "w").write("\n".join(chg) + "\n"); json.dump(r, open(SF + "/ans-judge/sanity.json", "w"), indent=1)
print(json.dumps({k: (v if not isinstance(v, (list, dict)) or len(v) < 12 else f"[{len(v)}]") for k, v in r.items()}, indent=0))
