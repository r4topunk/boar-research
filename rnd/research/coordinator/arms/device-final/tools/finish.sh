#!/bin/bash
# DEVICE-FINAL finish (s44 dropped 12:3x for time, r4to wants the app closed; 2 seeds = the ruler spec): wait for the running packproof request,
# pull it, run the cold starts, netstats, reinstall the bundled LabRat 0ad476ca.
A=~/Library/Android/sdk/platform-tools/adb; D=<workspace>/rnd/research/coordinator/arms/device-final; P=team.sopa.boar.lite; E=/sdcard/Android/data/$P/files/eval-out; LOG=$D/out/night.log
log() { echo "$(date '+%F %T') $*" >> $LOG; }
rid=df-m3-packproof-s42
until st=$($A shell cat $E/requests/$rid.status.json 2>/dev/null) && echo "$st" | grep -qE '"state":"(done|failed|stopped)"'; do sleep 30; done
echo "$st" > $D/out/$rid.status.json; res=$(echo "$st" | grep -o '"resultPath":"[^"]*"' | cut -d'"' -f4 | xargs basename); $A pull $E/$res $D/out/$rid.jsonl >/dev/null
log "end $rid $(echo "$st" | grep -o '"state":"[a-z]*"') rows $(wc -l < $D/out/$rid.jsonl)"
bash $D/tools/night.sh cold
$A shell dumpsys netstats detail > $D/out/netstats-after.txt 2>/dev/null
log "matrix done (s44 dropped); reinstalling bundled LabRat 0ad476ca"
$A install -r <workspace>/builds/boarlite-release/LabRat-0ad476ca-51a4aa4d.apk >> $LOG 2>&1 && log "bundled LabRat reinstalled" || log "REINSTALL FAILED"
$A shell svc power stayon false; log "night end"
