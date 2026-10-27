#!/bin/bash
# SEEDGEN probe: generate the 20 qa-health-se OFF requests (cut 7, one pack installed) twice per setting, sequentially, resumable
# (skips runs whose .status ends in DONE). A = run_selftest.sh as-is (control); B = as-is + --dump-prompts (observational: the
# sent messages are logged so prompt identity can be checked). 0 judge calls. Usage: nohup probe.sh > ../runs/probe.log 2>&1 &
set -u
D=<workspace>/rnd/research/coordinator/arms; R=$D/seedgen/runs; REQ=$D/packs/selftest-runs/st-qa-health-se-cut7-s42.requests.jsonl
for run in A1 A2 B1 B2; do
  OUT=$R/$run.traces.jsonl
  [ -f "$R/$run.traces.status" ] && [ "$(tail -1 "$R/$run.traces.status")" = DONE ] && { echo "skip $run"; continue; }
  while pgrep -f "llama-server.*Qwen3-4B" >/dev/null || pgrep -f adapter.ts >/dev/null; do echo "$(date '+%T') waiting: a 4B job is running"; sleep 30; done
  rm -f "$OUT" "$R/$run.prompts.jsonl"
  case $run in B*) export DUMP=$R/$run.prompts.jsonl ;; *) unset DUMP ;; esac
  echo "$(date '+%F %T') start $run"; "$D/seedgen/tools/run_probe.sh" "$REQ" "$OUT"; echo "$(date '+%F %T') end $run rc=$?"
done
echo ALLDONE
