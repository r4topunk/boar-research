#!/bin/bash
# SHIP15B-PACKS Opus pass: judge.v1 Opus, both orders, seed 7, N 4 (shard_judge.sh model opus), on opus/P.ids (P units without a pool row).
# Checks the criterion sha and the Opus cap (120) first; no preflight (as ruler/tools/cv5_ladder_run.sh; the criterion declares the Opus use).
set -u
A=<workspace>/rnd/research/coordinator/arms; S=$A/ship15b; BE=<workspace>/boar-eval/bench/v0.1
[ "$(shasum -a 256 $S/SHIP15B-PACKS-criterion.md | cut -d' ' -f1)" = "$(cut -d' ' -f1 $S/SHIP15B-PACKS-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
n=$(grep -c . $S/opus/P.ids); [ $((2*n)) -le 120 ] || { echo "planned $((2*n)) > cap 120"; exit 9; }
bash $A/deepthink/tools/shard_judge.sh $A/ship15b-packs/traces/ship15b-packs-K1-main-sub3e6183-s42.traces.jsonl $S/opus/P.judgments.jsonl $BE $S/opus/P.ids ship15b-P-opus 4 opus > $S/opus/P.log 2>&1
echo "$(date +%T) rc=$? planned_calls=$((2*n))" >> $S/opus/status.txt
