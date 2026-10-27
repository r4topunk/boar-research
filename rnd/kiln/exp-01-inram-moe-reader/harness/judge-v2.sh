#!/usr/bin/env bash
# Blind pairwise judge (BOAR answer vs Opus+web reference, both A/B orders) for the v2 items that reach the LLM.
# Reuses boar-app eval/scripts/judge.mjs (feat/eval-frontier 0a024db) unchanged, inside a private copy of the eval
# tree ($TREE, built by the README's "harness tree" step). CLI login only (`claude -p`), 5 s gap, resumable.
# Usage: bash judge-v2.sh <tree> <exp dir> <model-id>...
set -euo pipefail
TREE="$1"; EXP="$2"; shift 2
python3 - "$TREE" "$EXP" "$@" <<'PY'
import json, sys, os
tree, exp, models = sys.argv[1], sys.argv[2], sys.argv[3:]
ids = None
for m in models:
    rows = [json.loads(l) for l in open(f"{exp}/runs/{m}.jsonl")]
    rows = [r for r in rows if r["set"] == "v2-hard12" and r["route"] == "llm"]
    ids = sorted(r["queryId"] for r in rows)
    os.makedirs(f"{tree}/eval/results/runs/v2", exist_ok=True)
    with open(f"{tree}/eval/results/runs/v2/kiln-{m}.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps({"queryId": r["queryId"], "answer": r["answer"], "outcome": "success" if r["answer"].strip() else "failure"}) + "\n")
json.dump({"ids": ids, "note": "exp-01: v2-hard12 items routed to the LLM"}, open(f"{tree}/eval/dataset/subset.kiln7.v2.json", "w"))
print("judge ids:", ids)
PY
mkdir -p "$EXP/judge"
for m in "$@"; do
  (cd "$TREE/eval" && node scripts/judge.mjs --dataset v2 --system "kiln-$m" --subset kiln7 --gap-ms 5000)
  cp "$TREE/eval/results/judgments/v2/kiln-${m}__vs__claude-code__opus.jsonl" "$EXP/judge/"
done
