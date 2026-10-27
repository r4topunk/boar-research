#!/usr/bin/env python3
"""MINISTRAL3-3B stage-2 verdict (0 LLM). Usage: python3 -I stage2_verdict.py <candidate MAIN agg.json> <lpctl-K0-main-s42.json>
Frozen in MINISTRAL-criterion.md. U delta + CI are read from the candidate aggregate's paired deltas vs the mini MAIN control (agg_run.py,
bootstrap B 2000 seed 11). CE-unwarned (CEu, null-cal/tools/labels.py) rate change = mean over the 97 items of CEu(candidate) - CEu(control),
with a paired bootstrap (B 2000, seed 11) for information. Default-mode U (refused R scores 0) is reported, not gated.
PASS iff U delta >= +0.03 and U CI low > 0 and CEu rate change <= +0.02."""
import json, sys, os, random
sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/null-cal/tools"); from labels import label
c, k = (json.load(open(p)) for p in sys.argv[1:3]); C, K = c["items"], k["items"]; ids = sorted(K)
assert set(C) == set(K) and len(ids) == 97, "aggregates must cover the same 97 MAIN items"
du = c["deltas"]["U"] if "deltas" in c else c["vs_control"]["deltas"]["U"]
LC = {i: label(C[i]) for i in ids}; LK = {i: label(K[i]) for i in ids}
ceu = lambda L, xs: sum(L[i]["CEu"] for i in xs) / len(xs)
udm = lambda L, xs: sum(0 if L[i]["R"] else L[i]["s"] for i in xs) / sum(L[i]["sref"] for i in xs)
rnd = random.Random(11); bc, bu = [], []
for _ in range(2000):
    s = [rnd.choice(ids) for _ in ids]; bc.append(ceu(LC, s) - ceu(LK, s)); bu.append(udm(LC, s) - udm(LK, s))
bc.sort(); bu.sort()
dce = ceu(LC, ids) - ceu(LK, ids)
ok = du["d"] >= 0.03 and du["ci"][0] > 0 and dce <= 0.02
print(f"stage2 K0 MAIN 97: U {du['d']:+.4f} {du['ci']} (need >= +0.03, CI low > 0) | CEu rate {ceu(LK, ids):.3f} -> {ceu(LC, ids):.3f} ({dce:+.4f} [{bc[50]:+.4f}, {bc[1949]:+.4f}], need <= +0.02)"
      f" | default-mode U {udm(LK, ids):.4f} -> {udm(LC, ids):.4f} ({udm(LC, ids) - udm(LK, ids):+.4f} [{bu[50]:+.4f}, {bu[1949]:+.4f}], report only) -> {'PASS' if ok else 'FAIL'}")
