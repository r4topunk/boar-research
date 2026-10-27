#!/bin/bash
# Offline tests for smoke-project.py + arm.sh smoke/crit_check/launch gates (LOOP v2 T3): TEACHER-PROBE and MICROD2Q incident fixtures, X2 token gate, edited-criterion invalidation, Precheck block. 0 LLM calls, ssh stubbed, never reads blind/.
# Run: bash rnd/research/coordinator/arms/_lib/tests/smoke-tests.sh   (exit 0 = all pass, ~20 s)
set -u
TD=$(cd "$(dirname "$0")" && pwd); LIB=$(cd "$TD/.." && pwd); FX=$TD/fixtures/smoke; SP=$LIB/smoke-project.py
PASS=0; FAIL=0; ok() { if [ "$2" = 0 ]; then PASS=$((PASS+1)); echo "  [pass] $1"; else FAIL=$((FAIL+1)); echo "  [FAIL] $1"; fi; }
W=$(mktemp -d "${TMPDIR:-/tmp}/smoketest.XXXXXX"); trap 'rm -rf "$W"' EXIT
mkdir -p $W/bin $W/out $W/agg $W/lock; printf '#!/bin/bash\necho "$@" >> %s/ssh.calls\nexit 1\n' $W > $W/bin/ssh; cp $W/bin/ssh $W/bin/scp; chmod +x $W/bin/ssh $W/bin/scp; : > $W/ssh.calls
echo '{}' > $W/req.jsonl
# crit <dir> <ruleset> <run_type> <wall_cap_h> <token_budget|n/a> [extra tag] -> writes <dir>/c.md (a minimal criterion with a Power block and a filled Precheck block) and a conf <dir>/arm.conf
crit() { local d=$1 rs=$2 rt=$3 wc=$4 tb=$5 tag=${6:-none}; mkdir -p $d
  { echo "# T: fixture criterion"; echo; echo "## Tags"; echo "Tags: $tag"; echo "Ruleset: $rs"; echo; echo "## Power"; echo "expected_delta: 0.05 (source: fixture)"; echo "n: 51"; echo "seeds: 2"; echo "mde: 0.03"; echo
    if [ "$rs" -ge 30 ]; then echo "## Precheck (fixture)"; echo "token_projection: 1000 / token_budget: $tb"; echo "disk_peak_gib: 2"; echo "off_baseline: fx-off-s42"; echo 'call_pattern: Haiku N=4 both orders on random20 then full'
      echo "lane: mac-gen"; echo "opus_clause: none"; echo "wall_cap_h: $wc"; echo "parallelism: 1"; echo "run_type: $rt"; echo; fi
    echo "## Stages and rules"; echo "1. Smoke."; } > $d/c.md
  [ "$tb" = "n/a" ] && sed -i.bak 's|^token_projection: 1000 / token_budget: n/a|token_projection: n/a / token_budget: n/a|' $d/c.md && rm -f $d/c.md.bak
  cat > $d/arm.conf <<CONF
ARM=t; LABEL=P; TREE=t; REMOTE_RUNNER=t-remote-run.sh; REMOTE_ARM=D; SETTINGS='{}'; RUN_PREFIX=p
SET=t; BENCH=$d; QUESTIONS=-; JUDGED_IDS=$d/ids; OUT_DIR=$W/out; AGG_DIR=$W/agg; JUDGE_SYSTEM=t-P; CONTROLS=("C|$d|c-s{seed}")
CRITERION=$d/c.md
CONF
}
arm() { local d=$1; shift; PATH=$W/bin:$PATH MINI=localhost-invalid LOCK_DIR=$W/lock $LIB/arm.sh $d/arm.conf "$@"; }
vf() { jq -r "$2" $1/smoke.verdict.json; }

echo "S-a TEACHER-PROBE-like units (10 units, 4 empty; 120 x ~324 s = 10.8 h) -> KILL"
crit $W/a 30 teacher 4 n/a; arm $W/a smoke $FX/teacher-probe.units.jsonl --n-full 120 > $W/a.out 2>&1; r=$?
[ $r = 3 ] && [ "$(vf $W/a .verdict)" = KILL ] && [ "$(vf $W/a .empty_share)" = 0.4 ] && grep -q '"KILL: empty share 0.400 > 0.05 (4/10 units)"' $W/a/smoke.verdict.json; ok "smoke rc=$r (expect 3), verdict KILL, empty_share 0.4, projected $(vf $W/a .projected_wall_h) h" $?
arm $W/a crit_check > $W/a.cc 2>&1; r=$?; [ $r = 7 ] && grep -q "smoke verdict is KILL" $W/a.cc; ok "crit_check after KILL: rc=$r (expect 7): $(cut -c1-110 $W/a.cc)" $?

