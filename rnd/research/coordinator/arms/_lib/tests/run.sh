#!/bin/bash
# Fail-closed regression tests for the judge pipeline (FAILCLOSED-2026-10-11). Offline, 0 judge calls, never reads blind/.
# Run: bash rnd/research/coordinator/arms/_lib/tests/run.sh   (exit 0 = all pass). Data: R450 dev judgments (deepread/deeppar), 57 items, both complete.
# Queue runner tests (LOOP v2 T1): bash rnd/research/coordinator/arms/_lib/tests/queue-tests.sh
# State line tests (LOOP v2 T2): bash rnd/research/coordinator/arms/_lib/tests/state-tests.sh
# Log/queue-row writer tests (LOOP v2 T4): bash rnd/research/coordinator/arms/_lib/tests/log-tests.sh
# Smoke verdict / crit_check / Precheck block tests (LOOP v2 T3): bash rnd/research/coordinator/arms/_lib/tests/smoke-tests.sh
# Optional: DT512_BLIND_REPLAY=1 also replays the frozen DT512 aggregates (reads blind/ via arm.sh; coordinator-run only).
set -u
TD=$(cd "$(dirname "$0")" && pwd); LIB=$(cd "$TD/.." && pwd); ARMS=$(cd "$LIB/.." && pwd); EVAL=<workspace>/boar-eval
LEG=$TD/fixtures/legacy; W=$(mktemp -d "${TMPDIR:-/tmp}/failclosed.XXXXXX"); PASS=0; FAIL=0
sha() { shasum -a 256 "$1" | cut -c1-64; }
ok() { if [ "$2" = 0 ]; then PASS=$((PASS+1)); echo "  [pass] $1"; else FAIL=$((FAIL+1)); echo "  [FAIL] $1"; fi; }
A=$ARMS/deepread/deep35-R450; B=$ARMS/deeppar/bmoe-R450
mkdir -p $W/out $W/ctl $W/agg $W/bench
jq -r .itemId $A.traces.jsonl > $W/ids; N=$(wc -l < $W/ids | tr -d ' ')
for x in traces judgments; do cp $A.$x.jsonl $W/out/p-s42.$x.jsonl; cp $B.$x.jsonl $W/ctl/c-s42.$x.jsonl; done
jq -c -s 'map({id:.queryId,category:.category})|unique_by(.id)|.[]' $A.judgments.jsonl > $W/items.jsonl
jq -c '. + {question:("q-"+.id), rubric:[]}' $W/items.jsonl > $W/bench/questions.jsonl; jq -c '{id, ok:true, answer:("ref "+.id)}' $W/items.jsonl > $W/bench/refs.jsonl
cat > $W/arm.conf <<CONF
ARM=t; LABEL=P; TREE=t; REMOTE_RUNNER=t-remote-run.sh; REMOTE_ARM=D; SETTINGS='{}'; RUN_PREFIX=p
SET=t; BENCH=$W/bench; QUESTIONS=$W/items.jsonl; JUDGED_IDS=$W/ids; OUT_DIR=$W/out; AGG_DIR=$W/agg; JUDGE_SYSTEM=t-P
CONTROLS=("C|$W/ctl|c-s{seed}")
CONF
sed "s|^L=\$(cd \"\$(dirname \"\${BASH_SOURCE\[0\]}\")\" && pwd); ARMS=\$(cd \"\$L/..\" && pwd);|L=$LIB; ARMS=$ARMS;|" $LEG/arm.sh > $LEG/arm.run.sh; chmod +x $LEG/arm.run.sh
grep -q "ARMS=$ARMS;" $LEG/arm.run.sh || { echo "legacy arm.sh patch failed"; exit 2; }
ARM_NEW="$LIB/arm.sh $W/arm.conf"; ARM_OLD="$LEG/arm.run.sh $W/arm.conf"

