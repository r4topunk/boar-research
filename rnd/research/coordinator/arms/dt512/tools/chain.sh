#!/bin/bash
# DT512 stages 1–2: smoke (gate: 2/2 deep-thinking, 0 < reasoning <= 522, 0 errors) → slice 20 → L1. Prints progress/aggregates only.
set -u; TO=$(cd "$(dirname "$0")" && pwd); B=<private held-out dir>; K=<workspace>/boar-eval/runs/kiln/dt512; IDS=<workspace>/rnd/research/coordinator/arms/signal20-vpara.ids
wait_run() { local run=$1 t0=$(date +%s); while true; do
  st=$(<on the mini> "grep -c DONE <runner>/kiln/be-0cfd4a77-dt512/be-repo/runs/$run/STATUS 2>/dev/null; grep -cE ' (success|error|declined|fail)' <runner>/kiln/be-0cfd4a77-dt512/be-repo/runs/$run/run.log 2>/dev/null; grep -c FAIL <runner>/kiln/be-0cfd4a77-dt512/be-repo/runs/$run/STATUS 2>/dev/null" | tr '\n' ' '); set -- $st
  echo "$(date +%H:%M) $run done=${1:-0} progress=${2:-0} fail=${3:-0} elapsed=$(( ($(date +%s)-t0)/60 ))m"
  [ "${3:-0}" != 0 ] && { echo "RUNNER-FAIL $run"; return 3; }
  [ "${1:-0}" = 1 ] && return 0
  [ $(( $(date +%s) - t0 )) -ge 5400 ] && { echo "HARDSTOP $run"; return 3; }
  sleep 60; done; }
$TO/dh.sh launch $K/dh-smoke-H.requests.jsonl dh-smoke-H H && wait_run dh-smoke-H || exit 3
$TO/dh.sh fetch dh-smoke-H $K/dh-smoke-H.traces.jsonl $K/dh-smoke-H.requests.jsonl | tail -2
$TO/dh.sh think $K/dh-smoke-H.traces.jsonl "" $K/dh-smoke-H.think.json > $TO/../aggregates/think-H-smoke.json
python3 - "$K/dh-smoke-H.traces.jsonl" <<'PY' || exit 4
import json,sys
ok=True
for t in map(json.loads, open(sys.argv[1])):
    g=[e for e in t.get('events',[]) if e.get('kind')=='generation']; rc=t.get('route',{}).get('reasonCodes',[])
    r=sum(e.get('reasoningTokens') or 0 for e in g); a=t.get('answer'); a=a.get('text','') if isinstance(a,dict) else str(a or '')
    line=f"{t['itemId']} deepThinking={'generate:deep-thinking' in rc} reasoning={r} answerWords={len(a.split())} error={bool(t.get('error'))} totalS={round(t['timing']['totalMs']/1000,1)} budgetExceeded={any(e.get('thinkingBudgetExceeded') for e in g)}"
    print(line); ok = ok and ('generate:deep-thinking' in rc) and 0 < r <= 522 and len(a.split())>0 and not t.get('error')
print("SMOKE", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
PY
$TO/dh.sh launch $B/runs-dt512/dh-H-vpara-s42-slice.requests.jsonl dh-H-vpara-s42-slice H && wait_run dh-H-vpara-s42-slice || exit 3
$TO/l1.sh dh-H-vpara-s42-slice $IDS slice 2>&1 | grep -v " boar" | tail -4
echo CHAIN-DONE
