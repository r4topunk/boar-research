#!/bin/bash
# UXMATRIX MacBook generation (coordinator parallelism note 2026-10-23): same recipe as lp-screens/tools/mini_gen.sh + --dump-prompts (topics27 mini_gen_dump.sh),
# SEFIX-124 env (RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1; F3 unset), tree = APFS clone of kiln-local/be-0cfd4a77-cut7-litepacks
# + H4-MERGE.patch + SEFIX-ALL.patch (src identical to kiln-local/rs-SEFIX), adapter maxTokens set per mode by sed (succinct 512 = untouched, detailed 1024, deep 2048).
# One llama-server (b11010 CPU, -t 4 as the mini) started/stopped by the adapter; detector = local :8094 (v3b, must be up).
# Usage: local_gen.sh <tree dir> <requests.jsonl> <out dir>   -> out/traces.jsonl prompts.jsonl run.log STATUS
set -u
T=$1; REQ=$2; O=$3; mkdir -p $O; S=$O/STATUS; B=<workspace>
MD=$B/shared-models/emergency-detector; SRV=$B/spikes/llama-b11010-cpu/bin/llama-server; SRV=<scratch>   # wrapper: sets DYLD_LIBRARY_PATH (the local build's rpath points to a deleted build dir) and execs the b11010 binary
PK=<scratch>
curl -sf http://127.0.0.1:8094/health > /dev/null || { echo "FAIL detector down" > $S; exit 1; }
export BOAR_EVAL_PACK_DIRS=$PK BOAR_SHARED_MODELS=$B/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
  BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5 \
  RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1
unset RS_HEALTH_NOSOURCE_FALLBACK
echo "start $(date '+%F %T') maxTokens=$(grep -o 'styleReminder: persona.styleReminder, maxTokens: [0-9]*' $T/be/adapter-litedecline.ts | grep -o '[0-9]*$')" > $S
cd $T && be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests $REQ --out $O/traces.jsonl --backend server --server-bin $SRV \
  --threads 4 --timeout-ms 600000 --dump-prompts $O/prompts.jsonl > $O/run.log 2>&1; rc=$?
echo "end $(date '+%F %T') rc=$rc rows=$(wc -l < $O/traces.jsonl 2>/dev/null | tr -d ' ')" >> $S
[ $rc = 0 ] && [ "$(wc -l < $O/traces.jsonl | tr -d ' ')" = "$(wc -l < $REQ | tr -d ' ')" ] && echo DONE >> $S || { echo "FAIL rc=$rc" >> $S; exit 1; }
