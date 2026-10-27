#!/bin/bash
# Offline tests for `shard_judge.sh --preflight`, sets.tsv, identity.py and their arm.sh wiring (LOOP v2 T5): VITALADD-like missing control, RIVALSET-like foreign rows,
# calls_cap / declared calls, Opus-on-dev, the X2b nosidecar and TK2 replay-tree incidents. 0 LLM calls (JUDGE_CMD = stub-judge.sh), ssh never used, never reads blind/.
# Run: bash rnd/research/coordinator/arms/_lib/tests/judge-tests.sh   (exit 0 = all pass, ~20 s)
set -u
TD=$(cd "$(dirname "$0")" && pwd); LIB=$(cd "$TD/.." && pwd); SJ=$LIB/../deepthink/tools/shard_judge.sh; ID=$LIB/identity.py; FX=$TD/fixtures/smoke
PASS=0; FAIL=0; ok() { if [ "$2" = 0 ]; then PASS=$((PASS+1)); echo "  [pass] $1"; else FAIL=$((FAIL+1)); echo "  [FAIL] $1"; fi; }
W=$(mktemp -d "${TMPDIR:-/tmp}/judgetest.XXXXXX"); trap 'rm -rf "$W"' EXIT
mkdir -p $W/bench; for i in $(seq -w 1 20); do echo "q$i"; done > $W/ids; echo '{"itemId":"q01"}' > $W/tr.jsonl; echo '{"itemId":"q02"}' > $W/ctl.traces.jsonl
TSHA=$(shasum -a 256 $W/tr.jsonl | cut -d' ' -f1)
export BOAR_EVAL_DIR=$W JUDGE_CMD=$TD/stub-judge.sh
# mkrows <file> <tracesSha> <requestedModel> <judgeModel> <id>...: ok rows in both orders (provenance fields as judge.mjs writes them)
mkrows() { local f=$1 t=$2 r=$3 j=$4 i o; shift 4; for i in "$@"; do for o in boarA boarB; do echo "{\"queryId\":\"$i\",\"order\":\"$o\",\"ok\":true,\"judgeModel\":\"$j\",\"requestedModel\":\"$r\",\"tracesSha256\":\"$t\"}"; done; done >> $f; }
# mkcrit <file> <ruleset> <calls_cap value> <opus_clause value>
mkcrit() { { echo "# T: fixture"; echo; echo "## Tags"; echo "Tags: none"; echo "Ruleset: $2"; echo; echo "## Budget (RULE 29)"; echo "wall_cap: 2"; echo "calls_cap: $3"; echo "smoke: 10 items"; echo
  echo "## Precheck (fixture)"; echo "token_projection: n/a / token_budget: n/a"; echo "disk_peak_gib: n/a"; echo "off_baseline: n/a"; echo "call_pattern: x"; echo "lane: judge"; echo "opus_clause: $4"; echo "wall_cap_h: 2"; echo "parallelism: 1"; echo "run_type: judge"; echo; echo "## Stages and rules"; } > $1; }
# pf <out> <model> [extra env via caller]: preflight over the 20 ids; stdout/stderr in $W/pf.out
pf() { local o=$1 m=${2:-haiku}; $SJ --preflight $W/tr.jsonl $o $W/bench $W/ids sys 4 $m > $W/pf.out 2>&1; }
refused() { grep -q "^PREFLIGHT REFUSED $1:" $W/pf.out; }
mkctl() { local f=$1 skip=${2:-0}; : > $f; mkrows $f x claude-haiku-5-5 claude-haiku-5-5 $(head -n $((20-skip)) $W/ids); }

