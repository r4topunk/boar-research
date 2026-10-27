#!/bin/bash
# Offline tests for tools/loglog.sh + tools/qrow.sh (LOOP v2 T4). 0 LLM calls, mktemp dirs, never reads blind/.
# Run: bash rnd/research/coordinator/arms/_lib/tests/log-tests.sh   (exit 0 = all pass, < 10 s)
set -u
TD=$(cd "$(dirname "$0")" && pwd); TOOLS=$(cd "$TD/../../../tools" && pwd); L=$TOOLS/loglog.sh; Q=$TOOLS/qrow.sh
REALQ=$(cd "$TD/../../../.." && pwd)/QUEUE.md
PASS=0; FAIL=0; ok() { if [ "$2" = 0 ]; then PASS=$((PASS+1)); echo "  [pass] $1"; else FAIL=$((FAIL+1)); echo "  [FAIL] $1"; fi; }
W=$(mktemp -d "${TMPDIR:-/tmp}/logtest.XXXXXX"); export LOOP_LOG=$W/log.md QUEUE_MD=$W/q.md NOW="2026-10-15 21:05"
printf '# header\n' > $LOOP_LOG; printf -- '- **[main] OLD row (10:00):** an earlier row that is fine.\n' > $QUEUE_MD
RE='^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2} T[0-9]+ (main|burn) (PASS|FAIL|IDLE|META) [A-Za-z0-9_.-]+: [^|`]+ \| mini=[^|`]+ mac=[^|`]+ \| H/O=\+[0-9]+/\+[0-9]+ \| next=[^|`]+$'
ll() { bash $L "$@" 2>$W/err; }
good=(T4 main PASS bonsai2 "S0 measured, gate passed" "S1@21:30" idle "+2/+0" "bonsai2 S1@21:30")

echo "loglog"
before=$(wc -l < $LOOP_LOG); out=$(ll "${good[@]}"); rc=$?; after=$(wc -l < $LOOP_LOG)
r=1; [ $rc = 0 ] && [ $((after-before)) = 1 ] && [[ $(tail -1 $LOOP_LOG) =~ $RE ]] && [ "$out" = "$(tail -1 $LOOP_LOG)" ] && r=0
ok "valid line appends exactly one line and matches the D6 regex" $r
refuse_case() { # name expected-substr args...
  local n=$1 s=$2; shift 2; local sz; sz=$(wc -c < $LOOP_LOG); ll "$@" >/dev/null; local rc=$?
  r=1; [ $rc = 2 ] && grep -q "^REFUSED:.*$s" $W/err && [ "$(wc -c < $LOOP_LOG)" = "$sz" ] && r=0; ok "$n -> refused rc 2, file unchanged" $r; }
refuse_case "backtick in summary" backtick T4 main PASS arm 'has `code` inside' a b +1/+0 n@1
refuse_case "8 args (truncated)" "9 args" T4 main PASS arm "sum" a b +1/+0
refuse_case "30-word summary" words T4 main PASS arm "$(printf 'w%s ' $(seq 1 30) | sed 's/ $//')" a b +1/+0 n@1
refuse_case "pipe inside arm" "'|'" T4 main PASS "a|b" "sum" a b +1/+0 n@1
refuse_case "empty arg" empty T4 main PASS arm "sum" "" b +1/+0 n@1
refuse_case "bad status" status T4 main WIN arm "sum" a b +1/+0 n@1
refuse_case "bad H/O" "H/O" T4 main PASS arm "sum" a b 3 n@1
refuse_case "trailing space" space T4 main PASS arm "sum " a b +1/+0 n@1
refuse_case "newline in summary" newline T4 main PASS arm "a
b" a b +1/+0 n@1

echo "qrow"
body="Measured the 9B PTQ1_0 on the mini; result logged in arms/bonsai2/S0.md (3 of 5 items)."
sz=$(wc -c < $QUEUE_MD); out=$(NOW=21:07 bash $Q burn "BONSAI2 S0 done" "$body" 2>$W/err); rc=$?
exp=$(printf '%s' "$out" | wc -c | tr -d ' ')
r=1; [ $rc = 0 ] && [ $(( $(wc -c < $QUEUE_MD) )) = $((sz+exp+1)) ] && [ "$out" = "$(tail -1 $QUEUE_MD)" ] && [ "$out" = "- **[burn] BONSAI2 S0 done (21:07):** $body" ] && r=0
ok "valid qrow appends one line (bytes = prev + len(row) + 1)" $r
qr() { local n=$1 s=$2; shift 2; local sz; sz=$(wc -c < $QUEUE_MD); bash $Q "$@" >/dev/null 2>$W/err; local rc=$?
  r=1; [ $rc = 2 ] && grep -q "^REFUSED:.*$s" $W/err && [ "$(wc -c < $QUEUE_MD)" = "$sz" ] && r=0; ok "$n -> refused rc 2, file unchanged" $r; }
qr "body with a newline" newline main "Title ok" "first line of the row.
second line of the row."
qr "body with triple backtick" backtick main "Title ok" 'see ```code``` block here, long enough.'
qr "body with a single backtick" backtick main "Title ok" 'ran the script `qrow.sh` on the mini, long enough.'
qr "title with a backtick" backtick main 'Title `x` ok' "$body"
qr "body with <system-reminder>" artefact main "Title ok" "text <system-reminder> pasted in here, long enough."
qr "body ending mid-sentence" punctuation main "Title ok" "the arm finished and we moved on to the next"
qr "unbalanced **" "unbalanced" main "Title ok" "this has **bold open but never closed ok."
qr "bad tag" tag foo "Title ok" "$body"
qr "title with **" "title" main "Bad **title" "$body"
qr "short body" short main "Title ok" "too short."
printf -- '- **[main] legacy backticks (10:00):** quotes `path/to/x.sh` fine.\n' > $W/c1.md
bash $Q --check $W/c1.md >/dev/null 2>&1; ok "--check valid last row (legacy row with backticks: --check does not refuse them) -> rc 0" $?
printf -- '- **[main] ok (10:00):** fine row ends here.\n- **[main] cut off (10:01):** a body that stops in the middle of the' > $W/c2.md
bash $Q --check $W/c2.md >/dev/null 2>&1; rc=$?; r=1; [ $rc = 2 ] && r=0; ok "--check truncated last row -> rc 2" $r
printf -- '- **[main] cut off (10:01):** a body that stops in the middle of the next\n' > $W/c3.md
bash $Q --check $W/c3.md >/dev/null 2>&1; rc=$?; r=1; [ $rc = 2 ] && r=0; ok "--check last row without final punctuation -> rc 2" $r

echo "info: --check on the real QUEUE.md"
bash $Q --check "$REALQ"; echo "  real QUEUE.md --check rc=$?"
rm -rf $W
echo "pass=$PASS fail=$FAIL"; [ $FAIL = 0 ]
