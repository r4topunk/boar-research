#!/bin/bash
# DEEPTHINK judge shards = deepvpara shard_judge.sh + 7th arg MODEL (haiku: claude-haiku-5-5 --effort low [L1]; opus: judge.mjs default opus, judge.v1 [L2/OPUSSHARD]).
# Usage: shard_judge.sh <traces> <out.jsonl> <bench dir> <ids file (one per line)> <system name> [N=4]
# Round-robin ids (ids-file order) into N shards, judge.mjs --judge-model claude-haiku-5-5 --effort low --gap-ms 0 --seed 7,
# rerun a shard on exit 3/4 (judge.mjs resumes ok rows), STOP after 2 dies. Concatenates, asserts unique (queryId, order) = 2*n.
set -u
TR=$1; OUT=$2; BENCH=$3; IDF=$4; SYS=$5; N=${6:-4}; MODEL=${7:-haiku}
if [ "$MODEL" = opus ]; then JM=(--judge-model opus); else JM=(--judge-model claude-haiku-5-5 --effort low); fi
cd <workspace>/boar-eval
D="${OUT%.jsonl}.shards"; mkdir -p "$D"
IDS=(); while read -r x; do [ -n "$x" ] && IDS+=("$x"); done < "$IDF"; n=${#IDS[@]}
for k in $(seq 0 $((N-1))); do l=(); for i in $(seq $k $N $((n-1))); do l+=("${IDS[$i]}"); done; (IFS=,; echo "${l[*]}") > "$D/shard-$k.ids"; done
shard() { local k=$1 ids rc dies=0; ids=$(cat "$D/shard-$k.ids")
  while true; do
    node harness/judge.mjs --traces "$TR" --out "$D/shard-$k.jsonl" --bench "$BENCH" --ids "$ids" "${JM[@]}" \
      --gap-ms 0 --seed 7 --system "$SYS" >>"$D/shard-$k.log" 2>&1
    rc=$?; echo "### exit $rc at $(date +%H:%M:%S) dies=$dies" >>"$D/shard-$k.log"
    if [ $rc -eq 3 ] || [ $rc -eq 4 ]; then dies=$((dies+1)); [ $dies -ge 2 ] && { echo "### STOP" >>"$D/shard-$k.log"; touch "$D/STOP"; break; }; continue; fi
    break
  done; }
s=$(date +%s); for k in $(seq 0 $((N-1))); do shard "$k" & done; wait
cat "$D"/shard-*.jsonl > "$OUT"
node -e 'const r=require("fs").readFileSync(process.argv[1],"utf8").split("\n").filter(Boolean).map(JSON.parse);const k=new Set(r.map(x=>x.queryId+"|"+x.order));
console.log(`rows ${r.length} unique ${k.size} ok ${r.filter(x=>x.ok).length} model ${[...new Set(r.map(x=>x.judgeModel))]} expected ${2*+process.argv[2]}`);process.exit(r.length===2*+process.argv[2]&&k.size===r.length?0:1)' "$OUT" "$n"
echo "wall $(( $(date +%s) - s )) s; first log line: $(head -1 "$D/shard-0.log" | cut -c1-120)"