echo "T-J1 VITALADD-like: control judgments missing 3 of 20 ids"
mkctl $W/ctl.j 3; M=$W/mark1; : > $M; rm -f $M; export STUB_MARK=$M
PREFLIGHT_CONTROL=$W/ctl.j PREFLIGHT_CONTROL_REQUIRED=1 pf $W/j1/out.jsonl; r=$?
[ $r = 8 ] && refused control_missing && grep -q "3 of 20 ids (q18,q19,q20)" $W/pf.out; ok "control missing 3: rc=$r (expect 8): $(cut -c1-110 $W/pf.out)" $?
[ ! -e $M ]; ok "stub judge never ran (STUB_MARK absent)" $?
[ ! -e $W/j1/out.jsonl.lock ] && [ ! -e $W/j1/out.jsonl ] && [ ! -e $W/j1/out.jsonl.preflight ]; ok "no <out>.lock, no <out>, no probe dir left" $?
PREFLIGHT_CONTROL_REQUIRED=1 pf $W/j1/out.jsonl; r=$?; [ $r = 8 ] && refused control_missing; ok "required control file not given: rc=$r (expect 8)" $?
PREFLIGHT_CONTROL=$W/nonexistent.j pf $W/j1/out.jsonl; r=$?; [ $r = 8 ] && refused control_missing && grep -q "20 of 20" $W/pf.out; ok "control file absent: rc=$r, 20 of 20 ids" $?
mkctl $W/ctl.ok 0; PREFLIGHT_CONTROL=$W/ctl.ok PREFLIGHT_CONTROL_REQUIRED=1 pf $W/j1/out.jsonl; r=$?; [ $r = 0 ] && grep -q "control=ok" $W/pf.out; ok "complete control: rc=$r, control=ok" $?
grep -v '"boarB"' $W/ctl.ok > $W/ctl.oneorder; PREFLIGHT_CONTROL=$W/ctl.oneorder pf $W/j1/out2.jsonl; r=$?; [ $r = 8 ] && refused control_missing; ok "control with one order only: rc=$r (expect 8)" $?

echo "T-J2 RIVALSET-like foreign rows in <out> / its shards"
unset STUB_MARK; mkdir -p $W/j2; O=$W/j2/out.jsonl; : > $O; mkrows $O aaaaaaaaaaaa1111111111111111111111111111111111111111111111111111 claude-haiku-5-5 claude-haiku-5-5 q01 q02 q03; cp $O $W/j2/out.before; M=$W/mark2; rm -f $M; export STUB_MARK=$M
pf $O haiku; r=$?; [ $r = 8 ] && refused provenance && grep -q "ALLOW_SPLICE=1" $W/pf.out; ok "foreign tracesSha256: rc=$r (expect 8): $(cut -c1-100 $W/pf.out)" $?
cmp -s $O $W/j2/out.before && [ ! -e $O.lock ] && [ ! -e $M ]; ok "<out> untouched, no lock, no judge call" $?
ALLOW_SPLICE=1 pf $O haiku; r=$?; [ $r = 0 ] && grep -q "planned_calls=34 spent=6" $W/pf.out; ok "ALLOW_SPLICE=1 passes the provenance check (resume skips 3 ids): $(cut -c1-120 $W/pf.out)" $?
: > $O; mkrows $O $TSHA claude-haiku-5-5 claude-haiku-5-5 q01 q02 q03; pf $O haiku; r=$?; [ $r = 0 ] && grep -q "planned_calls=34 spent=6" $W/pf.out; ok "own tracesSha256 rows: rc=$r, planned 34, spent 6" $?
: > $O; mkrows $O $TSHA opus opus q01; pf $O haiku; r=$?; [ $r = 8 ] && refused provenance; ok "rows judged by opus under a haiku request: rc=$r (expect 8)" $?
: > $O; mkrows $O $TSHA claude-haiku-5-5 claude-haiku-5-5 q01; mkrows $O $TSHA claude-haiku-5-5 other-model q02; pf $O haiku; r=$?; [ $r = 8 ] && refused provenance; ok "two judge models in <out>: rc=$r (expect 8)" $?
rm -f $O; mkdir -p $O.shards 2>/dev/null; O3=$W/j2/o3.jsonl; mkdir -p $W/j2/o3.shards; mkrows $W/j2/o3.shards/shard-0.jsonl bbbb claude-haiku-5-5 claude-haiku-5-5 q05
pf $O3 haiku; r=$?; [ $r = 8 ] && refused provenance; ok "foreign rows only in <out>.shards (what a resume reuses): rc=$r (expect 8)" $?

