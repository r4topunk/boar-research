#!/bin/bash
# DEEPFULL stage 2: F1 slice (deepthink tree) then F2 slice (deepfull tree), sequential (one MoE server), then L1 for both. Prints progress lines only.
set -u; TO=$(cd "$(dirname "$0")" && pwd); B=<private held-out dir>; IDS=<workspace>/rnd/research/coordinator/arms/signal20-vpara.ids
wait_run() { local run=$1 tree=$2 t0=$(date +%s); while true; do
  st=$(<on the mini> "grep -c DONE <runner>/kiln/be-0cfd4a77-$tree/be-repo/runs/$run/STATUS 2>/dev/null; grep -cE ' (success|error|declined|fail)' <runner>/kiln/be-0cfd4a77-$tree/be-repo/runs/$run/run.log 2>/dev/null; grep -c FAIL <runner>/kiln/be-0cfd4a77-$tree/be-repo/runs/$run/STATUS 2>/dev/null" | tr '\n' ' '); set -- $st
  echo "$(date +%H:%M) $run done=${1:-0} progress=${2:-0} fail=${3:-0} elapsed=$(( ($(date +%s)-t0)/60 ))m"
  [ "${3:-0}" != 0 ] && { echo "RUNNER-FAIL $run"; return 3; }
  [ "${1:-0}" = 1 ] && return 0
  [ $(( $(date +%s) - t0 )) -ge 7200 ] && { echo "HARDSTOP $run"; return 3; }
  sleep 120; done; }
TREE=deepthink $TO/df.sh launch $B/runs-deepfull/df-F1-vpara-s42-slice.requests.jsonl df-F1-vpara-s42-slice F1 && wait_run df-F1-vpara-s42-slice deepthink || exit 3
TREE=deepfull $TO/df.sh launch $B/runs-deepfull/df-F2-vpara-s42-slice.requests.jsonl df-F2-vpara-s42-slice F2 && wait_run df-F2-vpara-s42-slice deepfull || exit 3
TREE=deepthink $TO/l1.sh df-F1-vpara-s42-slice $IDS slice F1 2>&1 | grep -v " boar" | tail -4
TREE=deepfull $TO/l1.sh df-F2-vpara-s42-slice $IDS slice F2 2>&1 | grep -v " boar" | tail -4
echo CHAIN-DONE
