#!/usr/bin/env python3
"""RETBENCH table printer: python3 -I table.py [--md] -> one row per aggregates/*.json (identity files skipped), ranked by the SWEEP rule."""
import json, glob, os
RB = "<workspace>/rnd/research/coordinator/arms/retbench"
B = json.load(open(RB + "/aggregates/base.json"))
rows = []
for f in sorted(glob.glob(RB + "/aggregates/*.json")):
    n = os.path.basename(f)[:-5]
    if n.startswith("identity") or n in ("sweep",): continue
    o = json.load(open(f)); v = o.get("vs_base", {}); M = o.get("main", {}); S = o.get("st", {})
    if not M: continue
    cx = round(M["ctx"]["p50"] / B["main"]["ctx"]["p50"], 3)
    hl = v.get("health_losses", 0); elig = hl == 0 and cx <= 1.15
    rows.append(dict(name=n, facts=M["facts"], d=M["facts"] - B["main"]["facts"], cm=M["cm"], v01=M["v01"], g=len(v.get("main", {}).get("gained", [])), l=len(v.get("main", {}).get("lost", [])),
                     st_fact=S.get("fact"), st_own=S.get("own_kept"), st_raw=S.get("own_raw"), topics=o.get("topics", {}).get("expected_in_kept"), f8=o.get("f8", {}).get("survived"), ls=o.get("ls", {}).get("survived"),
                     hl=hl, cx=cx, ctx=M["ctx"]["p50"], bq=round(M["bytes"]["per_q"] / 1e6, 2) if M["bytes"]["per_q"] else None, ms=M["ms_p50"], crowd=S.get("crowd_all"), elig=elig))
rows.sort(key=lambda r: (not r["elig"], -r["facts"], -(r["st_fact"] or 0), r["ctx"]))
print("| config | MAIN facts (d) | cm / v01 | +/- | ST fact | ST own kept / raw | TOPICS | F8 surv | LS surv | health losses | ctx p50 (x base) | ST crowd | MB/q | ms p50 | eligible |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r['name']} | {r['facts']} ({r['d']:+d}) | {r['cm']} / {r['v01']} | +{r['g']}/-{r['l']} | {r['st_fact']} | {r['st_own']} / {r['st_raw']} | {r['topics']} | {r['f8']} | {r['ls']} | {r['hl']} | {r['ctx']} ({r['cx']}) | {r['crowd']} | {r['bq']} | {r['ms']} | {'yes' if r['elig'] else 'no'} |")
json.dump(rows, open(RB + "/aggregates/sweep.json", "w"), indent=1)