echo "S-b MICROD2Q-like dry run (20 chunks at 5.23 s, n_full 5975, wall_cap_h 2.5 = the 1.5 s/chunk speed gate) -> FAIL with projected_wall_h"
crit $W/b 30 build 2.5 n/a; arm $W/b smoke $FX/microd2q.units.jsonl --n-full 5975 > $W/b.out 2>&1; r=$?
[ $r = 1 ] && [ "$(vf $W/b .verdict)" = FAIL ] && jq -e '.reasons|map(select(test("projected_wall_h 8\\.68 > 1\\.5 x wall_cap_h 2\\.5 = 3\\.75")))|length==1' $W/b/smoke.verdict.json > /dev/null && [ "$(vf $W/b .projected_wall_h)" = 8.68 ]; ok "smoke rc=$r (expect 1), projected_wall_h $(vf $W/b .projected_wall_h) in reasons" $?
arm $W/b crit_check > /dev/null 2>&1; r=$?; [ $r = 7 ]; ok "crit_check after FAIL: rc=$r (expect 7)" $?

echo "S-c clean 4b-patch smoke (10 traces, marker present, mean tokens 1100 = budget 1100) -> PASS, crit_check rc 0"
crit $W/c 30 4b-patch 2 1100; arm $W/c smoke $FX/clean-4b-patch.traces.jsonl --n-full 180 --marker addpack: > $W/c.out 2>&1; r=$?
[ $r = 0 ] && [ "$(vf $W/c .verdict)" = PASS ] && [ "$(vf $W/c '.reasons|length')" = 0 ] && [ "$(vf $W/c .mean_prompt_tokens)" = 1100 ] && [ "$(vf $W/c .criterion_sha)" = "$(shasum -a 256 $W/c/c.md | cut -d' ' -f1)" ]; ok "smoke rc=$r (expect 0), PASS, mean_prompt_tokens 1100 (== budget, no tolerance needed), s/unit $(vf $W/c .s_per_unit), projected $(vf $W/c .projected_wall_h) h" $?
arm $W/c crit_check > $W/c.cc 2>&1; r=$?; ok "crit_check after PASS: rc=$r (expect 0)" $r
jq -e 'keys==["computed_at","criterion_sha","empty_share","marker","mean_prompt_tokens","n","n_full","parse_share","projected_wall_h","reasons","run_type","s_per_unit","token_budget","verdict","wall_cap_h"]' $W/c/smoke.verdict.json > /dev/null; ok "verdict file carries the declared fields (+ run_type n n_full marker)" $?

echo "S-d one byte edited in the criterion -> the PASS no longer counts"
printf ' ' >> $W/c/c.md; arm $W/c crit_check > $W/d.out 2>&1; r=$?; [ $r = 7 ] && grep -q "criterion edited or re-frozen since the smoke" $W/d.out; ok "crit_check after a 1-byte edit: rc=$r (expect 7): $(cut -c1-100 $W/d.out)" $?