echo "T1 default behaviour byte-identical to the legacy code (n=$N items, real R450 judgments)"
node $LEG/paired.mjs $A.judgments.jsonl $B.judgments.jsonl $W/ids P C > $W/p.old 2>/dev/null
node $ARMS/deepvpara/tools/paired.mjs $A.judgments.jsonl $B.judgments.jsonl $W/ids P C > $W/p.new 2> $W/p.new.err
cmp -s $W/p.old $W/p.new; r=$?; ok "paired.mjs stdout old == new ($(sha $W/p.old | cut -c1-16) / $(sha $W/p.new | cut -c1-16)); stderr: $(cat $W/p.new.err)" $r; 
for d in deepthinkv02 deepthink2; do cmp -s $ARMS/deepvpara/tools/paired.mjs $ARMS/$d/tools/paired.mjs; ok "paired.mjs copy $d identical" $?; done
# --common-mode (RND-REVIEW C1): (a) default stdout unchanged, (b) cm CI wider + contains the estimate, (c) sigma 0 ~ plain CI (normal-approx vs bootstrap percentile: width ratio 0.8-1.25, not 1e-9)
PV=$ARMS/deepvpara/tools/paired.mjs
node $PV $A.judgments.jsonl $B.judgments.jsonl $W/ids P C > $W/cm.def 2>/dev/null; cmp -s $W/cm.def $W/p.old; s_=$?; ok "common-mode (a): default output sha $(sha $W/cm.def | cut -c1-16) == legacy $(sha $W/p.old | cut -c1-16)" $s_
node $PV $A.judgments.jsonl $B.judgments.jsonl $W/ids P C --common-mode 0.02 > $W/cm.02 2>/dev/null; node $PV $A.judgments.jsonl $B.judgments.jsonl $W/ids P C --common-mode 0 > $W/cm.00 2>/dev/null
jq -e '[.paired.dRatio,.paired.dRatioCI,.paired.dRatioCIcm,.paired.dFloor,.paired.dFloorCI,.paired.dFloorCIcm] as [$r,$ri,$rc,$f,$fi,$fc] | ($rc[1]-$rc[0]) > ($ri[1]-$ri[0]) and $rc[0] <= $r and $r <= $rc[1] and ($fc[1]-$fc[0]) > ($fi[1]-$fi[0]) and $fc[0] <= $f and $f <= $fc[1] and .P.ratioCIcm[0] < .P.ci[0] and .P.floorAdjCIcm[1] > .P.floorAdjCI[1] and .paired.commonMode.sigmaRaw==0.02 and .paired.commonMode.sigmaFloor==0.02' $W/cm.02 > /dev/null; ok "common-mode (b): --common-mode 0.02 widens dRatio/dFloor/per-arm CIs and contains the point estimate" $?
jq -e '[.paired.dRatioCI,.paired.dRatioCIcm,.paired.dFloorCI,.paired.dFloorCIcm] as [$a,$b,$c,$d] | (($b[1]-$b[0])/($a[1]-$a[0])) as $x | (($d[1]-$d[0])/($c[1]-$c[0])) as $y | $x>=0.8 and $x<=1.25 and $y>=0.8 and $y<=1.25' $W/cm.00 > /dev/null; s_=$?; ok "common-mode (c): sigma 0 width ratio vs bootstrap CI in 0.8-1.25 (ratio $(jq '(.paired.dRatioCIcm|.[1]-.[0]) / (.paired.dRatioCI|.[1]-.[0])' $W/cm.00), floor $(jq '(.paired.dFloorCIcm|.[1]-.[0]) / (.paired.dFloorCI|.[1]-.[0])' $W/cm.00))" $s_
mkdir -p $W/fm; for x in traces judgments; do ln -sf $A.$x.jsonl $W/fm/a.$x.jsonl; ln -sf $B.$x.jsonl $W/fm/b.$x.jsonl; done
python3 $LEG/floor_metrics.py --runs a b --dir $W/fm --decline-ratio 0.306 --ids $W/ids > $W/f.old 2>/dev/null
python3 $EVAL/bench/v0.2/plan/floor_metrics.py --runs a b --dir $W/fm --decline-ratio 0.306 --ids $W/ids > $W/f.new 2> $W/f.new.err
cmp -s $W/f.old $W/f.new; r=$?; ok "floor_metrics.py (v0.2) stdout old == new ($(sha $W/f.old | cut -c1-16) / $(sha $W/f.new | cut -c1-16)); stderr: $(cat $W/f.new.err)" $r
cmp -s $EVAL/bench/v0.2/plan/floor_metrics.py $EVAL/bench/v0.3/plan/floor_metrics.py; ok "floor_metrics.py v0.2 == v0.3 copy" $?
$ARM_OLD scales 42 > $W/scales.old.out 2>&1; ro=$?; mkdir -p $W/agg.old; cp $W/agg/* $W/agg.old/ 2>/dev/null; rm -rf $W/agg/* $W/agg/.agg* $W/out/paired-1seed
$ARM_NEW scales 42 > $W/scales.new.out 2>&1; rn=$?
diff -r $W/agg.old $W/agg > $W/agg.diff; r=$?; L2O=$(sha $W/agg.old/L2-P-1seed.opus.json); L2N=$(sha $W/agg/L2-P-1seed.opus.json)
ok "arm.sh scales stage: legacy rc=$ro new rc=$rn, aggregates identical ($(ls $W/agg | wc -l | tr -d ' ') files; L2 $(sha $W/agg.old/L2-P-1seed.opus.json | cut -c1-16) / $(sha $W/agg/L2-P-1seed.opus.json | cut -c1-16))" $(( r + rn + ro ))
[ -s $W/agg/L2-P-1seed.opus.json ] || { echo "scales produced no L2 file:"; tail -5 $W/scales.new.out; }
if [ "${DT512_BLIND_REPLAY:-0}" = 1 ]; then
  mkdir -p $W/dt512agg; AGG_DIR=$W/dt512agg WORK_DIR=$W/dt512work $LIB/arm.sh $ARMS/dt512/arm.conf scales "42 43" > $W/dt512.out 2>&1; echo "  dt512 replay rc=$?"
  for f in L2-H-2seed.opus.json paired_gap-HvsT-2seed.json paired_gap-HvsD-2seed.json; do cmp -s $ARMS/dt512/aggregates/$f $W/dt512agg/$f; s_=$?; ok "DT512 frozen $f $(sha $ARMS/dt512/aggregates/$f | cut -c1-16) / $(sha $W/dt512agg/$f | cut -c1-16)" $s_; done
else echo "  [skip] DT512 blind replay (DT512_BLIND_REPLAY=1; its inputs live under blind/, which the test author may not read)"; fi

echo "T2 truncated judgments (last 5 rows dropped) -> stage aborts and names the ids"
head -n $(( $(wc -l < $A.judgments.jsonl) - 5 )) $A.judgments.jsonl > $W/out/p-s42.judgments.jsonl; rm -rf $W/agg/* $W/agg/.agg*
want=$(tail -5 $A.judgments.jsonl | jq -r .queryId | sort -u | tr '\n' ' ')
$ARM_NEW scales 42 > $W/t2.out 2>&1; r=$?; [ $r = 5 ] && z=0 || z=1; ok "scales rc=$r (expect 5)" $z
named=0; for i in $want; do grep -q "$i" $W/t2.out || named=1; done; ok "ids named in output: $want" $named
[ -z "$(ls $W/agg | grep -v '^\.')" ]; ok "no aggregate written" $?; grep "CHECK FAIL" $W/t2.out | cut -c1-200
$ARM_OLD scales 42 > $W/t2.old.out 2>&1; echo "  (legacy arm.sh on the same input: rc=$? and silently wrote an aggregate)"; rm -rf $W/agg/* $W/agg/.agg*
cp $A.judgments.jsonl $W/out/p-s42.judgments.jsonl

echo "T3 errored trace: judge.mjs --floor-errored / WARN / --strict (stub claude on PATH, 0 judge calls)"
ERR=$(sed -n 5p $W/ids); mkdir -p $W/bin; printf '#!/bin/bash\n[ "$1" = --version ] && { echo "0.0-stub"; exit 0; }\necho "$@" >> %s/claude.calls; exit 1\n' $W > $W/bin/claude; chmod +x $W/bin/claude
jq -c --arg e "$ERR" 'if .itemId==$e then .error={code:"timeout",message:"synthetic timeout"} else . end' $A.traces.jsonl > $W/t3.traces.jsonl
grep -v "\"queryId\":\"$ERR\"" $A.judgments.jsonl | jq -c --arg t "$(sha $W/t3.traces.jsonl)" --arg q "$(sha $W/bench/questions.jsonl)" --arg r "$(sha $W/bench/refs.jsonl)" '.tracesSha256=$t | .questionsSha256=$q | .refsSha256=$r' > $W/t3.base.jsonl   # provenance = this fixture (judge.mjs resume check, audit F1)
JM="node $EVAL/harness/judge.mjs --traces $W/t3.traces.jsonl --bench $W/bench --refs $W/bench/refs.jsonl --system t3"
cp $W/t3.base.jsonl $W/t3.nof.jsonl; PATH=$W/bin:$PATH $JM --out $W/t3.nof.jsonl > $W/t3.nof.out 2>&1; r=$?
grep -q "WARN dropped 1 errored traces" $W/t3.nof.out && [ $r = 0 ]; ok "no flag: WARN dropped 1 errored traces, rc=$r" $?; grep WARN $W/t3.nof.out | cut -c1-110
PATH=$W/bin:$PATH $JM --out $W/t3.strict.jsonl --strict > $W/t3.strict.out 2>&1; r=$?; [ $r = 5 ] && [ ! -e $W/t3.strict.jsonl ]; ok "--strict: rc=$r (expect 5), no call, no output" $?
cp $W/t3.base.jsonl $W/t3.fl.jsonl; PATH=$W/bin:$PATH $JM --out $W/t3.fl.jsonl --floor-errored > $W/t3.fl.out 2>&1; r=$?
nrow=$(jq -c "select(.queryId==\"$ERR\" and .floorScored==true and .ok==true and .mapped.winner==\"ref\" and (.mapped.boar|[.correctness,.completeness,.usefulness]==[1,1,1]) and (.error|test(\"synthetic timeout\")))" $W/t3.fl.jsonl | wc -l | tr -d ' ')
[ $r = 0 ] && [ "$nrow" = 2 ]; ok "--floor-errored: rc=$r, 2 floor rows (boar 1/1/1, winner ref, error field) for $ERR" $?;
[ ! -s $W/claude.calls ]; ok "0 judge calls (stub claude only saw --version)" $?
node $ARMS/deepvpara/tools/paired.mjs $W/t3.fl.jsonl $B.judgments.jsonl $W/ids P C > /dev/null 2> $W/t3.pf.err; grep -q "n judged = $N of n planned = $N" $W/t3.pf.err; s_=$?; ok "paired.mjs on floor rows: $(head -1 $W/t3.pf.err)" $s_;
node $ARMS/deepvpara/tools/paired.mjs $W/t3.nof.jsonl $B.judgments.jsonl $W/ids P C > $W/t3.p0.json 2> $W/t3.p0.err; echo "  without floor rows: $(head -1 $W/t3.p0.err | cut -c1-120)"
node $ARMS/deepvpara/tools/paired.mjs $W/t3.nof.jsonl $B.judgments.jsonl $W/ids P C --strict > /dev/null 2>&1; r=$?; [ $r = 1 ]; ok "paired.mjs --strict on the dropped item: rc=$r (expect 1)" $?
node $ARMS/deepvpara/tools/paired.mjs $W/t3.nof.jsonl $B.judgments.jsonl $W/ids P C --floor-missing > $W/t3.pm.json 2> $W/t3.pm.err; echo "  --floor-missing: $(head -1 $W/t3.pm.err | cut -c1-60) | ratio P $(jq .P.ratio $W/t3.p0.json) (dropped) -> $(jq .P.ratio $W/t3.pm.json) (floored) vs floor-rows run $(node $ARMS/deepvpara/tools/paired.mjs $W/t3.fl.jsonl $B.judgments.jsonl $W/ids P C 2>/dev/null | jq .P.ratio)"
grep -q "n judged = $((N-1)) of n planned = $N .*scored at the rubric floor" $W/t3.pm.err && [ "$(jq -c .floorMissing $W/t3.pm.json)" = "{\"P\":[\"$ERR\"],\"C\":[]}" ]; ok "paired.mjs --floor-missing reports n judged = $((N-1)) of n planned = $N, floor-scores $ERR for P only" $?
for x in traces; do ln -sf $W/t3.traces.jsonl $W/fm/e.traces.jsonl; done; ln -sf $W/t3.base.jsonl $W/fm/e.judgments.jsonl
python3 $EVAL/bench/v0.2/plan/floor_metrics.py --runs e --dir $W/fm --decline-ratio 0.306 --ids $W/ids > $W/t3.f0.json 2> $W/t3.f0.err; python3 $EVAL/bench/v0.2/plan/floor_metrics.py --runs e --dir $W/fm --decline-ratio 0.306 --ids $W/ids --floor-missing > $W/t3.f1.json 2> $W/t3.f1.err
python3 $EVAL/bench/v0.2/plan/floor_metrics.py --runs e --dir $W/fm --decline-ratio 0.306 --ids $W/ids --strict > /dev/null 2>&1; rs=$?
echo "  floor_metrics: default [$(head -1 $W/t3.f0.err)] n_items $(jq .n_items $W/t3.f0.json) raw $(jq .raw.point $W/t3.f0.json) | --floor-missing [$(head -1 $W/t3.f1.err)] n_items $(jq .n_items $W/t3.f1.json) raw $(jq .raw.point $W/t3.f1.json) | --strict rc=$rs"
[ "$(jq .n_items $W/t3.f1.json)" = "$N" ] && [ "$(jq .n_items $W/t3.f0.json)" = "$((N-1))" ] && [ $rs = 1 ] && grep -q "n judged = $((N-1)) of n planned = $N" $W/t3.f0.err; ok "floor_metrics: default drops (n=$((N-1))), --floor-missing keeps (n=$N), --strict rc 1" $?;

echo "T4 STOP file (stub judge command, nothing may run)"
export BOAR_EVAL_DIR=$W; export JUDGE_CMD=$TD/stub-judge.sh; S=$LIB/../deepthink/tools/shard_judge.sh
head -8 $W/ids > $W/ids8; M=$W/mark; : > $M; export STUB_MARK=$M; O=$W/s4/out.jsonl; mkdir -p $W/s4; mkdir -p $W/s4/out.shards; touch $W/s4/out.shards/STOP
$S $W/out/p-s42.traces.jsonl $O $W/bench $W/ids8 t4 2 opus > $W/t4.out 2>&1; r=$?; [ $r = 4 ] && [ ! -s $M ]; ok "shards/STOP present: rc=$r (expect 4), stub never ran" $?; head -1 $W/t4.out | cut -c1-120
rm $W/s4/out.shards/STOP; touch $O.STOP; $S $W/out/p-s42.traces.jsonl $O $W/bench $W/ids8 t4 2 opus > $W/t4b.out 2>&1; r=$?; [ $r = 4 ] && [ ! -s $M ]; ok "<out>.STOP present: rc=$r (expect 4)" $?; rm $O.STOP
$S $W/out/p-s42.traces.jsonl $O $W/bench $W/ids8 t4 2 opus > $W/t4c.out 2>&1; r=$?; [ $r = 0 ] && [ -s $M ] && [ ! -s $W/s4/out.missing ] && [ "$(wc -l < $O | tr -d ' ')" = 16 ]; ok "no STOP: rc=$r, 16 rows, .missing empty (control run)" $?
rm -rf $W/s4/*; STUB_SKIP=$(sed -n 3p $W/ids8) $S $W/out/p-s42.traces.jsonl $O $W/bench $W/ids8 t4 2 opus > $W/t4d.out 2>&1; r=$?; [ $r = 1 ] && grep -q "$(sed -n 3p $W/ids8)" $W/s4/out.missing && grep -q MISSING $W/t4d.out; ok "stub skips one id: rc=$r (expect 1), id in .missing and on stderr" $?
rm -rf $W/s4/*; STUB_RC=1 $S $W/out/p-s42.traces.jsonl $O $W/bench $W/ids8 t4 2 opus > $W/t4e.out 2>&1; r=$?; [ $r = 3 ]; ok "judge rc=1 in every shard: rc=$r (expect 3, was always 0)" $?
rm -rf $W/s4/*; STUB_RC=3 $S $W/out/p-s42.traces.jsonl $O $W/bench $W/ids8 t4 2 opus > $W/t4f.out 2>&1; r=$?; [ $r = 3 ] && [ -e $W/s4/out.shards/STOP ]; ok "judge rc=3 twice: rc=$r, STOP touched" $?

echo "T5 lock (two concurrent invocations of the judge stage on the same output)"
rm -rf $W/out/p-s42.judgments.* ; : > $M
STUB_SLEEP=4 $LIB/arm.sh $W/arm.conf judge 42 > $W/t5a.out 2>&1 & P1=$!
for i in $(seq 1 40); do [ -d $W/out/p-s42.judgments.jsonl.lock ] && break; sleep 0.25; done
$LIB/arm.sh $W/arm.conf judge 42 > $W/t5b.out 2>&1; r=$?; [ $r != 0 ] && grep -q "LOCKED" $W/t5b.out; s_=$?; ok "second judge stage: rc=$r, fails fast: $(grep -m1 LOCKED $W/t5b.out | cut -c1-110)" $s_;
wait $P1; r=$?; [ $r = 0 ] && [ ! -d $W/out/p-s42.judgments.jsonl.lock ] && [ "$(wc -l < $W/out/p-s42.judgments.jsonl | tr -d ' ')" = $((2*N)) ]; ok "first stage finished rc=$r, lock released, $((2*N)) rows" $?
mkdir $W/agg/.agg-P.lock; $LIB/arm.sh $W/arm.conf scales 42 > $W/t5c.out 2>&1; r=$?; [ $r = 6 ] && grep -q LOCKED $W/t5c.out; ok "aggregate lock held: scales rc=$r (expect 6)" $?; rmdir $W/agg/.agg-P.lock
STUB_SKIP=$(sed -n 2p $W/ids) $LIB/arm.sh $W/arm.conf judge 42 > $W/t5d.out 2>&1; r=$?; rm -rf $W/out/p-s42.judgments.*
STUB_SKIP=$(sed -n 2p $W/ids) $LIB/arm.sh $W/arm.conf judge 42 > $W/t5d.out 2>&1; r=$?; [ $r = 5 ] && grep -q "ABORT judge" $W/t5d.out; ok "arm.sh judge with one id missing: rc=$r (expect 5)" $?
unset BOAR_EVAL_DIR JUDGE_CMD STUB_MARK

echo "T6 runner STATUS FAIL / wait / fetch"
bad=0; for f in $ARMS/*/tools/remote-run.sh; do grep -q 'FAIL rc=\$rc' $f && ! grep -q 'echo DONE >> \$S$' $f || { bad=1; echo "  not patched: $f"; }; done; ok "all $(ls $ARMS/*/tools/remote-run.sh | wc -l | tr -d ' ') remote-run.sh copies write FAIL rc=N on rc != 0" $bad
for rc in 0 7; do S=$W/status.$rc; : > $S; sed -n '/^echo "end /,$p' $ARMS/dt512/tools/remote-run.sh > $W/tail.sh; (rc=$rc; S=$S; . $W/tail.sh); done
grep -qx DONE $W/status.0 && grep -q "^FAIL rc=7" $W/status.7 && ! grep -q DONE $W/status.7; s_=$?; ok "tail of runner: rc=0 -> DONE; rc=7 -> '$(tail -1 $W/status.7)' and no DONE" $s_;
HM=$W/home; R=$HM/boar/kiln/be-0cfd4a77-t/be-repo/runs/rX; mkdir -p $R $W/sbin; printf '#!/bin/bash\neval "${@: -1}"\n' > $W/sbin/ssh; chmod +x $W/sbin/ssh
echo "start 1" > $R/STATUS; echo "FAIL rc=7" >> $R/STATUS; : > $R/run.log
HOME=$HM PATH=$W/sbin:$PATH WAIT_EVERY=1 $LIB/arm.sh $W/arm.conf wait rX > $W/t6w.out 2>&1; r=$?; [ $r = 3 ] && grep -q RUNNER-FAIL $W/t6w.out; ok "arm.sh wait on FAIL status: rc=$r (expect 3, RUNNER-FAIL)" $?
echo "end 2 rc=0" > $R/STATUS; echo DONE >> $R/STATUS
HOME=$HM PATH=$W/sbin:$PATH WAIT_EVERY=1 $LIB/arm.sh $W/arm.conf wait rX > $W/t6w2.out 2>&1; r=$?; ok "arm.sh wait on DONE status: rc=$r (expect 0)" $r
printf 'FAIL rc=7\n' > $W/out/rF.traces.status; REPLAY=1 $LIB/arm.sh $W/arm.conf fetch rF $W/out/rF.traces.jsonl > $W/t6f.out 2>&1; r=$?; [ $r = 3 ] && grep -q "ABORT fetch" $W/t6f.out; s_=$?; ok "arm.sh fetch on FAIL status: rc=$r (expect 3): $(head -1 $W/t6f.out | cut -c1-80)" $s_
printf 'start 1\n' > $W/out/rN.traces.status; REPLAY=1 $LIB/arm.sh $W/arm.conf fetch rN $W/out/rN.traces.jsonl > $W/t6n.out 2>&1; r=$?; [ $r = 3 ]; ok "arm.sh fetch without DONE: rc=$r (expect 3)" $?

