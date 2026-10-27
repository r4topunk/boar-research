#!/bin/bash
# RETRIEVE-SWEEP stage 2 / arm H3 COMPRESS-KEEP-HEAD: switch-off identity (20 + full QFORM wall), then ON on QFORM 432 and MAIN 97. 0 LLM.
set -u
cd <workspace>/rnd/research/coordinator/arms/retrieve-sweep
K=<workspace>/kiln-local; QQ=../qform/items/qform.questions.jsonl; MQ=../decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl
R() { local name=$1; shift; local t0=$(date +%s); echo "== $name"; "$@" 2>&1 | grep -E '^\{"n"|FATAL|NEW' ; echo "   $(( $(date +%s) - t0 ))s"; }
R H3.off20 env -u RS_COMPRESS_HEAD tools/replay.sh $K/rs-H3 replay/proof20.questions.jsonl replay/H3.off20.jsonl qform
python3 -I tools/proofdiff.py ../qform/replay/qform.replay.jsonl replay/H3.off20.jsonl
R H3.qform env RS_COMPRESS_HEAD=1 tools/replay.sh $K/rs-H3 $QQ replay/H3.qform.jsonl qform
R H3.main env RS_COMPRESS_HEAD=1 tools/replay.sh $K/rs-H3 $MQ replay/H3.main.jsonl main
R H3.qform.off env -u RS_COMPRESS_HEAD tools/replay.sh $K/rs-H3 $QQ replay/H3off.qform.jsonl qform
python3 -I tools/proofdiff.py ../qform/replay/qform.replay.jsonl replay/H3off.qform.jsonl
R H3.main.off env -u RS_COMPRESS_HEAD tools/replay.sh $K/rs-H3 $MQ replay/H3off.main.jsonl main
python3 -I tools/proofdiff.py replay/B0.main.jsonl replay/H3off.main.jsonl
echo ALLDONE
