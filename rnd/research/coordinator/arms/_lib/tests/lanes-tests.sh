#!/bin/bash
# Offline tests for tools/lanes-report.py, daybrief.sh, watchdog.sh, com.boar.watchdog.plist (LOOP v2 T7).
# 0 LLM calls, never reads blind/ or rnd/veil/, claude and discord are STUBS (no real `claude -p`, no real `discord send`).
# Run: bash rnd/research/coordinator/arms/_lib/tests/lanes-tests.sh   (exit 0 = all pass, < 30 s)
set -u
TD=$(cd "$(dirname "$0")" && pwd); TOOLS=$(cd "$TD/../../../tools" && pwd); FX=$TD/fixtures/lanes
LR=$TOOLS/lanes-report.py; DB=$TOOLS/daybrief.sh; WD=$TOOLS/watchdog.sh; PL=$TOOLS/com.boar.watchdog.plist; BF=$TOOLS/lanes-backfill-2026-10-11.tsv
PASS=0; FAIL=0; ok() { if [ "$2" = 0 ]; then PASS=$((PASS+1)); echo "  [pass] $1"; else FAIL=$((FAIL+1)); echo "  [FAIL] $1"; fi; }
W=$(mktemp -d "${TMPDIR:-/tmp}/lanestest.XXXXXX"); trap 'rm -rf "$W"' EXIT
unset WATCHDOG_DISCORD_TARGET DAYBRIEF_LINK LOOP_LOG NOW BACKLOG DECISIONS_FILE
lr() { python3 -I "$LR" "$@"; }
jget() { python3 -I -c 'import json,sys; d=json.load(sys.stdin); print(eval(sys.argv[1]))' "$1"; }

echo "T-L1 backfill reproduction (retro baseline: both-idle 25.6 h, overlap 11.8 h, 9 episodes)"
J=$(lr --log /dev/null --backfill "$BF" --from "2026-10-11 09:00" --to "2026-10-14 19:30" --json)
IDLE=$(echo "$J" | jget 'd["total"]["both_idle"]'); OV=$(echo "$J" | jget 'd["total"]["overlap"]'); EP=$(echo "$J" | jget 'd["total"]["episodes"]')
AV=$(echo "$J" | jget 'd["total"]["avail"]'); ND=$(echo "$J" | jget 'len(d["days"])')
r=1; python3 -I -c "import sys; sys.exit(0 if 23.0<=$IDLE<=28.2 else 1)" && r=0; ok "both-idle $IDLE h within 23.0-28.2 (baseline 25.6)" $r
r=1; python3 -I -c "import sys; sys.exit(0 if 10.6<=$OV<=13.0 else 1)" && r=0; ok "overlap $OV h within 10.6-13.0 (baseline 11.8)" $r
r=1; [ "$EP" -ge 8 ] && [ "$EP" -le 10 ] && r=0; ok "episodes $EP within 8-10 (baseline 9)" $r
r=1; [ "$AV" = "55.5" ] && [ "$ND" = 4 ]; [ $? = 0 ] && r=0; ok "window = 55.5 h over 4 days (avail $AV, days $ND)" $r
TXT=$(lr --log /dev/null --backfill "$BF" --from "2026-10-11 09:00" --to "2026-10-14 19:30")
r=1; echo "$TXT" | grep -Eq '^DAY 2026-10-13 \| mini [0-9.]+/15\.0 h busy \| mac [0-9.]+/15\.0 h \| both-idle [0-9.]+ h \| overlap [0-9.]+ h in [0-9]+ episodes$' && echo "$TXT" | tail -1 | grep -q '^TOTAL | ' && r=0; ok "text format: DAY lines + TOTAL line" $r
DI13=$(echo "$J" | jget '[x for x in d["days"] if x["day"]=="2026-10-13"][0]["both_idle"]')
r=1; python3 -I -c "import sys; sys.exit(0 if 1.5<=$DI13<=3.0 else 1)" && r=0; ok "10-13 (retro best day 2.2 h): both-idle $DI13 h" $r
# every data row: 5 columns, start < end, a traceable source, exactly 4 `est` rows
BAD=$(python3 -I - "$BF" <<'PY'
import sys, re
n = est = bad = 0
for l in open(sys.argv[1]):
    l = l.rstrip("\n")
    if not l.strip() or l.startswith("#") or l.startswith("machine\t"):
        continue
    c = l.split("\t"); n += 1
    if len(c) != 5 or c[0] not in ("mini", "mac") or not c[1] < c[2] or not re.search(r"QUEUE\.md:\d|status:|retro:mine_resources arms\[\d+\]", c[4]):
        bad += 1
    if re.search(r"\best\b", c[4]): est += 1
print(bad, est, n)
PY
)
set -- $BAD
r=1; [ "$1" = 0 ] && [ "$2" = 4 ] && r=0; ok "TSV: $3 rows, all traceable (QUEUE line / status / retro index), est rows = $2 (4 expected), malformed = $1" $r

