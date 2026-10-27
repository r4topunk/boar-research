#!/bin/bash
# H3 MAIN 97 ON/OFF with retry on "database is locked" (other replays share the K1 kit sqlite files).
cd <workspace>/rnd/research/coordinator/arms/retrieve-sweep
K=<workspace>/kiln-local; MQ=../decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl
try() { local out=$1; shift; for n in 1 2 3 4 5 6 7 8; do "$@" > replay/$out.log 2>&1; if grep -q '^{"n"' replay/$out.log; then grep -E '^\{"n"|NEW' replay/$out.log; return 0; fi; echo "retry $n: $(grep -E 'FATAL' replay/$out.log | head -1)"; sleep 60; done; return 1; }
try H3.main.run env RS_COMPRESS_HEAD=1 tools/replay.sh $K/rs-H3 $MQ replay/H3.main.jsonl main
try H3off.main.run env -u RS_COMPRESS_HEAD tools/replay.sh $K/rs-H3 $MQ replay/H3off.main.jsonl main
python3 -I tools/proofdiff.py replay/B0.main.jsonl replay/H3off.main.jsonl
echo MAINDONE
