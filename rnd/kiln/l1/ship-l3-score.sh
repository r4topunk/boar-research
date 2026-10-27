#!/usr/bin/env bash
# Ship L3 scoring (same metric as E3: plan/floor_metrics.py frozen, --decline-ratio 0.306, stratified bootstrap seed 11).
# Views: held-out 110 (headline) · full = E3 view (b) 170 ids (v0.1 public + v0.2-new) · EN-only subset of it. Aggregates only.
set -uo pipefail
B=<workspace>; V2=$B/blind/bench-v02/live/v0.2; OUT=$B/blind/bench-v02/runs-ship; E3=$B/blind/bench-v02/runs-e3
FM=$V2/plan/floor_metrics.py
for s in 42 43; do
  cat $OUT/ship-v02-s$s.traces.jsonl $OUT/ship-v01-s$s.traces.jsonl > $OUT/ship-all-s$s.traces.jsonl
  cat $OUT/ship-v02-s$s.judgments.jsonl $OUT/ship-v01-s$s.judgments.jsonl > $OUT/ship-all-s$s.judgments.jsonl
done
python3 - "$B" "$OUT" <<'PY'
import json, sys
B, OUT = sys.argv[1:]
lang = {}
for l in open(f"{B}/blind/bench-v02/live/v0.2/questions.v02-new.jsonl"): r = json.loads(l); lang[r["id"]] = r.get("lang")
for f in ("questions.public.jsonl", "safety/track.v0.3.jsonl"):
    for l in open(f"{B}/boar-eval/bench/v0.1/{f}"): r = json.loads(l); lang[r["id"]] = r.get("lang")
ids = open(f"{B}/blind/bench-v02/runs-e3/v02-all.ids").read().split()  # E3 view (b): v0.1 public 60 + v0.2-new 110
en = [i for i in ids if (lang.get(i) or "").lower().startswith("en")]
open(f"{OUT}/ship-all.en.ids", "w").write("\n".join(en) + "\n")
print(f"full {len(ids)} items, EN {len(en)}, non-EN {len(ids) - len(en)} (unknown lang {sum(1 for i in ids if i not in lang)})")
PY
echo "== HELD-OUT v0.2-new 110 (headline; E3 main was raw 0.506, 0.475-0.538)"
python3 $FM --runs ship-v02-s42 ship-v02-s43 --dir $OUT --decline-ratio 0.306 --questions $V2/questions.v02-new.jsonl > $OUT/ship-heldout.floor.json; cat $OUT/ship-heldout.floor.json
echo "== FULL (E3 view b: v0.1 public 60 + v0.2-new 110 = 170 ids; E3 main was 0.5083, 0.4796-0.5354, n=167)"
python3 $FM --runs ship-all-s42 ship-all-s43 --dir $OUT --decline-ratio 0.306 --questions $E3/v02-all.categories.jsonl --ids $E3/v02-all.ids > $OUT/ship-all.floor.json; cat $OUT/ship-all.floor.json
echo "== EN-only subset of the 170"
python3 $FM --runs ship-all-s42 ship-all-s43 --dir $OUT --decline-ratio 0.306 --questions $E3/v02-all.categories.jsonl --ids $OUT/ship-all.en.ids > $OUT/ship-all-en.floor.json; cat $OUT/ship-all-en.floor.json
