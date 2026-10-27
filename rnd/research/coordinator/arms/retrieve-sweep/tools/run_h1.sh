#!/bin/bash
# RETRIEVE-SWEEP stage 1b arm H1 HP-SLATE (0 LLM): sequential replays on the MacBook. Usage: tools/run_h1.sh
set -u
cd <workspace>/rnd/research/coordinator/arms/retrieve-sweep
K=<workspace>/kiln-local; QQ=../qform/items/qform.questions.jsonl; MQ=../decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl
K1='{"packHeadPass":"a2","packDense2":"append-budget"}'
R() { local name=$1; shift; local t0=$(date +%s); echo "== $name"; "$@" 2>&1 | grep -E '^\{"n"|FATAL|NEW|Error' ; echo "   $(( $(date +%s) - t0 ))s"; }
R H1.off.qform env -u RS_HP_SLATE tools/replay.sh $K/rs-H1 $QQ replay/H1.off.qform.jsonl qform --forward-opts --settings-json "$K1"
R H1.off.main env -u RS_HP_SLATE tools/replay.sh $K/rs-H1 $MQ replay/H1.off.main.jsonl main
R H1.qform env RS_HP_SLATE=1 tools/replay.sh $K/rs-H1 $QQ replay/H1.qform.jsonl qform --forward-opts --settings-json "$K1"
R H1.main env RS_HP_SLATE=1 tools/replay.sh $K/rs-H1 $MQ replay/H1.main.jsonl main
echo ALLDONE