echo "T7 launch criterion/Power gate (rc 7 before any ssh; ssh stubbed, never contacts a host)"
mkdir -p $W/c7 $W/c7bin $W/c7lock; printf '#!/bin/bash\necho "$@" >> %s/ssh.calls\nexit 1\n' $W/c7 > $W/c7bin/ssh; cp $W/c7bin/ssh $W/c7bin/scp; chmod +x $W/c7bin/ssh $W/c7bin/scp
echo '{}' > $W/c7/req.jsonl; : > $W/c7/ssh.calls
l7() { PATH=$W/c7bin:$PATH LOCK_DIR=$W/c7lock $LIB/arm.sh "$1" launch $W/c7/req.jsonl "r7-$2" > $W/c7/$2.out 2>&1; }
cp $W/arm.conf $W/c7/none.conf; l7 $W/c7/none.conf a; r=$?; [ $r = 7 ] && grep -q "CRITERION is not set" $W/c7/a.out && [ ! -s $W/c7/ssh.calls ]; ok "launch without CRITERION: rc=$r (expect 7), no ssh" $?
printf '# c\n\n## Tags\nTags: none\n\n## Question\nq\n' > $W/c7/nopower.md; { cat $W/arm.conf; echo "CRITERION=$W/c7/nopower.md"; } > $W/c7/nopower.conf
l7 $W/c7/nopower.conf b; r=$?; [ $r = 7 ] && grep -q "criterion lacks Power block (expected_delta, n, seeds, mde)" $W/c7/b.out && [ ! -s $W/c7/ssh.calls ]; ok "criterion without Power: rc=$r (expect 7), no ssh" $?
printf '# c\n\n## Power\nexpected_delta: 0.05 (source: x)\nn: 51\nseeds: 2\n\n## Stages\nmde: 0.03\n' > $W/c7/partial.md; { cat $W/arm.conf; echo "CRITERION=$W/c7/partial.md"; } > $W/c7/partial.conf
l7 $W/c7/partial.conf c; r=$?; [ $r = 7 ] && [ ! -s $W/c7/ssh.calls ]; ok "Power block missing mde (mde only outside the section): rc=$r (expect 7)" $?
printf '# c\n\n## Tags\nTags: none\n\n## Power\nexpected_delta: 0.05 (source: x)\nn: 51\nseeds: 2\nmde: 0.03\n' > $W/c7/good.md; { cat $W/arm.conf; echo "CRITERION=$W/c7/good.md"; } > $W/c7/good.conf
l7 $W/c7/good.conf d; r=$?; [ -s $W/c7/ssh.calls ] && ! grep -q "launch refused" $W/c7/d.out; ok "criterion with Power: passes the check (reaches the stubbed ssh, rc=$r from the stub)" $?
sha256sum_() { shasum -a 256 "$1" | cut -d' ' -f1; }; echo "deadbeef  good.md" > $W/c7/good.sha256; : > $W/c7/ssh.calls
l7 $W/c7/good.conf e; r=$?; [ $r = 7 ] && grep -q "sha256 mismatch" $W/c7/e.out && [ ! -s $W/c7/ssh.calls ]; ok "sha256 sibling mismatch: rc=$r (expect 7)" $?
echo "$(sha256sum_ $W/c7/good.md)  good.md" > $W/c7/good.sha256; l7 $W/c7/good.conf f; [ -s $W/c7/ssh.calls ]; ok "sha256 sibling match: passes the check" $?
printf '# c\n\n## Tags\nTags: blocker\n\n## Question\nq\n' > $W/c7/blocker.md; { cat $W/arm.conf; echo "CRITERION=$W/c7/blocker.md"; } > $W/c7/blocker.conf; : > $W/c7/ssh.calls
l7 $W/c7/blocker.conf g; [ -s $W/c7/ssh.calls ] && ! grep -q "launch refused" $W/c7/g.out; ok "blocker tag without Power: passes the check" $?
cp $LIB/CRITERION-TEMPLATE.md $W/c7/tpl.md; { cat $W/arm.conf; echo "CRITERION=$W/c7/tpl.md"; } > $W/c7/tpl.conf; : > $W/c7/ssh.calls
l7 $W/c7/tpl.conf h; ! grep -q "lacks Power block" $W/c7/h.out && grep -q "Precheck key token_projection is unfilled" $W/c7/h.out && [ ! -s $W/c7/ssh.calls ]; ok "CRITERION-TEMPLATE.md itself has a complete Power block and is not tagged blocker (passes the Power check; since T3 (Ruleset 30) the unfilled Precheck placeholders stop it before any ssh)" $?

