#!/bin/bash
# H3 sensitivity (not the verdict arm): RS_COMPRESS_HEAD_TOK 256 and 1000 (ceiling: every chunk whole under slack). 0 LLM.
cd <workspace>/rnd/research/coordinator/arms/retrieve-sweep
K=<workspace>/kiln-local; QQ=../qform/items/qform.questions.jsonl; MQ=../decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl
for T in 256 1000; do
  RS_COMPRESS_HEAD=1 RS_COMPRESS_HEAD_TOK=$T tools/replay.sh $K/rs-H3 $MQ replay/H3t$T.main.jsonl main 2>&1 | grep -E '^\{"n"|FATAL'
  RS_COMPRESS_HEAD=1 RS_COMPRESS_HEAD_TOK=$T tools/replay.sh $K/rs-H3 $QQ replay/H3t$T.qform.jsonl qform 2>&1 | grep -E '^\{"n"|FATAL'
done
echo SENSDONE
