#!/bin/bash
# Offline tests for LOOP v2 T6: tools/deny-hook.sh (5 deny rules, 0 false fires on the last 200 Bash commands of the 10-14 transcript), tools/lock.sh,
# the judge-lane check in arm.sh (judge / l1), tools/session-start.sh and the STATE locks count. 0 LLM calls (claude is a stub), never reads blind/ or rnd/veil/ (only path strings are tested).
# Run: bash rnd/research/coordinator/arms/_lib/tests/guard-tests.sh   (exit 0 = all pass, < 60 s)
set -u
TD=$(cd "$(dirname "$0")" && pwd); LIB=$(cd "$TD/.." && pwd); TOOLS=$(cd "$LIB/../../tools" && pwd); H=$TOOLS/deny-hook.sh; LK=$TOOLS/lock.sh; SS=$TOOLS/session-start.sh
FXJ=$TD/fixtures/deny/last200-bash-2026-10-14.jsonl
PASS=0; FAIL=0; ok() { if [ "$2" = 0 ]; then PASS=$((PASS+1)); echo "  [pass] $1"; else FAIL=$((FAIL+1)); echo "  [FAIL] $1"; fi; }
W=$(mktemp -d "${TMPDIR:-/tmp}/guardtest.XXXXXX"); BG=""; trap 'rm -rf "$W"; [ -n "$BG" ] && kill $BG 2>/dev/null' EXIT
sleep 0 & DEAD=$!; wait $DEAD 2>/dev/null   # a pid that is certainly dead