echo "T-J3 calls_cap and declared calls"
rm -f $M; mkdir -p $W/j3; O=$W/j3/out.jsonl
mkcrit $W/c10.md 30 "Haiku 10 / Opus 0" none; PREFLIGHT_CRITERION=$W/c10.md pf $O haiku; r=$?; [ $r = 8 ] && refused calls_cap && grep -q "planned 40 + spent 0 > cap 10 (haiku)" $W/pf.out; ok "Haiku cap 10, 20 ids: rc=$r (expect 8): $(cut -c1-90 $W/pf.out)" $?
mkcrit $W/c400.md 30 "Haiku 400 / Opus 0" none; PREFLIGHT_CRITERION=$W/c400.md pf $O haiku; r=$?; [ $r = 0 ] && grep -q "planned_calls=40 spent=0 cap=400" $W/pf.out; ok "Haiku cap 400: rc=$r, $(cut -c1-130 $W/pf.out)" $?
mkcrit $W/cN.md 30 "Haiku N / Opus N" none; PREFLIGHT_CRITERION=$W/cN.md pf $O haiku; r=$?; [ $r = 8 ] && refused calls_cap && grep -q "unfilled" $W/pf.out; ok "calls_cap 'Haiku N / Opus N' unfilled: rc=$r (expect 8)" $?
mkcrit $W/cT.md 30 "<Haiku N / Opus N>" none; PREFLIGHT_CRITERION=$W/cT.md pf $O haiku; r=$?; [ $r = 8 ] && grep -q "unfilled" $W/pf.out; ok "calls_cap template placeholder: rc=$r (expect 8)" $?
PREFLIGHT_CRITERION=$W/c400.md PREFLIGHT_DECLARED_CALLS=40 pf $O haiku; r=$?; ok "declared 40 = 2 x 20 ids: rc=$r" $r
PREFLIGHT_CRITERION=$W/c400.md PREFLIGHT_DECLARED_CALLS=30 pf $O haiku; r=$?; [ $r = 8 ] && refused calls_declared && grep -q "planned 40 != declared 30" $W/pf.out; ok "declared 30 vs planned 40: rc=$r (expect 8)" $?
: > $O; mkrows $O $TSHA claude-haiku-5-5 claude-haiku-5-5 q01 q02 q03 q04 q05; mkcrit $W/c39.md 30 "Haiku 39 / Opus 0" none; mkcrit $W/c40.md 30 "Haiku 40 / Opus 0" none
PREFLIGHT_CRITERION=$W/c39.md pf $O haiku; r=$?; [ $r = 8 ] && grep -q "planned 30 + spent 10 > cap 39" $W/pf.out; ok "resume: planned 30 + spent 10 > cap 39: rc=$r (expect 8)" $?
PREFLIGHT_CRITERION=$W/c40.md pf $O haiku; r=$?; [ $r = 0 ] && grep -q "planned_calls=30 spent=10 cap=40" $W/pf.out; ok "resume: planned 30 + spent 10 = cap 40 passes: rc=$r" $?
rm -f $O; mkrows $W/j3/other.jsonl x claude-haiku-5-5 claude-haiku-5-5 q01 q02 q03 q04 q05 q06; echo "other.jsonl" > $W/j3/.calls.ledger; mkcrit $W/c50.md 30 "Haiku 50 / Opus 0" none
PREFLIGHT_CRITERION=$W/c50.md pf $O haiku; r=$?; [ $r = 8 ] && grep -q "planned 40 + spent 12 > cap 50" $W/pf.out; ok ".calls.ledger adds 12 spent calls: rc=$r (expect 8)" $?
rm -f $W/j3/.calls.ledger