echo "S-e mean prompt tokens over budget by 1 -> FAIL (exact gate)"
crit $W/e 30 4b-patch 2 1100; jq -c 'if .itemId=="fx-009" then .timing.promptTokens+=10 else . end' $FX/clean-4b-patch.traces.jsonl > $W/e.traces.jsonl   # mean 1101
arm $W/e smoke $W/e.traces.jsonl --n-full 180 --marker addpack: > $W/e.out 2>&1; r=$?
[ $r = 1 ] && jq -e '.reasons|map(select(test("mean prompt tokens 1101\\.0 > token_budget 1100\\.0")))|length==1' $W/e/smoke.verdict.json > /dev/null; ok "mean 1101 vs budget 1100: rc=$r (expect 1): $(vf $W/e '.reasons[0]')" $?
echo "S-e2 marker missing on one trace / one empty answer / one error / one cut -> FAIL"
crit $W/e2 30 4b-patch 2 1100
jq -c 'if .itemId=="fx-001" then .route.reasonCodes=["task:qa"] else . end' $FX/clean-4b-patch.traces.jsonl > $W/m.traces.jsonl; arm $W/e2 smoke $W/m.traces.jsonl --n-full 180 --marker addpack: > /dev/null 2>&1; r=$?
[ $r = 1 ] && jq -e '.reasons|map(select(test("option not applied: reason code .addpack:. missing on 1/10")))|length==1' $W/e2/smoke.verdict.json > /dev/null; ok "marker missing on 1/10: rc=$r (expect 1)" $?
jq -c 'if .itemId=="fx-002" then .answer.text="" else . end' $FX/clean-4b-patch.traces.jsonl > $W/em.traces.jsonl; arm $W/e2 smoke $W/em.traces.jsonl --n-full 180 > /dev/null 2>&1; r=$?; [ $r = 1 ] && jq -e '.reasons|map(select(test("1/10 empty answers")))|length==1' $W/e2/smoke.verdict.json > /dev/null; ok "1 empty answer on a 4b-patch smoke: rc=$r (expect 1, FAIL not KILL)" $?
jq -c 'if .itemId=="fx-003" then .error={code:"timeout"} else . end' $FX/clean-4b-patch.traces.jsonl > $W/er.traces.jsonl; arm $W/e2 smoke $W/er.traces.jsonl --n-full 180 > /dev/null 2>&1; r=$?; [ $r = 1 ] && jq -e '.reasons|map(select(test("1/10 units with an error")))|length==1' $W/e2/smoke.verdict.json > /dev/null; ok "1 errored trace: rc=$r (expect 1)" $?
jq -c 'if .itemId=="fx-004" then .events[0].timedOut=true else . end' $FX/clean-4b-patch.traces.jsonl > $W/cu.traces.jsonl; arm $W/e2 smoke $W/cu.traces.jsonl --n-full 180 > /dev/null 2>&1; r=$?; [ $r = 1 ] && jq -e '.reasons|map(select(test("1/10 cut")))|length==1' $W/e2/smoke.verdict.json > /dev/null; ok "1 cut (timed-out) generation: rc=$r (expect 1)" $?

