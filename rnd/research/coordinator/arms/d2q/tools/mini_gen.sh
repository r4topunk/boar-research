#!/bin/bash
# D2Q generation on the mini inside a kiln slot lock (gen1|gen2); own llama-server :8131 (b11010 CPU, 4B Q4), never touches Docker/ollama/:8094.
# usage (on the mini): bash mini_gen.sh <jobdir> [limit]   jobdir holds chunks.jsonl, gen.mjs; writes gen.jsonl, server.log, STATUS
set -u
J=$1; LIM=${2:-}; K=<runner>/kiln; SL=$K/slots; S=$J/STATUS; export PATH=/opt/homebrew/bin:$PATH
SRV=$HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-server; M=$HOME/boar/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf
echo "queued $(date '+%F %T')" > $S; mkdir -p $SL; SLOT=""
while [ -z "$SLOT" ]; do
  for s in gen1 gen2; do
    if [ -d $SL/$s ] && [ -f $SL/$s.owner ]; then op=$(awk '{print $1}' $SL/$s.owner); kill -0 "$op" 2>/dev/null || { rm -f $SL/$s.owner; rmdir $SL/$s 2>/dev/null && echo "reclaimed stale $s (pid $op)" >> $S; }; fi
    if mkdir $SL/$s 2>/dev/null; then SLOT=$s; echo "$$ $(date '+%F %T') $J" > $SL/$s.owner; break; fi
  done
  [ -z "$SLOT" ] && sleep 20
done
SP=""; trap '[ -n "$SP" ] && kill $SP 2>/dev/null; rm -f $SL/$SLOT.owner; rmdir $SL/$SLOT 2>/dev/null' EXIT
echo "slot $SLOT $(date '+%F %T')" >> $S
FREE=$(df -g ~ | awk 'NR==2{print $4}'); [ "$FREE" -ge 25 ] || { echo "FAIL disk ${FREE} GiB < 25" >> $S; exit 1; }
while [ "$(pgrep -f 'bin/llama-server -m' | while read p; do ps -o command= -p $p; done | grep -vc -- '--port 8094')" -ge 2 ]; do sleep 20; done
echo "model sha $(shasum -a 256 $M | cut -c1-16) free=${FREE}GiB" >> $S
$SRV -m $M --port 8131 --host 127.0.0.1 -np 4 -c 8192 -t 8 > $J/server.log 2>&1 & SP=$!
for i in $(seq 1 120); do curl -sf http://127.0.0.1:8131/health > /dev/null && break; sleep 2; done
curl -sf http://127.0.0.1:8131/health > /dev/null || { echo "FAIL server" >> $S; exit 1; }
echo "start $(date '+%F %T')" >> $S
node $J/gen.mjs $J/chunks.jsonl $J/gen.jsonl $LIM 2> $J/gen.log; rc=$?
echo "end rc=$rc rows=$(wc -l < $J/gen.jsonl | tr -d ' ') $(date '+%F %T')" >> $S; echo DONE >> $S
