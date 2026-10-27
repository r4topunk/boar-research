#!/bin/bash
# OPUSSHARD runner (criterion sha b78c9550...). Usage: run.sh <N>. Logs in arms/opusshard/N<N>/.
set -u
N=$1
ARM=<workspace>/rnd/research/coordinator/arms/opusshard
T=<workspace>/rnd/research/coordinator/arms/deepread/deep35-R450.traces.jsonl
IDS=(dng-005 lan-exp-002 lan-hlt-001 lan-rsn-001 lan-rsn-003 lan-rsn-005 trv-002 trv-004 vit-cry-001 vit-cry-002)
cd <workspace>/boar-eval
D=$ARM/N$N; mkdir -p "$D"; : >"$D/times.txt"
for k in $(seq 0 $((N-1))); do l=""; for i in "${!IDS[@]}"; do [ $((i%N)) -eq $k ] && l="$l${l:+,}${IDS[$i]}"; done; echo "$l" >"$D/shard-$k.ids"; done
shard() { local k=$1 ids rc exits3=0; ids=$(cat "$D/shard-$k.ids"); echo "start $k $(date +%s)" >>"$D/times.txt"
  while true; do
    node harness/judge.mjs --traces "$T" --out "$D/shard-$k.jsonl" --bench bench/v0.1 --ids "$ids" --judge-model opus --gap-ms 0 --seed 7 --system opusshard-probe >>"$D/shard-$k.log" 2>&1
    rc=$?; echo "### exit $rc at $(date +%H:%M:%S)" >>"$D/shard-$k.log"
    if [ $rc -eq 3 ]; then exits3=$((exits3+1)); [ $exits3 -ge 4 ] && break; sleep 60; continue; fi
    break
  done; echo "end $k $(date +%s) rc=$rc exit3=$exits3" >>"$D/times.txt"; }
for k in $(seq 0 $((N-1))); do shard "$k" & done
wait
cat "$D"/shard-*.jsonl >"$D/probe.judgments.jsonl"
node -e 'const r=require("fs").readFileSync(process.argv[1],"utf8").split("\n").filter(Boolean).map(JSON.parse);const k=new Set(r.map(x=>x.queryId+"|"+x.order));console.log(`rows ${r.length} unique ${k.size} ok ${r.filter(x=>x.ok).length}`)' "$D/probe.judgments.jsonl"
