#!/bin/bash
# HAIKUJUDGE leg runner: reruns judge.mjs on exit 4 (structured-output/API error; resume), counts failures, stops at >2.
# Usage: run-leg.sh <traces> <leg> <effort>
set -u
cd <workspace>/boar-eval
T=$1; LEG=$2; EFF=$3; OUT=runs/kiln/haikujudge/$LEG.judgments.haiku55-$EFF.jsonl; LOG=runs/kiln/haikujudge/$LEG.haiku55-$EFF.log
mkdir -p runs/kiln/haikujudge; fails=0
while true; do
  node harness/judge.mjs --traces "$T" --out "$OUT" --bench bench/v0.1 --judge-model claude-haiku-5-5 --effort "$EFF" --gap-ms 1000 --seed 7 --system "$LEG-haiku55-$EFF" >>"$LOG" 2>&1
  rc=$?
  echo "### exit $rc at $(date +%H:%M:%S) fails=$fails" >>"$LOG"
  if [ $rc -eq 4 ]; then fails=$((fails+1)); echo "### FAILURE $fails" >>"$LOG"; [ $fails -gt 2 ] && { echo "### STOP: failures > 2" >>"$LOG"; exit 5; }; continue; fi
  echo "### FINAL rc=$rc failures=$fails" >>"$LOG"; exit $rc
done