echo "S-f launch refuses (rc 7, before any ssh) a Ruleset-30 criterion without the Precheck block / filled keys / smoke"
: > $W/ssh.calls
crit $W/f1 30 4b-patch 2 1100; sed -i.bak '/^## Precheck/,/^run_type/d' $W/f1/c.md; rm -f $W/f1/c.md.bak
arm $W/f1 launch $W/req.jsonl rf1 > $W/f1.out 2>&1; r=$?; [ $r = 7 ] && grep -q "lacks the ## Precheck block" $W/f1.out && [ ! -s $W/ssh.calls ]; ok "no Precheck block: rc=$r (expect 7): $(cut -c1-90 $W/f1.out)" $?
crit $W/f2 30 4b-patch 2 1100; sed -i.bak '/^off_baseline/d' $W/f2/c.md; rm -f $W/f2/c.md.bak
arm $W/f2 launch $W/req.jsonl rf2 > $W/f2.out 2>&1; r=$?; [ $r = 7 ] && grep -q "Precheck block lacks key off_baseline" $W/f2.out && [ ! -s $W/ssh.calls ]; ok "block without off_baseline: rc=$r (expect 7): $(cut -c1-90 $W/f2.out)" $?
crit $W/f3 30 4b-patch 2 1100; sed -i.bak 's|^lane: .*|lane: <mini-long\|mac-gen\|mac-cpu\|judge>|' $W/f3/c.md; rm -f $W/f3/c.md.bak
arm $W/f3 launch $W/req.jsonl rf3 > $W/f3.out 2>&1; r=$?; [ $r = 7 ] && grep -q "Precheck key lane is unfilled" $W/f3.out && [ ! -s $W/ssh.calls ]; ok "unfilled placeholder in the block: rc=$r (expect 7)" $?
crit $W/f4 30 4b-patch 2 1100 blocker; sed -i.bak '/^## Precheck/,/^run_type/d' $W/f4/c.md; rm -f $W/f4/c.md.bak
arm $W/f4 launch $W/req.jsonl rf4 > $W/f4.out 2>&1; r=$?; [ $r = 7 ] && grep -q "no smoke verdict" $W/f4.out && ! grep -q "Precheck" $W/f4.out && [ ! -s $W/ssh.calls ]; ok "Tags: blocker waives the block (still needs a smoke): rc=$r, $(cut -c1-80 $W/f4.out)" $?
crit $W/f5 30 4b-patch 2 1100
arm $W/f5 launch $W/req.jsonl rf5 > $W/f5.out 2>&1; r=$?; [ $r = 7 ] && grep -q "no smoke verdict" $W/f5.out && [ ! -s $W/ssh.calls ]; ok "block present, no smoke: rc=$r (expect 7): $(cut -c1-80 $W/f5.out)" $?
arm $W/f5 smoke $FX/clean-4b-patch.traces.jsonl --n-full 180 --marker addpack: > /dev/null 2>&1; arm $W/f5 launch $W/req.jsonl rf5b > $W/f5b.out 2>&1; r=$?
[ -s $W/ssh.calls ] && ! grep -q "launch refused" $W/f5b.out; ok "block + PASS smoke for this sha: launch passes every check and reaches the stubbed ssh (rc=$r from the stub)" $?
: > $W/ssh.calls; printf '\n' >> $W/f5/c.md; arm $W/f5 launch $W/req.jsonl rf5c > $W/f5c.out 2>&1; r=$?; [ $r = 7 ] && grep -q "criterion edited" $W/f5c.out && [ ! -s $W/ssh.calls ]; ok "criterion edited after the PASS: launch rc=$r (expect 7), no ssh" $?
crit $W/f6 30 build 2.5 n/a; arm $W/f6 smoke $FX/microd2q.units.jsonl --n-full 5975 > /dev/null 2>&1; arm $W/f6 launch $W/req.jsonl rf6 > $W/f6.out 2>&1; r=$?; [ $r = 7 ] && grep -q "smoke verdict is FAIL" $W/f6.out && [ ! -s $W/ssh.calls ]; ok "launch after a FAIL smoke: rc=$r (expect 7)" $?
SMOKE_SKIP=1 arm $W/f6 launch $W/req.jsonl rf6b > $W/f6b.out 2>&1; r=$?; [ $r = 7 ] && grep -q "SMOKE_SKIP=1 is allowed only" $W/f6b.out && [ ! -s $W/ssh.calls ]; ok "SMOKE_SKIP=1 on an untagged criterion: rc=$r (expect 7)" $?
crit $W/f7 30 4b-patch 2 1100 probe; SMOKE_SKIP=1 arm $W/f7 launch $W/req.jsonl rf7 > $W/f7.out 2>&1; [ -s $W/ssh.calls ] && grep -q "smoke gate waived" $W/f7.out; ok "SMOKE_SKIP=1 on Tags: probe: gate waived, reaches the stubbed ssh" $?
: > $W/ssh.calls; crit $W/f8 30 4b-patch 2 1100 blocker; SMOKE_SKIP=1 arm $W/f8 launch $W/req.jsonl rf8 > $W/f8.out 2>&1; [ -s $W/ssh.calls ] && grep -q "smoke gate waived" $W/f8.out; ok "SMOKE_SKIP=1 on Tags: blocker: gate waived" $?

echo "S-g regression: Ruleset 29 criterion with a Power block is not affected by the smoke gate"
: > $W/ssh.calls; crit $W/g 29 4b-patch 2 1100; arm $W/g launch $W/req.jsonl rg > $W/g.out 2>&1; [ -s $W/ssh.calls ] && ! grep -q "launch refused" $W/g.out; ok "Ruleset 29 + Power, no Precheck, no smoke: passes the criterion check (reaches the stubbed ssh)" $?
: > $W/ssh.calls; crit $W/g2 29 4b-patch 2 1100; sed -i.bak '/^## Power/,/^mde/d' $W/g2/c.md; rm -f $W/g2/c.md.bak; arm $W/g2 launch $W/req.jsonl rg2 > $W/g2.out 2>&1; r=$?; [ $r = 7 ] && grep -q "criterion lacks Power block" $W/g2.out && [ ! -s $W/ssh.calls ]; ok "Ruleset 29 without Power: still refused by the Power check (rc=$r)" $?
: > $W/ssh.calls; crit $W/g3 29 4b-patch 2 1100; sed -i.bak '/^Ruleset/d' $W/g3/c.md; rm -f $W/g3/c.md.bak; arm $W/g3 launch $W/req.jsonl rg3 > $W/g3.out 2>&1; [ -s $W/ssh.calls ] && ! grep -q "launch refused" $W/g3.out; ok "criterion with no Ruleset line (legacy) is not affected" $?
cp $LIB/CRITERION-TEMPLATE.md $W/tpl.md; python3 -I $SP --check-block $W/tpl.md > /dev/null 2> $W/tpl.err; r=$?; [ $r = 7 ] && grep -q "unfilled" $W/tpl.err; ok "CRITERION-TEMPLATE.md itself: Ruleset $(awk '/^Ruleset:/{print $2}' $LIB/CRITERION-TEMPLATE.md), unfilled Precheck refused as placeholders (rc=$r)" $?

