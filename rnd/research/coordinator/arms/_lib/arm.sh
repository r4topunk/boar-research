#!/bin/bash
# arm.sh <conf> <command> [args]  -- one parametrised driver for the per-arm tooling (mkreq launch status wait fetch think l1 judge scales exposure chain precheck smoke crit_check).
# Replaces the sed-derived dh.sh/gt.sh/df.sh/dt.sh + l1.sh/l2.sh/chain*.sh copies. Conf = sourced bash (see _lib/README.md, dt512/arm.conf). Prints counts/ids/hashes/aggregates only.
# Env overrides (win over the conf): AGG_DIR WORK_DIR LOCK_DIR; REPLAY=1 (no ssh/scp: fetch validates+aggregates local traces); SKIPJUDGE=1; MINI=<host>.
# Fail closed (2026-10-11): l1/judge/scales abort (rc 5) unless the judge exited 0 and every judged id has both orders (check_judgments.py); fetch aborts on a FAIL/missing-DONE STATUS;
# judge output and aggregates are mkdir-locked. CONTROL_CHECK=warn downgrades the control-arm checks (and drops --strict) for replays of old frozen controls.
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
CK=$L/check_judgments.py; PFLAGS=--strict; [ "${CONTROL_CHECK:-strict}" = warn ] && PFLAGS=""
with_lock() { local lk=$1; shift   # with_lock <lockdir> cmd...: mkdir-atomic lock held for the duration of cmd (own subshell EXIT trap releases it, also on exit/abort); rc 6 if held
  mkdir "$lk" 2>/dev/null || { echo "LOCKED: $lk is held ($(cat "$lk/owner" 2>/dev/null)); another chain writes the same output. If that run is dead: rm -r $lk" >&2; return 6; }
  echo "pid=$$ $(date '+%F %T') $CMD" > "$lk/owner"; ( trap 'rm -rf "$lk"' EXIT; "$@" ); }
