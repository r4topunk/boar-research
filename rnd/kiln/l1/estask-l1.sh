#!/usr/bin/env bash
# Compass's estask L1 (compass/chat-slice/replylang/estask/CRITERIA.md). Arm SWAPPED (Compass, before any data) to R1es-estask2.patch 6744e57c… (= control +
# estask2-delta-vs-R1es.patch f87ea80a…, verified identical); control = R1es-b6-health9-precedence-esstrings.patch d94c6177….
# 48 ES items (precedence/es_ids.json: v0/v1/v2 × 16) × 4B (chat-slice-base-s42) + 1.5B (p2-iphone13) × s42/s43, arm and
# control back to back. Runner 8ca619bd… (0b13be04…). v1/v2 outputs restricted (chat-slice v*-fresh/runs); mini copies deleted.
# Queued after the chat-v3 ladder (R2) and Anvil's B6E blind replay.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; CS=$B/rnd/research/compass/chat-slice; P=$CS/replylang/precedence
export HEAVY_CLASS=normal
C4=$E/runs/kiln/chat-slice-base-s42/config.json; C15=$E/adapters/desktop-node/configs/p2-iphone13-0cfd4a77.json
# (re-queued 13:05 behind the health11 blind confirm; completed runs with 16 traces are skipped, not re-run)
grep -q 6744e57c $CS/replylang/estask/CRITERIA.md || { echo 'CRITERIA does not name 6744e57c'; exit 1; }
run() { # slice model arm seed ids
  local s=$1 m=$2 arm=$3 seed=$4 ids=$5 cfg slicef d label=kiln-estask-$1-$2-$3-s$4
  [ $m = 4b ] && cfg=$C4 || cfg=$C15
  case $s in v0) slicef=$CS/slice.v0.jsonl; d=$E/runs/kiln/estask/v0-$m-$arm-s$seed ;; v1) slicef=$CS/v1-fresh/slice.v1.jsonl; d=$CS/v1-fresh/runs/estask-$m-$arm-s$seed ;; v2) slicef=$CS/v2-fresh/slice.v2.jsonl; d=$CS/v2-fresh/runs/estask-$m-$arm-s$seed ;; esac
  mkdir -p $d
  if [ -f $d/traces.jsonl ] && [ "$(wc -l < $d/traces.jsonl)" -eq 16 ]; then echo "$s $m $arm s$seed SKIP (done)"; return; fi
  python3 -c "import json; c=json.load(open('$cfg')); c['arm']='$arm'; c['seed']=$seed; json.dump(c, open('$d/config.json','w'))"
  pnpm -s -C $E/packages/protocol exec tsx src/makeRequests.ts --questions $slicef --config $d/config.json --run-id $label > $d/requests.jsonl 2>/dev/null
  BOAR_EVAL_RUNNER_DIR=be-$arm $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm $arm --requests $d/requests.jsonl --out $d/traces.jsonl --ids "$ids" > $d/runsh.out 2>&1
  echo "$s $m $arm s$seed rc=$? $(date +%H:%M)"
  <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-$arm/be-$arm/runs/$label"
}
for seed in 42 43; do for m in 4b 15b; do for s in v0 v1 v2; do
  ids=$(python3 -c "import json; print(','.join(json.load(open('$P/es_ids.json'))['$s']))")
  for arm in estask2 r1es; do run $s $m $arm $seed "$ids"; done
done; done; done
echo ESTASK-L1-DONE
