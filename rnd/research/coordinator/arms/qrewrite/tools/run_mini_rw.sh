#!/bin/bash
# QREWRITE stage 1 on the mini: kiln slot lock, own llama-server on :8097 (never :8094), Qwen3-1.7B Q4_K_M, -t 4, ctx 2048. usage: run_mini_rw.sh start|fetch
set -u
Q=<workspace>/rnd/research/coordinator/arms/qrewrite; M=MINI_HOST; K=<runner>/kiln; J=$K/qrewrite-rw
if [ "$1" = fetch ]; then ssh -T -n $M "cat $J/STATUS"; scp -q $M:$J/rw.jsonl $Q/gen/rw.jsonl && scp -q $M:$J/server.log $Q/gen/server.log; exit 0; fi
ssh -T -n $M "mkdir -p $J" && scp -q $Q/tools/rw_gen.py $Q/items/rw_in.jsonl $M:$J/ || exit 1
ssh $M bash -s -- "$J" "$K" <<'Y'
J=$1; K=$2; SL=$K/slots; S=$J/STATUS; SRV=$HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-server; MOD=$HOME/boar/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf
cat > $J/job.sh <<EOS
set -u; echo "queued \$(date '+%F %T')" > $S; mkdir -p $SL; SLOT=""
while [ -z "\$SLOT" ]; do for s in gen1 gen2; do
  if [ -d $SL/\$s ] && [ -f $SL/\$s.owner ]; then op=\$(awk '{print \$1}' $SL/\$s.owner); kill -0 "\$op" 2>/dev/null || { rm -f $SL/\$s.owner; rmdir $SL/\$s 2>/dev/null; }; fi
  if mkdir $SL/\$s 2>/dev/null; then SLOT=\$s; echo "\$\$ \$(date '+%F %T') $J" > $SL/\$s.owner; break; fi; done; [ -z "\$SLOT" ] && sleep 20; done
trap 'kill \$SP 2>/dev/null; rm -f $SL/\$SLOT.owner; rmdir $SL/\$SLOT 2>/dev/null' EXIT
FREE=\$(df -g ~ | awk 'NR==2{print \$4}'); [ "\$FREE" -ge 25 ] || { echo "FAIL disk \$FREE" >> $S; exit 1; }
echo "slot \$SLOT free=\${FREE}GiB model=\$(shasum -a 256 $MOD | cut -c1-8) \$(date '+%F %T')" >> $S
$SRV -m $MOD --port 8097 -t 4 -c 2048 -np 1 --seed 42 > $J/server.log 2>&1 & SP=\$!
for i in \$(seq 1 60); do curl -sf http://127.0.0.1:8097/health > /dev/null && break; sleep 1; done
echo "server up \$(date '+%F %T')" >> $S
/usr/bin/python3 -I $J/rw_gen.py $J/rw_in.jsonl $J/rw.jsonl 8097 >> $S 2>&1 && echo "DONE \$(wc -l < $J/rw.jsonl) \$(date '+%F %T')" >> $S || echo "FAIL gen" >> $S
EOS
nohup bash $J/job.sh > $J/nohup.log 2>&1 < /dev/null &
echo started
Y
