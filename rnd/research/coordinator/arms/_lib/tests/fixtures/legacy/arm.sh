#!/bin/bash
# arm.sh <conf> <command> [args]  -- one parametrised driver for the per-arm tooling (mkreq launch status wait fetch think l1 judge scales exposure chain).
# Replaces the sed-derived dh.sh/gt.sh/df.sh/dt.sh + l1.sh/l2.sh/chain*.sh copies. Conf = sourced bash (see _lib/README.md, dt512/arm.conf). Prints counts/ids/hashes/aggregates only.
# Env overrides (win over the conf): AGG_DIR WORK_DIR LOCK_DIR; REPLAY=1 (no ssh/scp: fetch validates+aggregates local traces); SKIPJUDGE=1; MINI=<host>.
set -u
CONF=${1:?usage: arm.sh <conf> <command> [args]}; CMD=${2:?command}; shift 2
L=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd); ARMS=$(cd "$L/.." && pwd); CONF_DIR=$(cd "$(dirname "$CONF")" && pwd)
H=${MINI:-MINI_HOST}; E=<workspace>/boar-eval; PL=$E/bench/v0.2/plan; PG=$E/bench/v0.3/plan/paired_gap.py
DT=$ARMS/deepthink/tools; PAIRED=$ARMS/deepvpara/tools/paired.mjs
_ag=${AGG_DIR:-}; _wd=${WORK_DIR:-}; _lk=${LOCK_DIR:-}
THINK_HIT=1024; DECL=0.306; SHARDS=4; PROMOTE_WINS=3; PROMOTE_D=0.03; CHEAPER=""; PARITY=""; REMOTE_ARGS=""; L1_SEED=42; GATE_MIN=1; GATE_MAX=1100; SMOKE_GATE=""; QUESTIONS=-
. "$CONF"
AGG_DIR=${_ag:-$AGG_DIR}; WORK_DIR=${_wd:-${WORK_DIR:-$OUT_DIR}}; LOCK_DIR=${_lk:-${LOCK_DIR:-$CONF_DIR/.locks}}
RUNNER=${REMOTE_RUNNER:-$TREE-remote-run.sh}; T=boar/kiln/be-0cfd4a77-$TREE; mkdir -p "$AGG_DIR" "$WORK_DIR" "$OUT_DIR"
QA=(); [ "$QUESTIONS" != - ] && QA=(--questions "$QUESTIONS")
cn_(){ echo "${1%%|*}"; }; cd_(){ local r=${1#*|}; echo "${r%%|*}"; }; cb_(){ local r=${1#*|}; r=${r#*|}; echo "${r//\{seed\}/$2}"; }   # CONTROLS entry "name|dir|basename-with-{seed}"

mkreq() { local src=$1 out=$2 run=$3 ids=${4:-}
  jq -c --arg r "$run" --argjson s "$SETTINGS" --arg ids "$ids" --arg a "$ARM" 'select($ids=="" or (.item.id as $i | ($ids|split(",")|index($i))!=null)) | .runId=$r | .config.settings=$s | .config.arm=$a' "$src" > "$out"
  echo "requests $(wc -l < "$out") runId $run settings $(head -1 "$out" | jq -c .config.settings) seed $(head -1 "$out" | jq .seed) sha $(shasum -a 256 "$out" | cut -c1-12)"; }
launch() { local req=$1 run=$2 lk="$LOCK_DIR/$TREE-$2.lock"; mkdir -p "$LOCK_DIR"
  [ -e "$lk" ] && { echo "REFUSE: local lock $lk exists ($(cat "$lk")); pick a new run id"; return 2; }
  ssh -T -n $H "test -e ~/$T/be-repo/runs/$run/STATUS" && { echo "REFUSE: $run already has a STATUS (a run started or finished); pick a new run id"; return 2; }
  echo "$(date +%F\ %T) sha $(shasum -a 256 "$req" | cut -c1-12)" > "$lk"
  ssh -T -n $H "mkdir -p ~/$T/be-repo/runs/$run" && scp -q "$req" "$H:$T/be-repo/runs/$run/requests.jsonl" || return 1
  ssh -T -n -f $H "nohup bash -l <runner>/kiln/$RUNNER $run $REMOTE_ARM $REMOTE_ARGS > <runner>/kiln/$TREE-$run.nohup.log 2>&1 < /dev/null &"
  echo "launched $run ($ARM/$REMOTE_ARM) at $(date +%H:%M)"; }
status() { ssh -T -n $H "cat ~/$T/be-repo/runs/$1/STATUS 2>/dev/null; echo progress \$(cat ~/$T/be-repo/runs/$1/run.log 2>/dev/null | grep -cE ' (success|error|declined|fail)') lines; tail -1 <runner>/heavy.log"; }
wait_run() { local run=$1 t0=$(date +%s) d p f r=\~/$T/be-repo/runs/$1; while :; do   # poll STATUS; WAIT_EVERY (60 s) / WAIT_HARD (5400 s)
  read -r d p f <<< "$(ssh -T -n $H "cat $r/STATUS 2>/dev/null | grep -c DONE; cat $r/run.log 2>/dev/null | grep -cE ' (success|error|declined|fail)'; cat $r/STATUS 2>/dev/null | grep -c FAIL" | tr '\n' ' ')"
  echo "$(date +%H:%M) $run done=${d:-0} progress=${p:-0} fail=${f:-0} elapsed=$(( ($(date +%s)-t0)/60 ))m"
  [ "${f:-0}" != 0 ] && { echo "RUNNER-FAIL $run"; return 3; }; [ "${d:-0}" = 1 ] && return 0
  [ $(( $(date +%s)-t0 )) -ge ${WAIT_HARD:-5400} ] && { echo "HARDSTOP $run"; return 3; }; sleep ${WAIT_EVERY:-60}; done; }
genagg() { python3 - "$1" <<'PY'
import json, sys, collections, statistics as st
T = [json.loads(l) for l in open(sys.argv[1])]
rc = lambda t: t.get("route", {}).get("reasonCodes", [])
deep = [t["itemId"] for t in T if any(c.startswith("generate:deep-model-") for c in rc(t))]
gen = collections.Counter(next((c for c in rc(t) if c.startswith("generate:")), "none") for t in T)
task = collections.Counter(next((c for c in rc(t) if c.startswith("task:")), "none") for t in T)
tier = collections.Counter(t.get("route", {}).get("tier") for t in T)
med = lambda k: st.median([t["timing"][k] for t in T if t.get("timing", {}).get(k) is not None] or [float("nan")])
det = sum(any(c.startswith("detector:p=") for c in rc(t)) for t in T)
gate = sum(any(e.get("kind") == "route-gate" for e in t.get("events", [])) for t in T)
print(json.dumps({"n": len(T), "errors": sum(bool(t.get("error")) for t in T), "errorCodes": dict(collections.Counter((t.get("error") or {}).get("code") for t in T if t.get("error"))),
  "deepRouted": len(deep), "detectorConsulted": det, "gateEvents": gate, "generate": dict(gen), "task": dict(task), "tier": dict(tier),
  "ttftMedMs": med("ttftMs"), "totalMedMs": med("totalMs"), "firstVisibleMedMs": med("firstVisibleMs"), "totalSumS": round(sum(t["timing"].get("totalMs") or 0 for t in T) / 1000),
  "deepModel": T[0]["runtime"]["versions"].get("deep.model"), "deepSha": (T[0]["runtime"]["versions"].get("deep.model.sha256") or "")[:12],
  "adapter": T[0]["runtime"]["versions"].get("adapter"), "backend": T[0]["runtime"].get("backend")}))
PY
}
fetch() { local run=$1 out=${2:-$OUT_DIR/$1.traces.jsonl} req=${3:-$OUT_DIR/$1.requests.jsonl}   # REPLAY=1: local traces only
  if [ "${REPLAY:-0}" != 1 ]; then scp -q "$H:$T/be-repo/runs/$run/traces.jsonl" "$out" || exit 1
    scp -q "$H:$T/be-repo/runs/$run/run.log" "${out%.jsonl}.log"; scp -q "$H:$T/be-repo/runs/$run/traces.server.log" "${out%.jsonl}.server.log" 2>/dev/null
    scp -q "$H:$T/be-repo/runs/$run/STATUS" "${out%.jsonl}.status"; fi
  pnpm -s -C $E/adapters/desktop-node exec tsx scripts/validate.ts "$out" --requests "$req" | grep -v '^{' | head -3
  genagg "$out"; echo "traces sha $(shasum -a 256 "$out" | cut -c1-12)"; }
think() { python3 - "$1" "${2:-}" "${3:-}" "$THINK_HIT" <<'PY'   # think <traces> [idsFile] [out.json]: per-item thinking stats (numbers only)
import json, sys, statistics as st
T=[json.loads(l) for l in open(sys.argv[1])]; want=set(open(sys.argv[2]).read().split()) if sys.argv[2] else None; HIT=int(sys.argv[4])
MSG="I have thought enough"; rows=[]
for t in T:
    if want is not None and t["itemId"] not in want: continue
    rc=t.get("route",{}).get("reasonCodes",[]); g=[e for e in t.get("events",[]) if e.get("kind")=="generation"]
    tm=t.get("timing",{}); raw=json.dumps(t)
    rows.append({"id":t["itemId"],"deepThinking":"generate:deep-thinking" in rc,"gens":len(g),
      "reasoningTokens":tm.get("reasoningTokens", sum(e.get("reasoningTokens") or 0 for e in g)),
      "maxGenReasoning":max([e.get("reasoningTokens") or 0 for e in g] or [0]),
      "budgetHitGen":sum(1 for e in g if (e.get("reasoningTokens") or 0)>=HIT),
      "budgetExceeded":any(e.get("thinkingBudgetExceeded") for e in g),
      "budgetMsgInTrace":raw.count(MSG),
      "outputTokens":sum(e.get("outputTokens") or 0 for e in g),
      "answerTokens":sum(max((e.get("outputTokens") or 0)-(e.get("reasoningTokens") or 0),0) for e in g),
      "totalMs":tm.get("totalMs"),"ttftMs":tm.get("ttftMs"),"reasoningMs":tm.get("reasoningMs"),"error":bool(t.get("error"))})
md=lambda k:st.median([r[k] for r in rows if r[k] is not None]) if rows else None
q=lambda k,p:sorted(r[k] for r in rows if r[k] is not None)[int(p*(len(rows)-1))]
th=[r for r in rows if r["deepThinking"]]
agg={"n":len(rows),"deepThinkingRouted":len(th),"errors":sum(r["error"] for r in rows),
 "reasoningTokens":{"median":md("reasoningTokens"),"p10":q("reasoningTokens",.1),"p90":q("reasoningTokens",.9),"max":max(r["reasoningTokens"] for r in rows),"zero":sum(r["reasoningTokens"]==0 for r in th)},
 "budgetHitItems_ge%d"%HIT:sum(r["budgetHitGen"]>0 for r in rows),"budgetExceededItems":sum(r["budgetExceeded"] for r in rows),"budgetMsgItems":sum(r["budgetMsgInTrace"]>0 for r in rows),
 "answerTokensMedian":md("answerTokens"),"outputTokensMedian":md("outputTokens"),"totalMsMedian":md("totalMs"),"totalMsP90":q("totalMs",.9),"ttftMsMedian":md("ttftMs"),"reasoningMsMedian":md("reasoningMs"),
 "totalSumS":round(sum(r["totalMs"] or 0 for r in rows)/1000)}
print(json.dumps(agg))
if sys.argv[3]: json.dump({"aggregate":agg,"perItem":rows},open(sys.argv[3],"w"),indent=1)
PY
}
rule() { local cl="[]"   # rule <paired.json> <arm p50 ms> <ctl p50 ms> <ctl name>: PROMOTE (wins >= ctl+PROMOTE_WINS or dRatio >= PROMOTE_D) | CHEAPER "dmin ratio" | PARITY "dmin ratio"
  [ -n "$CHEAPER" ] && cl=$(jq -c --arg a "$CHEAPER" '. + [{label:"cheaper",dmin:($a|split(" ")[0]|tonumber),ratio:($a|split(" ")[1]|tonumber)}]' <<<"$cl")
  [ -n "$PARITY" ] && cl=$(jq -c --arg a "$PARITY" '. + [{label:"parity-faster",dmin:($a|split(" ")[0]|tonumber),ratio:($a|split(" ")[1]|tonumber)}]' <<<"$cl")
  jq -r --arg L "$LABEL" --arg C "$4" --argjson gp "$2" --argjson tp "$3" --argjson pw "$PROMOTE_WINS" --argjson pd "$PROMOTE_D" --argjson cl "$cl" '
   .paired as $p | $p.winsVsRef[$L] as $wa | $p.winsVsRef[$C] as $wb | ($wa >= $wb+$pw) as $pa | ($p.dRatio >= $pd) as $pb |
   [range(0; $cl|length) as $i | $cl[$i] | . + {k: (["b","c"][$i]), ok: ($p.dRatio >= -(.dmin) and $gp <= $tp*.ratio)}] as $cs |
   "(a) wins \($L) \($wa) >= \($C) \($wb)+\($pw): \($pa) | dRatio \($p.dRatio) >= \($pd): \($pb)" +
   ($cs | map(" || (\(.k)) dRatio >= -\(.dmin): \($p.dRatio >= -(.dmin)) & p50 \($L) \($gp) <= \(.ratio)*\($C) \($tp) = \($tp*.ratio): \($gp <= $tp*.ratio)") | join("")) +
   " => " + (if $pa or $pb then "CONTINUE-promotion" else (($cs | map(select(.ok)) | .[0].label) // null | if . == null then "NO" else "CONTINUE-" + . end) end)' "$1"; }
shard() { "$DT/shard_judge.sh" "$1" "$2" "$BENCH" "$3" "$4" "$SHARDS" "$5"; }   # traces out ids system haiku|opus
l1() { local R=$1 IDS=$2 TAG=$3 tr=$OUT_DIR/$1.traces.jsonl J=$OUT_DIR/$1.judgments.haiku55-low.jsonl c0=${CONTROLS[0]} cn cdir cb gp tp   # fetch, think, Haiku N=4 judge, paired vs control, rule
  cn=$(cn_ "$c0"); cdir=$(cd_ "$c0"); cb=$cdir/$(cb_ "$c0" $L1_SEED); P=$WORK_DIR/$R.${LABEL}vs$cn.haiku55-low.json
  fetch "$R" "$tr" "$OUT_DIR/$R.requests.jsonl" | tee $AGG_DIR/gen-$TAG.txt
  think "$tr" "$IDS" "$WORK_DIR/think-$TAG.perItem.json" > $AGG_DIR/think-$LABEL-$TAG.json; cat $AGG_DIR/think-$LABEL-$TAG.json
  think "$cb.traces.jsonl" "$IDS" "" > $AGG_DIR/think-$cn-$TAG.json
  [ "${SKIPJUDGE:-0}" = 1 ] || shard "$tr" "$J" "$IDS" "$JUDGE_SYSTEM-haiku55-low" haiku
  [ -s "$J" ] || { echo "no Haiku judgments for $R: stop after think"; return 0; }
  node $PAIRED "$J" "$cb.judgments.haiku55-low.jsonl" "$IDS" $LABEL $cn > "$P"
  jq 'del(.perItem)' "$P" > $AGG_DIR/L1-${LABEL}vs$cn-$TAG.haiku55-low.json
  jq -c --arg L $LABEL --arg C $cn '{($L):{ratio:.[$L].ratio,ci:.[$L].ci,floorAdj:.[$L].floorAdj,win:.[$L].win}, ($C):{ratio:.[$C].ratio,ci:.[$C].ci,floorAdj:.[$C].floorAdj,win:.[$C].win}, paired, missing}' $AGG_DIR/L1-${LABEL}vs$cn-$TAG.haiku55-low.json
  gp=$(jq .totalMsMedian $AGG_DIR/think-$LABEL-$TAG.json); tp=$(jq .totalMsMedian $AGG_DIR/think-$cn-$TAG.json)
  rule $AGG_DIR/L1-${LABEL}vs$cn-$TAG.haiku55-low.json "$gp" "$tp" $cn | tee $AGG_DIR/L1-rule-$TAG.txt; }
judge() { local R=$RUN_PREFIX-s$1; shard "$OUT_DIR/$R.traces.jsonl" "$OUT_DIR/$R.judgments.jsonl" "$JUDGED_IDS" "$JUDGE_SYSTEM-opus" opus 2>&1 | tee "$WORK_DIR/$R.opus.shardrun.out" | grep -v " boar" | tail -3
  grep -h "### exit" "$OUT_DIR/$R.judgments.shards"/shard-*.log | sort | uniq -c; }
fm() { python3 $PL/floor_metrics.py --runs $1 --dir $2 --decline-ratio $DECL --ids $JUDGED_IDS "${QA[@]}"; }   # floor_metrics for runs/dir
scales() { local seeds=$1 n s i e rg="" jg="" P=() PGD obj gt; n=$(wc -w <<<"$seeds" | tr -d ' '); PGD=$WORK_DIR/paired-${n}seed; mkdir -p $PGD   # two-seed scales beside every control
  for s in $seeds; do rg="$rg $RUN_PREFIX-s$s"; jg="$jg $OUT_DIR/$RUN_PREFIX-s$s.judgments.jsonl"; done
  obj=$(jq -n --arg k $LABEL --argjson v "$(fm "$rg" "$OUT_DIR")" '{($k):$v}'); local -a RCS=()
  for e in "${CONTROLS[@]}"; do local rc="" nm=$(cn_ "$e") d=$(cd_ "$e"); for s in $seeds; do rc="$rc $(cb_ "$e" $s)"; done; RCS+=("$rc")
    obj=$(jq --arg k $nm --argjson v "$(fm "$rc" "$d")" '. + {($k):$v}' <<<"$obj"); done
  for s in $seeds; do for e in "${CONTROLS[@]}"; do local nm=$(cn_ "$e") d=$(cd_ "$e") b=$(cb_ "$e" $s)
    P+=("$(node $PAIRED $OUT_DIR/$RUN_PREFIX-s$s.judgments.jsonl $d/$b.judgments.jsonl $JUDGED_IDS $LABEL $nm | jq -c --arg s $s --arg v $nm '{seed:$s,vs:$v} + del(.perItem)')")
    for f in $OUT_DIR/$RUN_PREFIX-s$s $d/$b; do for x in judgments traces; do ln -sf $f.$x.jsonl $PGD/; done; done; done; done
  i=0; for e in "${CONTROLS[@]}"; do local nm=$(cn_ "$e") rc=${RCS[$i]}; i=$((i+1))
    gt=$(python3 $PG --dir $PGD --a $rg --b $rc "${QA[@]}" --decline-ratio $DECL 2>/dev/null | jq -c .); echo "$gt" > $AGG_DIR/paired_gap-${LABEL}vs$nm-${n}seed.json; echo "gap$nm $gt"
    if [ $i = 1 ]; then local jt=""; for s in $seeds; do jt="$jt $(cd_ "$e")/$(cb_ "$e" $s).judgments.jsonl"; done
      python3 $DT/dtcat.py ${LABEL}vs$nm-${n}seed $JUDGED_IDS "$jg" "$jt" $AGG_DIR/cat-${LABEL}vs$nm-${n}seed.opus.json > /dev/null 2>&1 || echo "dtcat failed (non-blocking)"; fi; done
  jq --argjson p "$(printf '%s\n' "${P[@]}" | jq -s .)" '. + {paired:$p}' <<<"$obj" > $AGG_DIR/L2-$LABEL-${n}seed.opus.json
  jq -c 'to_entries[] | select(.key!="paired") | {arm:.key, runs:.value.runs, n:.value.n_items, raw:.value.raw, floorAdj:.value.above_min, aboveDecl:.value.above_decl}' $AGG_DIR/L2-$LABEL-${n}seed.opus.json
  jq -c --arg L $LABEL '.paired[] | {seed, vs, n:.paired.n, (($L+"ratio")):.[$L].ratio, (("win"+$L)):.[$L].win, winRateCI:.[$L].winRateCI, dRatio:.paired.dRatio, dRatioCI:.paired.dRatioCI, dFloor:.paired.dFloor, dFloorCI:.paired.dFloorCI, h2h:.paired.headToHead}' $AGG_DIR/L2-$LABEL-${n}seed.opus.json; }
exposure() { local tf jf; tf=$(ls $OUT_DIR/$RUN_PREFIX*.traces.jsonl 2>/dev/null); jf=$(ls $OUT_DIR/$RUN_PREFIX*.judgments*.jsonl 2>/dev/null)   # one-line exposure summary (counts only)
  echo "EXPOSURE set=$SET arm=$ARM trace_runs=$(echo $tf | wc -w | tr -d ' ') trace_items=$(cat $tf 2>/dev/null | wc -l | tr -d ' ') judgment_files=$(echo $jf | wc -w | tr -d ' ') $(cat $jf 2>/dev/null | jq -r '"judge_calls=\(length) ok=\(map(select(.ok))|length) ids=\(map(.queryId)|unique|length) by_model=\(group_by(.judgeModel)|map("\(.[0].judgeModel//"?"):\(length)")|join(","))"' -s)"; }
gate() { GATE_MIN=$GATE_MIN GATE_MAX=$GATE_MAX python3 "${SMOKE_GATE:-/dev/stdin}" "$1" <<'PY'   # default gate: all deep-thinking, 0 errors, non-empty answers, GATE_MIN <= reasoning <= GATE_MAX
import json,sys,os
ok=True; lo,hi=int(os.environ["GATE_MIN"]),int(os.environ["GATE_MAX"])
for t in map(json.loads, open(sys.argv[1])):
    g=[e for e in t.get('events',[]) if e.get('kind')=='generation']; rc=t.get('route',{}).get('reasonCodes',[])
    r=sum(e.get('reasoningTokens') or 0 for e in g); a=t.get('answer'); a=a.get('text','') if isinstance(a,dict) else str(a or '')
    print(f"{t['itemId']} deepThinking={'generate:deep-thinking' in rc} reasoning={r} answerWords={len(a.split())} error={bool(t.get('error'))} totalS={round(t['timing']['totalMs']/1000,1)} budgetExceeded={any(e.get('thinkingBudgetExceeded') for e in g)}")
    ok = ok and ('generate:deep-thinking' in rc) and lo <= r <= hi and len(a.split())>0 and not t.get('error')
print("SMOKE", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
PY
}
chain() { local K=$SMOKE_DIR   # smoke (launch, wait, fetch, think, gate) -> slice (launch, wait, l1). Conf: SMOKE_{REQ,RUN,DIR} SLICE_{REQ,RUN,IDS}
  [ -n "$SMOKE_GATE" ] && [ ! -f "$SMOKE_GATE" ] && { echo "SMOKE_GATE not found"; exit 4; }
  launch "$SMOKE_REQ" "$SMOKE_RUN" && wait_run "$SMOKE_RUN" || exit 3
  fetch "$SMOKE_RUN" "$K/$SMOKE_RUN.traces.jsonl" "$K/$SMOKE_RUN.requests.jsonl" | tail -2
  think "$K/$SMOKE_RUN.traces.jsonl" "" "$K/$SMOKE_RUN.think.json" > $AGG_DIR/think-$LABEL-smoke.json
  gate "$K/$SMOKE_RUN.traces.jsonl" || exit 4
  launch "$SLICE_REQ" "$SLICE_RUN" && wait_run "$SLICE_RUN" || exit 3
  l1 "$SLICE_RUN" "$SLICE_IDS" slice 2>&1 | grep -v " boar" | tail -4; echo CHAIN-DONE; }
case $CMD in
  mkreq|launch|status|fetch|think|l1|judge|scales|exposure|chain|gate) $CMD "$@";;
  wait) wait_run "$@";;
  *) echo "unknown command $CMD (mkreq launch status wait fetch think l1 judge scales exposure chain gate)"; exit 2;;
esac
