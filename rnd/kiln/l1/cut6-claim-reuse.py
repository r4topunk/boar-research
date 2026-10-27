#!/usr/bin/env python3
"""Cut 6 claim runs: identical-text verdict reuse (CLAIM-RUNS-cut6.md "Judge economy"). Single source = the cut 3 claim run of the SAME seed
(blind/.../runs-cut3). For each item whose cut 6 answer text is byte-identical to the cut 3 answer text, copy that item's two ok judgment rows
(both orders) into the cut 6 judgments file (system/runId/arm relabelled, reusedFrom added); judge.mjs then resumes and judges only the rest.
Usage: cut6-claim-reuse.py <c6 traces> <c3 traces> <c3 judgments> <c6 judgments out> <system label>. Prints counts only (no text)."""
import json, sys
c6t, c3t, c3j, out, system = sys.argv[1:6]
rd = lambda p: [json.loads(l) for l in open(p) if l.strip()]
T6 = {t["itemId"]: t for t in rd(c6t) if not t.get("error")}
T3 = {t["itemId"]: t for t in rd(c3t) if not t.get("error")}
J3 = {}
for r in rd(c3j):
    if r.get("ok"): J3.setdefault(r["queryId"], {})[r["order"]] = r
try: have = {(r["queryId"], r["order"]) for r in rd(out) if r.get("ok")}
except FileNotFoundError: have = set()
src = c3j.split("/blind/", 1)[-1]
ident = reused = 0; changed = []
with open(out, "a") as w:
    for i, t in T6.items():
        if i in T3 and t["answer"]["text"] == T3[i]["answer"]["text"] and set(J3.get(i, {})) == {"boarA", "boarB"}:
            ident += 1
            for o, r in J3[i].items():
                if (i, o) in have: continue
                r = dict(r); r.update(system=system, runId=t["runId"], arm=t["engine"]["arm"], commit=t["engine"]["commit"], reusedFrom=src)
                w.write(json.dumps(r) + "\n"); reused += 1
        else: changed.append(i)
print(f"reuse {system}: items {len(T6)} identical-text {ident} changed/new {len(changed)} judgment rows reused {reused} (judge calls to make = {2 * len(changed)})")
json.dump({"identical": ident, "changed": len(changed), "changed_ids": sorted(changed), "reused_rows": reused}, open(out + ".reuse.json", "w"))
