#!/bin/bash
# DEVICE-FINAL overnight driver (never prints item text). Runs the requests in order on the Pixel, pulls rows to out/, then M5 cold starts,
# netstats, and reinstalls the bundled LabRat APK. Resumable: a request with out/<rid>.jsonl complete is skipped. usage: night.sh [rid ...]
set -uo pipefail
A=~/Library/Android/sdk/platform-tools/adb; D=<workspace>/rnd/research/coordinator/arms/device-final; P=team.sopa.boar.lite
E=/sdcard/Android/data/$P/files/eval-out; LOG=$D/out/night.log; mkdir -p $D/out
log() { echo "$(date '+%F %T') $*" | tee -a $LOG; }
temp() { $A shell dumpsys battery | awk '/temperature/{print $2/10}'; }
UID_=$($A shell dumpsys package $P | awk -F= '/userId=/{print $2; exit}' | tr -d '\r ')
net() { $A shell cat /proc/net/xt_qtaguid/stats 2>/dev/null | awk -v u=$UID_ '$4==u{rx+=$6;tx+=$8}END{print "rx="rx+0" tx="tx+0}'; $A shell dumpsys netstats --uid 2>/dev/null | grep -c "uid=$UID_" ; }
run() { # rid seed
  local rid=$1 seed=$2 f=$D/req/$1.json
  if [ -s $D/out/$rid.jsonl ] && [ -s $D/out/$rid.status.json ] && grep -q '"state":"done"' $D/out/$rid.status.json; then log "skip $rid (done)"; return 0; fi
  $A shell input keyevent KEYCODE_WAKEUP >/dev/null; $A shell svc power stayon true
  local b64; b64=$(base64 -i $f | tr -d '\n')
  log "start $rid seed $seed temp $(temp)"
  $A shell am start -S -W --activity-clear-task -f 0x10000000 -n $P/team.sopa.boar.bench.BenchActivity --es run eval --es request64 "$b64" --es ov.seed $seed --ei waitmin 2 >/dev/null
  local t0=$(date +%s) st=""
  while :; do
    sleep 30
    st=$($A shell cat $E/requests/$rid.status.json 2>/dev/null)
    case "$st" in *'"state":"done"'*|*'"state":"failed"'*|*'"state":"stopped"'*) break;; esac
    if [ $(( $(date +%s) - t0 )) -gt 14400 ]; then log "TIMEOUT $rid"; break; fi
    [ $(( ($(date +%s) - t0) % 600 )) -lt 30 ] && log "  $rid $(echo "$st" | grep -o '"completed":[0-9]*') temp $(temp)"
  done
  echo "$st" > $D/out/$rid.status.json
  local res; res=$(echo "$st" | grep -o '"resultPath":"[^"]*"' | cut -d'"' -f4 | xargs basename 2>/dev/null)
  [ -n "$res" ] && $A pull $E/$res $D/out/$rid.jsonl >/dev/null
  log "end $rid $(echo "$st" | grep -o '"state":"[a-z]*"') rows $(wc -l < $D/out/$rid.jsonl 2>/dev/null) $(( ($(date +%s) - t0) / 60 )) min temp $(temp)"
}
log "night start; apk $($A shell dumpsys package $P | grep -m1 versionName); airplane $($A shell settings get global airplane_mode_on); uid $UID_"
$A shell dumpsys netstats detail > $D/out/netstats-before.txt 2>/dev/null
QUEUE="${*:-df-m1-v04-s42b:42 df-m2-probes-s42:42 df-m4-uxmatrix-s42:42 df-m1-v04-s43:43 df-m3-packproof-s42:42 df-m1-v04-s44:44 cold}"
for x in $QUEUE; do
  if [ $x = cold ]; then
    for k in 1 2 3; do
      echo "{\"requestId\":\"df-m5-cold-$k\",\"pipeline\":\"legacy\",\"models\":[\"qwen3-1.7b-q4km\"],\"evalSetVersion\":\"cold\",\"questions\":[{\"id\":\"cold-$k\",\"query\":\"What is the capital of Australia?\",\"category\":\"fact\"}]}" > $D/req/df-m5-cold-$k.json
      $A shell am force-stop $P; sleep 60; run df-m5-cold-$k 42
    done
  else run ${x%%:*} ${x##*:}; fi
done
[ $# -gt 0 ] && { log "partial queue: no reinstall"; exit 0; }
$A shell dumpsys netstats detail > $D/out/netstats-after.txt 2>/dev/null
grep -c "uid=$UID_" $D/out/netstats-after.txt | xargs -I{} log "netstats lines for app uid after: {}"
log "matrix done; reinstalling bundled LabRat"
$A install -r <workspace>/builds/boarlite-release/LabRat-0ad476ca-51a4aa4d.apk >> $LOG 2>&1 && log "bundled LabRat reinstalled" || log "REINSTALL FAILED"
$A shell svc power stayon false
log "night end"