# ---- hook helpers: bash <command> / tool <name> <key> <value> -> rc in $?, stderr in $W/err
jb() { python3 -I -c 'import json,sys;print(json.dumps({"session_id":"t","tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "$1"; }
jt() { python3 -I -c 'import json,sys;print(json.dumps({"session_id":"t","tool_name":sys.argv[1],"tool_input":{sys.argv[2]:sys.argv[3]}}))' "$1" "$2" "$3"; }
hk() { jb "$1" | bash $H 2>$W/err >/dev/null; }
ht() { jt "$1" "$2" "$3" | bash $H 2>$W/err >/dev/null; }
deny() { local rule=$1 c=$2; hk "$c"; local rc=$?; r=1; [ $rc = 2 ] && grep -q "^DENY $rule:" $W/err && r=0; ok "$rule denies: $(echo "$c" | cut -c1-70)" $r; }
allow() { hk "$1"; local rc=$?; r=1; [ $rc = 0 ] && [ ! -s $W/err ] && r=0; ok "allowed: $(echo "$1" | cut -c1-70 | tr '\n' ' ')" $r; }

echo "T-G1 each deny rule fires"
deny R1 'git push origin main'
deny R1 'git -C rnd push origin main'
deny R1 "ssh mini 'cd x && git push'"
deny R1 'cd rnd && git --no-pager push --force'
deny R2 'hf upload r4topunk/boar-packs ./pack.gguf'
deny R2 'huggingface-cli upload r4topunk/boar-packs ./pack'
deny R2 'huggingface-cli repo create r4to/new --type dataset'
deny R2 'python3 -c "from huggingface_hub import HfApi; HfApi().upload_folder(folder_path=1, repo_id=2)"'
deny R3 "<on the mini> 'docker restart a database container'"
deny R3 'docker compose down'
deny R3 'cd x && docker rm -f a database container'
deny R4 'kill $(lsof -ti:8094)'
deny R4 "lsof -i :8094 | awk 'NR>1{print \$2}' | xargs kill -9"
deny R4 'pkill -f 8094'
deny R4 "<on the mini> 'pkill -f 8094'"
deny R5 'cat blind/x/items.jsonl'
deny R5 'head -3 <private held-out dir>'
deny R5 "jq -c . rnd/veil/old/items.jsonl"
ht Read file_path <private held-out dir>; rc=$?; r=1; [ $rc = 2 ] && grep -q '^DENY R5:' $W/err && r=0; ok "R5 denies Read tool on blind/x/questions.jsonl" $r
ht Grep path <workspace>/rnd/veil; rc=$?; r=1; [ $rc = 2 ] && grep -q '^DENY R5:' $W/err && r=0; ok "R5 denies Grep tool on rnd/veil" $r
ht Edit file_path <private held-out dir>; rc=$?; ok "R5 denies Edit tool under rnd/veil/ (rc=$rc)" $([ $rc = 2 ] && echo 0 || echo 1)

echo "T-G2 0 false fires on the last 200 Bash commands of the 10-14 transcript"
mkdir -p $W/cases; python3 -I - "$FXJ" "$W/cases" <<'PYEOF'
import json, sys
for n, l in enumerate(open(sys.argv[1])):
    open("%s/%03d.json" % (sys.argv[2], n), "w").write(json.dumps({"session_id": "t", "tool_name": "Bash", "tool_input": {"command": json.loads(l)["command"]}}))
PYEOF
cnt=0; off=0; : > $W/off.txt
for f in $W/cases/*.json; do cnt=$((cnt+1)); bash $H < $f >/dev/null 2>$W/e1; rc=$?; if [ $rc != 0 ]; then off=$((off+1)); echo "$f rc=$rc $(head -c 160 $W/e1)" >> $W/off.txt; fi; done
[ $cnt = 200 ] && [ $off = 0 ]; ok "fixture: $cnt commands fed, $off offenders" $?; [ $off = 0 ] || head -5 $W/off.txt
n8094=$(grep -c 8094 $FXJ); nbl=$(grep -c 'blind/' $FXJ); [ "$n8094" -ge 7 ] && [ "$nbl" -ge 12 ]; ok "fixture really contains the risky strings (8094 in $n8094, blind/ in $nbl)" $?

echo "T-G3 allowed cases"
allow 'BOAR_ALLOW_PUSH=1 git push origin main'
allow 'python3 rnd/kiln/packs/publish_pack.py --go'
allow 'docker ps'
allow 'docker logs a database container --tail 20'
allow 'curl localhost:8094/health'
allow 'ls blind/'
allow 'wc -l blind/x/items.jsonl'
allow 'cat blind/x/runs/foo.traces.jsonl'
allow 'git status && git log --oneline -3'
allow "grep -n 'git push' rnd/research/coordinator/LOOP-V2-2026-10-14.md"
allow "$(printf "python3 - <<'EOF'\ncrit = 'kill 8094 and docker restart'\nprint('cat blind/x/items.jsonl')\nEOF\necho done")"
allow "$(printf "cat > c.md <<EOF\nkill 8094\ncat blind/x/items.jsonl\nEOF")"
ht Read file_path <private held-out dir>; rc=$?; ok "Read of blind/x/runs-cut6/judged.ids allowed (rc=$rc)" $([ $rc = 0 ] && echo 0 || echo 1)
ht Read file_path <workspace>/rnd/research/coordinator/QUEUE.md; ok "Read of QUEUE.md allowed" $?
hk 'BOAR_BLIND_EXCEPTION="mint v0.3 hashes" head -2 blind/x/items.jsonl'; rc=$?; r=1; [ $rc = 0 ] && grep -q '^ALLOW blind exception: mint v0.3 hashes' $W/err && r=0; ok "BOAR_BLIND_EXCEPTION prefix allows one R5 command and says so (rc=$rc)" $r
hk 'BOAR_BLIND_EXCEPTION="x" git push'; rc=$?; ok "the blind exception does not cover git push (rc=$rc)" $([ $rc = 2 ] && echo 0 || echo 1)
printf 'this is not json {{{' | bash $H >/dev/null 2>$W/err; rc=$?; ok "malformed stdin -> exit 0 (rc=$rc)" $([ $rc = 0 ] && [ ! -s $W/err ] && echo 0 || echo 1)
printf '' | bash $H >/dev/null 2>&1; ok "empty stdin -> exit 0" $?
echo '{"tool_name":"Bash","tool_input":null}' | bash $H >/dev/null 2>&1; ok "tool_input null -> exit 0" $?
s=$(python3 -I -c 'import time;print(time.time())'); for i in 1 2 3 4 5; do jb 'cd x && git status | cat' | bash $H >/dev/null 2>&1; done; e=$(python3 -I -c 'import time,sys;print(int((time.time()-float(sys.argv[1]))*200))' $s)
[ "$e" -lt 200 ]; ok "hook latency ${e} ms mean (limit 200, incl. bash + python3 -I start)" $?

echo "T-G4 lock.sh"
export LOCK_ROOT=$W/lk ARMS_ROOT=$W/arms; mkdir -p $W/arms/a1 $W/arms/a2; unset BOAR_SESSION_PID
N0="2026-10-15 20:00"
NOW="$N0" bash $LK take judge burn --until "2026-10-15 23:00" --note "oracle cells" > $W/o 2>&1; rc=$?
ok "burn takes judge (rc=$rc)" $([ $rc = 0 ] && grep -q '^session=burn$' $LOCK_ROOT/judge.lock && grep -q '^until=2026-10-15 23:00$' $LOCK_ROOT/judge.lock && grep -q '^note=oracle cells$' $LOCK_ROOT/judge.lock && grep -q '^taken=2026-10-15 20:00$' $LOCK_ROOT/judge.lock && grep -q '^pid=' $LOCK_ROOT/judge.lock && echo 0 || echo 1)
r=$(NOW="$N0" bash $LK holder judge); ok "holder: '$r'" $([ "$r" = "burn until 2026-10-15 23:00" ] && echo 0 || echo 1)
r=$(NOW="$N0" bash $LK holder mac-gen); ok "holder of a free lane: '$r'" $([ "$r" = free ] && echo 0 || echo 1)
r=$(NOW="$N0" bash $LK take judge main); rc=$?; ok "main cannot take a lane held by burn: rc=$rc '$r'" $([ $rc = 9 ] && [ "$r" = "LOCKED judge by burn until 2026-10-15 23:00" ] && echo 0 || echo 1)
NOW="$N0" bash $LK take judge burn --until "2026-10-15 23:30" >/dev/null; rc=$?; r=$(NOW="$N0" bash $LK holder judge)
ok "burn renews (rc=$rc, '$r')" $([ $rc = 0 ] && [ "$r" = "burn until 2026-10-15 23:30" ] && echo 0 || echo 1)
NOW="$N0" bash $LK release judge main >/dev/null; rc=$?; ok "main cannot release burn's lock (rc=$rc)" $([ $rc = 9 ] && [ -f $LOCK_ROOT/judge.lock ] && echo 0 || echo 1)
r=$(NOW="2026-10-16 00:00" bash $LK holder judge); ok "expired lock reads free and is removed ('$r')" $([ "$r" = free ] && [ ! -e $LOCK_ROOT/judge.lock ] && echo 0 || echo 1)
NOW="$N0" bash $LK take judge burn --until "2026-10-15 21:00" >/dev/null; NOW="2026-10-15 22:00" bash $LK take judge main >/dev/null; rc=$?; r=$(NOW="2026-10-15 22:00" bash $LK holder judge | cut -d' ' -f1)
ok "main takes over an expired lock (rc=$rc, holder=$r)" $([ $rc = 0 ] && [ "$r" = main ] && echo 0 || echo 1)
r=$(NOW="2026-10-15 22:00" bash $LK take judge burn); rc=$?; ok "burn blocked by main's new lock: rc=$rc" $([ $rc = 9 ] && echo 0 || echo 1)
NOW="2026-10-15 22:00" bash $LK release judge main >/dev/null; rc=$?; r=$(bash $LK holder judge); ok "main releases (rc=$rc, holder=$r)" $([ $rc = 0 ] && [ "$r" = free ] && echo 0 || echo 1)
NOW="2026-10-15 21:30" bash $LK take mac-gen main >/dev/null; r=$(NOW="2026-10-15 21:30" bash $LK holder mac-gen); ok "default --until = now + 4 h ('$r')" $([ "$r" = "main until 2026-10-16 01:30" ] && echo 0 || echo 1)
NOW="2026-10-15 21:30" bash $LK take mac-cpu burn --until "2026-10-15 23:00" >/dev/null
r=$(NOW="2026-10-15 21:31" bash $LK audit); n=$(echo "$r" | wc -l | tr -d ' '); ok "audit: one line per lock ($n): $(echo "$r" | tr '\n' ';')" $([ "$n" = 2 ] && echo "$r" | grep -q '^mac-cpu burn until 2026-10-15 23:00 ok$' && echo "$r" | grep -q '^mac-gen main until 2026-10-16 01:30 ok$' && echo 0 || echo 1)
r=$(NOW="2026-10-15 23:30" bash $LK audit | grep '^mac-cpu'); ok "audit marks EXPIRED ('$r')" $([ "$r" = "mac-cpu burn until 2026-10-15 23:00 EXPIRED" ] && echo 0 || echo 1)
BOAR_SESSION_PID=$DEAD NOW="2026-10-15 21:30" bash $LK take mini-long burn --until "2026-10-15 23:00" >/dev/null; r=$(NOW="2026-10-15 21:31" bash $LK audit | grep '^mini-long')
ok "audit marks STALE for a dead session pid ('$r')" $([ "$r" = "mini-long burn until 2026-10-15 23:00 STALE" ] && echo 0 || echo 1)
BOAR_SESSION_PID=$$ NOW="2026-10-15 21:30" bash $LK take mac-cpu burn --until "2026-10-15 23:00" >/dev/null; r=$(NOW="2026-10-15 21:31" bash $LK audit | grep '^mac-cpu'); ok "a live session pid stays ok ('$r')" $([ "$r" = "mac-cpu burn until 2026-10-15 23:00 ok" ] && echo 0 || echo 1)
r=$(LOCK_ROOT=$W/empty bash $LK audit); rc=$?; ok "audit with no locks: '$r' rc=$rc" $([ "$r" = "locks: 0" ] && [ $rc = 0 ] && echo 0 || echo 1)
bash $LK take bogus main >/dev/null 2>&1; r1=$?; bash $LK take judge root >/dev/null 2>&1; r2=$?; bash $LK take judge main --until tomorrow >/dev/null 2>&1; r3=$?; ok "bad lane / session / --until -> rc 2 ($r1 $r2 $r3)" $([ $r1 = 2 ] && [ $r2 = 2 ] && [ $r3 = 2 ] && echo 0 || echo 1)
NOW="$N0" bash $LK own a1 main >/dev/null; rc=$?; ok "own a1 by main (rc=$rc): $(cat $W/arms/a1/.owner)" $([ $rc = 0 ] && grep -qE '^session=main since=2026-10-15 20:00 pid=[0-9]*$' $W/arms/a1/.owner && echo 0 || echo 1)
bash $LK own a1 burn >/dev/null; rc=$?; ok "a second session cannot own a1 while the owner is live/unknown (rc=$rc)" $([ $rc = 9 ] && grep -q 'session=main' $W/arms/a1/.owner && echo 0 || echo 1)
bash $LK disown a1 burn >/dev/null; rc=$?; ok "burn cannot disown main's arm (rc=$rc)" $([ $rc = 9 ] && [ -f $W/arms/a1/.owner ] && echo 0 || echo 1)
bash $LK own a1 main >/dev/null; rc=$?; ok "main renews ownership (rc=$rc)" $([ $rc = 0 ] && echo 0 || echo 1)
bash $LK disown a1 main >/dev/null; rc=$?; ok "main disowns (rc=$rc)" $([ $rc = 0 ] && [ ! -e $W/arms/a1/.owner ] && echo 0 || echo 1)
BOAR_SESSION_PID=$DEAD bash $LK own a2 main >/dev/null; bash $LK own a2 burn >/dev/null; rc=$?; ok "an owner with a dead pid can be taken over (rc=$rc): $(cat $W/arms/a2/.owner | cut -c1-40)" $([ $rc = 0 ] && grep -q 'session=burn' $W/arms/a2/.owner && echo 0 || echo 1)
bash $LK own nonexistent main >/dev/null 2>&1; rc=$?; ok "own of an unknown arm -> rc 2 ($rc)" $([ $rc = 2 ] && echo 0 || echo 1)
rm -f $W/arms/a2/.owner
b0=$(LOCK_ROOT=$W/empty STATE_NO_SSH=1 STATE_MAC_QUEUE=$W/noq bash $TOOLS/state.sh 2>/dev/null | sed -n 's/.*locks=\([0-9]*\).*/\1/p'); b1=$(STATE_NO_SSH=1 STATE_MAC_QUEUE=$W/noq bash $TOOLS/state.sh 2>/dev/null | sed -n 's/.*locks=\([0-9]*\).*/\1/p')
f=$(ls $LOCK_ROOT/*.lock | wc -l | tr -d ' '); ok "STATE locks= counts the lane locks (+$((b1-b0)) vs +$f lock files)" $([ $((b1-b0)) = "$f" ] && [ "$f" -gt 0 ] && echo 0 || echo 1)

echo "T-G5 arm.sh judge / l1 refuse while another session holds the judge lane"
S5=$W/s5; mkdir -p $S5/out $S5/agg $S5/bench $S5/ctl; for i in q01 q02 q03; do echo $i; done > $S5/ids
for i in q01 q02 q03; do echo "{\"itemId\":\"$i\",\"route\":{\"reasonCodes\":[\"generate:x\"]},\"timing\":{\"totalMs\":1000},\"events\":[],\"answer\":{\"text\":\"a\"}}"; done > $S5/out/p-s42.traces.jsonl
cp $S5/out/p-s42.traces.jsonl $S5/out/rA.traces.jsonl; cp $S5/out/p-s42.traces.jsonl $S5/ctl/c-s42.traces.jsonl
cat > $S5/arm.conf <<CONF
ARM=t; LABEL=P; TREE=t; REMOTE_RUNNER=t-remote-run.sh; REMOTE_ARM=D; SETTINGS='{}'; RUN_PREFIX=p
SET=t; BENCH=$S5/bench; QUESTIONS=-; JUDGED_IDS=$S5/ids; OUT_DIR=$S5/out; AGG_DIR=$S5/agg; JUDGE_SYSTEM=t-P; CONTROLS=("C|$S5/ctl|c-s{seed}")
CONF
M5=$W/mark5; export STUB_MARK=$M5 JUDGE_CMD=$TD/stub-judge.sh BOAR_EVAL_DIR=$S5 REPLAY=1; unset BOAR_SESSION; rm -f $M5
export LOCK_ROOT=$W/lk5; mkdir -p $LOCK_ROOT; bash $LK take judge burn --until "2099-01-01 00:00" >/dev/null
$LIB/arm.sh $S5/arm.conf judge 42 > $S5/a.out 2>&1; rc=$?
ok "judge while burn holds the lane: rc=$rc, line: $(grep ABORT $S5/a.out)" $([ $rc = 9 ] && [ "$(grep -c '^ABORT judge:' $S5/a.out)" = 1 ] && grep -qx 'ABORT judge: judge lane locked by burn until 2099-01-01 00:00 (lock.sh)' $S5/a.out && echo 0 || echo 1)
ok "0 stub judges ran" $([ ! -e $M5 ] && [ ! -e $S5/out/p-s42.judgments.jsonl ] && echo 0 || echo 1)
$LIB/arm.sh $S5/arm.conf l1 rA $S5/ids t5 > $S5/b.out 2>&1; rc=$?
ok "l1 while burn holds the lane: rc=$rc, ABORT line printed, 0 stub judges" $([ $rc = 9 ] && grep -qx 'ABORT judge: judge lane locked by burn until 2099-01-01 00:00 (lock.sh)' $S5/b.out && [ ! -e $M5 ] && echo 0 || echo 1)
BOAR_SESSION=burn $LIB/arm.sh $S5/arm.conf judge 42 > $S5/c.out 2>&1; rc=$?
ok "the holder itself (BOAR_SESSION=burn) is not blocked (rc=$rc, stub runs: $(wc -l < $M5 2>/dev/null | tr -d ' '))" $([ -e $M5 ] && ! grep -q 'judge lane locked' $S5/c.out && echo 0 || echo 1)
bash $LK release judge burn >/dev/null; rm -f $M5 $S5/out/p-s42.judgments.jsonl; rm -rf $S5/out/p-s42.judgments.shards
$LIB/arm.sh $S5/arm.conf judge 42 > $S5/d.out 2>&1; rc=$?
ok "after release the path is unchanged (rc=$rc, no ABORT lock line, stub ran)" $([ -e $M5 ] && ! grep -q 'judge lane locked' $S5/d.out && echo 0 || echo 1)
bash $LK take judge burn --until "2000-01-01 00:00" >/dev/null 2>&1; NOW="2026-10-15 20:00" bash $LK take judge burn --until "2026-10-15 20:01" >/dev/null; rm -f $M5 $S5/out/p-s42.judgments.jsonl; rm -rf $S5/out/p-s42.judgments.shards
NOW="2026-10-15 22:00" $LIB/arm.sh $S5/arm.conf judge 42 > $S5/e.out 2>&1
ok "an expired burn lock does not block (stub ran)" $([ -e $M5 ] && ! grep -q 'judge lane locked' $S5/e.out && echo 0 || echo 1)
unset STUB_MARK JUDGE_CMD BOAR_EVAL_DIR REPLAY

echo "T-G6 session-start.sh"
export LOCK_ROOT=$W/lk6 ARMS_ROOT=$W/arms6; mkdir -p $LOCK_ROOT $ARMS_ROOT/a1 $W/sched/daily-digest $W/sched/boar-team-hourly
bash -c 'sleep 60; :' live-session-$$ & BG=$!
printf 'id=c-live session=live-session-%s created=2026-10-15 18:00 purpose=tick\nid=c-dead session=dead-session-0000000-zz created=2026-10-14 09:00 purpose=old loop\n' $$ > $W/cron-registry.txt
printf '2026-10-15 19:40 T3 main PASS arm1: did a thing | mini=idle mac=idle | H/O=+1/+0 | next=x\n' > $W/loop.md
NOW="2026-10-15 19:00" bash $LK take judge burn --until "2026-10-15 19:30" >/dev/null
echo "pid=$DEAD" > /dev/null; BOAR_SESSION_PID=$DEAD bash $LK own a1 burn >/dev/null
printf '#!/bin/bash\nexit 0\n' > $W/claude-ok; printf '#!/bin/bash\nexit 1\n' > $W/claude-bad; chmod +x $W/claude-ok $W/claude-bad
export SCHEDULED_DIR=$W/sched CRON_REGISTRY=$W/cron-registry.txt LOOP_LOG=$W/loop.md NOW="2026-10-15 20:00"
CLAUDE_BIN=$W/claude-ok bash $SS > $W/ss.out 2>&1; rc=$?; n=$(wc -l < $W/ss.out | tr -d ' ')
ok "auth stub exits 0 -> 'auth: OK', rc=$rc, $n lines (<= 12)" $([ $rc = 0 ] && grep -q '^auth: OK (' $W/ss.out && [ "$n" -le 12 ] && echo 0 || echo 1)
ok "cron audit: 2 registered, 1 stale (the dead session) + reminder" $(grep -qx 'cron: 2 registered, 1 stale (c-dead)' $W/ss.out && grep -q 'CronList and delete the stale ids' $W/ss.out && echo 0 || echo 1)
ok "scheduled-task names listed" $(grep -q '^sched: boar-team-hourly,daily-digest' $W/ss.out && echo 0 || echo 1)
ok "expired lock listed (EXPIRED)" $(grep -q '^lock: judge burn until 2026-10-15 19:30 EXPIRED$' $W/ss.out && echo 0 || echo 1)
ok "owner with a dead pid listed (STALE)" $(grep -q '^owner: a1 STALE' $W/ss.out && echo 0 || echo 1)
ok "last LOOP-LOG line and age (20 min)" $(grep -q '^loop-log: 20 min ago: 2026-10-15 19:40 T3 main PASS arm1' $W/ss.out && echo 0 || echo 1)
CLAUDE_BIN=$W/claude-bad bash $SS > $W/ss2.out 2>&1; rc=$?
ok "auth stub exits 1 -> 'auth: FAIL rc=1', rc 3 (rc=$rc)" $([ $rc = 3 ] && grep -qx 'auth: FAIL rc=1' $W/ss2.out && echo 0 || echo 1)
printf '#!/bin/bash\nsleep 20\n' > $W/claude-hang; chmod +x $W/claude-hang; s=$(date +%s); CANARY_TIMEOUT=2 CLAUDE_BIN=$W/claude-hang bash $SS > $W/ss3.out 2>&1; rc=$?; d=$(( $(date +%s) - s ))
ok "a hanging claude is cut by the timeout (rc=$rc after $d s)" $([ $rc = 3 ] && [ $d -lt 10 ] && grep -q '^auth: FAIL' $W/ss3.out && echo 0 || echo 1)
CRON_REGISTRY=$W/none LOCK_ROOT=$W/lkempty LOOP_LOG=$W/none CLAUDE_BIN=$W/claude-ok bash $SS > $W/ss4.out 2>&1; rc=$?
ok "empty registry / locks / log: 'cron: 0 registered', 'lock: locks: 0', no crash (rc=$rc)" $([ $rc = 0 ] && grep -qx 'cron: 0 registered, 0 stale (none)' $W/ss4.out && grep -qx 'lock: locks: 0' $W/ss4.out && grep -qx 'loop-log: no lines' $W/ss4.out && echo 0 || echo 1)

echo; echo "guard-tests: $PASS pass, $FAIL fail"; [ $FAIL = 0 ]
