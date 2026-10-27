#!/bin/bash
# QUANT17 mini job: slot lock, greedy gens (Q4,Q8), then kld3. Usage: run.sh
set -u; K=<runner>/kiln; Q=$K/quant17; SL=$K/slots; B=<runner>/spikes/llama-b11010/build-cpu/bin; M=<runner>/shared-models/lite
mkdir -p $SL; SLOT=""
while [ -z "$SLOT" ]; do
  for s in gen1 gen2; do
    if [ -d $SL/$s ] && [ -f $SL/$s.owner ]; then op=$(awk '{print $1}' $SL/$s.owner); kill -0 "$op" 2>/dev/null || { rm -f $SL/$s.owner; rmdir $SL/$s 2>/dev/null; }; fi
    if mkdir $SL/$s 2>/dev/null; then SLOT=$s; echo "$$ $(date '+%F %T') $Q" > $SL/$s.owner; break; fi
  done
  [ -z "$SLOT" ] && sleep 20
done
trap 'rm -f $SL/$SLOT.owner; rmdir $SL/$SLOT 2>/dev/null; kill $SPID 2>/dev/null' EXIT
echo "slot $SLOT $(date '+%F %T')" > $Q/STATUS
FREE=$(df -g ~ | awk 'NR==2{print $4}'); echo "free ${FREE}GiB" >> $Q/STATUS; [ "$FREE" -ge 25 ] || { echo FAIL disk >> $Q/STATUS; exit 1; }
SPID=""
for m in Q4_K_M Q8_0; do
  F=$M/Qwen3-1.7B-Q4_K_M.gguf; [ $m = Q8_0 ] && F=$Q/models/Qwen3-1.7B-Q8_0.gguf
  $B/llama-server -m $F --port 18971 -t 4 -c 4096 --reasoning off > $Q/server-$m.log 2>&1 & SPID=$!
  until curl -sf http://127.0.0.1:18971/health >/dev/null; do sleep 2; done
  python3 -I $Q/tools/gen.py $Q/items 18971 $Q/gen-$m.jsonl; echo "gen $m done $(date '+%F %T')" >> $Q/STATUS
  kill $SPID; wait $SPID 2>/dev/null; SPID=""
done
python3 -I $Q/tools/mkanswers.py $Q/gen-Q4_K_M.jsonl $Q/items-q4
python3 -I $Q/tools/mkanswers.py $Q/gen-Q8_0.jsonl $Q/items-q8
for s in q4 q8; do cp $Q/items/*.prompt.txt $Q/items-$s/; done
R=$Q/models/Qwen3-1.7B-BF16.gguf
for s in q4 q8; do
  $Q/tools/kld3 $Q/items-$s 30 $R $M/Qwen3-1.7B-Q4_K_M.gguf $Q/models/Qwen3-1.7B-Q8_0.gguf > $Q/kld-$s.tsv 2> $Q/kld-$s.log
  echo "kld $s done $(date '+%F %T')" >> $Q/STATUS
done
echo DONE >> $Q/STATUS
