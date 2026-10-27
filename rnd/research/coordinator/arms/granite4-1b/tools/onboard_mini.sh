#!/bin/bash
# GRANITE4-1B onboarding (runs on the mini under nohup; 0 judge calls). Takes a gen slot (atomic mkdir, same protocol as
# lp-screens/tools/mini_gen.sh), then:
# (1) template check: two llama-servers b11010 with the adapter flags (--jinja --reasoning off), A = GGUF-embedded template,
#     B = --chat-template-file with the HF chat_template.jinja (ibm-granite/granite-4.0-1b @ 6a7381ba); /apply-template renders of the
#     first LITEPACKS prompt (kwargs none / enable_thinking false / true); /tokenize over all LITEPACKS prompts;
# (2) one greedy 256-token generation on A (load + coherence + thought/role-token leak check);
# (3) llama-bench -t 4 -p 512 -n 128 -r 3, interleaved over two rounds: Qwen3-1.7B Q4_K_M, granite-4.0-1b Q4_K_M.
# Usage: onboard_mini.sh <workdir with hf-chat_template.jinja + prompts-litepacks.jsonl>
set -u; W=$1; K=<runner>/kiln; SL=$K/slots; BIN=$HOME/boar/spikes/llama-b11010/build-cpu/bin; L=$HOME/boar/shared-models/lite
G=$L/granite-4.0-1b-Q4_K_M.gguf
cd $W; S=$W/STATUS; echo "queued $(date '+%F %T')" > $S
mkdir -p $SL; SLOT=""
while [ -z "$SLOT" ]; do
  for s in gen1 gen2; do
    if [ -d $SL/$s ] && [ -f $SL/$s.owner ]; then op=$(awk '{print $1}' $SL/$s.owner); kill -0 "$op" 2>/dev/null || { rm -f $SL/$s.owner; rmdir $SL/$s 2>/dev/null; }; fi
    if mkdir $SL/$s 2>/dev/null; then SLOT=$s; echo "$$ $(date '+%F %T') $W" > $SL/$s.owner; break; fi
  done
  [ -z "$SLOT" ] && sleep 20
done
trap 'kill $PA $PB 2>/dev/null; rm -f $SL/$SLOT.owner; rmdir $SL/$SLOT 2>/dev/null' EXIT
PA=""; PB=""
echo "slot $SLOT $(date '+%F %T') load=$(sysctl -n vm.loadavg)" >> $S
$BIN/llama-server -m $G -t 4 -c 4096 -ngl 0 -np 1 --jinja --no-webui --cache-ram 0 --reasoning off --host 127.0.0.1 --port 18841 > srvA.log 2>&1 & PA=$!
$BIN/llama-server -m $G -t 2 -c 4096 -ngl 0 -np 1 --jinja --no-webui --cache-ram 0 --reasoning off --chat-template-file $W/hf-chat_template.jinja --host 127.0.0.1 --port 18842 > srvB.log 2>&1 & PB=$!
for p in 18841 18842; do for i in $(seq 1 300); do curl -sf http://127.0.0.1:$p/health > /dev/null && break; sleep 0.5; done; done
/usr/bin/python3 -I - > template_check.out 2>&1 <<'PY'
import json, urllib.request
def post(p, path, body):
    r = urllib.request.Request(f"http://127.0.0.1:{p}{path}", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r))
def get(p, path): return json.load(urllib.request.urlopen(f"http://127.0.0.1:{p}{path}"))
rows = [json.loads(l) for l in open("prompts-litepacks.jsonl")]
open("gguf-embedded_template.jinja", "w").write(get(18841, "/props")["chat_template"])
open("server-B_template.jinja", "w").write(get(18842, "/props")["chat_template"])
m = rows[0]["messages"]; out = {"itemId": rows[0]["itemId"]}
for name, kw in (("none", None), ("false", {"enable_thinking": False}), ("true", {"enable_thinking": True})):
    for p, tag in ((18841, "gguf"), (18842, "hf")):
        b = {"messages": m}
        if kw is not None: b["chat_template_kwargs"] = kw
        out[f"{tag}_{name}"] = post(p, "/apply-template", b)["prompt"]
json.dump(out, open("renders.json", "w"), indent=1)
for name in ("none", "false", "true"):
    pr = out['gguf_' + name]
    print(f"render kwargs={name}: gguf == hf: {pr == out['hf_' + name]}; == kwargs-none: {pr == out['gguf_none']}; has <think>: {'<think>' in pr}; "
          f"IBM documents msg: {'<documents>' in pr}; IBM default system: {'Please ensure responses are professional' in pr}; head={pr[:70]!r}; tail={pr[-70:]!r}")
toks = []
for r in rows:
    pr = post(18841, "/apply-template", {"messages": r["messages"]})["prompt"]
    t = post(18841, "/tokenize", {"content": pr, "add_special": True})["tokens"]
    toks.append((len(t), r["itemId"], r["nPredict"]))
toks.sort(); json.dump(toks, open("prompt-tokens.json", "w"))
first = post(18841, "/tokenize", {"content": out["gguf_none"], "add_special": True, "with_pieces": True})["tokens"][:4]
print(f"first tokens (add_special): {first}")
print(f"prompts {len(toks)} tokens min {toks[0][0]} median {toks[len(toks)//2][0]} max {toks[-1][0]} ({toks[-1][1]}); max nPredict {max(t[2] for t in toks)}; "
      f"max prompt+nPredict {max(t[0] + t[2] for t in toks)} vs -c 4096")
g = post(18841, "/v1/chat/completions", {"messages": m, "max_tokens": 256, "temperature": 0, "top_k": 1, "seed": 42, "chat_template_kwargs": {"enable_thinking": False}})
json.dump(g, open("gen1.json", "w"), indent=1)
msg = g["choices"][0]["message"]; c = msg.get("content") or ""
leak = [t for t in ("<think>", "</think>", "<|start_of_role|>", "<|end_of_role|>", "<|end_of_text|>", "<tool_call>") if t in c]
print(f"gen1: finish {g['choices'][0]['finish_reason']} usage {g['usage']} timings {g.get('timings', {}).get('predicted_per_second')} tok/s; "
      f"reasoning_content {len(msg.get('reasoning_content') or '')} chars; leaks {leak}; content={c!r}")
PY
grep -i -E "arch|general.name|file type|model params|n_layer|ssm|chat template|error|unknown|failed" srvA.log | head -30 > srvA.grep
kill $PA $PB 2>/dev/null; wait $PA $PB 2>/dev/null; PA=""; PB=""
echo "template+gen done $(date '+%F %T')" >> $S
for rnd in 1 2; do
  for m in Qwen3-1.7B-Q4_K_M granite-4.0-1b-Q4_K_M; do
    echo "bench r$rnd $m start $(date '+%T') load=$(sysctl -n vm.loadavg)" >> $S
    $BIN/llama-bench -m $L/$m.gguf -t 4 -p 512 -n 128 -r 3 -ngl 0 -o json > bench-r$rnd-$m.json 2> bench-r$rnd-$m.err
  done
done
echo "DONE $(date '+%F %T') load=$(sysctl -n vm.loadavg)" >> $S