echo "S-h crit_check frozen-part hash (END FROZEN marker) + committed-blob guard (tracked criterion)"
GC="git -c user.email=t@t -c user.name=t -c commit.gpgsign=false"
crit $W/h 30 4b-patch 2 1100; printf '<!-- END FROZEN -->\nnotes after the marker\n' >> $W/h/c.md
arm $W/h smoke $FX/clean-4b-patch.traces.jsonl --n-full 180 --marker addpack: > /dev/null 2>&1
[ "$(vf $W/h .criterion_sha)" = "$(sed '/^<!-- END FROZEN -->$/q' $W/h/c.md | shasum -a 256 | cut -d' ' -f1)" ]; ok "marker present: verdict sha = sha of the frozen part only" $?
printf 'edited notes\n' >> $W/h/c.md; arm $W/h crit_check > $W/h1.out 2>&1; r=$?; ok "marker present, edit AFTER the marker (untracked): crit_check rc=$r (expect 0)" $r
sed -i.bak 's|^# T: fixture criterion|# T: fixture criterion EDITED|' $W/h/c.md; rm -f $W/h/c.md.bak; arm $W/h crit_check > $W/h2.out 2>&1; r=$?
[ $r = 7 ] && grep -q "criterion edited or re-frozen since the smoke" $W/h2.out && ! grep -q "after commit" $W/h2.out; ok "untracked file, edit before the marker: rc=$r (expect 7, sha mismatch, no git message)" $?
crit $W/i 30 4b-patch 2 1100; arm $W/i smoke $FX/clean-4b-patch.traces.jsonl --n-full 180 --marker addpack: > /dev/null 2>&1
[ "$(vf $W/i .criterion_sha)" = "$(shasum -a 256 $W/i/c.md | cut -d' ' -f1)" ]; ok "marker absent: verdict sha = sha of the whole file" $?
( cd $W/i && git init -q . && git add c.md && $GC commit -q -m c ) > /dev/null 2>&1
arm $W/i crit_check > /dev/null 2>&1; r=$?; ok "tracked, working copy == HEAD, PASS verdict: rc=$r (expect 0)" $r
printf 'x\n' >> $W/i/c.md; arm $W/i smoke $FX/clean-4b-patch.traces.jsonl --n-full 180 --marker addpack: > /dev/null 2>&1   # re-smoke the EDITED, uncommitted criterion: verdict sha now matches the working file
arm $W/i crit_check > $W/i1.out 2>&1; r=$?; [ $r = 7 ] && grep -q "criterion edited after commit" $W/i1.out; ok "tracked, working frozen part != HEAD (even with a matching verdict): rc=$r (expect 7): $(cut -c1-80 $W/i1.out)" $?
( cd $W/i && $GC commit -q -am c2 ) > /dev/null 2>&1; arm $W/i crit_check > /dev/null 2>&1; r=$?; ok "after committing the edit (and the smoke is for that sha): rc=$r (expect 0)" $r
crit $W/j 30 4b-patch 2 1100; printf '<!-- END FROZEN -->\nnotes\n' >> $W/j/c.md; ( cd $W/j && git init -q . && git add c.md && $GC commit -q -m c ) > /dev/null 2>&1
arm $W/j smoke $FX/clean-4b-patch.traces.jsonl --n-full 180 --marker addpack: > /dev/null 2>&1; printf 'more notes\n' >> $W/j/c.md; arm $W/j crit_check > /dev/null 2>&1; r=$?
ok "tracked + marker, only the post-marker part differs from HEAD: rc=$r (expect 0)" $r

echo "smoke-tests: $PASS passed, $FAIL failed"; [ $FAIL = 0 ]
