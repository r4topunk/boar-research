#!/usr/bin/env python3
"""CE-OPUS-RU set builder (0 calls). python3 -I prep.py
Decisive RU K3 items at t = 0.919 from ../analysis.json (frozen RU output): control CE-unwarned (shownC and Haiku corr <= 1.5),
gate-refused (shownC, gated, P_FAIL >= 0.919), supported-correct (shownC, gated, SUPPORTED, Haiku corr >= 4), CE-unwarned still shown by R.
Writes in/set.json and in/<unit>.ids (unit -> MacBook LITEPACKS K3 traces + bench dir)."""
import json, collections
A = "<workspace>/rnd/research/coordinator/arms"; H = f"{A}/refuse-unsupported"; C = f"{H}/ce-opus-ru"
R = json.load(open(f"{H}/analysis.json"))["rows"]; t = 0.919
ce = [r["key"] for r in R if r["shownC"] and r["corr"] <= 1.5]
ref = [r["key"] for r in R if r["shownC"] and r["gated"] and r["s_gate"] >= t]
sc = [r["key"] for r in R if r["shownC"] and r["gated"] and r["sup"] is True and r["corr"] >= 4]
still = [k for k in ce if k not in ref]
u = sorted(set(ce) | set(ref) | set(sc))
def unit(k):
    if k.startswith(("vit-", "lan-")): return "v01"
    if k.startswith("st-qa-money-se-"): return "qa-money-se"
    if k.startswith("st-qa-cooking-se-"): return "qa-cooking-se"
    return k[3:].rsplit("-", 1)[0]
by = collections.defaultdict(list)
for k in u: by[unit(k)].append(k)
for un, ks in by.items(): open(f"{C}/in/{un}.ids", "w").write("".join(x + "\n" for x in ks))
json.dump(dict(control_ce_unwarned=ce, gate_refused=ref, supported_correct=sc, ce_unwarned_still_shown_R=still, union=u,
               units={k: len(v) for k, v in by.items()}), open(f"{C}/in/set.json", "w"), indent=1)
print(len(ce), len(ref), len(sc), len(still), "union", len(u), dict((k, len(v)) for k, v in by.items()))
