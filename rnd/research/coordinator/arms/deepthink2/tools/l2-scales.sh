#!/bin/bash
# DEEPVPARA L2 claim scales (as CLAIM-RESULTS-cut6): raw + floor-removed (= floor-adjusted) + above-decline via the frozen
# bench/v0.2/plan/floor_metrics.py (stratified by category when a questions file is given, D = 0.306, seed 11, 2000 boots);
# win/tie/loss vs the reference + win-rate CI + paired Δ vs K (items resampled jointly, 2000 boots) via paired.mjs.
# Usage: l2-scales.sh <dirD> "<D runs>" <dirK> "<K runs>" <ids> <questions|-> <out.json>
set -eu
dD=$1; rD=$2; dK=$3; rK=$4; IDS=$5; Q=$6; OUT=$7; TOOLS=$(cd "$(dirname "$0")" && pwd); FM=<workspace>/boar-eval/bench/v0.2/plan/floor_metrics.py
QA=(); [ "$Q" != - ] && QA=(--questions "$Q")
fD=$(python3 $FM --runs $rD --dir $dD --decline-ratio 0.306 --ids $IDS "${QA[@]}")
fK=$(python3 $FM --runs $rK --dir $dK --decline-ratio 0.306 --ids $IDS "${QA[@]}")
pr=(); for r in $rD; do pr+=("$r"); done; pk=(); for r in $rK; do pk+=("$r"); done
P=()
for i in "${!pr[@]}"; do P+=("$(node $TOOLS/paired.mjs $dD/${pr[$i]}.judgments.jsonl $dK/${pk[$i]}.judgments.jsonl $IDS D K | jq -c 'del(.perItem)')"); done
jq -n --argjson d "$fD" --argjson k "$fK" --argjson p "$(printf '%s\n' "${P[@]}" | jq -s .)" '{floorD: $d, floorK: $k, pairedPerSeed: $p}' > $OUT
jq -c '{D: {raw: .floorD.raw, floorAdj: .floorD.above_min, aboveDecl: .floorD.above_decl, n: .floorD.n_items}, K: {raw: .floorK.raw, floorAdj: .floorK.above_min, n: .floorK.n_items}}' $OUT
jq -c '.pairedPerSeed[] | {D: {win: .D.win, winRateCI: .D.winRateCI, tie: .D.tie}, K: {win: .K.win, winRateCI: .K.winRateCI}, winsVsRef: .paired.winsVsRef, dRatio: .paired.dRatio, dRatioCI: .paired.dRatioCI, dFloor: .paired.dFloor, dFloorCI: .paired.dFloorCI, h2h: .paired.headToHead}' $OUT
