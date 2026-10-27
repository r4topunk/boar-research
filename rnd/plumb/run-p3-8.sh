#!/bin/bash
# Plumb #8 (bench v0 day 4): BOAR P3 on 8 new items, iPhone 13, aoair 14de107, airplane mode.
# usage: run-p3-8.sh [--rollback]   (--rollback only when #8 runs alone; before #7 the pack stays installed)
# Precondition (caller): lock written, r4to released the phone, no other app in the foreground.
set -euo pipefail
B=<workspace>
UDID=<DEVICE_UDID>
DC=(xcrun devicectl device)
C=(--domain-type appDataContainer --domain-identifier team.sopa.aoair)
SCR=<scratch>

size() { "${DC[@]}" info files --device $UDID "${C[@]}" --json-output $SCR/f.json >/dev/null 2>&1
  python3 -c "import json;print(next((f['metadata']['size'] for f in json.load(open('$SCR/f.json'))['result']['files'] if f['name']=='Documents/corpus/wiki-vital5.sqlite'),'absent'))"; }

echo "$(date +%T) vital5 before: $(size)"
"${DC[@]}" copy to --device $UDID "${C[@]}" --source $B/shared-data/packs/wiki-vital5.sqlite --destination Documents/corpus/wiki-vital5.sqlite >/dev/null
S=$(size); echo "$(date +%T) vital5 after copy: $S"; [ "$S" = "163647488" ] || { echo "size mismatch, abort"; exit 1; }

cd $B/wt/eval-vitalik
node scripts/eval-iphone.mjs \
  --questions eval/dataset/questions.bench-v0-p3.jsonl \
  --models qwen2.5-1.5b --quick-first on --always-complete off \
  --install-places Berlin,Lisbon,Tokyo \
  --dataset bench-v0-p3 --out eval-results/iphone/bench-v0-p3 --timeout-min 15 \
  --runs-file eval/results/runs/bench-v0-p3/qwen2.5-1.5b-instruct-q4km__iphone-14de107-bench-p3-8.jsonl
cp eval/results/runs/bench-v0-p3/qwen2.5-1.5b-instruct-q4km__iphone-14de107-bench-p3-8.jsonl $B/rnd/plumb/data/
cp eval-results/iphone/bench-v0-p3/report.md $B/rnd/plumb/data/iphone-bench-p3-8-report.md

if [ "${1:-}" = "--rollback" ]; then
  : > $SCR/wiki-vital5.sqlite
  "${DC[@]}" copy to --device $UDID "${C[@]}" --source $SCR/wiki-vital5.sqlite --destination Documents/corpus/wiki-vital5.sqlite >/dev/null
  echo "$(date +%T) vital5 rolled back: $(size)"
fi
echo "$(date +%T) done"
