#!/bin/bash
# Plumb, D10 window: one device session on team.sopa.aoair with the O2 eval build (611a4b9 = main fd24992 + O2 behind a flag).
# Run ONE stage per call, in order; stop and report on any error (no retries, no improvising).
#   status          apps, packs, pending.json (read-only)
#   install         devicectl install o2eval-aoair-611a4b9 over aoair (keeps the container)
#   neutralize      overwrite any leftover pending.json with non-JSON (so a launch can't start an eval)
#   launch-once     ONE plain launch (r4to has mobile data on), check it opened, then terminate it
#   kit-a           P3 kit: boar-crypto + boar-wikivoyage-en + wiki-vital5 (copied) + city tiles
#   kit-b           factory 'essential' kit: crypto, wikivoyage, vital5 -> 0 byte (tiles stay: places-only, unused off food items)
#   kit-restore     put crypto + wikivoyage back from shared-data (pins), vital5 stays as it is
#   bench60 <tag>   the 60 public bench items, --o2 off   (tag: kitA | kitB)
#   o2ab            the O2 A/B, ABBA (off h1, on h1, on h2, off h2) on questions.o2-ab.jsonl
#   safety <file>   the safety-track items (converted to {id,query}), --o2 off
#   vital5-off      rollback wiki-vital5 to 0 byte
set -euo pipefail
B=<workspace>; W=$B/wt/eval-vitalik; U=<DEVICE_UDID>
APP=$B/builds/ios/device/o2eval-aoair-611a4b9/std/BOAR.app
SCR=<scratch>
C=(--domain-type appDataContainer --domain-identifier team.sopa.aoair)
put() { xcrun devicectl device copy to --device $U "${C[@]}" --source "$1" --destination "$2" >/dev/null; }
files() { xcrun devicectl device info files --device $U "${C[@]}" --json-output $SCR/d10f.json >/dev/null 2>&1
  python3 -c "
import json;fs={f['name']:f['metadata']['size'] for f in json.load(open('$SCR/d10f.json'))['result']['files']}
for n in sorted(fs):
  if (n.startswith('Documents/corpus/') and n.endswith('.sqlite')) or n=='Documents/eval/requests/pending.json': print('  ',n,fs[n])
print('   poi tiles:',sum(1 for n in fs if n.startswith('Documents/poi/')))"; }
EV=(node scripts/eval-iphone.o2.mjs --bundle team.sopa.aoair --models qwen2.5-1.5b --quick-first on --always-complete off)
log() { echo "$(date +%T) $*"; }

case "${1:?stage}" in
status)
  xcrun devicectl device info apps --device $U --json-output $SCR/d10a.json >/dev/null 2>&1
  python3 -c "
import json
for a in json.load(open('$SCR/d10a.json'))['result']['apps']:
  if 'sopa' in a['bundleIdentifier']: print('  ',a['bundleIdentifier'],a['version'],a.get('bundleVersion'))"
  files ;;
install)
  plutil -p $APP/Info.plist | grep -E '"CFBundleIdentifier" => "team.sopa.aoair"' >/dev/null || { echo "not aoair"; exit 1; }
  log "install $(plutil -p $APP/Info.plist | grep -E 'CFBundleShortVersionString|CFBundleVersion"' | tr -s ' ' | tr '\n' ' ') main.jsbundle $(shasum -a 256 $APP/main.jsbundle | cut -c1-16)"
  xcrun devicectl device install app --device $U $APP | tail -2 ;;
neutralize)
  printf 'neutralized-by-plumb: not a request' > $SCR/pending.json; put $SCR/pending.json Documents/eval/requests/pending.json
  xcrun devicectl device copy from --device $U "${C[@]}" --source Documents/eval/requests/pending.json --destination $SCR/pending.chk >/dev/null
  log "pending.json now: $(cat $SCR/pending.chk)" ;;
launch-once)
  xcrun devicectl device copy from --device $U "${C[@]}" --source Documents/eval/requests/pending.json --destination $SCR/pending.chk >/dev/null 2>&1 \
    && { grep -q '^neutralized' $SCR/pending.chk || { echo "pending.json is a REAL request: run 'neutralize' first"; exit 1; }; }
  rm -f $SCR/d10l.json
  # '|| true': a refused launch must reach the PID check below instead of aborting under set -e + pipefail
  log "single launch"; xcrun devicectl device process launch --device $U -e '{"GGML_METAL_DEVICES":"0"}' --json-output $SCR/d10l.json team.sopa.aoair 2>&1 | tail -6 || true
  PID=$(python3 -c "import json;print(json.load(open('$SCR/d10l.json')).get('result',{}).get('process',{}).get('processIdentifier',''))" 2>/dev/null || true)
  [ -n "$PID" ] || { echo "LAUNCH FAILED (see above): stop and report"; exit 1; }
  log "opened pid $PID"; sleep 8; xcrun devicectl device process terminate --device $U --pid $PID | tail -1 ;;
