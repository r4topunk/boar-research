#!/bin/bash
# DECODE-GROUND MAIN 97 chain: S -> SB(b4) -> SCp01 -> C1p01, one job at a time on the mini. Log: runs/logs/chain.log
cd "$(dirname "$0")/.." || exit 1
[ "$(shasum -a 256 DG-criterion.md | cut -d' ' -f1)" = "$(cut -d' ' -f1 DG-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
run() { echo "$(date +%T) >>> $*"; "$@" || echo "$(date +%T) FAIL: $*"; }
run env bash tools/run_dg.sh S  runs/req/dg-S-K1-main-s42.requests.jsonl  dg-S-K1-main-s42
run env DG_BIAS=4.0 bash tools/run_dg.sh SB runs/req/dg-SB-K1-main-s42.requests.jsonl dg-SBb4-K1-main-s42
run env DG_PLAUS=0.1 bash tools/run_dg.sh SC runs/req/dg-SC-K1-main-s42.requests.jsonl dg-SCp01-K1-main-s42
run env DG_PLAUS=0.1 bash tools/run_dg.sh C1 runs/req/dg-C1-K1-main-s42.requests.jsonl dg-C1p01-K1-main-s42
echo "$(date +%T) CHAIN DONE"
