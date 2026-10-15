#!/usr/bin/env python3
"""HEADPASS-ST precheck (0 LLM): share of the 180 ON generations whose model input changed vs S (arms/packs/selftest-runs/st-<pack>-cut7-s42.traces.jsonl):
changed = retrieval.kept (title, section) list differs OR timing.promptTokens differs. Bar >= 0.20 (else: do not judge, rc 8).
Also: agreement with the step-0 replay (runs/split.jsonl: unchanged vs changed) and headpass:add counts from the ON traces' reasonCodes.
Usage: python3 -I precheck_hp.py [--out aggregates/precheck.json]"""
import json, sys, collections
A = "$BOAR_WS/rnd/research/coordinator/arms"; G = f"{A}/headpass-st/gen"
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se", "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
tr = lambda p: {(t := json.loads(l))["itemId"]: t for l in open(p) if l.strip()}
kept = lambda t: [(s.get("title"), s.get("section")) for s in (t.get("retrieval") or {}).get("kept") or []]
pt = lambda t: (t.get("timing") or {}).get("promptTokens")
split = {d["id"]: d["split"] for d in map(json.loads, open(f"{A}/headpass-st/runs/split.jsonl"))}
n = ch = 0; agree = collections.Counter(); per = {}; adds = 0; fired = 0; errs = 0
for p in PACKS:
    S = tr(f"{A}/packs/selftest-runs/st-{p}-cut7-s42.traces.jsonl"); O = tr(f"{G}/st-{p}-cut7-headpass-s42.traces.jsonl")
    c = 0
    for i in S:
        s, o = S[i], O[i]; n += 1; errs += bool(o.get("error"))
        d = kept(s) != kept(o) or pt(s) != pt(o); c += d; ch += d
        a = [x for x in (o.get("route") or {}).get("reasonCodes") or [] if x.startswith("headpass:add:")]; adds += len(a); fired += bool(a)
        agree[(split[i] != "unchanged", d)] += 1
    per[p] = c
out = {"n": n, "changed": ch, "share": round(ch / n, 3), "bar": 0.2, "pass": ch / n >= 0.2, "per_pack": per, "errors": errs,
       "fired_traces": fired, "appended_traces": adds, "replay_changed_vs_gen_changed": {f"replay_{'chg' if a else 'same'}|gen_{'chg' if b else 'same'}": v for (a, b), v in agree.items()}}
print(json.dumps(out))
if "--out" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
sys.exit(0 if out["pass"] else 8)
