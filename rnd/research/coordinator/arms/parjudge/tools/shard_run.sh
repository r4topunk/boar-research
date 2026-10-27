#!/bin/bash
# PARJUDGE level runner (criterion PARJUDGE-criterion.md, sha256 f47b3bb5…). No harness edit.
# Usage: shard_run.sh <N>
# Shards the 57 deep35-R450 ids (traces file order) round-robin into N lists (arms/parjudge/shards-N/shard-k.ids),
# starts N judge.mjs processes at once (--gap-ms 0), reruns a shard once on exit 3 (rate limit) or 4 (structured-output/API
# error; judge.mjs resumes ok rows); a shard dying twice -> STOP flag. Records epoch start/end in runs/kiln/parjudge/N<N>/times.txt.
set -u
N=$1
ARM=<workspace>/rnd/research/coordinator/arms/parjudge
T=<workspace>/rnd/research/coordinator/arms/deepread/deep35-R450.traces.jsonl
cd <workspace>/boar-eval
D=runs/kiln/parjudge/N$N; mkdir -p "$D" "$ARM/shards-$N"
node -e 'const fs=require("fs");const [t,n,dir]=process.argv.slice(1);const ids=fs.readFileSync(t,"utf8").split("\n").filter(Boolean).map(l=>JSON.parse(l).itemId);
const s=Array.from({length:+n},()=>[]);ids.forEach((id,i)=>s[i%n].push(id));s.forEach((l,k)=>fs.writeFileSync(`${dir}/shard-${k}.ids`,l.join(",")+"\n"));' "$T" "$N" "$ARM/shards-$N"
shard() { local k=$1 ids rc dies=0; ids=$(cat "$ARM/shards-$N/shard-$k.ids")
  echo "start $k $(date +%s)" >>"$D/times.txt"
  while true; do
    node harness/judge.mjs --traces "$T" --out "$D/shard-$k.jsonl" --bench bench/v0.1 --ids "$ids" --judge-model claude-haiku-5-5 --effort low \
      --gap-ms 0 --seed 7 --system "deep35-R450-par$N-$k" >>"$D/shard-$k.log" 2>&1
    rc=$?; echo "### exit $rc at $(date +%H:%M:%S) dies=$dies" >>"$D/shard-$k.log"
    if [ $rc -eq 3 ] || [ $rc -eq 4 ]; then dies=$((dies+1)); echo "### DIE $dies rc=$rc" >>"$D/shard-$k.log"
      [ $dies -ge 2 ] && { echo "### STOP: shard died twice" >>"$D/shard-$k.log"; touch "$D/STOP"; break; }; continue; fi
    break
  done
  echo "end $k $(date +%s) rc=$rc dies=$dies" >>"$D/times.txt"; }
echo "level $N begin $(date +%s)" >"$D/times.txt"
for k in $(seq 0 $((N-1))); do shard "$k" & done
wait
echo "level $N done $(date +%s)" >>"$D/times.txt"
cat "$D"/shard-*.jsonl >"runs/kiln/parjudge/N$N.judgments.jsonl"
node -e 'const r=require("fs").readFileSync(process.argv[1],"utf8").split("\n").filter(Boolean).map(JSON.parse);const k=new Set(r.map(x=>x.queryId+"|"+x.order));
console.log(`rows ${r.length} unique ${k.size} ok ${r.filter(x=>x.ok).length}`);process.exit(r.length===114&&k.size===114?0:1)' "runs/kiln/parjudge/N$N.judgments.jsonl"