echo "T8 precheck (arm.sh precheck: did the arm change the input vs control; offline, no judge)"
mkdir -p $W/pc
head -20 $W/ids > $W/pc/ids; jq -R -c '{itemId:., route:{reasonCodes:["task:qa","context:1200->800","detector:p=0.41","generate:deep"]}, retrieval:{kept:[{title:("T-"+.)},{title:"Common"}]}}' $W/pc/ids > $W/pc/ctl.jsonl
cp $W/pc/ctl.jsonl $W/pc/same.jsonl; sed 's/context:1200->800/context:900->7/; s/detector:p=0.41/detector:p=0.93/' $W/pc/ctl.jsonl > $W/pc/noise.jsonl
$LIB/arm.sh $W/arm.conf precheck $W/pc/same.jsonl $W/pc/ctl.jsonl > $W/pc/o1 2>&1; r=$?; [ $r = 8 ] && grep -q "n=20 changed=0 (0.00)" $W/pc/o1 && grep -q "PRECHECK FAIL" $W/pc/o1; ok "precheck identical traces: rc=$r (expect 8)" $?
$LIB/arm.sh $W/arm.conf precheck $W/pc/noise.jsonl $W/pc/ctl.jsonl > $W/pc/o1b 2>&1; r=$?; [ $r = 8 ]; ok "precheck run-dependent noise codes only (context:N->M, detector:p=): rc=$r (expect 8)" $?
jq -c 'if (.itemId|IN($ids[])) then .retrieval.kept[0].title="OTHER" else . end' --argjson ids "$(head -6 $W/pc/ids | jq -R . | jq -s .)" $W/pc/ctl.jsonl > $W/pc/kept.jsonl
$LIB/arm.sh $W/arm.conf precheck $W/pc/kept.jsonl $W/pc/ctl.jsonl > $W/pc/o2 2>&1; r=$?; [ $r = 0 ] && grep -q "n=20 changed=6 (0.30) kept-diff=6 codes-diff=0 marker=0" $W/pc/o2; s_=$?; ok "precheck kept differs on 30%: rc=$r (expect 0): $(head -1 $W/pc/o2)" $s_
jq -c --argjson ids "$(sed -n 1,10p $W/pc/ids | jq -R . | jq -s .)" 'if (.itemId|IN($ids[])) then .route.reasonCodes += ["addpack:wiki-vital5"] else . end' $W/pc/ctl.jsonl > $W/pc/mk.jsonl
$LIB/arm.sh $W/arm.conf precheck $W/pc/mk.jsonl $W/pc/ctl.jsonl > $W/pc/o3 2>&1; r=$?; grep -q "codes-diff=10 marker=0" $W/pc/o3; ok "precheck extra code diff counted (codes-diff=10) rc=$r" $?
{ cat $W/arm.conf; echo 'PRECHECK_MARKERS="addpack: deepcover:"'; } > $W/pc/mk.conf; $LIB/arm.sh $W/pc/mk.conf precheck $W/pc/mk.jsonl $W/pc/ctl.jsonl > $W/pc/o3b 2>&1; r=$?; [ $r = 0 ] && grep -q "n=20 changed=10 (0.50) kept-diff=0 codes-diff=10 marker=10" $W/pc/o3b; s_=$?; ok "precheck marker codes on 50%: rc=$r (expect 0): $(head -1 $W/pc/o3b)" $s_
sed -n 11,20p $W/pc/ids > $W/pc/ids_unch; $LIB/arm.sh $W/arm.conf precheck $W/pc/mk.jsonl $W/pc/ctl.jsonl $W/pc/ids_unch > $W/pc/o4 2>&1; r=$?; [ $r = 8 ] && grep -q "n=10 changed=0" $W/pc/o4 && grep -q "^unchanged: " $W/pc/o4; ok "precheck idsFile restricted to unchanged items: rc=$r (expect 8), ids listed" $?
$LIB/arm.sh $W/arm.conf precheck $W/pc/mk.jsonl $W/pc/ctl.jsonl --min 0.6 > $W/pc/o5 2>&1; r=$?; [ $r = 8 ]; ok "precheck --min 0.6 on 50%: rc=$r (expect 8)" $?