echo "T-J4 Opus on a dev-tagged set"
mkdir -p $W/j4; O=$W/j4/out.jsonl
mkcrit $W/o_none.md 30 "Haiku 0 / Opus 400" none; mkcrit $W/o_cl.md 30 "Haiku 0 / Opus 400" "near-miss within 0.01 of the threshold -> Opus N=4 on the same 20 ids"
PREFLIGHT_CRITERION=$W/o_none.md PREFLIGHT_SET=bench-v02 pf $O opus; r=$?; [ $r = 8 ] && refused opus_on_dev && grep -q "set bench-v02 is dev" $W/pf.out; ok "opus + bench-v02 + opus_clause none: rc=$r (expect 8)" $?
PREFLIGHT_CRITERION=$W/o_cl.md PREFLIGHT_SET=bench-v02 pf $O opus; r=$?; [ $r = 0 ] && grep -q "status=dev model=opus" $W/pf.out; ok "opus + bench-v02 + filled opus_clause: rc=$r" $r
PREFLIGHT_CRITERION=$W/o_none.md PREFLIGHT_SET=es-fresh2 pf $O opus; r=$?; [ $r = 0 ] && grep -q "status=clean" $W/pf.out; ok "opus + es-fresh2 (clean) without clause: rc=$r" $r
PREFLIGHT_CRITERION=$W/o_none.md PREFLIGHT_SET=health-fresh3 pf $O opus; r=$?; [ $r = 0 ] && grep -q "status=held-out" $W/pf.out; ok "opus + health-fresh3 (held-out) without clause: rc=$r" $r
PREFLIGHT_CRITERION=$W/o_none.md PREFLIGHT_SET=no-such-set pf $O opus; r=$?; [ $r = 8 ] && refused opus_on_dev; ok "unknown set fails closed as dev: rc=$r (expect 8)" $?
PREFLIGHT_CRITERION=$W/o_none.md PREFLIGHT_SET=st-boar-factbook pf $O opus; r=$?; [ $r = 8 ] && refused opus_on_dev; ok "st-* glob row is dev: rc=$r (expect 8)" $?
PREFLIGHT_CRITERION=$W/c400.md PREFLIGHT_SET=bench-v02 pf $O haiku; r=$?; [ $r = 0 ]; ok "haiku on a dev set is not restricted: rc=$r" $?
PREFLIGHT_SET=bench-v02 pf $O opus; r=$?; [ $r = 8 ] && refused opus_on_dev; ok "opus on dev with no criterion at all: rc=$r (expect 8)" $?

echo "T-J5 OK path: live probe on arm + control, then a normal run"
mkdir -p $W/j5; O=$W/j5/out.jsonl; rm -f $M
PREFLIGHT_CRITERION=$W/c400.md PREFLIGHT_SET=bench-v02 PREFLIGHT_CONTROL=$W/ctl.ok PREFLIGHT_CONTROL_TRACES=$W/ctl.traces.jsonl PREFLIGHT_CONTROL_REQUIRED=1 PREFLIGHT_DECLARED_CALLS=40 pf $O haiku; r=$?
[ $r = 0 ] && [ "$(cat $W/pf.out)" = "PREFLIGHT OK set=bench-v02 status=dev model=haiku ids=20 planned_calls=40 spent=0 cap=400 control=ok probe=1 ids" ]; ok "rc=$r, line: $(cat $W/pf.out)" $?
[ "$(wc -l < $M | tr -d ' ')" = 2 ] && grep -q "preflight/arm.jsonl" $M && grep -q "preflight/control.jsonl" $M; ok "stub ran exactly twice (arm + control probe)" $?
[ "$(wc -l < $O.preflight/arm.jsonl | tr -d ' ')" = 2 ] && [ "$(wc -l < $O.preflight/control.jsonl | tr -d ' ')" = 2 ] && [ "$(jq -r .queryId $O.preflight/arm.jsonl | sort -u)" = q01 ] && [ "$(jq -r .order $O.preflight/arm.jsonl | sort | tr '\n' ' ')" = "boarA boarB " ]; ok "each probe file: 1 id (q01), both orders" $?
[ ! -e $O ] && [ ! -e $O.lock ]; ok "<out> not written, no lock after the preflight" $?
: > $M; $SJ $W/tr.jsonl $O $W/bench $W/ids sys 4 haiku > $W/run5.out 2>&1; r=$?; [ $r = 0 ] && [ "$(wc -l < $O | tr -d ' ')" = 40 ] && [ ! -e $O.lock ]; ok "a normal run right after the preflight: rc=$r, 40 rows, lock released" $?
PREFLIGHT_PROBE_IDS=2 PREFLIGHT_CRITERION=$W/c400.md PREFLIGHT_CONTROL_TRACES=$W/ctl.traces.jsonl pf $W/j5/out2.jsonl haiku; r=$?; [ $r = 0 ] && [ "$(wc -l < $W/j5/out2.jsonl.preflight/arm.jsonl | tr -d ' ')" = 4 ] && grep -q "probe=2 ids" $W/pf.out; ok "PREFLIGHT_PROBE_IDS=2: 4 rows per probe file" $?
STUB_RC=1 pf $W/j5/out3.jsonl haiku; r=$?; [ $r = 8 ] && refused probe_failed; ok "judge exiting rc 1 in the probe: rc=$r (expect 8)" $?
STUB_SKIP=q01 pf $W/j5/out4.jsonl haiku; r=$?; [ $r = 8 ] && refused probe_failed && [ ! -e $W/j5/out4.jsonl ]; ok "probe id skipped by the judge: probe_failed, <out> absent" $?
unset STUB_MARK

