#!/usr/bin/env python3
"""cmp5.py <ctl.traces> <arm.traces> [--ids-out file]: CUT5-SPEED G2 identity + G3 retrieval time.
Identity: answer text, route tier, retrieved passages (raw/kept/dropped as (title, section, source) lists, in order; traces carry no chunk id).
Reason codes are compared with route-gate:* removed (a skipped gate has no verdict codes). Prints per-item diffs and totals."""
import json, sys, statistics
ld = lambda p: {t["itemId"]: t for t in map(json.loads, open(p))}
a, b = ld(sys.argv[1]), ld(sys.argv[2])
def pas(t):
    r = t.get("retrieval") or {}
    return [[(x.get("title"), x.get("section"), x.get("source")) for x in (r.get(k) or [])] for k in ("raw", "kept", "dropped")]
def codes(t): return [c for c in t["route"]["reasonCodes"] if not c.startswith("route-gate:")]
def rms(t): return (t.get("timing") or {}).get("retrievalMs")
def gate(t): return any(e.get("kind") == "route-gate" for e in t.get("events", []))
n = txt = tier = pid = cod = 0; diffs = []
sa = sb = 0.0; na = nb = 0; skipped = []; stages = {}
for k, x in a.items():
    y = b.get(k)
    if y is None: print("MISSING in arm:", k); continue
    n += 1
    d = []
    if x["answer"]["text"] != y["answer"]["text"]: txt += 1; d.append("text")
    if x["route"]["tier"] != y["route"]["tier"]: tier += 1; d.append("tier")
    if pas(x) != pas(y): pid += 1; d.append("passages")
    if codes(x) != codes(y): cod += 1; d.append("codes")
    if d: diffs.append((k, d))
    if rms(x) is not None: sa += rms(x); na += 1
    if rms(y) is not None: sb += rms(y); nb += 1
    if gate(x) and not gate(y): skipped.append(k)
    for e in y.get("events", []):
        rs = (e.get("receipt") or {}).get("retrievalStages")
        if rs:
            for f in ("zstdMs", "utf8Ms", "sqlMs", "corpusSqlMs", "corpusScoreMs", "embedMs", "totalMs", "sqlCalls", "zstdBlocks"): stages[f] = stages.get(f, 0) + (rs.get(f) or 0)
            for br, v in (rs.get("branches") or {}).items(): stages["branch." + br] = stages.get("branch." + br, 0) + v
            stages["_rows"] = stages.get("_rows", 0) + 1
            stages["_cacheHit"] = stages.get("_cacheHit", 0) + (1 if rs.get("corpusCacheHit") else 0)
print(f"items {n}: text diff {txt}, tier diff {tier}, passages diff {pid}, reason-code diff (excl. route-gate) {cod}")
for k, d in diffs: print("  DIFF", k, d)
print(f"retrieval wall ms (timing.retrievalMs) sum: ctl {sa:.0f} ({na} items), arm {sb:.0f} ({nb} items), ratio arm/ctl {sb / sa:.3f}" if sa else "no retrieval ms")
print(f"gate called in ctl but not arm (skipped): {len(skipped)}", skipped if len(sys.argv) > 3 else "")
gc = sum(1 for t in a.values() if gate(t)); ga = sum(1 for t in b.values() if gate(t))
print(f"gate events: ctl {gc}, arm {ga}")
if stages: print("arm retrievalStages sums:", {k: round(v, 1) for k, v in stages.items()})
