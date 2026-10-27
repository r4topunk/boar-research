#!/bin/bash
# Plumb #7: blind A/B of O2 (off-subject decline on the compact tier), iPhone 13, team.sopa.aoair, airplane mode.
# usage: run-o2-ab.sh <path/to/BOAR.app from modelos ai #2, aoair variant of 611a4b9>
# Design: 82 items (Veil 30 + vitalik device 52), 2 halves, ABBA arm order (off h1, on h1, on h2, off h2) against drift.
# Precondition (caller): lock written, r4to released the phone, #8 done (wiki-vital5 stays installed for P3 parity).
set -euo pipefail
APP=${1:?path to the aoair BOAR.app built from 611a4b9}
B=<workspace>; UDID=<DEVICE_UDID>
W=$B/wt/eval-vitalik; Q=eval/dataset/questions.o2-ab.jsonl
OUT=eval/results/runs/o2-ab; mkdir -p $W/$OUT

echo "$(date +%T) app bundle sha256 (main.jsbundle): $(shasum -a 256 "$APP/main.jsbundle" | cut -c1-16)"
plutil -p "$APP/Info.plist" | grep -E "CFBundleIdentifier"
grep -q '"CFBundleIdentifier" => "team.sopa.aoair"' <(plutil -p "$APP/Info.plist") || { echo "not team.sopa.aoair, abort"; exit 1; }
xcrun devicectl device install app --device $UDID "$APP" | tail -2      # keeps the container (packs, models, vital5)

cd $W
H1=$(python3 -c "import json;ids=[json.loads(l)['id'] for l in open('$Q')];print(','.join(ids[0::2]))")
H2=$(python3 -c "import json;ids=[json.loads(l)['id'] for l in open('$Q')];print(','.join(ids[1::2]))")
run() {  # arm half
  echo "$(date +%T) arm=$1 half=$2"
  node scripts/eval-iphone.o2.mjs --questions $Q --only "$3" --bundle team.sopa.aoair \
    --models qwen2.5-1.5b --quick-first on --always-complete off --o2 $1 \
    --dataset o2-ab --out eval-results/iphone/o2-ab-$1-$2 --timeout-min 25 \
    --runs-file $OUT/qwen2.5-1.5b__o2-$1__$2.jsonl | tail -4
}
run off h1 "$H1"; run on h1 "$H1"; run on h2 "$H2"; run off h2 "$H2"
cat $OUT/qwen2.5-1.5b__o2-off__h1.jsonl $OUT/qwen2.5-1.5b__o2-off__h2.jsonl > $OUT/qwen2.5-1.5b__o2-off.jsonl
cat $OUT/qwen2.5-1.5b__o2-on__h1.jsonl  $OUT/qwen2.5-1.5b__o2-on__h2.jsonl  > $OUT/qwen2.5-1.5b__o2-on.jsonl
python3 -c "
import json
for a in ('off','on'):
  rs=[json.loads(l) for l in open('$OUT/qwen2.5-1.5b__o2-'+a+'.jsonl')]
  arms={str(r.get('answerSettings',{}).get('o2Compact')) for r in rs}
  print(a, len(rs), 'o2Compact recorded:', arms, 'o2-off-subject declines:', sum('grounding:o2-off-subject' in (r.get('reasonCodes') or []) for r in rs))"
echo "$(date +%T) done (next: make-blind + rollback vital5 + release lock)"
