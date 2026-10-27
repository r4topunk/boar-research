#!/usr/bin/env python3
"""MIN3CITE projected Pixel 8a answer time (0 LLM). Usage: pixel_proj.py <candidate traces.jsonl> <K0|K1> [ids file]
Per generated item (outputTokens > 0): time = outputTokens / decode + promptTokens / prefill (full prefill, no prefix cache: upper bound).
Ministral: decode 6.5-8.7 tok/s (ONBOARDING stage 0: 12-16 x tg ratio 0.541), prefill 85 x 0.483 = 41.1 tok/s (pp512 ratio r2 86/178).
Qwen3-1.7B control (same items, mini control traces): decode 12-16 tok/s (measured), prefill 85 tok/s (arms/litelat). Reports p50 / p90."""
import json, sys, statistics as st
A = "<workspace>/rnd/research/coordinator/arms"
tr, K = sys.argv[1], sys.argv[2]; ids = set(open(sys.argv[3]).read().split()) if len(sys.argv) > 3 else None
C = {r["itemId"]: r for r in map(json.loads, open(tr)) if not ids or r["itemId"] in ids}
ctl = {}
for p in [f"{A}/lp-screens/control/traces/lpctl-{K}-main-s42.traces.jsonl", f"{A}/null-cal/control/traces/poolctl-{K}-st180-s42.traces.jsonl"]:
    for r in map(json.loads, open(p)): ctl[r["itemId"]] = r
def q(xs, p): xs = sorted(xs); return xs[min(len(xs) - 1, int(round(p * (len(xs) - 1))))]
def proj(rows, dec, pre):
    return [r["timing"]["outputTokens"] / dec + (r["timing"].get("promptTokens") or 0) / pre for r in rows if (r["timing"].get("outputTokens") or 0) > 0]
cand = list(C.values()); base = [ctl[i] for i in C if i in ctl]
out = []
for name, rows, (dlo, dhi), pre in [("ministral", cand, (6.5, 8.7), 41.1), ("qwen3-1.7b ctl", base, (12, 16), 85.0)]:
    slow, fast = proj(rows, dlo, pre), proj(rows, dhi, pre)
    out.append(f"{name}: n {len(slow)} p50 {q(fast, .5):.1f}-{q(slow, .5):.1f} s, p90 {q(fast, .9):.1f}-{q(slow, .9):.1f} s")
print(" | ".join(out))
