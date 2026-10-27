#!/bin/bash
# L1 control (signal20, Haiku 5.5-low), adapted from arms/parjudge/tools/shard_run.sh: N=4 round-robin over signal20.ids,
# --gap-ms 0, rerun a shard on exit 3/4 (resume), STOP on second death; concatenate, assert 40 unique (queryId, order).
set -u
N=4
ARM=<workspace>/rnd/research/coordinator/arms/l1ctl
IDS=<workspace>/rnd/research/coordinator/arms/signal20.ids
cd <workspace>/boar-eval
T=runs/kiln/speedpack-l1/spctl-v01-s44.traces.jsonl
OUT=runs/kiln/speedpack-l1/spctl-v01-s44.judgments.haiku55-low.jsonl
D=runs/kiln/speedpack-l1/haiku55-shards; mkdir -p "$D" "$ARM/shards-$N"
node -e 'const fs=require("fs");const [f,n,dir]=process.argv.slice(1);const ids=fs.readFileSync(f,"utf8").split("\n").filter(Boolean);
const s=Array.from({length:+n},()=>[]);ids.forEach((id,i)=>s[i%n].push(id));s.forEach((l,k)=>fs.writeFileSync(`${dir}/shard-${k}.ids`,l.join(",")+"\n"));' "$IDS" "$N" "$ARM/shards-$N"
shard() { local k=$1 ids rc dies=0; ids=$(cat "$ARM/shards-$N/shard-$k.ids")
  echo "start $k $(date +%s)" >>"$D/times.txt"
  while true; do
    node harness/judge.mjs --traces "$T" --out "$D/shard-$k.jsonl" --bench bench/v0.1 --ids "$ids" --judge-model claude-haiku-5-5 --effort low \
      --gap-ms 0 --seed 7 --system "spctl-v01-s44-haiku55-low" >>"$D/shard-$k.log" 2>&1
    rc=$?; echo "### exit $rc at $(date +%H:%M:%S) dies=$dies" >>"$D/shard-$k.log"
    if [ $rc -eq 3 ] || [ $rc -eq 4 ]; then dies=$((dies+1)); echo "### DIE $dies rc=$rc" >>"$D/shard-$k.log"
      [ $dies -ge 2 ] && { echo "### STOP: shard died twice" >>"$D/shard-$k.log"; touch "$D/STOP"; break; }; continue; fi
    break
  done
  echo "end $k $(date +%s) rc=$rc dies=$dies" >>"$D/times.txt"; }
echo "begin $(date +%s)" >"$D/times.txt"
for k in $(seq 0 $((N-1))); do shard "$k" & done
wait
echo "done $(date +%s)" >>"$D/times.txt"
cat "$D"/shard-*.jsonl >"$OUT"
node -e 'const r=require("fs").readFileSync(process.argv[1],"utf8").split("\n").filter(Boolean).map(JSON.parse);const k=new Set(r.map(x=>x.queryId+"|"+x.order));
console.log(`rows ${r.length} unique ${k.size} ok ${r.filter(x=>x.ok).length}`);process.exit(r.length===40&&k.size===40?0:1)' "$OUT"
