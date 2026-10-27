#!/usr/bin/env bash
# CV5-LADDER-CODEX: r4to runs this on the MacBook with his Codex CLI logged in (CLI login; no API key). bash, not fish.
#   bash run.sh pilot     # dry run (0 calls) for all 4 rungs, then 4 real calls on L3 (2 ids x 2 orders) -> check out/pilot.*
#   bash run.sh all       # 4 rungs x 51 ids x 2 orders = 408 calls, resumable (rerun the same command after a stop)
#   bash run.sh status    # rows done per rung (102 each when complete)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; RU="$(dirname "$HERE")"; BE=<workspace>/boar-eval
CONC=${CONC:-2}; GAP=${GAP:-2000}
[ "$(shasum -a 256 "$RU/CV5-LADDER-CODEX-criterion.md" | cut -d' ' -f1)" = "$(cut -d' ' -f1 "$RU/CV5-LADDER-CODEX-criterion.sha256")" ] || { echo "criterion sha mismatch: stop"; exit 9; }
(cd "$HERE" && shasum -a 256 -c SHA256SUMS >/dev/null) || { echo "packet files changed (SHA256SUMS): stop"; exit 9; }
command -v codex >/dev/null || { echo "codex CLI not on PATH"; exit 9; }
IDS=$(cat "$HERE/in/ids51.csv")
trace() { python3 -I -c "import json; print(json.load(open('$RU/cv5-ladder/in/set.json'))['rungs']['$1'])"; }
RUNGS="L3_4B_phone_cut7 L1_17B_K0_s42 L2_GemmaE2B_desk_s42 L0_15B_closedbook"
judge() { # rung out extra-args...
  local r=$1 o=$2; shift 2
  node "$BE/harness/judge-codex.mjs" --bench "$BE/bench/v0.1" --refs "$BE/bench/v0.1/refs/refs.jsonl" --ids "$IDS" --strict \
    --traces "$(trace "$r")" --out "$o" --seed 7 --gap-ms "$GAP" --concurrency "$CONC" "$@"
}
case "${1:-}" in
  pilot)
    for r in $RUNGS; do judge "$r" "$HERE/out/dry-$r.jsonl" --dry-run || exit $?; done    # each must print "51 items, 102 calls to do"
    judge L3_4B_phone_cut7 "$HERE/out/pilot.L3.jsonl" --limit 4; echo "pilot rc=$?"; python3 -I -c "
import json; rows=[json.loads(l) for l in open('$HERE/out/pilot.L3.jsonl')]
print(len(rows), 'rows;', [(r['queryId'], r['order'], r['mapped']['winner'], r['requestedModel'], r['judgeVersion']) for r in rows])" ;;
  all)
    for r in $RUNGS; do judge "$r" "$HERE/out/$r.codex.judgments.jsonl"; echo "$(date +%T) $r rc=$?" | tee -a "$HERE/out/status.txt"; done ;;
  status)
    for r in $RUNGS; do f="$HERE/out/$r.codex.judgments.jsonl"; printf '%s %s/102\n' "$r" "$(cat "$f" 2>/dev/null | grep -c '"ok": *true')"; done ;;
  *) echo "usage: bash run.sh pilot|all|status"; exit 2 ;;
esac