echo "T-J6 identity.py"
mktr() { python3 -I - "$@" <<'PY'
import json, sys
n, commit, patch, adapter, codes, pre = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], json.loads(sys.argv[5]), sys.argv[6]
for i in range(n):
    v = {"adapter": adapter}
    if patch != "-": v["engine.patch.sha256"] = patch
    print(json.dumps({"itemId": "%s%02d" % (pre, i), "engine": {"commit": commit, "arm": "x"}, "runtime": {"versions": v}, "config": {"settings": {}}, "route": {"reasonCodes": codes}}))
PY
}
P1=0fba26b8c55aa776b0cfa397998c82741bdbe50cfc4ed5dd2059ad6a2cee7f26; C1=0cfd4a77badd01297af8dc9a3a10924f8a895105; A1=desktop-node@3ae3b494bc9d
mktr 10 $C1 $P1 $A1 '["task:qa","headpass:dense"]' t > $W/g.ok; mktr 10 $C1 $P1 $A1 '["task:qa","headpass:dense:nosidecar"]' t > $W/g.nosc
python3 -I $ID --gen $W/g.ok > $W/i.out; r=$?; [ $r = 0 ] && [ "$(cat $W/i.out)" = "identity: PASS n=10 tree=0cfd4a77 patch=0fba26b8 adapter=$A1" ]; ok "clean traces: rc=$r: $(cat $W/i.out)" $?
python3 -I $ID --gen $W/g.nosc > $W/i.out; r=$?; [ $r = 1 ] && grep -q "FAIL option-not-applied n=10 notapplied=10/10" $W/i.out; ok "X2b nosidecar on an ON run: rc=$r: $(cat $W/i.out)" $?
python3 -I $ID --gen $W/g.nosc --mode off > $W/i.out; r=$?; [ $r = 0 ]; ok "same traces with --mode off: rc=$r" $?
mktr 10 deadbeef00112233445566778899aabbccddeeff $P1 $A1 '["task:qa"]' t > $W/r.commit; python3 -I $ID --gen $W/g.ok --replay $W/r.commit > $W/i.out; r=$?; [ $r = 1 ] && grep -q "FAIL replay-tree" $W/i.out; ok "TK2: replay tree != generation tree: rc=$r" $?
python3 -I $ID --gen $W/g.ok --replay $W/g.ok > $W/i.out; r=$?; [ $r = 0 ]; ok "replay identical to generation: rc=$r" $r
mktr 10 $C1 - $A1 '[]' t > $W/r.patch; python3 -I $ID --gen $W/g.ok --replay $W/r.patch > $W/i.out; r=$?; [ $r = 1 ] && grep -q "replay-patch" $W/i.out; ok "replay without the patch: rc=$r, replay-patch" $?
mktr 10 $C1 $P1 desktop-node@other '[]' t > $W/r.ad; python3 -I $ID --gen $W/g.ok --replay $W/r.ad > $W/i.out; r=$?; [ $r = 1 ] && grep -q "replay-adapter" $W/i.out; ok "replay with another adapter: rc=$r, replay-adapter" $?
python3 -I $ID --gen $W/g.ok --adapter desktop-node@zzz > $W/i.out; r=$?; [ $r = 1 ] && grep -q "FAIL pinned-mismatch" $W/i.out; ok "--adapter pin mismatch: rc=$r" $?
python3 -I $ID --gen $W/g.ok --adapter 3ae3b494bc9d --patch-sha ${P1:0:12} --tree 0cfd4a77 > $W/i.out; r=$?; [ $r = 0 ]; ok "pins that match (adapter substring, patch/tree prefixes): rc=$r" $r
python3 -I $ID --gen $W/g.ok --patch-sha ffff > $W/i.out; r=$?; [ $r = 1 ] && grep -q "pinned-mismatch" $W/i.out; ok "--patch-sha mismatch: rc=$r" $?
{ mktr 5 $C1 $P1 $A1 '[]' a; mktr 5 deadbeef00112233445566778899aabbccddeeff $P1 $A1 '[]' b; } > $W/g.mixed; python3 -I $ID --gen $W/g.mixed > $W/i.out; r=$?; [ $r = 1 ] && grep -q "FAIL mixed-tree" $W/i.out; ok "two commits inside one file: rc=$r, mixed-tree" $?
python3 -I $ID --gen $FX/clean-4b-patch.traces.jsonl --adapter whatever > $W/i.out; r=$?; [ $r = 0 ] && grep -q "tree=unknown patch=unknown" $W/i.out; ok "traces without metadata are unknown, not a failure: rc=$r: $(cat $W/i.out)" $?
{ mktr 3 $C1 $P1 $A1 '["x:nosidecar"]' bad; mktr 3 $C1 $P1 $A1 '[]' good; } > $W/g.part; printf 'good00\ngood01\ngood02\n' > $W/some.ids; python3 -I $ID --gen $W/g.part --ids $W/some.ids > $W/i.out; r=$?; [ $r = 0 ] && grep -q "n=3" $W/i.out; ok "--ids restricts the check to the listed items: rc=$r" $?
python3 -I $ID --gen $W/missing.jsonl > /dev/null 2>&1; r=$?; [ $r = 2 ]; ok "unreadable input: rc=$r (expect 2)" $?
python3 -I $ID > /dev/null 2>&1; r=$?; [ $r = 2 ]; ok "no --gen: usage, rc=$r (expect 2)" $?

