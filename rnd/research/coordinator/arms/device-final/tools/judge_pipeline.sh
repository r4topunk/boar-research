#!/bin/bash
# DEVICE-FINAL judge pipeline (never prints item text): for each seed, wait for the phone's rows (out/df-m1-v04-s<seed>.status.json done),
# build traces, run G1 Opus (and G2 Codex on seeds 42/43, criterion cap 2 x 160), aggregate after each step. Log: judge/pipeline.log
D=<workspace>/rnd/research/coordinator/arms/device-final; L=$D/judge/pipeline.log; mkdir -p $D/judge
log() { echo "$(date '+%F %T') $*" >> $L; }
until grep -q '"state":"done"' $D/out/df-m1-v04-s42b.status.json 2>/dev/null && [ -s $D/out/df-m1-v04-s42b.jsonl ]; do sleep 30; done
cat $D/out/df-m1-v04-s42.part1.keep.jsonl $D/out/df-m1-v04-s42b.jsonl > $D/out/df-m1-v04-s42.jsonl; echo '{"state":"done","merged":"part1.keep + s42b"}' > $D/out/df-m1-v04-s42.status.json
for s in 42 43 44; do
  until grep -q '"state":"done"' $D/out/df-m1-v04-s$s.status.json 2>/dev/null && [ -s $D/out/df-m1-v04-s$s.jsonl ]; do sleep 60; done
  log "s$s rows ready"; python3 -I $D/tools/m1_traces.py $s > $D/judge/traces-s$s.log 2>&1; log "s$s traces rc=$?"
  log "$(bash $D/tools/m1_judge.sh g1 $s)"
  if [ $s != 44 ]; then
    for k in 1 2 3; do r=$(bash $D/tools/m1_judge.sh g2 $s); log "$r (try $k)"; [ "$r" = "g2 s$s rc=0" ] && break; sleep 900; done
  fi
  python3 -I $D/tools/m1_agg.py > $D/judge/agg-after-s$s.log 2>&1; log "agg after s$s rc=$?"
done
log "pipeline done"
