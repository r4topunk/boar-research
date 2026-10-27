#!/bin/bash
# DEEPTHINK judge shards = deepvpara shard_judge.sh + 7th arg MODEL (haiku: claude-haiku-5-5 --effort low [L1]; opus: judge.mjs default opus, judge.v1 [L2/OPUSSHARD]).
# Usage: shard_judge.sh <traces> <out.jsonl> <bench dir> <ids file (one per line)> <system name> [N=4] [haiku|opus]
# Round-robin ids (ids-file order) into N shards, judge.mjs --judge-model ... --gap-ms 0 --seed 7,
# rerun a shard on exit 3/4 (judge.mjs resumes ok rows), STOP after 2 dies. Concatenates, asserts every id has both orders (rows = 2*n).
# FAIL CLOSED (2026-10-11): exits non-zero unless every shard exited 0 AND every id has both orders judged.
#   rc 0 ok | 1 incomplete (ids named on stderr, listed in <out>.missing) | 3 a shard failed (rc in <out>.shards/shard-K.rc) | 4 STOP file present
#   (<out>.shards/STOP or <out>.STOP: refuses to start; also checked before every shard rerun; touched after 2 dies) | 5 output locked (mkdir lock <out>.lock).
# Env: BOAR_EVAL_DIR (default boar-eval), JUDGE_CMD (default "node harness/judge.mjs"; tests stub it), JUDGE_FLOOR_ERRORED=1 -> pass --floor-errored.
set -u
abs() { case $1 in /*) echo "$1";; *) echo "$PWD/$1";; esac; }
TR=$(abs "$1"); OUT=$(abs "$2"); BENCH=$(abs "$3"); IDF=$(abs "$4"); SYS=$5; N=${6:-4}; MODEL=${7:-haiku}
EVAL=${BOAR_EVAL_DIR:-<workspace>/boar-eval}; read -r -a JC <<< "${JUDGE_CMD:-node harness/judge.mjs}"
if [ "$MODEL" = opus ]; then JM=(--judge-model opus); else JM=(--judge-model claude-haiku-5-5 --effort low); fi
[ "${JUDGE_FLOOR_ERRORED:-0}" = 1 ] && JM+=(--floor-errored)
D="${OUT%.jsonl}.shards"; MISSING="${OUT%.jsonl}.missing"
for st in "$OUT.STOP" "$D/STOP"; do [ -e "$st" ] && { echo "STOP file present ($st): refusing to run; remove it after fixing the cause" >&2; exit 4; }; done
LK="$OUT.lock"; mkdir -p "$(dirname "$OUT")"
mkdir "$LK" 2>/dev/null || { echo "LOCKED: $LK is held ($(cat "$LK/owner" 2>/dev/null)); another judge run owns $OUT. If that run is dead, rm -r $LK" >&2; exit 5; }
echo "pid=$$ started=$(date '+%F %T') host=$(hostname -s)" > "$LK/owner"
trap 'rm -rf "$LK"' EXIT; trap 'exit 130' INT TERM
cd "$EVAL" || exit 2
mkdir -p "$D"; rm -f "$D"/shard-*.rc
IDS=(); while read -r x; do [ -n "$x" ] && IDS+=("$x"); done < "$IDF"; n=${#IDS[@]}
for k in $(seq 0 $((N-1))); do l=(); for i in $(seq $k $N $((n-1))); do l+=("${IDS[$i]}"); done; (IFS=,; echo "${l[*]}") > "$D/shard-$k.ids"; done
shard() { local k=$1 ids rc=0 dies=0; ids=$(cat "$D/shard-$k.ids")
  [ -z "$ids" ] && { echo 0 > "$D/shard-$k.rc"; return; }
  while true; do
    [ -e "$D/STOP" ] || [ -e "$OUT.STOP" ] && { echo "### STOP file present, not (re)running" >>"$D/shard-$k.log"; rc=4; break; }
    "${JC[@]}" --traces "$TR" --out "$D/shard-$k.jsonl" --bench "$BENCH" --ids "$ids" "${JM[@]}" \
      --gap-ms 0 --seed 7 --system "$SYS" >>"$D/shard-$k.log" 2>&1
    rc=$?; echo "### exit $rc at $(date +%H:%M:%S) dies=$dies" >>"$D/shard-$k.log"
    if [ $rc -eq 3 ] || [ $rc -eq 4 ]; then dies=$((dies+1)); [ $dies -ge 2 ] && { echo "### STOP" >>"$D/shard-$k.log"; touch "$D/STOP"; break; }; continue; fi
    break
  done; echo $rc > "$D/shard-$k.rc"; }
s=$(date +%s); for k in $(seq 0 $((N-1))); do shard "$k" & done; wait
cat "$D"/shard-*.jsonl > "$OUT" 2>/dev/null || : > "$OUT"
bad=0; for k in $(seq 0 $((N-1))); do r=$(cat "$D/shard-$k.rc" 2>/dev/null || echo "?"); [ "$r" = 0 ] || { echo "shard $k failed rc=$r (see $D/shard-$k.log)" >&2; bad=1; }; done
node -e 'const fs=require("fs");const [out,idf,miss]=process.argv.slice(1);const r=fs.readFileSync(out,"utf8").split("\n").filter(Boolean).map(JSON.parse);const ids=fs.readFileSync(idf,"utf8").split("\n").map(x=>x.trim()).filter(Boolean);
const k=new Set(r.map(x=>x.queryId+"|"+x.order)),ok=new Set(r.filter(x=>x.ok).map(x=>x.queryId+"|"+x.order));const m=ids.filter(i=>!ok.has(i+"|boarA")||!ok.has(i+"|boarB"));fs.writeFileSync(miss,m.map(x=>x+"\n").join(""));
console.log(`rows ${r.length} unique ${k.size} ok ${r.filter(x=>x.ok).length} model ${[...new Set(r.map(x=>x.judgeModel))]} expected ${2*ids.length}`);
if(m.length)console.error(`MISSING ${m.length} of ${ids.length} ids (no ok judgment in both orders): ${m.join(",")}`);
process.exit(r.length===2*ids.length&&k.size===r.length&&!m.length?0:1)' "$OUT" "$IDF" "$MISSING"; chk=$?
echo "wall $(( $(date +%s) - s )) s; first log line: $(head -1 "$D/shard-0.log" 2>/dev/null | cut -c1-120)"
[ $bad -ne 0 ] && exit 3; exit $chk
