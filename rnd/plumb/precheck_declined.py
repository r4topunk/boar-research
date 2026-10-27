#!/usr/bin/env python3
"""OBSOLETE (2026-09-30 15:0x): superseded by rnd/lantern/tools/precheck.py v2 (refused status + grading v2). Kept for the record.
Lantern's precheck (rnd/lantern/tools/precheck.py) plus the app's own `declined` flag.
The upstream refusal regex misses BOAR's refusal strings ("I didn't find this in this phone's library.",
"The passages found don't support this answer."), so declined rows land in fail-missing. Here a declined row is
pass-refused when the item has refuse_ok, else fail-refused. Everything else is unchanged.
Usage: precheck_declined.py <runs.jsonl> --questions <questions.jsonl> [--subset <subset.json>] [--json out.json]"""
import argparse, json, re

REFUSAL = re.compile(r"(don't|do not|cannot|can't) (have|find|cover)|not (in|covered by) (my|the) (offline )?(sources|packs)|no (offline )?source", re.I)
ap = argparse.ArgumentParser()
ap.add_argument("runs"); ap.add_argument("--questions", required=True); ap.add_argument("--subset"); ap.add_argument("--json")
a = ap.parse_args()
qs = {q["id"]: q for q in map(json.loads, open(a.questions))}
keep = set(json.load(open(a.subset))["ids"]) if a.subset else set(qs)
rows = {r["queryId"]: r for r in map(json.loads, open(a.runs)) if r.get("queryId") in keep}
res = []
for qid in sorted(keep):
    g = qs[qid].get("grading", {}); r = rows.get(qid)
    if g.get("type") == "venue-list": continue
    if not r: res.append({"id": qid, "v": "missing", "why": ""}); continue
    t = (r.get("answer") or "").lower()
    bad = [f for grp in g.get("forbid", []) for f in grp if f.lower() in t]
    refused = bool(r.get("declined")) or bool(REFUSAL.search(t))
    miss = [grp for grp in g.get("must_any", []) if not any(k.lower() in t for k in grp)]
    if not t.strip(): v = "empty"
    elif bad: v = "confident-wrong"
    elif refused and g.get("refuse_ok"): v = "pass-refused"
    elif refused: v = "fail-refused"
    elif miss: v = "fail-missing"
    else: v = "pass"
    res.append({"id": qid, "category": qs[qid]["category"], "v": v, "why": ";".join(bad) or ";".join(m[0] for m in miss)})
n = len(res); cnt = {}
for x in res: cnt[x["v"]] = cnt.get(x["v"], 0) + 1
for x in res: print(f"{x['id']}\t{x['v']}\t{x['why']}")
passed = cnt.get("pass", 0) + cnt.get("pass-refused", 0)
print(f"\nn={n} pass={passed} ({passed/max(n,1):.0%}) confident-wrong={cnt.get('confident-wrong',0)} ({cnt.get('confident-wrong',0)/max(n,1):.0%}) {cnt}")
if a.json: json.dump(res, open(a.json, "w"), indent=1)
