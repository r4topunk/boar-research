#!/usr/bin/env python3
"""changed_items.py <dir>: before/after rubric mean (judge.v1-med, both orders) for each item whose text changed."""
import sys, json
sys.argv = [sys.argv[0], sys.argv[1], "ctl", "arm"]
exec(open(__file__.replace("changed_items.py", "analyze.py")).read().split("# paired bootstrap")[0])
for s in SEEDS:
    c, a = res[("ctl", s)], res[("arm", s)]
    for i in sorted(a["traces"]):
        if a["traces"][i]["answer"]["text"] != c["traces"][i]["answer"]["text"]:
            pc, pa = c["rep"]["pairs"][i], a["rep"]["pairs"][i]
            print(f"s{s} {i}: boarMean {pc['boarMean']:.3f} -> {pa['boarMean']:.3f} (ref {pc['refMean']:.3f}); correctness {pc['correctness']:.2f} -> {pa['correctness']:.2f}; keys {sorted(k for k in pa if k not in ('boarMean','refMean'))}")
            print("   rubric ctl", {k: v for k, v in pc.items() if k not in ('boarMean', 'refMean')})
            print("   rubric arm", {k: v for k, v in pa.items() if k not in ('boarMean', 'refMean')})
