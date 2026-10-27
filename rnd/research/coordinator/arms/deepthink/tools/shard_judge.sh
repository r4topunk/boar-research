#!/bin/bash
# DEEPTHINK judge shards = deepvpara shard_judge.sh + 7th arg MODEL (haiku: claude-haiku-5-5 --effort low [L1]; opus: judge.mjs default opus, judge.v1 [L2/OPUSSHARD]).
# Usage: shard_judge.sh <traces> <out.jsonl> <bench dir> <ids file (one per line)> <system name> [N=4] [haiku|opus]
# Round-robin ids (ids-file order) into N shards, judge.mjs --judge-model ... --gap-ms 0 --seed 7,
# rerun a shard on exit 3/4 (judge.mjs resumes ok rows), STOP after 2 dies. Concatenates, asserts every id has both orders (rows = 2*n).
# FAIL CLOSED (2026-10-11): exits non-zero unless every shard exited 0 AND every id has both orders judged.
#   rc 0 ok | 1 incomplete (ids named on stderr, listed in <out>.missing) | 3 a shard failed (rc in <out>.shards/shard-K.rc) | 4 STOP file present
#   (<out>.shards/STOP or <out>.STOP: refuses to start; also checked before every shard rerun; touched after 2 dies) | 5 output locked (mkdir lock <out>.lock).
# Env: BOAR_EVAL_DIR (default boar-eval), JUDGE_CMD (default "node harness/judge.mjs"; tests stub it), JUDGE_FLOOR_ERRORED=1 -> errored traces are
#   floor-scored in one final judge.mjs --floor-errored pass over the concatenated output (0 calls; reference mean pooled over all shards, not per shard),
#   ALLOW_SPLICE=1 -> pass --allow-splice (judge.mjs resumes rows of other provenance) and skip the one-tracesSha256 check below.
# PIPELINE-AUDIT 2026-10-13: F1 the final check also asserts one judgeModel (floor rows aside), requestedModel = this run's model when present, and
#   (unless ALLOW_SPLICE=1) every row's tracesSha256 = sha256 of <traces>; F4 floor pass as above; F6 INT/TERM kill the shards before the lock is released.
# --preflight (LOOP v2 T5/D5): `shard_judge.sh --preflight <same args as a run>` runs the guards of _lib/preflight.py (provenance of resumed rows, control rows present, calls_cap /
#   declared calls, Opus-on-dev) and a live both-orders probe (PREFLIGHT_PROBE_IDS ids, default 1; on the arm traces and on PREFLIGHT_CONTROL_TRACES) BEFORE any pass. rc 0 = `PREFLIGHT OK ...`;
#   rc 8 = `PREFLIGHT REFUSED <code>: ...` on stderr, nothing written to <out>, no lock. Env: PREFLIGHT_CRITERION PREFLIGHT_CONTROL PREFLIGHT_CONTROL_REQUIRED=1 PREFLIGHT_CONTROL_TRACES
#   PREFLIGHT_SET PREFLIGHT_SETS_TSV PREFLIGHT_PROBE_IDS PREFLIGHT_DECLARED_CALLS (+ ALLOW_SPLICE JUDGE_CMD BOAR_EVAL_DIR). Probe rows go to <out>.preflight/{arm,control}.jsonl.
set -u
PF=0; [ "${1:-}" = "--preflight" ] && { PF=1; shift; }
abs() { case $1 in /*) echo "$1";; *) echo "$PWD/$1";; esac; }
TR=$(abs "$1"); OUT=$(abs "$2"); BENCH=$(abs "$3"); IDF=$(abs "$4"); SYS=$5; N=${6:-4}; MODEL=${7:-haiku}
EVAL=${BOAR_EVAL_DIR:-<workspace>/boar-eval}; read -r -a JC <<< "${JUDGE_CMD:-node harness/judge.mjs}"
if [ "$MODEL" = opus ]; then JM=(--judge-model opus); else JM=(--judge-model claude-haiku-5-5 --effort low); fi
[ "${ALLOW_SPLICE:-0}" = 1 ] && JM+=(--allow-splice)
D="${OUT%.jsonl}.shards"; MISSING="${OUT%.jsonl}.missing"
if [ $PF = 1 ]; then
  PL=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../_lib" && pwd); PFD="$OUT.preflight"; pfm=haiku; [ "$MODEL" = opus ] && pfm=opus
  [ -e "$OUT.lock" ] && { echo "PREFLIGHT REFUSED locked: $OUT.lock is held ($(cat "$OUT.lock/owner" 2>/dev/null))" >&2; exit 8; }
  pa=(check --traces "$TR" --out "$OUT" --ids "$IDF" --model "$pfm" --set "${PREFLIGHT_SET:-unknown}" --sets-tsv "${PREFLIGHT_SETS_TSV:-$PL/sets.tsv}")
  [ -n "${PREFLIGHT_CRITERION:-}" ] && pa+=(--criterion "$PREFLIGHT_CRITERION"); [ -n "${PREFLIGHT_CONTROL:-}" ] && pa+=(--control "$PREFLIGHT_CONTROL")
  [ "${PREFLIGHT_CONTROL_REQUIRED:-0}" = 1 ] && pa+=(--control-required); [ -n "${PREFLIGHT_DECLARED_CALLS:-}" ] && pa+=(--declared "$PREFLIGHT_DECLARED_CALLS")
  [ "${ALLOW_SPLICE:-0}" = 1 ] && pa+=(--allow-splice)
  line=$(python3 -I "$PL/preflight.py" "${pa[@]}") || exit $?
  K=${PREFLIGHT_PROBE_IDS:-1}; PIDS=(); while read -r x; do [ -n "$x" ] && PIDS+=("$x"); done < "$IDF"; pj=""; if [ ${#PIDS[@]} -gt 0 ]; then PIDS=("${PIDS[@]:0:$K}"); [ ${#PIDS[@]} -gt 0 ] && pj=$(IFS=,; echo "${PIDS[*]}"); fi
  if [ -n "$pj" ]; then
    cd "$EVAL" || exit 2; rm -rf "$PFD"; mkdir -p "$PFD"
    pjudge() { "${JC[@]}" --traces "$1" --out "$2" --bench "$BENCH" --ids "$pj" "${JM[@]}" --gap-ms 0 --seed 7 --system "$SYS" >"$2.log" 2>&1; }
    pjf() { echo "PREFLIGHT REFUSED probe_failed: judge exited rc=$1 on the probe ($2; log $2.log)" >&2; exit 8; }
    pjudge "$TR" "$PFD/arm.jsonl" || pjf $? arm.jsonl; python3 -I "$PL/preflight.py" verify --file "$PFD/arm.jsonl" --ids "$pj" || exit $?
    if [ -n "${PREFLIGHT_CONTROL_TRACES:-}" ]; then
      pjudge "$(abs "$PREFLIGHT_CONTROL_TRACES")" "$PFD/control.jsonl" || pjf $? control.jsonl; python3 -I "$PL/preflight.py" verify --file "$PFD/control.jsonl" --ids "$pj" || exit $?; fi
  fi
  echo "$line probe=${#PIDS[@]} ids"; exit 0
fi
for st in "$OUT.STOP" "$D/STOP"; do [ -e "$st" ] && { echo "STOP file present ($st): refusing to run; remove it after fixing the cause" >&2; exit 4; }; done
LK="$OUT.lock"; mkdir -p "$(dirname "$OUT")"
mkdir "$LK" 2>/dev/null || { echo "LOCKED: $LK is held ($(cat "$LK/owner" 2>/dev/null)); another judge run owns $OUT. If that run is dead, rm -r $LK" >&2; exit 5; }
echo "pid=$$ started=$(date '+%F %T') host=$(hostname -s)" > "$LK/owner"
trap 'rm -rf "$LK"' EXIT
on_sig() { local j; for j in $(jobs -p); do pkill -TERM -P "$j" 2>/dev/null; kill "$j" 2>/dev/null; done; wait; exit 130; }   # F6: shards die before the lock goes
trap on_sig INT TERM
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
if [ $bad = 0 ] && [ "${JUDGE_FLOOR_ERRORED:-0}" = 1 ]; then   # F4: floor-score errored traces once, over all shards' rows (pooled reference mean)
  "${JC[@]}" --traces "$TR" --out "$OUT" --bench "$BENCH" --ids "$(IFS=,; echo "${IDS[*]}")" "${JM[@]}" --floor-errored --gap-ms 0 --seed 7 --system "$SYS" >>"$D/floor.log" 2>&1 \
    || { echo "floor pass failed rc=$? (see $D/floor.log)" >&2; bad=1; }; fi
TSHA=$(shasum -a 256 "$TR" | cut -d' ' -f1); RQM=${JM[1]}
node -e 'const fs=require("fs");const [out,idf,miss,tsha,rqm,splice]=process.argv.slice(1);const r=fs.readFileSync(out,"utf8").split("\n").filter(Boolean).map(JSON.parse);const ids=fs.readFileSync(idf,"utf8").split("\n").map(x=>x.trim()).filter(Boolean);
const k=new Set(r.map(x=>x.queryId+"|"+x.order)),ok=new Set(r.filter(x=>x.ok).map(x=>x.queryId+"|"+x.order));const m=ids.filter(i=>!ok.has(i+"|boarA")||!ok.has(i+"|boarB"));fs.writeFileSync(miss,m.map(x=>x+"\n").join(""));
console.log(`rows ${r.length} unique ${k.size} ok ${r.filter(x=>x.ok).length} model ${[...new Set(r.map(x=>x.judgeModel))]} expected ${2*ids.length}`);
if(m.length)console.error(`MISSING ${m.length} of ${ids.length} ids (no ok judgment in both orders): ${m.join(",")}`);
const okr=r.filter(x=>x.ok),jm=[...new Set(okr.filter(x=>!x.floorScored).map(x=>String(x.judgeModel)))],rq=[...new Set(okr.map(x=>x.requestedModel).filter(x=>x!==undefined))],ts=[...new Set(okr.map(x=>x.tracesSha256).filter(x=>x!==undefined))];let prov=true;
if(jm.length>1){console.error(`PROVENANCE: ${jm.length} judge models in ${out}: ${jm.join(",")}`);prov=false}
const lg=[...new Set(okr.filter(x=>!x.floorScored&&x.requestedModel===undefined&&x.tracesSha256!==undefined).map(x=>String(x.judgeModel)))].filter(x=>!x.includes(rqm));
if(rq.some(x=>x!==rqm)||lg.length){console.error(`PROVENANCE: requested model ${[...rq,...lg].join(",")} != this run ${rqm}`);prov=false}
if(splice!=="1"&&ts.some(x=>x!==tsha)){console.error(`PROVENANCE: tracesSha256 ${ts.map(x=>x.slice(0,12)).join(",")} != traces ${tsha.slice(0,12)} (ALLOW_SPLICE=1 declares a splice)`);prov=false}
process.exit(r.length===2*ids.length&&k.size===r.length&&!m.length&&prov?0:1)' "$OUT" "$IDF" "$MISSING" "$TSHA" "$RQM" "${ALLOW_SPLICE:-0}"; chk=$?
echo "wall $(( $(date +%s) - s )) s; first log line: $(head -1 "$D/shard-0.log" 2>/dev/null | cut -c1-120)"
[ $bad -ne 0 ] && exit 3; exit $chk