echo "T9 resume provenance (audit F1): rows from other traces / another judge model are refused unless the splice is declared (0 judge calls)"
SJ=$ARMS/deepthink/tools/shard_judge.sh
cp $A.judgments.jsonl $W/t9.jsonl; PATH=$W/bin:$PATH node $EVAL/harness/judge.mjs --traces $B.traces.jsonl --out $W/t9.jsonl --bench $W/bench --refs $W/bench/refs.jsonl --judge-model claude-haiku-5-5 --dry-run > $W/t9a.out 2>&1; r=$?
[ $r = 7 ] && grep -q "^STALE: $((2*N)) ok rows" $W/t9a.out; s_=$?; ok "Repro A (deep35 Opus rows, bmoe traces, Haiku requested): rc=$r (expect 7): $(head -c 110 $W/t9a.out)" $s_
PATH=$W/bin:$PATH node $EVAL/harness/judge.mjs --traces $B.traces.jsonl --out $W/t9.jsonl --bench $W/bench --refs $W/bench/refs.jsonl --judge-model claude-haiku-5-5 --dry-run --allow-splice > $W/t9b.out 2>&1; r=$?
[ $r = 0 ] && grep -q "^SPLICE" $W/t9b.out && grep -q "0 calls to do" $W/t9b.out; s_=$?; ok "--allow-splice declares it: rc=$r, SPLICE warning, 0 calls" $s_
mkdir -p $W/bench9/refs; cp $W/bench/questions.jsonl $W/bench9/; cp $W/bench/refs.jsonl $W/bench9/refs/refs.jsonl   # shard_judge passes no --refs
export BOAR_EVAL_DIR=$EVAL; unset JUDGE_CMD; mkdir -p $W/t9s/out.shards; cp $A.judgments.jsonl $W/t9s/out.shards/shard-0.jsonl; : > $W/claude.calls
PATH=$W/bin:$PATH $SJ $B.traces.jsonl $W/t9s/out.jsonl $W/bench9 $W/ids t9 1 opus > $W/t9c.out 2>&1; r=$?
[ $r = 3 ] && grep -q "### exit 7" $W/t9s/out.shards/shard-0.log && grep -q "PROVENANCE: tracesSha256" $W/t9c.out && [ ! -s $W/claude.calls ]; s_=$?; ok "Repro B (shard-0 = deep35 rows, bmoe traces): shard_judge rc=$r (expect 3; shard exit 7 + PROVENANCE), 0 calls" $s_
rm -rf $W/t9s; mkdir -p $W/t9s/out.shards; cp $A.judgments.jsonl $W/t9s/out.shards/shard-0.jsonl
JUDGE_CMD=true ALLOW_SPLICE=1 $SJ $B.traces.jsonl $W/t9s/out.jsonl $W/bench9 $W/ids t9 1 haiku > $W/t9d.out 2>&1; r=$?; [ $r = 1 ] && grep -q "PROVENANCE: requested model" $W/t9d.out; s_=$?; ok "ALLOW_SPLICE=1 still refuses another judge model: rc=$r (expect 1)" $s_
JUDGE_CMD=true ALLOW_SPLICE=1 $SJ $B.traces.jsonl $W/t9s/out.jsonl $W/bench9 $W/ids t9 1 opus > $W/t9e.out 2>&1; r=$?; ok "ALLOW_SPLICE=1 + same model: declared splice accepted, rc=$r" $r
unset BOAR_EVAL_DIR
echo "T10 floor rows vs fixed traces (audit F4) and --ids hygiene (F9)"
PATH=$W/bin:$PATH node $EVAL/harness/judge.mjs --traces $A.traces.jsonl --bench $W/bench --refs $W/bench/refs.jsonl --system t3 --out $W/t3.fl.jsonl --dry-run --allow-splice > $W/t10a.out 2>&1; r=$?
grep -q "floor rows superseded (trace no longer errored): 2 rows ($ERR)" $W/t10a.out && grep -q " 2 calls to do" $W/t10a.out; s_=$?; ok "trace fixed: the 2 floor rows of $ERR no longer count as done (2 calls to do), rc=$r" $s_
node $EVAL/harness/judge.mjs --traces $A.traces.jsonl --bench $W/bench --refs $W/bench/refs.jsonl --out $W/t10.jsonl --ids "$(sed -n 1p $W/ids), $(sed -n 2p $W/ids),zz-0O5" --dry-run > $W/t10b.out 2>&1; r=$?
grep -q "WARN --ids: 1 ids not in the questions file" $W/t10b.out && grep -q "judge: 2 items" $W/t10b.out; s_=$?; ok "--ids trimmed (2 items) and the unknown id named, rc=$r" $s_
node $EVAL/harness/judge.mjs --traces $A.traces.jsonl --bench $W/bench --refs $W/bench/refs.jsonl --out $W/t10.jsonl --ids "zz-0O5" --dry-run --strict > /dev/null 2>&1; r=$?; [ $r = 5 ]; s_=$?; ok "--ids unknown id with --strict: rc=$r (expect 5)" $s_
echo "T11 SIGTERM (audit F6): shards are killed before the lock is released"
export BOAR_EVAL_DIR=$W JUDGE_CMD=$TD/stub-judge.sh; mkdir -p $W/t11
STUB_SLEEP=5 $SJ $W/out/p-s42.traces.jsonl $W/t11/out.jsonl $W/bench $W/ids8 t11 2 opus > $W/t11.out 2>&1 & P1=$!
for i in $(seq 1 40); do [ -d $W/t11/out.jsonl.lock ] && [ -s $W/t11/out.shards/shard-0.log ] || pgrep -f "stub-judge.sh.*$W/t11/" > /dev/null && break; sleep 0.1; done; sleep 0.5
kill -TERM $P1; wait $P1; r=$?; sleep 0.3; alive=$(pgrep -f "stub-judge.sh.*$W/t11/" | wc -l | tr -d ' ')
[ $r = 130 ] && [ "$alive" = 0 ] && [ ! -d $W/t11/out.jsonl.lock ]; s_=$?; ok "SIGTERM: rc=$r (expect 130), stub judges alive $alive (expect 0), lock released" $s_
sleep 5; [ -z "$(cat $W/t11/out.shards/shard-*.jsonl 2>/dev/null)" ]; s_=$?; ok "no shard row written after the kill" $s_
unset BOAR_EVAL_DIR JUDGE_CMD

echo; echo "RESULT: $PASS passed, $FAIL failed (scratch $W)"; echo "T1 sha256 old/new:"; echo "  paired.mjs       $(sha $W/p.old)  $(sha $W/p.new)"; echo "  floor_metrics.py $(sha $W/f.old)  $(sha $W/f.new)"; echo "  L2 scales stage  $L2O  $L2N"
rm -f $LEG/arm.run.sh; [ "${KEEP:-0}" = 1 ] || rm -rf "$W"
[ $FAIL = 0 ]
