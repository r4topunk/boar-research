#!/bin/bash
# DT512 stage 3: wait for the DEEPTHINK-V02 s43 generation to free the mini, then H full s42 → Haiku L1 (51) → on continue: Opus s42, H s43, Opus s43, two-seed scales. Progress/aggregates only.
set -u; TO=$(cd "$(dirname "$0")" && pwd); AG=$TO/../aggregates; B=<private held-out dir>; IDS=$B/runs-cut6/judged.ids; S43=<scratch>
wait_run() { local run=$1 t0=$(date +%s); while true; do
  st=$(<on the mini> "grep -c DONE <runner>/kiln/be-0cfd4a77-dt512/be-repo/runs/$run/STATUS 2>/dev/null; grep -cE ' (success|error|declined|fail)' <runner>/kiln/be-0cfd4a77-dt512/be-repo/runs/$run/run.log 2>/dev/null; grep -c FAIL <runner>/kiln/be-0cfd4a77-dt512/be-repo/runs/$run/STATUS 2>/dev/null" | tr '\n' ' '); set -- $st
  echo "$(date +%H:%M) $run done=${1:-0} progress=${2:-0} fail=${3:-0} elapsed=$(( ($(date +%s)-t0)/60 ))m"
  [ "${3:-0}" != 0 ] && { echo "RUNNER-FAIL $run"; return 3; }
  [ "${1:-0}" = 1 ] && return 0
  [ $(( $(date +%s) - t0 )) -ge 9000 ] && { echo "HARDSTOP $run"; return 3; }
  sleep 300; done; }
# wait until the v0.2 s43 generation is done (its chain prints "s43 done=1") or the chain ended, and no MoE server runs
while ! grep -qE "s43 done=1|S43-DONE|RUNNER-FAIL|HARDSTOP" $S43 2>/dev/null; do sleep 300; done
while <on the mini> 'pgrep -f "llama-server.*Qwen3.6-35B" >/dev/null'; do sleep 60; done; echo "$(date +%H:%M) mini free"
$TO/dh.sh launch $B/runs-dt512/dh-H-vpara-s42.requests.jsonl dh-H-vpara-s42 H && wait_run dh-H-vpara-s42 || exit 3
$TO/l1.sh dh-H-vpara-s42 $IDS full-s42 2>&1 | grep -v " boar" | tail -3
grep -q "CONTINUE" $AG/L1-rule-full-s42.txt || { echo "STAGE3-NO"; exit 0; }
$TO/l2.sh judge 42 2>&1 | tail -4
$TO/dh.sh launch $B/runs-dt512/dh-H-vpara-s43.requests.jsonl dh-H-vpara-s43 H && wait_run dh-H-vpara-s43 || exit 3
SKIPJUDGE=1 $TO/l1.sh dh-H-vpara-s43 $IDS full-s43 2>&1 | tail -1
$TO/l2.sh judge 43 2>&1 | tail -4
$TO/l2.sh scales "42 43" 2>&1 | grep -v "^{\"comparison" | head -12
echo FULL-DONE
