#!/bin/bash
# DEEPTHINK-V02 Addendum 1: wait for the DT512 chain to finish (mini free), then TV s43 generation (deepthink tree), Opus N=4, two-seed scales. Progress/aggregates only.
set -u; TO=$(cd "$(dirname "$0")" && pwd); AG=$TO/../aggregates; B=<private held-out dir>; O=$B/runs-deepthinkv02; CH=<scratch>
while ! grep -qE "CHAIN-DONE|RUNNER-FAIL|HARDSTOP|SMOKE FAIL" $CH 2>/dev/null; do sleep 120; done; echo "$(date +%H:%M) DT512 chain ended"
while <on the mini> 'pgrep -f "llama-server.*Qwen3.6-35B" >/dev/null'; do echo "$(date +%H:%M) waiting for the MoE server to exit"; sleep 60; done
$TO/dtv.sh place $O/dtv-TV-v02-s43.requests.jsonl dtv-TV-v02-s43 && TREE=deepthink $TO/dtv.sh launch dtv-TV-v02-s43 || exit 3
t0=$(date +%s); while true; do st=$(<on the mini> "grep -c DONE <runner>/kiln/be-0cfd4a77-deepthink/be-repo/runs/dtv-TV-v02-s43/STATUS 2>/dev/null; grep -cE ' (success|error|declined|fail)' <runner>/kiln/be-0cfd4a77-deepthink/be-repo/runs/dtv-TV-v02-s43/run.log 2>/dev/null; grep -c FAIL <runner>/kiln/be-0cfd4a77-deepthink/be-repo/runs/dtv-TV-v02-s43/STATUS 2>/dev/null" | tr '\n' ' '); set -- $st
  echo "$(date +%H:%M) s43 done=${1:-0} progress=${2:-0} fail=${3:-0} elapsed=$(( ($(date +%s)-t0)/60 ))m"; [ "${3:-0}" != 0 ] && { echo RUNNER-FAIL; exit 3; }; [ "${1:-0}" = 1 ] && break; [ $(( $(date +%s)-t0 )) -ge 25200 ] && { echo HARDSTOP; exit 3; }; sleep 600; done
SKIPJUDGE=1 TREE=deepthink HIT=1024 $TO/l1.sh 43 | tail -2
$TO/l2.sh judge 43 2>&1 | grep -v " boar" | tail -5
$TO/l2.sh scales "42 43" 2>&1 | grep -v "^{\"comparison" | head -9
echo S43-DONE
