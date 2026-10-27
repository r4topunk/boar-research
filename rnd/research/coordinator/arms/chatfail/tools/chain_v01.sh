#!/bin/bash
# waits for the M4 chat generation, then runs the v0.1 57 single-turn generation for C0 and A1 (same server), then converts traces.
cd <workspace>/rnd/research/coordinator/arms/chatfail
while pgrep -f "gen.mts --model m4 --arms C0,A1,A2,A3" > /dev/null; do sleep 20; done
grep -q "ALL-DONE m4" tools/out/gen-m4.nohup.log || { echo "chat run did not finish cleanly"; exit 1; }
tools/gen.sh --model m4 --arms C0,A1 --chatsfile tools/out/chats-v01.jsonl --ctx v01 --tag v01 > tools/out/gen-m4-v01.nohup.log 2>&1
grep -q "ALL-DONE m4" tools/out/gen-m4-v01.nohup.log && python3 -I tools/v01_traces.py > tools/out/v01_traces.log 2>&1
echo CHAIN-V01-DONE $(date +%T)
