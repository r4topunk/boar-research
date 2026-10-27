#!/bin/bash
# MINISTRAL3-3B stage 0 (mini, 0 judge calls): takes a gen slot (same atomic-mkdir protocol as lp-screens/tools/mini_gen.sh), then
# (1) one generation through llama-server b11010 (adapter flags, greedy, first LITEPACKS prompt) to prove load + coherent output;
# (2) llama-bench -t 4 -p 512 -n 128 -r 3, interleaved over two rounds: Qwen3-1.7B Q4_K_M, Ministral-3-3B Q4_K_M, Qwen3-4B-2507 Q4_K_M.
# Usage: stage0_bench.sh <workdir> ; writes <workdir>/gen1.json, bench-r{1,2}-<model>.json, STATUS
set -u; W=$1; K=<runner>/kiln; SL=$K/slots; BIN=$HOME/boar/spikes/llama-b11010/build-cpu/bin; SM=$HOME/boar/shared-models
cd $W; S=$W/STATUS; echo "queued $(date '+%F %T')" > $S
mkdir -p $SL; SLOT=""
while [ -z "$SLOT" ]; do
  for s in gen1 gen2; do
    if [ -d $SL/$s ] && [ -f $SL/$s.owner ]; then op=$(awk '{print $1}' $SL/$s.owner); kill -0 "$op" 2>/dev/null || { rm -f $SL/$s.owner; rmdir $SL/$s 2>/dev/null; }; fi
    if mkdir $SL/$s 2>/dev/null; then SLOT=$s; echo "$$ $(date '+%F %T') $W" > $SL/$s.owner; break; fi
  done
  [ -z "$SLOT" ] && sleep 20
done
trap 'rm -f $SL/$SLOT.owner; rmdir $SL/$SLOT 2>/dev/null' EXIT
echo "slot $SLOT $(date '+%F %T') load=$(sysctl -n vm.loadavg)" >> $S
MIN=$SM/lite/Ministral-3-3B-Instruct-2512-Q4_K_M.gguf
$BIN/llama-server -m $MIN -t 4 -tb 4 -c 4096 -ngl 0 -np 1 --jinja --no-webui --cache-ram 0 --reasoning-format deepseek --reasoning off --host 127.0.0.1 --port 18831 > srv-gen.log 2>&1 & P=$!
for i in $(seq 1 300); do curl -sf http://127.0.0.1:18831/health > /dev/null && break; sleep 0.5; done
/usr/bin/python3 -I - <<'PY'
import json, urllib.request
r = json.loads(open("prompts-litepacks.jsonl").readline())
b = {"messages": r["messages"], "temperature": 0, "top_k": 1, "seed": 42, "max_tokens": 256, "chat_template_kwargs": {"enable_thinking": False}}
q = urllib.request.Request("http://127.0.0.1:18831/v1/chat/completions", data=json.dumps(b).encode(), headers={"Content-Type": "application/json"})
o = json.load(urllib.request.urlopen(q)); json.dump(o, open("gen1.json", "w"), indent=1)
print("gen1", r["itemId"], o["choices"][0]["finish_reason"], o["usage"], repr(o["choices"][0]["message"]["content"][:400]))
PY
kill $P; wait $P 2>/dev/null
echo "gen done $(date '+%F %T')" >> $S
for rnd in 1 2; do
  for m in lite/Qwen3-1.7B-Q4_K_M.gguf lite/Ministral-3-3B-Instruct-2512-Q4_K_M.gguf Qwen3-4B-Instruct-2507-Q4_K_M.gguf; do
    n=$(basename $m .gguf); echo "bench r$rnd $n start $(date '+%T') load=$(sysctl -n vm.loadavg)" >> $S
    $BIN/llama-bench -m $SM/$m -t 4 -p 512 -n 128 -r 3 -ngl 0 -o json > bench-r$rnd-$n.json 2> bench-r$rnd-$n.err
  done
done
echo "DONE $(date '+%F %T') load=$(sysctl -n vm.loadavg)" >> $S
