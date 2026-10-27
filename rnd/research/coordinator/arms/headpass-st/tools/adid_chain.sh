#!/bin/bash
# ADAPTER-IDENTITY: qa-health-se S requests (no settings) on the cut7-headpass-x2 tree with adapter 8dd1faff, then with the pinned
# 6298e5d3 (swapped in, then restored). No dump, no judge. Usage: nohup tools/adid_chain.sh > logs/adid.log 2>&1 &
A=<workspace>/rnd/research/coordinator/arms/headpass-st; D=$A/gen-adapter-id; T=<workspace>/kiln-local/be-0cfd4a77-cut7-headpass-x2
PIN=<scratch>
cp -p $T/be/adapter.ts $D/adapter.8dd1faff.bak
for tag in 8dd1faff 6298e5d3; do
  while $A/tools/busy.sh >/dev/null; do sleep 60; done
  [ $tag = 6298e5d3 ] && cp $PIN $T/be/adapter.ts
  R=st-qa-health-se-cut7-adid-$tag-s42
  EXPECT_ADAPTER=$(shasum -a 256 $T/be/adapter.ts | cut -c1-16) bash $A/tools/run_adid_gen.sh $D/$R.requests.jsonl $D/$R.traces.jsonl
  echo "$R rc=$? rows=$(wc -l < $D/$R.traces.jsonl) adapter=$(shasum -a 256 $T/be/adapter.ts | cut -c1-16) $(date +%T)"
done
cp $D/adapter.8dd1faff.bak $T/be/adapter.ts; echo "restored adapter $(shasum -a 256 $T/be/adapter.ts | cut -c1-16)"; echo ALLDONE
