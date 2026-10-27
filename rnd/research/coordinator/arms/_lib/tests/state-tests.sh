#!/bin/bash
# Offline tests for tools/state.sh (LOOP v2 T2): 5 fixture states (byte-for-byte) + 1 live call. 0 LLM calls, never reads blind/.
# Run: bash rnd/research/coordinator/arms/_lib/tests/state-tests.sh   (exit 0 = all pass, a few seconds)
set -u
TD=$(cd "$(dirname "$0")" && pwd); S=$(cd "$TD/../../../tools" && pwd)/state.sh; FX=$TD/fixtures/state
PASS=0; FAIL=0; ok() { if [ "$2" = 0 ]; then PASS=$((PASS+1)); echo "  [pass] $1"; else FAIL=$((FAIL+1)); echo "  [FAIL] $1"; fi; }
for c in idle running overdue-heartbeat fail-disk auth-stale-unreachable; do
  got=$(TZ=UTC bash "$S" --fixture "$FX/$c" 2>&1); rc=$?
  r=0; [ $rc = 0 ] && [ "$got" = "$(cat "$FX/$c/expected.txt")" ] && [ ${#got} -le 300 ] || r=1
  ok "state fixture $c (rc=$rc, ${#got} chars)" $r; [ $r = 1 ] && echo "    got:      $got" && echo "    expected: $(cat "$FX/$c/expected.txt")"
done
AC=$(cd "$TD/../../../tools" && pwd)/auth-canary.sh
echo "auth canary parser"
cp_() { printf '%s\n' "$2" | bash "$AC" parse "$3"; }
for case_ in "alive|ok|0" "alive|Error: Exceeded USD budget (0.05)|1" "dead|Failed to authenticate. API Error: 401 authentication_error|1" "timeout||124"; do
  IFS='|' read -r want txt rc <<<"$case_"; got=$(cp_ x "$txt" "$rc"); r=0; [ "$got" = "$want" ] || r=1; ok "canary parse rc=$rc '$txt' -> $got (expect $want)" $r; done
CF=$(mktemp -d "${TMPDIR:-/tmp}/canfx.XXXXXX"); cp -R "$FX/idle/." "$CF/"; echo 0 > "$CF/canary.rc"
echo "Failed to authenticate. API Error: 401" > "$CF/canary.txt"; got=$(STATE_AUTH_CANARY=1 TZ=UTC bash "$S" --fixture "$CF" 2>&1); r=1; case "$got" in *AUTH-DEAD*) r=0;; esac; ok "state with canary dead -> AUTH-DEAD" $r
echo ok > "$CF/canary.txt"; got=$(STATE_AUTH_CANARY=1 TZ=UTC bash "$S" --fixture "$CF" 2>&1); r=1; case "$got" in *AUTH-*) ;; *) r=0;; esac; ok "state with canary alive -> no AUTH flag" $r
echo 124 > "$CF/canary.rc"; : > "$CF/canary.txt"; got=$(STATE_AUTH_CANARY=1 TZ=UTC bash "$S" --fixture "$CF" 2>&1); r=1; case "$got" in *AUTH-TIMEOUT*) r=0;; esac; ok "state with canary timeout -> AUTH-TIMEOUT" $r
rm -rf "$CF"
echo "live call (real ssh)"
t0=$(date +%s); out=$(bash "$S" 2>&1); rc=$?; el=$(( $(date +%s) - t0 ))
if echo "$out" | grep -q 'mini=UNREACHABLE' && [ $el -lt 5 ]; then echo "  [skip] live: ssh failed in ${el}s: $out"
else r=0; [ $rc = 0 ] && [ ${#out} -le 300 ] && [ "$(echo "$out" | wc -l | tr -d ' ')" = 1 ] && [ $el -lt 10 ] || r=1
  ok "state live rc=$rc ${#out} chars ${el}s" $r; echo "    $out"; fi
echo "state-tests: $PASS passed, $FAIL failed"; [ $FAIL = 0 ]