echo "T-J7 arm.sh smoke runs identity before smoke-project"
# crit <dir> [tag]: Ruleset-30 criterion + conf (same fixture shape as smoke-tests.sh)
critd() { local d=$1 tag=${2:-none}; mkdir -p $d; mkcrit $d/c.md 30 "Haiku 400 / Opus 0" none; sed -i.bak "s|^Tags: none|Tags: $tag|; s|^run_type: judge|run_type: 4b-patch|; s|^token_budget: n/a|x|" $d/c.md; rm -f $d/c.md.bak
  sed -i.bak 's|^token_projection: n/a / token_budget: n/a|token_projection: 1000 / token_budget: 1100|' $d/c.md; rm -f $d/c.md.bak
  printf '## Power\nexpected_delta: 0.05 (source: x)\nn: 51\nseeds: 2\nmde: 0.03\n' >> $d/c.md
  cat > $d/arm.conf <<CONF
ARM=t; LABEL=P; TREE=t; REMOTE_RUNNER=t-remote-run.sh; REMOTE_ARM=D; SETTINGS='{}'; RUN_PREFIX=p
SET=bench-v02; BENCH=$d; QUESTIONS=-; JUDGED_IDS=$d/ids; OUT_DIR=$W/out7; AGG_DIR=$W/agg7; JUDGE_SYSTEM=t-P; CONTROLS=("C|$d|c-s{seed}")
CRITERION=$d/c.md
CONF
}
arm() { local d=$1; shift; LOCK_DIR=$W/lock7 $LIB/arm.sh $d/arm.conf "$@"; }
META='. + {engine:{commit:"0cfd4a77ba",arm:"x"},runtime:{versions:{adapter:"desktop-node@aaa","engine.patch.sha256":"0fba26b8"}}}'
jq -c "$META" $FX/clean-4b-patch.traces.jsonl > $W/s.clean; jq -c "$META | .route.reasonCodes += [\"headpass:dense:nosidecar\"]" $FX/clean-4b-patch.traces.jsonl > $W/s.nosc
critd $W/k1; arm $W/k1 smoke $W/s.nosc --n-full 180 > $W/k1.out 2>&1; r=$?
[ $r = 1 ] && [ "$(jq -r .verdict $W/k1/smoke.verdict.json)" = FAIL ] && jq -e '.reasons|length==1 and (.[0]|test("identity: FAIL option-not-applied"))' $W/k1/smoke.verdict.json > /dev/null && [ "$(jq -r .criterion_sha $W/k1/smoke.verdict.json)" = "$(shasum -a 256 $W/k1/c.md | cut -d' ' -f1)" ]; ok "nosidecar smoke: rc=$r (expect 1), verdict FAIL, reason 'identity: ...'" $?
jq -e 'has("computed_at") and has("criterion_sha") and has("verdict") and has("reasons")' $W/k1/smoke.verdict.json > /dev/null; ok "verdict file has the smoke-project fields (criterion_sha verdict reasons computed_at)" $?
arm $W/k1 crit_check > $W/k1.cc 2>&1; r=$?; [ $r = 7 ] && grep -q "smoke verdict is FAIL" $W/k1.cc && grep -q identity $W/k1.cc; ok "crit_check after the identity FAIL: rc=$r (expect 7): $(cut -c1-110 $W/k1.cc)" $?
critd $W/k2; arm $W/k2 smoke $W/s.clean --n-full 180 > $W/k2.out 2>&1; r=$?; [ $r = 0 ] && grep -q "identity: PASS" $W/k2.out && [ "$(jq -r .verdict $W/k2/smoke.verdict.json)" = PASS ]; ok "clean traces: identity PASS then smoke PASS, rc=$r" $?
ADAPTER_PIN=desktop-node@bbb arm $W/k2 smoke $W/s.clean --n-full 180 > $W/k2b.out 2>&1; r=$?; [ $r = 1 ] && grep -q "pinned-mismatch" $W/k2/smoke.verdict.json; ok "ADAPTER_PIN mismatch fails the smoke: rc=$r" $?
IDENTITY_SKIP=1 arm $W/k1 smoke $W/s.nosc --n-full 180 > $W/k3.out 2>&1; r=$?; [ $r = 7 ] && grep -q "IDENTITY_SKIP=1 is allowed only" $W/k3.out; ok "IDENTITY_SKIP=1 refused on a Tags: none criterion: rc=$r (expect 7)" $?
critd $W/k4 probe; IDENTITY_SKIP=1 arm $W/k4 smoke $W/s.nosc --n-full 180 > $W/k4.out 2>&1; r=$?; grep -q "IDENTITY_SKIP=1: identity check waived" $W/k4.out && ! grep -q "identity: FAIL" $W/k4.out; ok "IDENTITY_SKIP=1 waived on Tags: probe (smoke-project then decides, rc=$r)" $?
arm $W/k4 smoke $FX/teacher-probe.units.jsonl --n-full 120 > $W/k5.out 2>&1; ! grep -q "identity" $W/k5.out; ok "units.jsonl input skips identity" $?

