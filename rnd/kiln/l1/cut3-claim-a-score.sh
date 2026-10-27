#!/usr/bin/env bash
# Claim run A scoring (frozen plan; same metric scripts as ship-l3-score.sh). Aggregates only. Writes json under blind/bench-v02/runs-cut3/.
set -uo pipefail
B=<workspace>; V2=$B/blind/bench-v02/live/v0.2; OUT=$B/blind/bench-v02/runs-cut3; SH=$B/blind/bench-v02/runs-ship; E3=$B/blind/bench-v02/runs-e3
PL=$B/boar-eval/bench/v0.2/plan; FM=$PL/floor_metrics.py; PG=$PL/paired_gap.py
for s in 42 43; do
  cat $OUT/cut3-v02-s$s.traces.jsonl $OUT/cut3-v01-s$s.traces.jsonl > $OUT/cut3-all-s$s.traces.jsonl
  cat $OUT/cut3-v02-s$s.judgments.jsonl $OUT/cut3-v01-s$s.judgments.jsonl > $OUT/cut3-all-s$s.judgments.jsonl
done
EN=$SH/ship-all.en.ids
python3 $FM --runs cut3-v02-s42 cut3-v02-s43 --dir $OUT --decline-ratio 0.306 --questions $V2/questions.v02-new.jsonl > $OUT/cut3-heldout.floor.json
python3 $FM --runs cut3-all-s42 cut3-all-s43 --dir $OUT --decline-ratio 0.306 --questions $E3/v02-all.categories.jsonl --ids $E3/v02-all.ids > $OUT/cut3-all.floor.json
python3 $FM --runs cut3-all-s42 cut3-all-s43 --dir $OUT --decline-ratio 0.306 --questions $E3/v02-all.categories.jsonl --ids $EN > $OUT/cut3-all-en.floor.json
# paired: one scratch dir with symlinks (cut3, ship, e3 judgments), restricted to the 170 EN ids by the E3 files' own item set; filter explicitly anyway
P=$OUT/paired; rm -rf $P; mkdir -p $P
python3 - "$OUT" "$SH" "$E3" "$P" "$EN" <<'PY'
import json, sys
OUT, SH, E3, P, EN = sys.argv[1:]
ids = set(open(EN).read().split())
src = {f"cut3-s{s}": f"{OUT}/cut3-all-s{s}" for s in (42, 43)} | {f"ship-s{s}": f"{SH}/ship-all-s{s}" for s in (42, 43)} | {f"e3-s{s}": f"{E3}/v02all-s{s}" for s in (42, 43)}
for k, p in src.items():
    n = 0
    with open(f"{P}/{k}.judgments.jsonl", "w") as w:
        for l in open(p + ".judgments.jsonl"):
            if l.strip() and json.loads(l)["queryId"] in ids: w.write(l); n += 1
    print(f"{k}: {n} judgment rows on the 170 EN ids")
PY
for b in ship e3; do
  python3 $PG --dir $P --a cut3-s42 cut3-s43 --b $b-s42 $b-s43 --questions $E3/v02-all.categories.jsonl --decline-ratio 0.306 > $OUT/paired-cut3-vs-$b.json
done
python3 - "$P" "$B/boar-eval" <<'PY'
import json, sys, collections
sys.path.insert(0, sys.argv[2])
from scorers import stats
P = sys.argv[1]; K = ("correctness", "completeness", "usefulness"); mr = lambda s: sum(s[k] for k in K) / 3
def load(run):
    J = collections.defaultdict(list)
    for l in open(f"{P}/{run}.judgments.jsonl"):
        r = json.loads(l)
        if r.get("ok"): J[r["queryId"]].append(r["mapped"])
    return {q: ((mr(v[0]["boar"]) + mr(v[1]["boar"])) / 2, (mr(v[0]["ref"]) + mr(v[1]["ref"])) / 2) for q, v in J.items() if len(v) == 2}
for b in ("ship", "e3"):
    A = [load("cut3-s42"), load("cut3-s43")]; Bb = [load(f"{b}-s42"), load(f"{b}-s43")]
    n = len(set.intersection(*[set(d) for d in A + Bb]))
    m = stats.mde_block(A, Bb, n_items=n); print(f"MDE vs {b}: n={n} mde={m['mde']:.4f} se={m['se']:.4f}")
PY
echo "== held-out"; cat $OUT/cut3-heldout.floor.json; echo "== full170"; cat $OUT/cut3-all.floor.json; echo "== EN"; cat $OUT/cut3-all-en.floor.json
for b in ship e3; do echo "== paired vs $b"; cat $OUT/paired-cut3-vs-$b.json; done
