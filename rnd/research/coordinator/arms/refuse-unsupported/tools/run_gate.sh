#!/bin/bash
# RU gate pass (copy of arms/gate17/tools/run_gate.sh; mini_gate.py used from arms/gate17/tools unchanged) on the mini. Usage: run_gate.sh <name> <inputs.jsonl (MacBook)>  -> gate/<name>.outputs.jsonl
# Mini: slot lock (atomic mkdir <runner>/kiln/slots/gen1|gen2, owner file, stale-pid reclaim, rmdir on exit), disk >= 25 GiB, own llama-server
# b11010 CPU -t 4 on a free port: -m shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf (b139949c) --lora <runner>/kiln/gate17/gate17-lora-f16.gguf (d022352e),
# -c 8192, --reasoning off; stopped after the pass. Detector :8094 untouched.
set -u
NAME=$1; IN=$2
D=<workspace>/rnd/research/coordinator/arms/refuse-unsupported; G=<workspace>/rnd/research/coordinator/arms/gate17; M=MINI_HOST; GJ=<runner>/kiln/gate17/jobs/ru-$NAME
ssh -T -n $M "rm -rf $GJ; mkdir -p $GJ" && scp -q $IN $M:$GJ/inputs.jsonl && scp -q $G/tools/mini_gate.py $M:$GJ/mini_gate.py || exit 1
ssh $M bash -s -- "$GJ" <<'EOF'
set -u; J=$1; K=<runner>/kiln; SL=$K/slots; export PATH=/opt/homebrew/bin:$PATH
SRV=$HOME/boar/spikes/llama-b11010/build-cpu/bin/llama-server; BASE=$HOME/boar/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf; LORA=$K/gate17/gate17-lora-f16.gguf
[ "$(shasum -a 256 $BASE | cut -c1-8)" = b139949c ] && [ "$(shasum -a 256 $LORA | cut -c1-8)" = d022352e ] || { echo "model sha mismatch"; exit 1; }
FREE=$(df -g ~ | awk 'NR==2{print $4}'); [ "$FREE" -ge 25 ] || { echo "disk $FREE < 25"; exit 1; }
mkdir -p $SL; SLOT=""
while [ -z "$SLOT" ]; do
  for s in gen1 gen2; do
    if [ -d $SL/$s ] && [ -f $SL/$s.owner ]; then op=$(awk '{print $1}' $SL/$s.owner); kill -0 "$op" 2>/dev/null || { rm -f $SL/$s.owner; rmdir $SL/$s 2>/dev/null; }; fi
    if mkdir $SL/$s 2>/dev/null; then SLOT=$s; echo "$$ $(date '+%F %T') $J" > $SL/$s.owner; break; fi
  done
  [ -z "$SLOT" ] && sleep 20
done
PORT=$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1])'); echo $PORT > $J/PORT
$SRV -m $BASE --lora $LORA -c 8192 -t 4 --port $PORT --host 127.0.0.1 --reasoning off -np 1 > $J/server.log 2>&1 & SP=$!
trap 'kill $SP 2>/dev/null; wait $SP 2>/dev/null; rm -f $SL/$SLOT.owner; rmdir $SL/$SLOT 2>/dev/null' EXIT
for i in $(seq 120); do curl -sf http://127.0.0.1:$PORT/health > /dev/null && break; sleep 1; done
echo "slot $SLOT port $PORT start $(date '+%T') free ${FREE}GiB"
python3 -I $J/mini_gate.py $J > $J/gate.log 2>&1 || { echo FAIL; tail -5 $J/gate.log; tail -5 $J/server.log; exit 1; }
grep -i -E "lora|adapter" $J/server.log | head -5
echo "end $(date '+%T') rows $(wc -l < $J/outputs.jsonl)"
EOF
rc=$?; [ $rc = 0 ] || exit $rc
scp -q $M:$GJ/outputs.jsonl $D/gate/$NAME.outputs.jsonl && scp -q $M:$GJ/server.log $D/runs/logs/$NAME.server.log && echo "-> $D/gate/$NAME.outputs.jsonl"
