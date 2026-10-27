#!/bin/bash
# Plumb, night queue 2026-10-01 (plan + log: rnd/plumb/night-2026-10-01.md). ONE stage per call; stop on any error.
#   q1            611a4b9, vital5 = 0, crypto+wikivoyage+tiles: bench60+Veil30 (90 q) O2 off/on, ABBA by halves
#   q4            611a4b9, kit A (vital5 copied), bench 60, O2 off: exact repeat of the D10 run (test-retest)
#   q3            611a4b9, kit A, 150 questions in ONE request (thermal), O2 off
#   switch-14de107  install rc6eval-r11-0459 + one launch check (no request). On failure: reinstall 611a4b9 + one launch, then STOP
#   q2            14de107, kit A, LFM2.5-1.2B on bench 60 (no O2 on this build)
#   q5 <on|off>   14de107, kit A, Qwen 1.5B factual 38, always-complete on|off
set -euo pipefail
B=<workspace>; W=$B/wt/eval-vitalik; U=<DEVICE_UDID>
SCR=<scratch>
D10=$B/rnd/plumb/run-d10.sh; D=$B/rnd/plumb/data; R=eval/results/runs/night; DS=eval/dataset
EV=(node scripts/eval-iphone.o2.mjs --bundle team.sopa.aoair --quick-first on --dataset night)
log() { echo "$(date +%T) $*"; }
run() {  # name questions extra-args...
  local N=$1 Q=$2; shift 2; cd $W; mkdir -p $R
  $B/rnd/plumb/netcheck.sh || { echo "NETWORK SEEN: stop"; exit 2; }
  log "run $N"
  "${EV[@]}" --questions $Q --out eval-results/iphone/night-$N --timeout-min 60 --runs-file $R/$N.jsonl "$@" | tail -16
  cp $R/$N.jsonl $D/$N.jsonl; cp eval-results/iphone/night-$N/report.md $D/$N.report.md
  python3 -c "
import json;rs=[json.loads(l) for l in open('$D/$N.jsonl')]
print('rows',len(rs),'| model',{r.get('modelId') for r in rs},'| o2Compact',{str(r.get('answerSettings',{}).get('o2Compact')) for r in rs},'| declined',sum(bool(r.get('declined')) for r in rs))"
}
halves() { python3 -c "import json;ids=[json.loads(l)['id'] for l in open('$W/$1')];print(','.join(ids[$2::2]))"; }
case "${1:?stage}" in
q1)
  bash $D10 vital5-off
  Q=$DS/questions.q1-bench60-veil30.jsonl; H1=$(halves $Q 0); H2=$(halves $Q 1); P=q1-611a4b9-qwen1.5b-quick-kitnovital5
  run $P-o2off-h1 $Q --models qwen2.5-1.5b --always-complete off --o2 off --only "$H1"
  run $P-o2on-h1  $Q --models qwen2.5-1.5b --always-complete off --o2 on  --only "$H1"
  run $P-o2on-h2  $Q --models qwen2.5-1.5b --always-complete off --o2 on  --only "$H2"
  run $P-o2off-h2 $Q --models qwen2.5-1.5b --always-complete off --o2 off --only "$H2"
  cat $D/$P-o2off-h1.jsonl $D/$P-o2off-h2.jsonl > $D/$P-o2off.jsonl; cat $D/$P-o2on-h1.jsonl $D/$P-o2on-h2.jsonl > $D/$P-o2on.jsonl
  wc -l $D/$P-o2off.jsonl $D/$P-o2on.jsonl ;;
q4)
  bash $D10 kit-a
  run q4-611a4b9-qwen1.5b-quick-kitA-o2off-bench60-retest $DS/questions.bench-v0-public.jsonl --models qwen2.5-1.5b --always-complete off --o2 off ;;
q3)
  run q3-611a4b9-qwen1.5b-quick-kitA-o2off-thermal150 $DS/questions.q3-thermal150.jsonl --models qwen2.5-1.5b --always-complete off --o2 off
  python3 -c "
import json;rs=[json.loads(l) for l in open('$D/q3-611a4b9-qwen1.5b-quick-kitA-o2off-thermal150.jsonl')]
rs.sort(key=lambda r:r.get('createdAt',''))
g=[r for r in rs if (r.get('tokensGenerated') or 0)>=20 and r.get('tokPerSec')]
for i in range(0,len(g),max(1,len(g)//6)):
  seg=g[i:i+max(1,len(g)//6)]; print(f'gen-rows {i:3d}-{i+len(seg)-1:3d}: tok/s median {sorted(x[\"tokPerSec\"] for x in seg)[len(seg)//2]:.1f}  ttft median {sorted(x[\"ttftMs\"] for x in seg)[len(seg)//2]/1000:.1f}s')" ;;
switch-14de107)
  A=$B/builds/ios/device/rc6eval-r11-0459/std/BOAR.app
  bash $D10 neutralize >/dev/null 2>&1 || true
  log "install 14de107 (main.jsbundle $(shasum -a 256 $A/main.jsbundle | cut -c1-16))"; xcrun devicectl device install app --device $U $A | tail -1
  rm -f $SCR/n-l.json   # a stale JSON must not read as success
  # '|| true': under set -e + pipefail a refused launch would abort the script before the fallback below (bug of 2026-10-01 04:40)
  xcrun devicectl device process launch --device $U -e '{"GGML_METAL_DEVICES":"0"}' --json-output $SCR/n-l.json team.sopa.aoair 2>&1 | grep -E "Launched|ERROR|Reason" | head -2 || true
  PID=$(python3 -c "import json;print(json.load(open('$SCR/n-l.json')).get('result',{}).get('process',{}).get('processIdentifier',''))" 2>/dev/null || true)
  if [ -n "$PID" ]; then log "14de107 opened pid $PID"; sleep 8; xcrun devicectl device process terminate --device $U --pid $PID | tail -1
  else log "14de107 did NOT open: reinstall 611a4b9 and stop"
    xcrun devicectl device install app --device $U $B/builds/ios/device/o2eval-aoair-611a4b9/std/BOAR.app | tail -1
    xcrun devicectl device process launch --device $U -e '{"GGML_METAL_DEVICES":"0"}' team.sopa.aoair 2>&1 | grep -E "Launched|ERROR" | head -1 || true; exit 3; fi ;;
q2)
  bash $D10 kit-a
  run q2-14de107-lfm2.5-1.2b-quick-kitA-noO2-bench60 $DS/questions.bench-v0-public.jsonl --models lfm2.5-1.2b --always-complete off ;;
q5)
  M=${2:?on|off}
  run q5-14de107-qwen1.5b-complete$M-kitA-noO2-factual38 $DS/questions.vitalik-lantern.jsonl --models qwen2.5-1.5b --always-complete $M \
    --only "$(python3 -c 'import json;print(",".join(json.load(open("'$W'/eval/dataset/subset.factual.vitalik-lantern.json"))["ids"]))')" ;;
*) echo "unknown stage"; exit 1 ;;
esac
