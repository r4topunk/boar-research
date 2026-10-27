#!/usr/bin/env python3
"""Deterministic pre-check of BOAR answers against vitalik-evalset grading (must_any / forbid / refuse_ok).
Usage: python3 tools/precheck.py <runs.jsonl> [--questions handoff/questions.vitalik-lantern.jsonl] [--subset handoff/subset.factual.vitalik-lantern.json]
Runs file: eval/ judge format (one row per question with queryId + answer). Venue-list items are skipped (need the OSM grader)."""
import json, sys, re, argparse
REFUSAL = re.compile(r"(don't|do not|cannot|can't) (have|find|cover)|not (in|covered by) (my|the) (offline )?(sources|packs)|no (offline )?source", re.I)
ap = argparse.ArgumentParser(); ap.add_argument("runs"); ap.add_argument("--questions", default="handoff/questions.vitalik-lantern.jsonl"); ap.add_argument("--subset")
a = ap.parse_args()
qs = {q["id"]: q for q in map(json.loads, open(a.questions))}
keep = set(json.load(open(a.subset))["ids"]) if a.subset else set(qs)
rows = {r["queryId"]: r for r in map(json.loads, open(a.runs)) if r.get("queryId") in keep}
res = []
for qid in sorted(keep):
    g = qs[qid].get("grading", {}); r = rows.get(qid)
    if g.get("type") == "venue-list": continue
    if not r: res.append((qid, "missing", "")); continue
    t = (r.get("answer") or "").lower()
    bad = [f for grp in g.get("forbid", []) for f in grp if f.lower() in t]
    refused = bool(REFUSAL.search(t))
    miss = [grp for grp in g.get("must_any", []) if not any(k.lower() in t for k in grp)]
    if not t.strip(): v = "empty"
    elif bad: v = "confident-wrong"
    elif refused and g.get("refuse_ok"): v = "pass-refused"
    elif refused: v = "fail-refused"
    elif miss: v = "fail-missing"
    else: v = "pass"
    res.append((qid, v, ";".join(bad) or ";".join(m[0] for m in miss)))
n = len(res); cnt = {}
for _, v, _ in res: cnt[v] = cnt.get(v, 0) + 1
for qid, v, why in res: print(f"{qid}\t{v}\t{why}")
passed = cnt.get("pass", 0) + cnt.get("pass-refused", 0)
print(f"\nn={n} pass={passed} ({passed/max(n,1):.0%}) confident-wrong={cnt.get('confident-wrong',0)} ({cnt.get('confident-wrong',0)/max(n,1):.0%}) {cnt}")
