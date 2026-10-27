#!/bin/bash
# GATELAT mini job (adapted from arms/refuse-unsupported/tools/run_gate.sh). Usage: run.sh <inputs.jsonl (MacBook)>
# One slot hold (gen1|gen2, atomic mkdir, stale-pid reclaim), disk >= 25 GiB. Server F = llama-server b11010 CPU -t 4 -c 8192 --reasoning off -np 1
# with Qwen3-1.7B-Q4_K_M (b139949c) + --lora gate17-lora-f16.gguf (d022352e): modes tok, plain. Then the aLoRA copy (tools/mk_alora.py,
# invocation ids from tok) and server H (same flags, --lora gate17-alora-f16.gguf): mode hyb. Each server stopped after; detector :8094 untouched.
set -u
IN=$1
D=<workspace>/rnd/research/coordinator/arms/gate-latency; M=MINI_HOST; GJ=<runner>/kiln/gate17/jobs/gatelat
ssh -T -n $M "[ \"${RESUME:-0}\" = 1 ] || rm -rf $GJ; mkdir -p $GJ" && scp -q $IN $M:$GJ/inputs.jsonl && scp -q $D/tools/mini_gatelat.py $D/tools/mk_alora.py $M:$GJ/ || exit 1
ssh $M bash -s -- "$GJ" <<'EOF'
set -u; J=$1; K=<runner>/kiln; SL=$K/slots; export PATH=/opt/homebrew/bin:$PATH
L=$HOME/boar/spikes/llama-b11010; SRV=$L/build-cpu/bin/llama-server; BASE=$HOME/boar/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf
LORA=$K/gate17/gate17-lora-f16.gguf; ALORA=$J/gate17-alora-f16.gguf
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
SP=""
trap '[ -n "$SP" ] && kill $SP 2>/dev/null; wait 2>/dev/null; rm -f $SL/$SLOT.owner; rmdir $SL/$SLOT 2>/dev/null' EXIT
start() { PORT=$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1])'); echo $PORT > $J/PORT
  $SRV -m $BASE --lora $1 -c 8192 -t 4 --port $PORT --host 127.0.0.1 --reasoning off -np 1 > $J/server-$2.log 2>&1 & SP=$!
  for i in $(seq 120); do curl -sf http://127.0.0.1:$PORT/health > /dev/null && break; sleep 1; done; echo "server $2 port $PORT $(date '+%T')"; }
stop() { kill $SP 2>/dev/null; wait $SP 2>/dev/null; SP=""; }
echo "slot $SLOT start $(date '+%T') free ${FREE}GiB"
if [ "$(wc -l < $J/plain.jsonl 2>/dev/null | tr -d ' ')" = 124 ]; then echo "resume: tok/plain present"; else
start $LORA F
python3 -I $J/mini_gatelat.py $J tok > $J/tok.log 2>&1 || { echo FAIL tok; tail -5 $J/tok.log; exit 1; }
python3 -I $J/mini_gatelat.py $J plain > $J/plain.log 2>&1 || { echo FAIL plain; tail -5 $J/plain.log; exit 1; }
stop; echo "plain end $(date '+%T')"
fi
INV=$(head -1 $J/tok.jsonl | python3 -c 'import json,sys;print(",".join(map(str,json.load(sys.stdin)["invocation_tokens"])))')
python3 $J/mk_alora.py $L $LORA $ALORA $INV > $J/mk_alora.log 2>&1 || { echo FAIL alora; tail -5 $J/mk_alora.log; exit 1; }
tail -1 $J/mk_alora.log
start $ALORA H
python3 -I $J/mini_gatelat.py $J hyb > $J/hyb.log 2>&1 || { echo FAIL hyb; tail -5 $J/hyb.log; tail -5 $J/server-H.log; exit 1; }
grep -i -E "alora|lora" $J/server-H.log | head -5
stop; rm -f $ALORA; echo "end $(date '+%T')"
EOF
rc=$?; [ $rc = 0 ] || exit $rc
for f in tok plain hyb; do scp -q $M:$GJ/$f.jsonl $D/gate/$f.jsonl; done
for f in server-F.log server-H.log mk_alora.log; do scp -q $M:$GJ/$f $D/runs/$f; done
echo "-> $D/gate/{tok,plain,hyb}.jsonl"
