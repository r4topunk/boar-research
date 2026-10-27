#!/usr/bin/env python3
"""FACTS-R9 plug adjudication rule (applied identically to the pre-fix and post-fix assets): a plug row is TABLE-WRONG when
none of the reference letters (Wikipedia mains table U Wikivoyage S2) is in the table, or at least half of the table's letters
are in neither reference. Usage: python3 -I plugrule_r9.py <audit.json> <wpcheck.json>"""
import json, sys, re
A = {(r["q"], r["field"]): r for r in json.load(open(sys.argv[1]))["rows"]}
out = []
for x in json.load(open(sys.argv[2])):
    if x["field"] != "plug": continue
    t = set(re.findall(r"Type ([A-N])\b", " ".join(x["table"]))) | ({"D", "G", "M"} if any("British-related" in p for p in x["table"]) else set()) | ({"D", "M"} if any("D/M" in p for p in x["table"]) else set())
    ref = set(re.findall(r"\b([A-O])\b", x.get("wp", ""))) | set(A[(x["q"], "plug")]["ref"]["S2letters"])
    if not ref: continue
    extra = t - ref
    # "D/M" counts as one listed type: extraneous only if neither D nor M is in the references
    units = [{"D", "M"} if "D/M" in p else ({"D", "G", "M"} if "British-related" in p else set(re.findall(r"Type ([A-N])\b", p))) for p in x["table"]]
    bad = [u for u in units if u and not (u & ref)]
    wrong = not (t & ref) or 2 * len(bad) >= len(units)
    if wrong: out.append((x["n"], x["table"], sorted(ref)))
print("plug rows with a reference", sum(1 for x in json.load(open(sys.argv[2])) if x["field"] == "plug" and (x.get("wp") or A[(x["q"], "plug")]["ref"]["S2letters"])), "TABLE-WRONG", len(out))
for o in out: print("  ", o)
