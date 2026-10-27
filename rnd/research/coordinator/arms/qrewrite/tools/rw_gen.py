#!/usr/bin/env python3
"""QREWRITE stage 1 rewrite generation (runs ON THE MINI against a local llama-server). usage: rw_gen.py <in.jsonl> <out.jsonl> <port>
Prompt = criterion 60fdc688 (system + 3 fixed few-shot turns), temperature 0, seed 42, max_tokens 32, enable_thinking false."""
import json, sys, time, urllib.request
SYSTEM = "Rewrite the question as the single sentence that would answer it, keeping its key terms; do not answer; one line"
SHOTS = [("Why does my phone battery die faster when it's cold outside?", "A phone battery dies faster in cold weather because low temperature slows the lithium-ion battery chemistry and raises its internal resistance."),
         ("Which planet has the most moons?", "The planet with the most moons is Saturn, which has more confirmed moons than Jupiter."),
         ("Can I use my laptop's USB-C charger for my phone?", "A laptop USB-C charger can charge a phone safely because USB Power Delivery negotiates a voltage the phone accepts.")]
def call(port, q):
    msgs = [{"role": "system", "content": SYSTEM}]
    for u, a in SHOTS: msgs += [{"role": "user", "content": u}, {"role": "assistant", "content": a}]
    msgs.append({"role": "user", "content": q})
    body = json.dumps(dict(messages=msgs, temperature=0, seed=42, max_tokens=32, chat_template_kwargs={"enable_thinking": False})).encode()
    t = time.time(); r = json.load(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{port}/v1/chat/completions", body, {"Content-Type": "application/json"}), timeout=120))
    return r["choices"][0]["message"]["content"], time.time() - t, r.get("usage", {}), r["choices"][0].get("finish_reason")
inp, out, port = sys.argv[1], sys.argv[2], int(sys.argv[3])
call(port, "What is the tallest mountain in Africa?")  # warm-up, not recorded
with open(out, "w") as f:
    for l in open(inp):
        x = json.loads(l); txt, dt, u, fr = call(port, x["question"])
        f.write(json.dumps(dict(id=x["id"], question=x["question"], raw=txt, ms=round(dt * 1000, 1), usage=u, finish=fr), ensure_ascii=False) + "\n"); f.flush()
