#!/usr/bin/env python3
"""LITE17 generation (criterion 453826c0): Qwen3-1.7B Q4_K_M, llama-server b11010 CPU on the MacBook :8192 (tools/serve.sh), app sampler
0.7/40/0.95/0.05, seed 42 (as PACKREAD/CHAINWHEN gen.py). Resumable; appends to ../answers/answers-Q17.jsonl. Per item, arms run back to back
(B, Q1, Q2, T, S) so the shared system prefix is reused from the slot KV (cache_prompt; outputs unaffected).
  B : thinking off (chat_template_kwargs.enable_thinking=false), max_tokens 1024.
  T : thinking on (enable_thinking=true) + per-request thinking_budget_tokens=256 (b11010 reasoning-budget sampler: after 256 reasoning tokens
      the server forces the end-of-thinking tag; logged "reasoning budget: tokens=256"), --reasoning-format deepseek splits reasoning_content;
      max_tokens = 1024 + 256 + 8 so the answer keeps its 1024 (thinking tokens count against max_tokens in llama-server). Only content is judged.
  Q1: pass-1 quote prompt (build.py), thinking off, max_tokens 200.
  Q2: B messages with the user turn + "\\nRelevant quote: <pass-1 output, whitespace collapsed to one line>", thinking off, max_tokens 1024.
  S : SE question-only chunks dropped (build.py), thinking off, max_tokens 1024; only items where S != B.
Usage: python3 -I gen.py [--limit N]"""
import json, os, sys, time, urllib.request
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "http://127.0.0.1:8192/v1/chat/completions"
P = {}
for l in open(f"{H}/data/prompts.jsonl"):
    r = json.loads(l); P[(r["arm"], r["id"])] = r
ids = [l.strip() for l in open(f"{H}/data/ids-150.ids") if l.strip()]
AP = f"{H}/answers/answers-Q17.jsonl"
done = {}
if os.path.exists(AP):
    for l in open(AP):
        r = json.loads(l); done[(r["arm"], r["id"])] = r
lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None

def call(messages, max_tokens, think, budget=None):
    b = {"messages": messages, "max_tokens": max_tokens, "temperature": 0.7, "top_k": 40, "top_p": 0.95, "min_p": 0.05, "seed": 42,
         "cache_prompt": True, "stream": False, "chat_template_kwargs": {"enable_thinking": think}}
    if budget is not None: b["thinking_budget_tokens"] = budget
    for k in range(3):
        try:
            t = time.time()
            j = json.loads(urllib.request.urlopen(urllib.request.Request(URL, json.dumps(b).encode(), {"Content-Type": "application/json"}), timeout=3600).read())
            return j, round((time.time() - t) * 1000)
        except Exception as e:
            print("ERR", repr(e), flush=True); time.sleep(5)
    raise SystemExit("server failed 3x")

def run(arm, iid, pack, messages, max_tokens, think=False, budget=None, extra=None):
    if (arm, iid) in done: return done[(arm, iid)]
    j, ms = call(messages, max_tokens, think, budget)
    m = j["choices"][0]["message"]; u = j["usage"]; rc = m.get("reasoning_content") or ""
    rec = dict(model="Q17", pack=pack, id=iid, arm=arm, text=(m.get("content") or "").strip(), reasoning=rc, reasoning_chars=len(rc),
               tokens=u["completion_tokens"], n_prompt_tokens=u["prompt_tokens"], ms=ms, finish=j["choices"][0]["finish_reason"],
               timings=j.get("timings", {}).get("predicted_per_second"))
    if extra: rec.update(extra)
    open(AP, "a").write(json.dumps(rec, ensure_ascii=False) + "\n"); done[(arm, iid)] = rec
    print(arm, iid, rec["tokens"], rec["finish"], round(ms / 1000), "s", flush=True)
    return rec

n = 0
for iid in ids:
    if lim is not None and n >= lim: break
    n += 1
    B = P[("B", iid)]; pack = B["pack"]
    run("B", iid, pack, B["messages"], 1024)
    q1 = run("Q1", iid, pack, P[("Q1", iid)]["messages"], 200)
    quote = " ".join(q1["text"].split())
    m2 = [B["messages"][0], {"role": "user", "content": B["messages"][1]["content"] + "\nRelevant quote: " + quote}]
    run("Q2", iid, pack, m2, 1024, extra=dict(quote=quote))
    run("T", iid, pack, P[("T", iid)]["messages"], 1024 + 256 + 8, think=True, budget=256)
    if ("S", iid) in P: run("S", iid, pack, P[("S", iid)]["messages"], 1024)
print("DONE", len(done), "rows", flush=True)
