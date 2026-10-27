#!/usr/bin/env python3
"""Blind-safe coverage count for the first-aid cards: prints ONLY per-condition counts and totals, never item ids or text.
Usage (coordinator): python3 coverage.py path/to/set.jsonl [--danger-field danger]
Counts, over items whose `danger` is true (or category in health/danger/danger-situation): which card condition the frozen
regex picks (unique match), how many match >1 condition (no card), and how many match none (generic card)."""
import json, sys, collections
from terms import regex_condition
path = sys.argv[1]
C = collections.Counter(); n = 0
for line in open(path):
    r = json.loads(line)
    is_danger = r.get("danger") is True or r.get("category") in ("health", "danger", "danger-situation")
    if not is_danger: continue
    n += 1
    p = regex_condition(r.get("question") or r.get("query") or "")
    C["(none)" if p is None else "(multi)" if p.startswith("MULTI") else p] += 1
print(f"danger items: {n}")
for k, v in C.most_common(): print(f"  {k:12} {v}")
print(f"card coverage (unique condition): {n - C['(none)'] - C['(multi)']}/{n}")
