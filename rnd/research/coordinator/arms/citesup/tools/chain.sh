#!/bin/bash
# CITESUP unattended chain after the calibration runs (criterion steps 4-7): calib -> tau -> on-patch -> Ministral vendor K1 + K0 (on) -> judge changed + gate.
# Usage (from arms/): nohup bash citesup/tools/chain.sh > citesup/runs/chain.log 2>&1 &
set -u
A=<workspace>/rnd/research/coordinator/arms; C=$A/citesup; cd $A
log() { echo "$(date +%T) [chain] $*"; }
until grep -q "GEN-ONLY DONE" $C/runs/ctl-K0.log; do grep -q FAIL $C/runs/ctl-K0.log && { log "ctl K0 FAIL"; exit 1; }; sleep 30; done
T1=$C/runs/citesupctl/traces/citesupctl-K1-screen2-K1-s42.traces.jsonl; T0=$C/runs/citesupctl/traces/citesupctl-K0-screen2-K0-s42.traces.jsonl
python3 -I $C/tools/calib.py $T1.citesup.jsonl $T0.citesup.jsonl -- \
  $T1:null-cal/control/pool-K1.json:null-cal/control/traces/poolctl-K1-st180-s42.traces.jsonl,lp-screens/control/traces/lpctl-K1-main-s42.traces.jsonl \
  $T0:null-cal/control/pool-K0.json:null-cal/control/traces/poolctl-K0-st180-s42.traces.jsonl,lp-screens/control/traces/lpctl-K0-main-s42.traces.jsonl | tee $C/runs/calib.out
grep -q "LOG MODE OK" $C/runs/calib.out || { log "STOP: log-mode check failed"; exit 1; }
TAU=$(awk '/^TAU/{print $2}' $C/runs/calib.out); log "tau $TAU"
bash $C/tools/mkon.sh $TAU || exit 1
for K in K1 K0; do
  OUT_BASE=$C/runs bash $C/tools/gen.sh citesupm3v $K null-cal/pool/screen2-$K.ids $C/min3v-citesup-on.patch > $C/runs/m3v-$K.log 2>&1 &
  sleep 60
done
wait
for K in K1 K0; do grep -q "GEN-ONLY DONE" $C/runs/m3v-$K.log || { log "m3v $K gen failed"; cat $C/runs/m3v-$K.log; continue; }
  bash $C/tools/judge_gate.sh $K > $C/runs/judge-$K.log 2>&1; log "judge_gate $K rc=$?"; tail -3 $C/runs/judge-$K.log; done
log "CHAIN DONE"