kit-a)
  put $B/shared-data/packs/wiki-vital5.sqlite Documents/corpus/wiki-vital5.sqlite; log "vital5 copied (sha $(shasum -a 256 $B/shared-data/packs/wiki-vital5.sqlite | cut -c1-16))"; files ;;
kit-b)
  : > $SCR/empty.sqlite
  for p in boar-crypto boar-wikivoyage-en wiki-vital5; do put $SCR/empty.sqlite Documents/corpus/$p.sqlite; done; log "kit-b: 3 packs -> 0 byte"; files ;;
kit-restore)
  put $B/shared-data/crypto/boar-crypto.sqlite Documents/corpus/boar-crypto.sqlite
  put $B/shared-data/packs/boar-wikivoyage-en.sqlite Documents/corpus/boar-wikivoyage-en.sqlite; log "crypto + wikivoyage restored"; files ;;
bench60)
  T=${2:?kitA|kitB}; cd $W; mkdir -p eval/results/runs/bench-v0
  "${EV[@]}" --questions eval/dataset/questions.bench-v0-public.jsonl --o2 off --dataset bench-v0 \
    --out eval-results/iphone/bench-v0-611a4b9-$T --timeout-min 30 \
    --runs-file eval/results/runs/bench-v0/qwen2.5-1.5b-instruct-q4km__iphone-611a4b9-o2off-bench-v0-$T.jsonl | tail -20
  N=qwen2.5-1.5b-instruct-q4km__iphone-611a4b9-o2off-bench-v0; [ "$T" = kitA ] && D=$N || D=$N-$T   # kit A = Lantern's requested name
  cp eval/results/runs/bench-v0/$N-$T.jsonl $B/rnd/plumb/data/$D.jsonl
  cp eval-results/iphone/bench-v0-611a4b9-$T/report.md $B/rnd/plumb/data/$D.report.md
  cp eval-results/iphone/bench-v0-611a4b9-$T/request.json $B/rnd/plumb/data/$D.request.json
  python3 -c "import json;r=json.load(open('$B/rnd/plumb/data/$D.request.json'));print('O2 flag in request:',r.get('o2Compact'),'| answerSettings:',r.get('answerSettings'))" ;;
o2ab)
  cd $W; Q=eval/dataset/questions.o2-ab.jsonl; O=eval/results/runs/o2-ab; mkdir -p $O
  H1=$(python3 -c "import json;print(','.join([json.loads(l)['id'] for l in open('$Q')][0::2]))")
  H2=$(python3 -c "import json;print(','.join([json.loads(l)['id'] for l in open('$Q')][1::2]))")
  for blk in "off h1 $H1" "on h1 $H1" "on h2 $H2" "off h2 $H2"; do set -- $blk; log "o2=$1 $2"
    "${EV[@]}" --questions $Q --only "$3" --o2 $1 --dataset o2-ab --out eval-results/iphone/o2-ab-$1-$2 --timeout-min 25 \
      --runs-file $O/qwen2.5-1.5b__o2-$1__$2.jsonl | tail -3; done
  cat $O/qwen2.5-1.5b__o2-off__h1.jsonl $O/qwen2.5-1.5b__o2-off__h2.jsonl > $O/qwen2.5-1.5b__o2-off.jsonl
  cat $O/qwen2.5-1.5b__o2-on__h1.jsonl $O/qwen2.5-1.5b__o2-on__h2.jsonl > $O/qwen2.5-1.5b__o2-on.jsonl
  python3 -c "
import json
for a in ('off','on'):
  rs=[json.loads(l) for l in open('$O/qwen2.5-1.5b__o2-'+a+'.jsonl')]
  print(a,len(rs),'o2Compact seen:',{str(r.get('answerSettings',{}).get('o2Compact')) for r in rs},'o2-off-subject:',sum('grounding:o2-off-subject' in (r.get('reasonCodes') or []) for r in rs))" ;;
safety)
  F=${2:?safety items jsonl}; cd $W; mkdir -p eval/results/runs/safety
  python3 -c "
import json,sys
with open('eval/dataset/questions.safety-track.jsonl','w') as o:
  for q in map(json.loads,open('$F')): o.write(json.dumps({'id':q['id'],'query':q.get('query') or q['question'],'category':q.get('category','safety'),'lang':q.get('lang','en')},ensure_ascii=False)+'\n')"
  "${EV[@]}" --questions eval/dataset/questions.safety-track.jsonl --o2 off --dataset safety-track --out eval-results/iphone/safety-611a4b9 --timeout-min 15 \
    --runs-file eval/results/runs/safety/qwen2.5-1.5b-instruct-q4km__iphone-611a4b9-o2off-safety.jsonl | tail -12
  cp eval/results/runs/safety/qwen2.5-1.5b-instruct-q4km__iphone-611a4b9-o2off-safety.jsonl $B/rnd/plumb/data/ ;;
vital5-off)
  : > $SCR/empty.sqlite; put $SCR/empty.sqlite Documents/corpus/wiki-vital5.sqlite; log "vital5 -> 0 byte"; files ;;
*) echo "unknown stage"; exit 1 ;;
esac
