#!/usr/bin/env bash
# exp-08b bisect step for `git bisect run`: tests HEAD of the current worktree on the 3 lost items.
# bad (exit 1) = vit-hlt-001 or vit-hlt-002 answered (not declined) with no shown source. good (exit 0) otherwise.
# Also prints vit-trv-003 status (informative). Exit 125 = skip (setup/run failed).
set -uo pipefail
HERE=<workspace>/rnd/kiln/exp-08b-ios-main-regression
SHA=$(git rev-parse --short=8 HEAD)
bash "$HERE/setup.sh" "$SHA" >/dev/null 2>&1 || exit 125
bash "$HERE/run.sh" "$SHA" -ids3 "--ids vit-hlt-001,vit-hlt-002,vit-trv-003" || exit 125
python3 - "$HERE/runs/x8b-$SHA-ids3.jsonl" "$SHA" <<'PY'
import json, sys
rows = {r["id"]: r for r in map(json.loads, open(sys.argv[1]))}
if len(rows) != 3 or any(r.get("error") for r in rows.values()): sys.exit(125)
def mem(r): return not (r.get("flags") or {}).get("declined") and not r.get("shownSources")
st = {i: ("MEMORY" if mem(r) else "declined" if (r.get("flags") or {}).get("declined") else f"answered+{len(r['shownSources'])}src") for i, r in rows.items()}
bad = mem(rows["vit-hlt-001"]) or mem(rows["vit-hlt-002"])
print(f"[bisect] {sys.argv[2]} {'BAD' if bad else 'GOOD'} {st}", flush=True)
open("<workspace>/rnd/kiln/exp-08b-ios-main-regression/bisect.log", "a").write(f"{sys.argv[2]} {'BAD' if bad else 'GOOD'} {st}\n")
sys.exit(1 if bad else 0)
PY