echo "T-L2 D6 parsing (hand-computed: mini 10:30-12:30 = 2.0 h, mac 11:30-13:00 = 1.5 h, union 10:30-13:00 = 2.5 h -> both-idle 15-2.5 = 12.5 h, overlap 11:30-12:30 = 1.0 h in 1 episode; last tick 14:00 idle)"
J=$(lr --log "$FX/loop-log-d6.md" --from "2026-10-16 09:00" --to "2026-10-17 00:00" --json); rc=$?
ok "mixed old-prose + D6 file parses without error (rc $rc)" $([ $rc = 0 ] && echo 0 || echo 1)
for kv in 'mini_busy=2.0' 'mac_busy=1.5' 'both_idle=12.5' 'overlap=1.0' 'episodes=1' 'avail=15.0'; do
  k=${kv%%=*}; v=${kv#*=}; got=$(echo "$J" | jget "d['total']['$k']"); ok "total $k = $v (got $got)" $([ "$got" = "$v" ] && echo 0 || echo 1)
done
ok "one day row, same numbers as total" $([ "$(echo "$J" | jget 'len(d["days"])')" = 1 ] && [ "$(echo "$J" | jget 'd["days"][0]["both_idle"]')" = 12.5 ] && echo 0 || echo 1)
# last tick cap: a single busy tick lasts 90 min
printf '2026-10-16 10:00 T1 main PASS a: x | mini=job mac=idle | H/O=+0/+0 | next=n\n' > $W/one.md
got=$(lr --log $W/one.md --from "2026-10-16 09:00" --to "2026-10-17 00:00" --json | jget 'd["total"]["mini_busy"]'); ok "last tick capped at 90 min (mini_busy $got = 1.5)" $([ "$got" = 1.5 ] && echo 0 || echo 1)
# episodes: overlaps < 5 min apart are one episode, a larger gap splits
printf 'mini\t2026-10-16 10:00\t2026-10-16 11:00\ta\ttest\nmac\t2026-10-16 10:00\t2026-10-16 10:20\ta\ttest\nmac\t2026-10-16 10:23\t2026-10-16 10:40\ta\ttest\nmac\t2026-10-16 10:50\t2026-10-16 11:00\ta\ttest\n' > $W/ep.tsv
got=$(lr --log /dev/null --backfill $W/ep.tsv --from "2026-10-16 09:00" --to "2026-10-17 00:00" --json | jget '(d["total"]["episodes"], d["total"]["overlap"])')
ok "3-min gap merges, 10-min gap splits: (episodes, overlap) = $got = (2, 0.78)" $([ "$got" = "(2, 0.78)" ] && echo 0 || echo 1)
# window argument
got=$(lr --log "$FX/loop-log-d6.md" --from "2026-10-16 11:00" --to "2026-10-16 13:00" --window 11:00-13:00 --json | jget 'd["total"]["avail"]'); ok "--window/--from/--to clip the available hours (avail $got = 2.0)" $([ "$got" = 2.0 ] && echo 0 || echo 1)

echo "T-L3 daybrief (fixture: 4 ticks in the last 24 h, armA PASS x2, armB FAIL, META)"
cat > $W/discord-stub.sh <<'S'
#!/bin/bash
echo "$#" >> "$STUB_CALLS"; printf '%s\n' "$1" > "$STUB_ARGS.1"; printf '%s\n' "$2" > "$STUB_ARGS.2"; printf '%s\n' "$3" > "$STUB_ARGS.3"; printf '%s' "$4" > "$STUB_ARGS.4"; exit 0
S
chmod +x $W/discord-stub.sh
export STUB_CALLS=$W/discord.calls STUB_ARGS=$W/discord.args
export LOOP_LOG=$FX/daybrief-log.md NOW="2026-10-16 08:00" BACKLOG=$W/nobacklog.md DECISIONS_FILE=$W/nodecisions.md
OUT=$(bash $DB); rc=$?
ok "daybrief rc 0 (rc $rc)" $([ $rc = 0 ] && echo 0 || echo 1)
ok "exactly 4 lines" $([ "$(printf '%s\n' "$OUT" | wc -l | tr -d ' ')" = 4 ] && echo 0 || echo 1)
L1=$(printf '%s\n' "$OUT" | sed -n 1p); L2=$(printf '%s\n' "$OUT" | sed -n 2p); L3=$(printf '%s\n' "$OUT" | sed -n 3p); L4=$(printf '%s\n' "$OUT" | sed -n 4p)
RE='^DAY 2026-10-16 \| mini 1\.0/24\.0 h busy, mac 1\.0/24\.0 h \| both-idle 22\.0 h \| arms moved 2 -> closed 1 \| calls H/O \+6/\+5 \| decisions needed: none$'
ok "line 1 matches the D11 regex (mini 1.0, mac 1.0, idle 22.0, 2 arms -> 1 closed, +6/+5; the 10-14 line is outside 24 h)" $([[ $L1 =~ $RE ]] && echo 0 || echo 1)
ok "line 2 = last META/FAIL summary, <= 25 words ($L2)" $([[ $L2 == "META weekly: planned the week"* ]] && [ "$(echo $L2 | wc -w | tr -d ' ')" -le 27 ] && echo 0 || echo 1)
ok "line 3 = decisions: none (no file, no backlog)" $([ "$L3" = "decisions: none" ] && echo 0 || echo 1)
ok "line 4 = plain path without DAYBRIEF_LINK" $([ "$L4" = "rnd/research/coordinator/LOOP-LOG.md" ] && echo 0 || echo 1)
printf '# decisions\n- [x] done one\n- [ ] pick the 12 GB device test\n- [ ] approve PR-2 text\nnot a checkbox\n' > $W/dec.md
OUT=$(DECISIONS_FILE=$W/dec.md bash $DB); L1=$(printf '%s\n' "$OUT" | sed -n 1p); L3=$(printf '%s\n' "$OUT" | sed -n 3p)
ok "seeded '- [ ]' lines -> line 3 lists both open ones, not the [x]; line 1 says 2" $([[ $L3 == "decisions: pick the 12 GB device test ; approve PR-2 text" ]] && [[ $L1 == *"decisions needed: 2" ]] && echo 0 || echo 1)
printf '# B\n## 0. Budget\n- [ ] from backlog zero\n## 1. Ranked\n- [ ] not in section zero\n' > $W/bl.md
L3=$(BACKLOG=$W/bl.md bash $DB | sed -n 3p); ok "no DECISIONS file: BACKLOG section 0 only ($L3)" $([ "$L3" = "decisions: from backlog zero" ] && echo 0 || echo 1)
rm -f $STUB_CALLS
OUT=$(DAYBRIEF_LINK="https://example.com/brief/1" DISCORD_BIN=$W/discord-stub.sh bash $DB --send CHAN123); rc=$?
ok "--send: stub called exactly once (rc $rc)" $([ "$(wc -l < $STUB_CALLS | tr -d ' ')" = 1 ] && [ $rc = 0 ] && echo 0 || echo 1)
ok "--send argv = send CHAN123 --msg <brief>" $([ "$(cat $STUB_ARGS.1)" = send ] && [ "$(cat $STUB_ARGS.2)" = CHAN123 ] && [ "$(cat $STUB_ARGS.3)" = "--msg" ] && echo 0 || echo 1)
ok "--send message = the 4 printed lines joined by newlines" $([ "$(cat $STUB_ARGS.4)" = "$OUT" ] && [ "$(printf '%s' "$OUT" | wc -l | tr -d ' ')" = 3 ] && echo 0 || echo 1)
ok "link wrapped in <...> when DAYBRIEF_LINK is a URL" $([ "$(printf '%s\n' "$OUT" | sed -n 4p)" = "<https://example.com/brief/1>" ] && echo 0 || echo 1)
rm -f $STUB_CALLS; bash $DB >/dev/null; ok "no --send: stub never called, nothing posted" $([ ! -f $STUB_CALLS ] && echo 0 || echo 1)
unset LOOP_LOG NOW BACKLOG DECISIONS_FILE

echo "T-L4 watchdog (stub claude + stub discord, state dir per case)"
cat > $W/claude-stub.sh <<'S'
#!/bin/bash
echo "$*" >> "$CLAUDE_CALLS"; exit "${CLAUDE_RC:-0}"
S
cat > $W/claude-hang.sh <<'S'
#!/bin/bash
echo "$*" >> "$CLAUDE_CALLS"; exec sleep 8
S
chmod +x $W/claude-stub.sh $W/claude-hang.sh
export CLAUDE_CALLS=$W/claude.calls DISCORD_BIN=$W/discord-stub.sh CLAUDE_BIN=$W/claude-stub.sh
WL=$W/wd-log.md; printf '# fixture\n2026-10-16 09:30 T1 main PASS old: x | mini=idle mac=idle | H/O=+0/+0 | next=n\n2026-10-16 10:00 T9 main PASS loopv2: done | mini=job mac=idle | H/O=+0/+0 | next=n\n' > $WL
export LOOP_LOG=$WL
newcase() { rm -rf $W/q $W/a $W/st; mkdir -p $W/q $W/a $W/st; rm -f $STUB_CALLS $CLAUDE_CALLS; export QUEUE_DIR=$W/q ARMS_DIR=$W/a WATCHDOG_STATE=$W/st WATCHDOG_DISCORD_TARGET=CHAN123; unset CLAUDE_RC; }
wd() { NOW="$1" bash $WD; }
calls() { [ -f "$1" ] && wc -l < "$1" | tr -d ' ' || echo 0; }
# fresh log, no queue: canary only on run 6
newcase; outs=""; for i in 1 2 3 4 5; do outs="$outs$(wd '2026-10-16 10:20')
"; done
ok "fresh log + no queue, runs 1-5: alert=none, canary=skip, claude never called" $([ "$(printf '%s' "$outs" | grep -c 'canary=skip alert=none')" = 5 ] && [ "$(calls $CLAUDE_CALLS)" = 0 ] && echo 0 || echo 1)
o6=$(wd '2026-10-16 10:20')
ok "run 6: canary=OK ($o6)" $([[ $o6 == *"canary=OK alert=none"* ]] && [ "$(calls $CLAUDE_CALLS)" = 1 ] && echo 0 || echo 1)
ok "canary invoked as -p ok --max-budget-usd 0.05" $([ "$(head -1 $CLAUDE_CALLS)" = "-p ok --max-budget-usd 0.05" ] && echo 0 || echo 1)
ok "log line format" $([[ $o6 =~ ^2026-10-16\ 10:20\ watchdog\ stale=20\ queued=0\ canary=OK\ alert=none$ ]] && echo 0 || echo 1)
ok "no discord call while healthy" $([ ! -f $STUB_CALLS ] && echo 0 || echo 1)
# stale + one RUNNING step
newcase; printf 's\n' > $W/q/a.step; printf 'STATUS RUNNING 40 300\n' > $W/q/a.status
o1=$(wd '2026-10-16 11:30')
ok "stale 90 min + 1 queued: alert=sent:STALE, canary run immediately ($o1)" $([[ $o1 == *"stale=90 queued=1 canary=OK alert=sent:STALE"* ]] && echo 0 || echo 1)
MSG=$(cat $STUB_ARGS.4)
ok "discord called once with 'stale' and '1 queued' ($MSG)" $([ "$(calls $STUB_CALLS)" = 1 ] && [[ $MSG == *stale* ]] && [[ $MSG == *"1 queued"* ]] && echo 0 || echo 1)
ok "message <= 200 chars, names the last tick and the log path" $([ "${#MSG}" -le 200 ] && [[ $MSG == *"10:00 T9 main PASS loopv2"* ]] && [[ $MSG == *"LOOP-LOG.md" ]] && echo 0 || echo 1)
o2=$(wd '2026-10-16 11:40')
ok "second run: alert=suppressed, no new discord call" $([[ $o2 == *"alert=suppressed"* ]] && [ "$(calls $STUB_CALLS)" = 1 ] && echo 0 || echo 1)
o3=$(wd '2026-10-16 16:30')
ok "NOW +300 min: sent again (2 calls)" $([[ $o3 == *"alert=sent:STALE"* ]] && [ "$(calls $STUB_CALLS)" = 2 ] && echo 0 || echo 1)
printf 'STATUS RUNNING 40 300\nDONE\n' > $W/q/a.status
o4=$(wd '2026-10-16 16:40')
ok "queued work finished: condition clears (alert=none, state file removed)" $([[ $o4 == *"queued=0"*"alert=none"* ]] && [ ! -f $W/st/alerted.STALE ] && echo 0 || echo 1)
# a queued .step without a .status counts; arms/*/runs/*.status RUNNING counts; DONE does not
newcase; rm -f $W/q/*; printf 's\n' > $W/q/p.step; mkdir -p $W/a/x/runs; printf 'start 1 t\nSTATUS RUNNING 10 20\n' > $W/a/x/runs/r.status; printf 'start 1 t\nend 2\nDONE\n' > $W/a/x/runs/d.status
o=$(wd '2026-10-16 10:20'); ok "queued counts a pending .step and a RUNNING arm status, not a DONE one (queued=2)" $([[ $o == *"queued=2"* ]] && echo 0 || echo 1)
# stale but nothing queued
newcase; o=$(wd '2026-10-16 11:30')
ok "stale log + no queued work: no alert (stale=90 queued=0), discord not called" $([[ $o == *"stale=90 queued=0"*"alert=none"* ]] && [ ! -f $STUB_CALLS ] && echo 0 || echo 1)
# auth canary failure
newcase; export CLAUDE_RC=1 WATCHDOG_CANARY_EVERY=1
o1=$(wd '2026-10-16 10:20'); o2=$(wd '2026-10-16 10:30')
ok "canary exit 1 -> canary=FAIL, AUTH alert sent once ($o1)" $([[ $o1 == *"canary=FAIL alert=sent:AUTH"* ]] && [[ $(cat $STUB_ARGS.4) == *auth* ]] && echo 0 || echo 1)
ok "AUTH second run suppressed, discord called once" $([[ $o2 == *"canary=FAIL alert=suppressed"* ]] && [ "$(calls $STUB_CALLS)" = 1 ] && echo 0 || echo 1)
unset CLAUDE_RC; o3=$(wd '2026-10-16 10:40')
ok "canary recovers: AUTH state cleared" $([[ $o3 == *"canary=OK alert=none"* ]] && [ ! -f $W/st/alerted.AUTH ] && echo 0 || echo 1)
# canary timeout
newcase; export WATCHDOG_CANARY_EVERY=1 WATCHDOG_CANARY_TIMEOUT=1 CLAUDE_BIN=$W/claude-hang.sh; t0=$(date +%s)
o=$(wd '2026-10-16 10:20'); t1=$(date +%s)
ok "hanging canary killed after the timeout -> FAIL in < 6 s (took $((t1-t0)) s)" $([[ $o == *"canary=FAIL alert=sent:AUTH"* ]] && [ $((t1-t0)) -lt 6 ] && echo 0 || echo 1)
export CLAUDE_BIN=$W/claude-stub.sh; unset WATCHDOG_CANARY_TIMEOUT
# no target: never post
newcase; export WATCHDOG_CANARY_EVERY=6; unset WATCHDOG_DISCORD_TARGET; printf 's\n' > $W/q/a.step
o=$(wd '2026-10-16 11:30')
ok "WATCHDOG_DISCORD_TARGET unset: log says 'alert not sent', discord stub never called" $([[ $o == *"alert not sent"* ]] && [ ! -f $STUB_CALLS ] && [ ! -f $W/st/alerted.STALE ] && echo 0 || echo 1)
# URL link wrapped
newcase; printf 's\n' > $W/q/a.step; DAYBRIEF_LINK="https://example.com/b" wd '2026-10-16 11:30' >/dev/null
ok "DAYBRIEF_LINK URL wrapped in <...> in the alert" $([[ $(cat $STUB_ARGS.4) == *"<https://example.com/b>" ]] && echo 0 || echo 1)
ok "stub discord argv = send <target> --msg" $([ "$(cat $STUB_ARGS.1)" = send ] && [ "$(cat $STUB_ARGS.2)" = CHAN123 ] && [ "$(cat $STUB_ARGS.3)" = "--msg" ] && echo 0 || echo 1)
unset WATCHDOG_CANARY_EVERY LOOP_LOG QUEUE_DIR ARMS_DIR WATCHDOG_STATE WATCHDOG_DISCORD_TARGET

echo "T-L5 launchd plist"
plutil -lint "$PL" >/dev/null 2>&1; ok "plutil -lint OK" $?
ok "Label com.boar.watchdog" $([ "$(plutil -extract Label raw -o - "$PL" 2>/dev/null)" = com.boar.watchdog ] && echo 0 || echo 1)
ok "StartInterval 600" $([ "$(plutil -extract StartInterval raw -o - "$PL" 2>/dev/null)" = 600 ] && echo 0 || echo 1)
ok "ProgramArguments = /bin/bash + absolute watchdog.sh" $([ "$(plutil -extract ProgramArguments.0 raw -o - "$PL" 2>/dev/null)" = /bin/bash ] && [ "$(plutil -extract ProgramArguments.1 raw -o - "$PL" 2>/dev/null)" = "$TOOLS/watchdog.sh" ] && echo 0 || echo 1)
ok "the watchdog.sh named by the plist exists" $([ -f "$(plutil -extract ProgramArguments.1 raw -o - "$PL" 2>/dev/null)" ] && echo 0 || echo 1)
ok "PATH has /opt/homebrew/bin and ~/.local/bin; RunAtLoad true; log in ~/Library/Logs" $([[ $(plutil -extract EnvironmentVariables.PATH raw -o - "$PL") == "/opt/homebrew/bin:<home>/.local/bin:"* ]] && [ "$(plutil -extract RunAtLoad raw -o - "$PL")" = true ] && [[ $(plutil -extract StandardOutPath raw -o - "$PL") == */Library/Logs/boar-watchdog.log ]] && echo 0 || echo 1)

echo "pass=$PASS fail=$FAIL"; [ $FAIL = 0 ]
