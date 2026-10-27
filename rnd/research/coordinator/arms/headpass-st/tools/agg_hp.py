#!/usr/bin/env python3
"""HEADPASS-ST stage 2 aggregation (0 LLM; component estimate, Haiku 5.5-low only). Estimator = packs-l2/tools/l2_agg.py unchanged
(load/ratios/boot/setstats/paired: per-item bootstrap of the ratio-of-sums difference, B 2000, seed 11, paired on queryId).
Cells: X1 (gen/st-<pack>-cut7-headpass-s42.judgments.jsonl) - S (packs/selftest-runs/st-<pack>-cut7-s42.judgments.jsonl) on the 180:
pooled, SE/topic, per pack, and the declared split from the step-0 replay (runs/split.jsonl: newly_present / nonfact_only / unchanged /
other_changed). No-harm: v0.1 + boar-simplewiki-en ON - OFF (57). Writes aggregates/agg.json. Usage: python3 -I agg_hp.py"""
import json, os, sys, collections, importlib.util, io, contextlib
ARMS = "<workspace>/rnd/research/coordinator/arms"; H = f"{ARMS}/headpass-st"
src = open(f"{ARMS}/packs-l2/tools/l2_agg.py").read().split("cell = sys.argv[1]")[0]  # estimator functions only
ns = {"__file__": f"{ARMS}/packs-l2/tools/l2_agg.py"}; exec(src, ns)
load, setstats, paired, SE, TOPIC = ns["load"], ns["setstats"], ns["paired"], ns["SE"], ns["TOPIC"]
W, N, fam, pk = {}, {}, {}, {}
out = {"estimator": "l2_agg.py: per-item bootstrap ratio-of-sums diff, B 2000, seed 11, paired on queryId", "judge": "claude-haiku-5-5 effort low, N=4 shards, both orders", "packs": {}}
for p in SE + TOPIC:
    w = load(f"{H}/gen/st-{p}-cut7-headpass-s42.judgments.jsonl"); n = load(f"{ARMS}/packs/selftest-runs/st-{p}-cut7-s42.judgments.jsonl")
    ids = sorted(set(w) & set(n))
    if len(ids) != 20: print(f"WARN {p}: n_paired {len(ids)} != 20 (left out)", file=sys.stderr); continue
    out["packs"][p] = {"X1": setstats(w, ids), "S": setstats(n, ids), "paired": paired(w, n, ids)}
    for q in ids: W[q], N[q], fam[q], pk[q] = w[q], n[q], "SE" if p in SE else "topic", p
split = {d["id"]: d["split"] for d in map(json.loads, open(f"{H}/runs/split.jsonl"))}
groups = {"pooled": sorted(W), "SE": sorted(q for q in W if fam[q] == "SE"), "topic": sorted(q for q in W if fam[q] == "topic")}
for k in ("newly_present", "nonfact_only", "unchanged", "other_changed"): groups[f"split:{k}"] = sorted(q for q in W if split[q] == k)
groups["split:changed_all"] = sorted(q for q in W if split[q] != "unchanged")
# Generation-side split (the ON traces' headpass:add:* codes; fact chunks = oracle-facts.json; off_present from the step-0 replay = S's engine path):
# gen:fact_newly = a fact chunk appended and no fact chunk kept under OFF; gen:nonfact_only = fired, no fact chunk appended; gen:not_fired.
FACTS = json.load(open(f"{ARMS}/oracle-st/tools/oracle-facts.json")); offp = {d["id"]: d["off_present"] for d in map(json.loads, open(f"{H}/runs/split.jsonl"))}
gcls = {}
for p in SE + TOPIC:
    for l in open(f"{H}/gen/st-{p}-cut7-headpass-s42.traces.jsonl"):
        t = json.loads(l); q = t["itemId"]; fc = {int(x.rsplit(":", 1)[1]) for x in FACTS[q]["fact_chunks"]}
        app = {int(c.rsplit(":", 1)[1]) for c in (t.get("route") or {}).get("reasonCodes") or [] if c.startswith("headpass:add:")}
        gcls[q] = "not_fired" if not app else ("fact_appended_already_present" if offp[q] else "fact_newly") if fc & app else "nonfact_only"
for k in ("fact_newly", "nonfact_only", "not_fired", "fact_appended_already_present"): groups[f"gen:{k}"] = sorted(q for q in W if gcls.get(q) == k)
out["gen_split_counts"] = dict(collections.Counter(gcls.values()))
out["groups"] = {g: {"X1": setstats(W, ids), "S": setstats(N, ids), "paired": paired(W, N, ids)} for g, ids in groups.items() if ids}
on, off = load(f"{H}/gen/v01sw-cut7-headpass-on-s42.judgments.jsonl"), load(f"{H}/gen/v01sw-cut7-headpass-off-s42.judgments.jsonl")
vid = sorted(set(on) & set(off))
if vid:
    fired = set()
    for l in open(f"{H}/gen/v01sw-cut7-headpass-on-s42.traces.jsonl"):
        t = json.loads(l)
        if any(c.startswith("headpass:add:") for c in (t.get("route") or {}).get("reasonCodes") or []): fired.add(t["itemId"])
    out["v01sw"] = {"all": {"ON": setstats(on, vid), "OFF": setstats(off, vid), "paired": paired(on, off, vid)}}
    fv = sorted(fired & set(vid))
    if fv: out["v01sw"]["fired"] = {"ON": setstats(on, fv), "OFF": setstats(off, fv), "paired": paired(on, off, fv)}
    out["v01sw"]["fired_n_gen"] = len(fired)
json.dump(out, open(f"{H}/aggregates/agg.json", "w"), indent=1)
f = lambda r: f"n={r['paired']['n']:3d} d_raw {r['paired']['d_raw']:+.3f} ({r['paired']['d_raw_ci'][0]:+.3f}..{r['paired']['d_raw_ci'][1]:+.3f}) b/w {r['paired']['items_better_worse'][0]}/{r['paired']['items_better_worse'][1]}"
for g, r in out["groups"].items(): print(f"{g:22s} X1 {r['X1']['raw']:.3f} S {r['S']['raw']:.3f} {f(r)}")
for p, r in out["packs"].items(): print(f"pack {p:20s} X1 {r['X1']['raw']:.3f} S {r['S']['raw']:.3f} {f(r)}")
for g, r in (out.get("v01sw") or {}).items():
    if isinstance(r, dict): print(f"v01sw {g:6s} ON {r['ON']['raw']:.3f} OFF {r['OFF']['raw']:.3f} {f(r)}")
