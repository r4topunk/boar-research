#!/usr/bin/env python3
"""H1+H2 answer screen: stage-0 sanity + changed set (0 LLM). python3 -I sanity_h12.py <h12.traces.jsonl> <out dir>
Control = arms/litepacks/traces/mini/lp-K1-{cm,v01}-s42.mini.traces.jsonl (same-host MINI-BASELINE; not regenerated).
Writes <out>/sanity.json, <out>/changed.ids (kept (title,section,source) sequence differs from the control AND answer text differs), <out>/kept-differs.ids."""
import json, sys, glob, collections, os
A = "<workspace>/rnd/research/coordinator/arms"; RS = A + "/retrieve-sweep"
tr, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True)
ids = open(A + "/lp-screens/main-97.ids").read().split()
ld = lambda p: {json.loads(l)["itemId"]: json.loads(l) for l in open(p)}
T = ld(tr); ctl = {}
for f in glob.glob(A + "/litepacks/traces/mini/lp-K1-*-s42.mini.traces.jsonl"): ctl.update(ld(f))
rep = {json.loads(l)["id"]: json.loads(l) for l in open(RS + "/replay/H1.main.jsonl")}
B0 = {json.loads(l)["id"]: json.loads(l) for l in open(RS + "/replay/B0.main.jsonl")}
h2 = {}
for f in ("H2.main.sub.jsonl",):
    for l in open(RS + "/replay/h2/" + f): r = json.loads(l); h2[r["id"]] = r
def loop(txt):
    w = txt.split(); c = collections.Counter(tuple(w[i:i+6]) for i in range(len(w) - 5)); return any(v >= 3 for v in c.values())
def det(t): return (t["timing"].get("outputTokens") or 0) == 0 or not any(r.startswith("generate:user-model") for r in t["route"]["reasonCodes"])
seq = lambda t: [(c["title"], c.get("section"), c.get("source")) for c in t["retrieval"]["kept"]]
ttl = lambda t: [c["title"] for c in t["retrieval"]["kept"]]
r = dict(rows=len(T), expected=len(ids), missing=[i for i in ids if i not in T], extra=[i for i in T if i not in ids])
r["errors"] = [i for i in ids if i in T and T[i].get("error")]
r["empty"] = [i for i in ids if i in T and not (T[i]["answer"]["text"] or "").strip()]
r["loops"] = [i for i in ids if i in T and loop(T[i]["answer"]["text"] or "")]
dets = [i for i in ids if det(ctl[i])]
r["det_items"] = len(dets)
r["det_text_diff_ctl"] = [i for i in dets if T[i]["answer"]["text"] != ctl[i]["answer"]["text"]]   # expected: the two H2 targets (card answer replaced by an extractive excerpt)
r["det_codes_only_diff_ctl"] = [i for i in dets if T[i]["answer"]["text"] == ctl[i]["answer"]["text"] and T[i]["route"]["reasonCodes"] != ctl[i]["route"]["reasonCodes"]]  # counter changes (headpass:dense:health-dropped-N), same text
r["det_unexpected_text_diff"] = [i for i in r["det_text_diff_ctl"] if i not in ("vit-hlt-001", "vit-hlt-002")]
kd = [i for i in ids if seq(T[i]) != seq(ctl[i])]
td = [i for i in ids if T[i]["answer"]["text"] != ctl[i]["answer"]["text"]]
chg = [i for i in kd if i in td]
r["kept_differs_vs_ctl"] = len(kd); r["text_differs_vs_ctl"] = len(td); r["changed"] = len(chg)
r["kept_differs_text_same"] = [i for i in kd if i not in td]; r["text_differs_kept_same"] = [i for i in td if i not in kd]
r["text_same_kept_same"] = len(ids) - len(set(kd) | set(td))
r["changed_ids"] = chg
# kept identity vs the H1 replay (titles), and vs the H2 replay for the health-strict items (11), combined-aware
idn = [i for i in ids if ttl(T[i]) == [c["title"] for c in rep[i]["keptFull"]]]
r["kept_identity_vs_H1_replay"] = [len(idn), len(ids)]; r["kept_identity_share"] = round(len(idn) / len(ids), 3)
nid = [i for i in ids if i not in idn]
r["kept_not_identical_vs_H1_replay"] = nid
r["of_which_health_strict_H2_sub"] = [i for i in nid if i in h2]
idn2 = [i for i in nid if i in h2 and ttl(T[i]) == [c["title"] for c in h2[i]["keptFull"]]]
r["identical_to_H2_replay_instead"] = idn2
r["kept_identity_share_with_H2_replay_for_health"] = round((len(idn) + len(idn2)) / len(ids), 3)
msid = lambda i, R: collections.Counter(ttl(T[i])) == collections.Counter(c["title"] for c in R[i]["keptFull"])
ms = [i for i in ids if msid(i, rep) or (i in h2 and msid(i, h2))]
r["kept_multiset_identity_vs_H1_or_H2_replay"] = [len(ms), len(ids)]; r["kept_multiset_identity_share"] = round(len(ms) / len(ids), 3); r["kept_multiset_not_identical"] = [i for i in ids if i not in ms]
r["ctl_run_vs_B0_replay_sequence_identity"] = sum(ttl(ctl[i]) == [c["title"] for c in B0[i]["keptFull"]] for i in ids)
r["reason_codes_h12"] = {k: sum(any(c.startswith(k) for c in T[i]["route"]["reasonCodes"]) for i in ids) for k in ("rs:hp", "rs:health-topic-fb", "headpass:")}
m = lambda D, xs, f: round(sum(f(D[i]) for i in xs) / len(xs), 2)
for nm, D in (("h12", T), ("ctl", ctl)):
    r[f"mean_out_tok_{nm}"] = m(D, ids, lambda t: t["timing"].get("outputTokens") or 0); r[f"mean_totalMs_{nm}"] = m(D, ids, lambda t: t["timing"].get("totalMs") or 0)
r["kill"] = bool(r["missing"] or r["errors"] or r["empty"] or r["loops"] or r["det_unexpected_text_diff"])
json.dump(r, open(out + "/sanity.json", "w"), indent=1)
open(out + "/changed.ids", "w").write("\n".join(chg) + "\n"); open(out + "/kept-differs.ids", "w").write("\n".join(kd) + "\n")
print(json.dumps({k: v for k, v in r.items() if k not in ("changed_ids",)}, indent=0))
