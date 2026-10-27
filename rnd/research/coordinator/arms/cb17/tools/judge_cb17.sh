#!/bin/bash
# CB17 judging (MacBook). Step H: Haiku 5.5-low judge.v1-low N=4 both orders on all 97 (units v01 / qa-cooking-se / qa-money-se).
# Step O: Opus judge.v1 N=4 both orders seed 7 on in/opus.ids (CV5 51 minus units reused from the Opus pool; tools/prep_cb17.py).
# Step S: DECLINE2STAGE stage 1 on in/stage1.units.jsonl (97). Caps from CB17-criterion.md: Opus 110, Haiku 900. Usage: judge_cb17.sh [H] [O] [S]
set -u
H=<workspace>/rnd/research/coordinator/arms/cb17; A=$H/..; SJ=$A/deepthink/tools/shard_judge.sh; L=$A/_lib
BE=<workspace>/boar-eval/bench; RUN=cb17-main-s42; TR=$H/traces/$RUN.traces.jsonl; CR=$H/CB17-criterion.md
[ "$(shasum -a 256 $CR | cut -d' ' -f1)" = "$(cut -d' ' -f1 $H/CB17-criterion.sha256)" ] || { echo "criterion sha mismatch"; exit 9; }
for step in "$@"; do case $step in
H) for u in v01 qa-cooking-se qa-money-se; do
     case $u in v01) B=$BE/v0.1; PS=v01; SEL="grep -Fx -f $A/litepacks/data/v01-57.ids";; *) B=$BE/selftest/$u; PS=st-$u; SEL="grep ^st-$u-";; esac
     O=$H/judgments/$RUN-$u.judgments.jsonl; I=$H/judgments/$RUN-$u.jids; $SEL $A/lp-screens/main-97.ids > $I; m=$(wc -l < $I | tr -d ' ')
     if python3 -I $L/check_judgments.py $O $I > /dev/null 2>&1; then echo "judged already $u"; continue; fi
     env PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=$PS PREFLIGHT_DECLARED_CALLS=$((2*m)) bash $SJ --preflight $TR $O $B $I cb17-$u-haiku55-low 4 haiku > /dev/null || { echo "PREFLIGHT FAIL $u"; exit 8; }
     bash $SJ $TR $O $B $I cb17-$u-haiku55-low 4 haiku > $H/runs/logs/$RUN-$u.judge.log 2>&1 || { echo "judge FAIL $u"; exit 1; }
     python3 -I $L/check_judgments.py $O $I "$RUN-$u" || exit 1
     echo "$(date '+%F %T') haiku $u ids=$m calls=$((2*m))" >> $H/runs/logs/calls.log
   done;;
O) I=$H/in/opus.ids; m=$(grep -c . $I); [ $((2*m)) -le 110 ] || { echo "opus calls $((2*m)) > 110"; exit 9; }
   O=$H/judgments/$RUN-v01.opus.judgments.jsonl
   [ "$m" = 0 ] || { bash $SJ $TR $O $BE/v0.1 $I cb17-v01-opus 4 opus > $H/runs/logs/$RUN-v01.opus.log 2>&1 || { echo "opus FAIL"; exit 1; }
     python3 -I $L/check_judgments.py $O $I "$RUN-v01-opus" || exit 1; echo "$(date '+%F %T') opus v01 ids=$m calls=$((2*m))" >> $H/runs/logs/calls.log; };;
S) node <workspace>/rnd/research/coordinator/ruler/tools/decline2stage_stage1.mjs --units $H/in/stage1.units.jsonl --out $H/judgments/$RUN.stage1.jsonl \
     --cap 100 --conc 4 --ledger $H/runs/logs/stage1.calls.log || { echo "stage1 FAIL"; exit 1; }
   echo "$(date '+%F %T') stage1 calls=$(grep -c . $H/runs/logs/stage1.calls.log)" >> $H/runs/logs/calls.log;;
esac; done; echo "ALLDONE $*"
