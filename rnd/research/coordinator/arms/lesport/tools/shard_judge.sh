#!/bin/bash
# LESPORT-L1 judge runner (criterion 5756268c...). OPUSSHARD pattern (arms/parjudge/tools/shard_run.sh): N = 4 round-robin shards,
# Opus judge.v1 default model, --gap-ms 0, same bench/seed as DEEPPAR-L1, a shard dying on exit 3/4 is resumed once more.
set -u
N=4
ARM=<workspace>/rnd/research/coordinator/arms/lesport
T=$ARM/les-R450.traces.jsonl
cd <workspace>/boar-eval
D=runs/kiln/lesport-l1; mkdir -p "$D" "$ARM/shards"
node -e 'const fs=require("fs");const [t,n,dir]=process.argv.slice(1);const ids=fs.readFileSync(t,"utf8").split("\n").filter(Boolean).map(l=>JSON.parse(l).itemId);
const s=Array.from({length:+n},()=>[]);ids.forEach((id,i)=>s[i%n].push(id));s.forEach((l,k)=>fs.writeFileSync(`${dir}/shard-${k}.ids`,l.join(",")+"\n"));' "$T" "$N" "$ARM/shards"
shard() { local k=$1 ids rc dies=0; ids=$(cat "$ARM/shards/shard-$k.ids")
  echo "start $k $(date +%s)" >>"$D/times.txt"
  while true; do
    node harness/judge.mjs --traces "$T" --out "$D/shard-$k.jsonl" --bench bench/v0.1 --ids "$ids" \
      --gap-ms 0 --seed 7 --system oracle-R450-les >>"$D/shard-$k.log" 2>&1
    rc=$?; echo "### exit $rc at $(date +%H:%M:%S) dies=$dies" >>"$D/shard-$k.log"
    if [ $rc -eq 3 ] || [ $rc -eq 4 ]; then dies=$((dies+1)); echo "### DIE $dies rc=$rc" >>"$D/shard-$k.log"
      [ $dies -ge 2 ] && { echo "### STOP: shard died twice" >>"$D/shard-$k.log"; touch "$D/STOP"; break; }; sleep 60; continue; fi
    break
  done
  echo "end $k $(date +%s) rc=$rc dies=$dies" >>"$D/times.txt"; }
echo "begin $(date +%s)" >"$D/times.txt"
for k in $(seq 0 $((N-1))); do shard "$k" & done
wait
echo "done $(date +%s)" >>"$D/times.txt"
cat "$D"/shard-*.jsonl >"$ARM/les-R450.judgments.jsonl"
node -e 'const r=require("fs").readFileSync(process.argv[1],"utf8").split("\n").filter(Boolean).map(JSON.parse);const k=new Set(r.map(x=>x.queryId+"|"+x.order));
console.log(`rows ${r.length} unique ${k.size} ok ${r.filter(x=>x.ok).length}`);process.exit(r.length===114&&k.size===114?0:1)' "$ARM/les-R450.judgments.jsonl"