echo "T-J8 arm.sh l1 / judge wiring (Ruleset 30 criterion, REPLAY, stub judge)"
S8=$W/s8; mkdir -p $S8/out $S8/ctl $S8/agg $S8/bench; cp $W/ids $S8/ids
mktrl() { for i in $(cat $W/ids); do echo "{\"itemId\":\"$i\",\"route\":{\"reasonCodes\":[\"generate:x\"]},\"timing\":{\"totalMs\":1000},\"events\":[],\"answer\":{\"text\":\"a\"}}"; done; }
mktrl > $S8/out/rA.traces.jsonl; mktrl > $S8/ctl/c-s42.traces.jsonl
mkcrit $S8/c30.md 30 "Haiku 400 / Opus 400" "x"; mkcrit $S8/c29.md 29 "Haiku 400 / Opus 400" "x"
conf8() { cat > $S8/$1.conf <<CONF
ARM=t; LABEL=P; TREE=t; REMOTE_RUNNER=t-remote-run.sh; REMOTE_ARM=D; SETTINGS='{}'; RUN_PREFIX=p
SET=bench-v02; BENCH=$S8/bench; QUESTIONS=-; JUDGED_IDS=$S8/ids; OUT_DIR=$S8/out; AGG_DIR=$S8/agg; JUDGE_SYSTEM=t-P; CONTROLS=("C|$S8/ctl|c-s{seed}")
CRITERION=$S8/$2
CONF
}
conf8 c30 c30.md; conf8 c29 c29.md; M8=$W/mark8; export STUB_MARK=$M8 REPLAY=1; : > $S8/ctl/c-s42.judgments.haiku55-low.jsonl   # control rows missing entirely
rm -f $M8; $LIB/arm.sh $S8/c30.conf l1 rA $S8/ids t8 > $S8/a.out 2>&1; r=$?
[ $r = 8 ] && grep -q "PREFLIGHT REFUSED control_missing" $S8/a.out && grep -q "ABORT l1: preflight refused" $S8/a.out && [ ! -e $M8 ]; ok "l1, Ruleset 30, control rows missing: rc=$r (expect 8), ABORT l1: preflight refused, 0 stub runs" $?
[ ! -d $S8/out/rA.judgments.haiku55-low.jsonl.lock ] && [ ! -d $S8/agg/.agg-P.lock ]; ok "no judge or aggregate lock left after the refusal" $?
rm -f $M8; PREFLIGHT=0 $LIB/arm.sh $S8/c30.conf l1 rA $S8/ids t8 > $S8/b.out 2>&1; r=$?
grep -q "preflight skipped (PREFLIGHT=0)" $S8/b.out && [ "$(wc -l < $M8 | tr -d ' ')" = 4 ] && ! grep -q "preflight refused" $S8/b.out; ok "PREFLIGHT=0: one skip line, old path runs (4 shard runs, then rc=$r from its own control check)" $?
rm -f $M8; $LIB/arm.sh $S8/c29.conf l1 rA $S8/ids t8 > $S8/c.out 2>&1; r=$?
! grep -qi "preflight" $S8/c.out && [ "$(wc -l < $M8 | tr -d ' ')" = 4 ]; ok "legacy Ruleset 29 criterion: no preflight at all, silent (rc=$r)" $?
rm -f $M8 $S8/out/rA.judgments.haiku55-low.jsonl; rm -rf $S8/out/rA.judgments.haiku55-low.shards; mkctl $S8/ctl/c-s42.judgments.haiku55-low.jsonl 0
$LIB/arm.sh $S8/c30.conf l1 rA $S8/ids t8 > $S8/d.out 2>&1; r=$?
grep -q "PREFLIGHT OK set=bench-v02 status=dev model=haiku ids=20 planned_calls=40 spent=0 cap=400 control=ok probe=1 ids" $S8/d.out && [ "$(wc -l < $M8 | tr -d ' ')" = 6 ]; ok "l1 with complete control rows: PREFLIGHT OK printed, 2 probe + 4 shard runs (rc=$r)" $?
# judge (Opus) on a dev set: opus_clause 'x' is filled -> passes; none -> refused before the pass
mktrl > $S8/out/p-s42.traces.jsonl; mkctl $S8/ctl/c-s42.judgments.jsonl 0
rm -f $M8; $LIB/arm.sh $S8/c30.conf judge 42 > $S8/e.out 2>&1; r=$?; grep -q "PREFLIGHT OK set=bench-v02 status=dev model=opus" $S8/e.out && [ "$(wc -l < $M8 | tr -d ' ')" = 6 ]; ok "judge (Opus) with a filled opus_clause: preflight OK, 2 probe + 4 shard runs (rc=$r)" $?
mkcrit $S8/c30n.md 30 "Haiku 400 / Opus 400" none; conf8 c30n c30n.md; rm -f $M8 $S8/out/p-s42.judgments.jsonl; rm -rf $S8/out/p-s42.judgments.shards
$LIB/arm.sh $S8/c30n.conf judge 42 > $S8/f.out 2>&1; r=$?; [ $r = 8 ] && grep -q "ABORT judge: preflight refused" $S8/f.out && grep -q "PREFLIGHT REFUSED opus_on_dev" $S8/f.out && [ ! -e $M8 ]; ok "judge (Opus) on dev with opus_clause none: rc=$r (expect 8), ABORT judge: preflight refused, 0 stub runs" $?
unset STUB_MARK REPLAY

echo; echo "judge-tests: $PASS pass, $FAIL fail"; [ $FAIL = 0 ]