chk_() { python3 "$CK" "$@"; }   # chk_ <judgments> <ids> [label]
cn_(){ echo "${1%%|*}"; }; cd_(){ local r=${1#*|}; echo "${r%%|*}"; }; cb_(){ local r=${1#*|}; r=${r#*|}; echo "${r//\{seed\}/$2}"; }   # CONTROLS entry "name|dir|basename-with-{seed}"

mkreq() { local src=$1 out=$2 run=$3 ids=${4:-}
  jq -c --arg r "$run" --argjson s "$SETTINGS" --arg ids "$ids" --arg a "$ARM" 'select($ids=="" or (.item.id as $i | ($ids|split(",")|index($i))!=null)) | .runId=$r | .config.settings=$s | .config.arm=$a' "$src" > "$out"
  echo "requests $(wc -l < "$out") runId $run settings $(head -1 "$out" | jq -c .config.settings) seed $(head -1 "$out" | jq .seed) sha $(shasum -a 256 "$out" | cut -c1-12)"; }
crit_power() {   # (was crit_check before LOOP v2 T3) rc 7 unless $CRITERION exists, matches its sibling .sha256 (if any), and has a ## Power block (expected_delta n seeds mde) or the tag blocker
  local c=${CRITERION:-} k s h
  [ -z "$c" ] && { echo "launch refused: CRITERION is not set in the arm conf — set CRITERION=<frozen criterion .md> (see _lib/CRITERION-TEMPLATE.md)" >&2; return 7; }
  case $c in /*) ;; *) c=$CONF_DIR/$c;; esac
  [ -f "$c" ] || { echo "launch refused: criterion file not found: $c — see _lib/CRITERION-TEMPLATE.md" >&2; return 7; }
  for s in "${c%.md}.sha256" "$c.sha256"; do [ -f "$s" ] && { h=$(awk 'NR==1{print $1}' "$s"); [ "$h" = "$(shasum -a 256 "$c" | cut -d' ' -f1)" ] || { echo "launch refused: sha256 mismatch for criterion $c (expected $h in $s)" >&2; return 7; }; break; }; done
  awk '/^## Tags/{t=1; if($0~/blocker/)f=1; next} /^## /{t=0} t&&/^Tags:.*blocker/{f=1} END{exit !f}' "$c" && return 0
  local pw; pw=$(awk '/^## Power[[:space:]]*$/{p=1;next} /^## /{p=0} p' "$c")
  for k in expected_delta n seeds mde; do printf '%s\n' "$pw" | grep -Eq "^[-* ]*$k:[[:space:]]*[^[:space:]]" || { echo "launch refused: criterion lacks Power block (expected_delta, n, seeds, mde) — see _lib/CRITERION-TEMPLATE.md" >&2; return 7; }; done
  return 0; }
crit_path() { local c=${CRITERION:-}; case $c in /*) ;; *) c=$CONF_DIR/$c;; esac; echo "$c"; }
tag_has() { awk -v w="$2" '/^## Tags/{t=1; if(index($0,w))f=1; next} /^## /{t=0} t&&/^Tags:/&&index($0,w){f=1} END{exit !f}' "$1"; }   # tag_has <criterion> <blocker|probe>
ruleset_of() { awk '/^Ruleset:/{n=$2; gsub(/[^0-9]/,"",n); print n+0; f=1; exit} END{if(!f)print 0}' "$1"; }   # Ruleset: N line, 0 if absent (legacy criterion)
frozen_sha() { local f=$1 d; d=$(cd "$(dirname "$f")" && pwd) || return 1   # frozen_sha <file> [<rev>]: sha256 of the frozen part (sed boundary rule; whole file when no marker). With <rev>, of that git blob (git show <rev>:<path>) instead of the working file
  if [ -n "${2:-}" ]; then local top rel; top=$(git -C "$d" rev-parse --show-toplevel 2>/dev/null) || return 1; rel=$(git -C "$d" ls-files --full-name -- "$(basename "$f")" | head -1); [ -n "$rel" ] || return 1
    git -C "$top" show "$2:$rel" 2>/dev/null | sed '/^<!-- END FROZEN -->$/q' | shasum -a 256 | cut -d' ' -f1
  else sed '/^<!-- END FROZEN -->$/q' "$f" | shasum -a 256 | cut -d' ' -f1; fi; }
crit_check() {   # LOOP v2 D3 (T3): rc 0 only if <criterion dir>/smoke.verdict.json exists, verdict PASS and criterion_sha == sha256 of the criterion now; else rc 7 + one line. A FAIL/KILL is cleared only by a new freeze (new sha) and a new smoke.
  [ -n "${CRITERION:-}" ] || { echo "launch refused: CRITERION is not set in the arm conf" >&2; return 7; }
  local c v got want vd rs hd; c=$(crit_path); v=$(dirname "$c")/smoke.verdict.json
  [ -f "$c" ] || { echo "launch refused: criterion file not found: $c" >&2; return 7; }
  [ -f "$v" ] || { echo "launch refused: no smoke verdict ($v): run arm.sh <conf> smoke <smoke traces|units.jsonl> --n-full N (smoke FAIL is cleared only by a new freeze)" >&2; return 7; }
  want=$(frozen_sha "$c"); got=$(jq -r '.criterion_sha // ""' "$v" 2>/dev/null); vd=$(jq -r '.verdict // ""' "$v" 2>/dev/null)
  if git -C "$(dirname "$c")" ls-files --error-unmatch -- "$(basename "$c")" >/dev/null 2>&1; then   # tracked: the frozen part must equal the committed blob
    hd=$(frozen_sha "$c" HEAD) && [ -n "$hd" ] && [ "$hd" != "$want" ] && { echo "launch refused: criterion edited after commit (frozen part ${want:0:12} != HEAD ${hd:0:12}): commit or revert, then re-freeze and smoke again" >&2; return 7; }
  fi
  [ "$got" = "$want" ] || { echo "launch refused: smoke verdict is for criterion sha ${got:0:12}, not ${want:0:12} (criterion edited or re-frozen since the smoke): smoke again" >&2; return 7; }
  [ "$vd" = PASS ] || { rs=$(jq -r '(.reasons // []) | join("; ")' "$v" 2>/dev/null); echo "launch refused: smoke verdict is $vd for this criterion sha (${rs:0:200}); cleared only by a new freeze" >&2; return 7; }
  return 0; }
smoke_gate() {   # launch-time gate of LOOP v2 T3; applies to criteria with Ruleset >= 30 only (older frozen criteria keep the Power-block check alone)
  local c; c=$(crit_path); [ "$(ruleset_of "$c")" -ge 30 ] || return 0
  tag_has "$c" blocker || python3 -I "$L/smoke-project.py" --check-block "$c" || return 7   # ## Precheck block complete and filled (waived by Tags: blocker)
  if [ "${SMOKE_SKIP:-0}" = 1 ]; then
    if tag_has "$c" blocker || tag_has "$c" probe; then echo "SMOKE_SKIP=1: smoke gate waived (Tags: blocker|probe)" >&2; return 0; fi
    echo "launch refused: SMOKE_SKIP=1 is allowed only for a criterion tagged blocker or probe" >&2; return 7; fi
  crit_check; }
smoke() { [ -n "${CRITERION:-}" ] || { echo "smoke refused: CRITERION is not set in the arm conf" >&2; return 7; }   # smoke <smoke traces|units.jsonl> --n-full N [--marker code]: verdict -> <criterion dir>/smoke.verdict.json (rc 0 PASS, 1 FAIL, 3 KILL)
  local c in=${1:?usage: smoke <smoke traces|units.jsonl> --n-full N [--marker code]}; shift; c=$(crit_path)
  [ -f "$c" ] || { echo "smoke refused: criterion file not found: $c" >&2; return 7; }
  if [ -f "$in" ] && head -1 "$in" | grep -q '"itemId"'; then   # LOOP v2 T5: identity of the smoke traces (units.jsonl have no trace metadata and skip it)
    if [ "${IDENTITY_SKIP:-0}" = 1 ]; then
      if tag_has "$c" blocker || tag_has "$c" probe; then echo "IDENTITY_SKIP=1: identity check waived (Tags: blocker|probe)" >&2
      else echo "smoke refused: IDENTITY_SKIP=1 is allowed only for a criterion tagged blocker or probe" >&2; return 7; fi
    else local ia=(--gen "$in" --mode on --write-verdict "$c"); [ -n "${ADAPTER_PIN:-}" ] && ia+=(--adapter "$ADAPTER_PIN"); [ -n "${PATCH_SHA256:-}" ] && ia+=(--patch-sha "$PATCH_SHA256")
      python3 -I "$L/identity.py" "${ia[@]}" || return 1; fi
  fi
  python3 -I "$L/smoke-project.py" "$in" "$c" "$@"; }
preflight_() {   # preflight_ <traces> <out> <ids> <system> <haiku|opus> <control judgments|-> <control traces|->: shard_judge.sh --preflight for Ruleset >= 30 criteria (LOOP v2 T5); rc 8 = refused
  local c; [ -n "${CRITERION:-}" ] || return 0; c=$(crit_path); [ -f "$c" ] || return 0; [ "$(ruleset_of "$c")" -ge 30 ] || return 0
  [ "${PREFLIGHT:-1}" = 0 ] && { echo "preflight skipped (PREFLIGHT=0)"; return 0; }
  local req=1; [ "${CONTROL_CHECK:-strict}" = warn ] && req=0
  PREFLIGHT_CRITERION=$c PREFLIGHT_SET=$SET PREFLIGHT_CONTROL_REQUIRED=$req PREFLIGHT_CONTROL=$( [ "$6" = - ] && echo "" || echo "$6") PREFLIGHT_CONTROL_TRACES=$( [ "$7" = - ] && echo "" || echo "$7") \
    "$DT/shard_judge.sh" --preflight "$1" "$2" "$BENCH" "$3" "$4" "$SHARDS" "$5" || return 8; }
launch() { local req=$1 run=$2 lk="$LOCK_DIR/$TREE-$2.lock"; crit_power || return 7; smoke_gate || return 7; mkdir -p "$LOCK_DIR"
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
  local st=${out%.jsonl}.status
  if [ "${REPLAY:-0}" != 1 ]; then scp -q "$H:$T/be-repo/runs/$run/STATUS" "$st" || { echo "ABORT fetch: no STATUS for $run"; exit 3; }; fi
  if [ -s "$st" ]; then grep -q '^FAIL' "$st" && { echo "ABORT fetch: runner $run FAILED: $(grep '^FAIL' "$st" | head -1)"; exit 3; }
    grep -qx DONE "$st" || { echo "ABORT fetch: STATUS of $run has no DONE"; exit 3; }
  elif [ "${REPLAY:-0}" != 1 ]; then echo "ABORT fetch: empty STATUS for $run"; exit 3; fi
  if [ "${REPLAY:-0}" != 1 ]; then scp -q "$H:$T/be-repo/runs/$run/traces.jsonl" "$out" || exit 1
    scp -q "$H:$T/be-repo/runs/$run/run.log" "${out%.jsonl}.log"; scp -q "$H:$T/be-repo/runs/$run/traces.server.log" "${out%.jsonl}.server.log" 2>/dev/null; fi
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
judge_lane_() { local h s; h=$("$ARMS/../tools/lock.sh" holder judge 2>/dev/null) || return 0; s=${h%% *}   # LOOP v2 T6: rc 9 when another session (lock.sh) holds the judge lane
  case "$h" in free|"") return 0;; esac; [ "$s" = "${BOAR_SESSION:-main}" ] && return 0; echo "ABORT judge: judge lane locked by $s until ${h#* until } (lock.sh)"; return 9; }
l1() { with_lock "$AGG_DIR/.agg-$LABEL.lock" l1_ "$@"; }
l1_() { local R=$1 IDS=$2 TAG=$3 tr=$OUT_DIR/$1.traces.jsonl J=$OUT_DIR/$1.judgments.haiku55-low.jsonl c0=${CONTROLS[0]} cn cdir cb gp tp   # fetch, think, Haiku N=4 judge, paired vs control, rule
  cn=$(cn_ "$c0"); cdir=$(cd_ "$c0"); cb=$cdir/$(cb_ "$c0" $L1_SEED); P=$WORK_DIR/$R.${LABEL}vs$cn.haiku55-low.json
  fetch "$R" "$tr" "$OUT_DIR/$R.requests.jsonl" | tee $AGG_DIR/gen-$TAG.txt
  think "$tr" "$IDS" "$WORK_DIR/think-$TAG.perItem.json" > $AGG_DIR/think-$LABEL-$TAG.json; cat $AGG_DIR/think-$LABEL-$TAG.json
  think "$cb.traces.jsonl" "$IDS" "" > $AGG_DIR/think-$cn-$TAG.json
  [ "${SKIPJUDGE:-0}" = 1 ] || judge_lane_ || return 9
  [ "${SKIPJUDGE:-0}" = 1 ] || preflight_ "$tr" "$J" "$IDS" "$JUDGE_SYSTEM-haiku55-low" haiku "$cb.judgments.haiku55-low.jsonl" "$cb.traces.jsonl" || { echo "ABORT l1: preflight refused"; return 8; }
  [ "${SKIPJUDGE:-0}" = 1 ] || shard "$tr" "$J" "$IDS" "$JUDGE_SYSTEM-haiku55-low" haiku || { echo "ABORT l1: judge stage failed (rc $?) for $R"; return 5; }
  if [ ! -e "$J" ]; then [ "${SKIPJUDGE:-0}" = 1 ] && { echo "no Haiku judgments for $R: stop after think (SKIPJUDGE=1)"; return 0; }; echo "ABORT l1: no judgments file for $R"; return 5; fi
  chk_ "$J" "$IDS" "l1 $R" || { echo "ABORT l1: judgments of $R incomplete"; return 5; }
  chk_ "$cb.judgments.haiku55-low.jsonl" "$IDS" "l1 control $cn" || [ "${CONTROL_CHECK:-strict}" = warn ] || { echo "ABORT l1: control judgments incomplete"; return 5; }
  node $PAIRED "$J" "$cb.judgments.haiku55-low.jsonl" "$IDS" $LABEL $cn $PFLAGS > "$P" || { echo "ABORT l1: paired.mjs failed"; return 5; }
  jq 'del(.perItem)' "$P" > $AGG_DIR/L1-${LABEL}vs$cn-$TAG.haiku55-low.json
  jq -c --arg L $LABEL --arg C $cn '{($L):{ratio:.[$L].ratio,ci:.[$L].ci,floorAdj:.[$L].floorAdj,win:.[$L].win}, ($C):{ratio:.[$C].ratio,ci:.[$C].ci,floorAdj:.[$C].floorAdj,win:.[$C].win}, paired, missing}' $AGG_DIR/L1-${LABEL}vs$cn-$TAG.haiku55-low.json
  gp=$(jq .totalMsMedian $AGG_DIR/think-$LABEL-$TAG.json); tp=$(jq .totalMsMedian $AGG_DIR/think-$cn-$TAG.json)
  rule $AGG_DIR/L1-${LABEL}vs$cn-$TAG.haiku55-low.json "$gp" "$tp" $cn | tee $AGG_DIR/L1-rule-$TAG.txt; }
judge() { local R=$RUN_PREFIX-s$1 rc c0=${CONTROLS[0]:-} cj=- ct=-
  [ -n "$c0" ] && { cj=$(cd_ "$c0")/$(cb_ "$c0" $1).judgments.jsonl; ct=$(cd_ "$c0")/$(cb_ "$c0" $1).traces.jsonl; }
  judge_lane_ || return 9
  preflight_ "$OUT_DIR/$R.traces.jsonl" "$OUT_DIR/$R.judgments.jsonl" "$JUDGED_IDS" "$JUDGE_SYSTEM-opus" opus "$cj" "$ct" || { echo "ABORT judge: preflight refused"; return 8; }
  shard "$OUT_DIR/$R.traces.jsonl" "$OUT_DIR/$R.judgments.jsonl" "$JUDGED_IDS" "$JUDGE_SYSTEM-opus" opus 2>&1 | tee "$WORK_DIR/$R.opus.shardrun.out" | grep -v " boar" | tail -3; rc=${PIPESTATUS[0]}
  grep -h "### exit" "$OUT_DIR/$R.judgments.shards"/shard-*.log 2>/dev/null | sort | uniq -c
  [ $rc = 0 ] || { echo "ABORT judge: shard_judge rc $rc for $R"; return 5; }
  chk_ "$OUT_DIR/$R.judgments.jsonl" "$JUDGED_IDS" "judge $R" || { echo "ABORT judge: judgments of $R incomplete"; return 5; }; }
fm() { python3 $PL/floor_metrics.py --runs $1 --dir $2 --decline-ratio $DECL --ids $JUDGED_IDS ${QA[@]+"${QA[@]}"} $PFLAGS; }   # floor_metrics for runs/dir
scales() { with_lock "$AGG_DIR/.agg-$LABEL.lock" scales_ "$@"; }
scales_() { local seeds=$1 n s i e rg="" jg="" P=() PGD obj gt; n=$(wc -w <<<"$seeds" | tr -d ' '); PGD=$WORK_DIR/paired-${n}seed; mkdir -p $PGD   # two-seed scales beside every control
  for s in $seeds; do rg="$rg $RUN_PREFIX-s$s"; jg="$jg $OUT_DIR/$RUN_PREFIX-s$s.judgments.jsonl"; done
  local bad=0   # fail closed: every judgments file feeding the scales must be complete (both orders for every JUDGED_ID) before anything is computed or written
  for s in $seeds; do chk_ "$OUT_DIR/$RUN_PREFIX-s$s.judgments.jsonl" "$JUDGED_IDS" "scales $LABEL s$s" || bad=1; done
  for e in "${CONTROLS[@]}"; do for s in $seeds; do chk_ "$(cd_ "$e")/$(cb_ "$e" $s).judgments.jsonl" "$JUDGED_IDS" "scales control $(cn_ "$e") s$s" || [ "${CONTROL_CHECK:-strict}" = warn ] || bad=1; done; done
  [ $bad = 0 ] || { echo "ABORT scales: incomplete judgments, no aggregate written"; return 5; }
  local v pj pe; v=$(fm "$rg" "$OUT_DIR") || { echo "ABORT scales: floor_metrics failed (rc $?) for $LABEL; no aggregate written" >&2; return 5; }   # fail closed (audit F2): every tool rc is checked
  obj=$(jq -n --arg k $LABEL --argjson v "$v" '{($k):$v}') || { echo "ABORT scales: jq failed on floor_metrics output for $LABEL" >&2; return 5; }; local -a RCS=()
  for e in "${CONTROLS[@]}"; do local rc="" nm=$(cn_ "$e") d=$(cd_ "$e"); for s in $seeds; do rc="$rc $(cb_ "$e" $s)"; done; RCS+=("$rc")
    v=$(fm "$rc" "$d") || { echo "ABORT scales: floor_metrics failed (rc $?) for control $nm" >&2; return 5; }
    obj=$(jq --arg k $nm --argjson v "$v" '. + {($k):$v}' <<<"$obj") || { echo "ABORT scales: jq failed on floor_metrics output for control $nm" >&2; return 5; }; done
  for s in $seeds; do for e in "${CONTROLS[@]}"; do local nm=$(cn_ "$e") d=$(cd_ "$e") b=$(cb_ "$e" $s)
    pj=$(node $PAIRED $OUT_DIR/$RUN_PREFIX-s$s.judgments.jsonl $d/$b.judgments.jsonl $JUDGED_IDS $LABEL $nm $PFLAGS) || { echo "ABORT scales: paired.mjs failed (rc $?) for s$s vs $nm" >&2; return 5; }
    pj=$(jq -c --arg s $s --arg v $nm '{seed:$s,vs:$v} + del(.perItem)' <<<"$pj") && [ -n "$pj" ] || { echo "ABORT scales: jq failed on paired.mjs output for s$s vs $nm" >&2; return 5; }; P+=("$pj")
    for f in $OUT_DIR/$RUN_PREFIX-s$s $d/$b; do for x in judgments traces; do ln -sf $f.$x.jsonl $PGD/; done; done; done; done
  i=0; for e in "${CONTROLS[@]}"; do local nm=$(cn_ "$e") rc=${RCS[$i]}; i=$((i+1))
    pe=$WORK_DIR/paired_gap-${LABEL}vs$nm-${n}seed.stderr
    gt=$(python3 $PG --dir $PGD --a $rg --b $rc ${QA[@]+"${QA[@]}"} --decline-ratio $DECL 2>"$pe") || { echo "ABORT scales: paired_gap.py failed (rc $?) for vs $nm: $(tail -2 "$pe" | tr '\n' ' ')" >&2; return 5; }
    gt=$(jq -c . <<<"$gt") && [ -n "$gt" ] || { echo "ABORT scales: paired_gap.py output is not JSON for vs $nm" >&2; return 5; }
    echo "$gt" > $AGG_DIR/paired_gap-${LABEL}vs$nm-${n}seed.json; echo "gap$nm $gt"
    if [ $i = 1 ]; then local jt=""; for s in $seeds; do jt="$jt $(cd_ "$e")/$(cb_ "$e" $s).judgments.jsonl"; done
      python3 $DT/dtcat.py ${LABEL}vs$nm-${n}seed $JUDGED_IDS "$jg" "$jt" $AGG_DIR/cat-${LABEL}vs$nm-${n}seed.opus.json > /dev/null 2>&1 || echo "dtcat failed (non-blocking)"; fi; done
  local pa; pa=$(printf '%s\n' "${P[@]}" | jq -s .) || { echo "ABORT scales: jq failed collecting paired rows" >&2; return 5; }
  jq --argjson p "$pa" '. + {paired:$p}' <<<"$obj" > $AGG_DIR/L2-$LABEL-${n}seed.opus.json || { echo "ABORT scales: jq failed writing L2-$LABEL-${n}seed.opus.json" >&2; return 5; }
  [ -s $AGG_DIR/L2-$LABEL-${n}seed.opus.json ] || { echo "ABORT scales: L2-$LABEL-${n}seed.opus.json is empty" >&2; return 5; }
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
precheck() { local a=${1:?arm traces} c=${2:?control traces} ids=- min=0.20; shift 2   # precheck <arm traces> <control traces> [idsFile] [--min 0.20]: rc 8 if the arm changed the input on < min of the paired items (no judge call)
  while [ $# -gt 0 ]; do case $1 in --min) min=$2; shift 2;; *) ids=$1; shift;; esac; done
  python3 -I "$L/precheck.py" "$a" "$c" "$ids" "$min" ${PRECHECK_MARKERS:-}; }
case $CMD in
  mkreq|launch|status|fetch|think|l1|judge|scales|exposure|chain|gate|precheck|smoke|crit_check) $CMD "$@";;
  wait) wait_run "$@";;
  *) echo "unknown command $CMD (mkreq launch status wait fetch think l1 judge scales exposure chain gate precheck smoke crit_check)"; exit 2;;
esac
