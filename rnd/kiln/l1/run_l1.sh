#!/usr/bin/env bash
# Kiln L1 runner (fast-loop.md level 1): one Compass L1 slice, 1 rep, desktop-node on the mini, judged (judge.v1, Opus,
# both orders, CLI login `claude -p`), scored with safety rules v0.7. No freeze at L1: commit + slice ids are logged.
#   rnd/kiln/l1/run_l1.sh <slice> <label> <config.json> [--seed 42] [--arm <arm>] [--no-judge] [-- <extra run.sh args>]
#   slice  = a key of compass/fast-loop/l1-slices.json (retrieval-inkit | outofkit-quality | routing-chat | safety)
#   config = an EngineConfig json (makeRequests RunConfig); its "arm" must match a tree from setup.sh (--arm only to override)
# Out: boar-eval/runs/kiln/l1/<label>-<slice>-s<seed>/ {questions,requests,traces,judgments}.jsonl, score.json, summary.txt
set -euo pipefail
BOAR=<workspace>; BE_REPO=${BOAR}/boar-eval
SLICES=${BOAR}/rnd/research/compass/fast-loop/l1-slices.json
SLICE="${1:?slice}"; LABEL="${2:?label}"; CFG="${3:?config.json}"; shift 3
SEED=42; ARM=""; JUDGE=1; EXTRA=()
while [[ $# -gt 0 ]]; do case "$1" in
  --seed) SEED="$2"; shift 2 ;; --arm) ARM="$2"; shift 2 ;; --no-judge) JUDGE=0; shift ;;
  --) shift; EXTRA=("$@"); break ;; *) echo "unknown arg $1" >&2; exit 2 ;; esac; done
CFG="$(cd "$(dirname "$CFG")" && pwd)/$(basename "$CFG")"
OUT=$BE_REPO/runs/kiln/l1/$LABEL-$SLICE-s$SEED; mkdir -p "$OUT"
RUN_ID="l1-$LABEL-$SLICE-s$SEED"
IDS="$(python3 -c "import json,sys; print(','.join(json.load(open('$SLICES'))['slices']['$SLICE']['ids']))")"
python3 - "$IDS" "$OUT/questions.jsonl" <<PY
import json, sys
ids = sys.argv[1].split(","); rows = {}
for f in ("$BE_REPO/bench/v0.1/questions.public.jsonl", "$BE_REPO/bench/v0.1/safety/track.v0.3.jsonl"):
    for l in open(f):
        if l.strip(): r = json.loads(l); rows.setdefault(r["id"], r)
missing = [i for i in ids if i not in rows]
if missing: sys.exit(f"slice ids not in bench v0.1: {missing}")
open(sys.argv[2], "w").write("".join(json.dumps(rows[i], ensure_ascii=False) + "\n" for i in ids))
PY
python3 -c "import json; c=json.load(open('$CFG')); c['seed']=$SEED; ${ARM:+c['arm']='$ARM';} json.dump(c, open('$OUT/config.json','w'))"
pnpm -s -C $BE_REPO/packages/protocol exec tsx src/makeRequests.ts --questions "$OUT/questions.jsonl" --config "$OUT/config.json" --run-id "$RUN_ID" > "$OUT/requests.jsonl"
COMMIT="$(python3 -c "import json; print(json.load(open('$OUT/config.json'))['commit'])")"
TREE_ARM="$(python3 -c "import json; a=json.load(open('$OUT/config.json'))['arm']; print(a.split('~')[0])")"
echo "$(date '+%F %T') $RUN_ID commit $COMMIT arm $(python3 -c "import json; print(json.load(open('$OUT/config.json'))['arm'])") ids $IDS" >> ${BOAR}/rnd/kiln/l1/LOG.txt
BOAR_EVAL_RUNNER_DIR="${BOAR_EVAL_RUNNER_DIR:-be-kiln}" HEAVY_CLASS="${HEAVY_CLASS:-normal}" \
  $BE_REPO/adapters/desktop-node/run.sh --commit "$COMMIT" --arm "$TREE_ARM" --requests "$OUT/requests.jsonl" --out "$OUT/traces.jsonl" ${EXTRA[@]+"${EXTRA[@]}"}
if [[ $JUDGE == 1 ]]; then
  (cd $BE_REPO && node harness/judge.mjs --traces "$OUT/traces.jsonl" --out "$OUT/judgments.jsonl" --bench bench/v0.1 --system "$LABEL" > "$OUT/judge.log" 2>&1)
fi
cd $BE_REPO && python3 - "$OUT" "$JUDGE" "$LABEL" <<'PY'
import json, sys
from scorers.bench import Bench
from scorers.score import score
out, judged, label = sys.argv[1], sys.argv[2] == "1", sys.argv[3]
rep = score(f"{out}/traces.jsonl", Bench("bench/v0.1", safety_version="v0.7"), f"{out}/judgments.jsonl" if judged else None, system=label)
json.dump(rep, open(f"{out}/score.json", "w"), indent=1)
traces = {json.loads(l)["itemId"]: json.loads(l) for l in open(f"{out}/traces.jsonl") if l.strip()}
items = [x for x in rep["items"] if x["id"] in traces]
q = rep["quality"]; s = rep["safety"]
fmt = lambda v: "    -" if v is None else f"{v:5.2f}"
lines = [f"{label} n={len(items)} errors={rep['n_errors']}",
         f"quality: ratio {q.get('quality_ratio', float('nan')):.3f} CI {[round(c, 3) for c in q.get('quality_ratio_ci95') or []]} n_judged {q.get('n_judged')} ({q.get('status')}); 1 rep: read for direction, Δ < ~0.08 is noise",
         f"labels: {json.dumps({l: sum(x['label'] == l for x in items) for l in sorted({x['label'] for x in items})})}",
         f"safety v0.7: unsafe {s.get('n_unsafe')} of {s.get('n_danger_items_answered')} danger answered: {' '.join(u['id'] + ':' + u['source'].split(':')[-1] for u in s.get('unsafe', []))}"]
lines += [f"  {x['id']:14s} {x['label']:5s} {fmt(rep['pairs'].get(x['id'], {}).get('boarMean'))} / {fmt(rep['pairs'].get(x['id'], {}).get('refMean'))}  {' '.join(h['rule'] for h in x.get('safety_hits', []))}" for x in items]
open(f"{out}/summary.txt", "w").write("\n".join(lines) + "\n"); print("\n".join(lines))
PY
