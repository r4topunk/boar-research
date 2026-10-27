#!/usr/bin/env python3
"""check_judgments.py <judgments.jsonl> <ids file> [label]  -- fail-closed completeness check of a judge output (FAILCLOSED-2026-10-11).
Passes (rc 0) only if: the file exists; its sidecar <file minus .jsonl>.missing (written by shard_judge.sh) is absent or empty; every id in the ids file
(whitespace/newline separated) has an ok row in BOTH orders (boarA, boarB); and the number of rows for those ids is exactly 2 x ids (no duplicates).
Otherwise rc 1 and the ids that fail are named on stdout. Prints one summary line either way. Reads no LLM, writes nothing."""
import json, os, sys
p, idf = sys.argv[1], sys.argv[2]; label = sys.argv[3] if len(sys.argv) > 3 else os.path.basename(p)
if not os.path.exists(p): print(f"CHECK FAIL {label}: {p} does not exist"); sys.exit(1)
want = [x for x in open(idf).read().split() if x]; W = set(want)
rows = [json.loads(l) for l in open(p) if l.strip()]; rows = [r for r in rows if r.get("queryId") in W]
ok = {(r["queryId"], r["order"]) for r in rows if r.get("ok")}
missing = [i for i in want if (i, "boarA") not in ok or (i, "boarB") not in ok]
side = p[:-6] + ".missing" if p.endswith(".jsonl") else p + ".missing"
side_ids = [x for x in open(side).read().split() if x] if os.path.exists(side) else []
bad = []
if missing: bad.append(f"missing ids ({len(missing)}): {','.join(missing)}")
if len(rows) != 2 * len(want): bad.append(f"rows {len(rows)} != 2 x ids {2 * len(want)}")
if side_ids: bad.append(f"sidecar {os.path.basename(side)} lists {len(side_ids)}: {','.join(side_ids)}")
print(f"{'CHECK FAIL' if bad else 'check ok'} {label}: ids={len(want)} rows={len(rows)} expected={2 * len(want)}" + ("".join(" | " + b for b in bad)))
sys.exit(1 if bad else 0)
