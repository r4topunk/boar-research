"""CHAINWHEN generation on the mini (copy of PACKREAD gen.py; criterion adba95cb): python3 -I gen.py ; resumable; answers-M4.jsonl.
M4 = Qwen3-4B-Instruct-2507 Q4_K_M via llama-server b11010 CPU :8191 (serve.sh), app sampler 0.7/40/0.95/0.05, seed 42, max_tokens 1024 (D4)."""
import json, os, sys, time, urllib.request
D = os.path.expanduser("<runner>/kiln/chainwhen"); rows = [json.loads(l) for l in open(f"{D}/prompts.jsonl")]; AP = f"{D}/answers-M4.jsonl"
done = {(json.loads(l)["arm"], json.loads(l)["id"]) for l in open(AP)} if os.path.exists(AP) else set()
for r in rows:
    if (r["arm"], r["id"]) in done: continue
    b = {"messages": r["messages"], "max_tokens": 1024, "temperature": 0.7, "top_k": 40, "top_p": 0.95, "min_p": 0.05, "seed": 42, "cache_prompt": True, "stream": False}
    t = time.time()
    for k in range(3):
        try: j = json.loads(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8191/v1/chat/completions", json.dumps(b).encode(), {"Content-Type": "application/json"}), timeout=1800).read()); break
        except Exception as e: print("ERR", repr(e), flush=True); time.sleep(5)
    else: continue
    m = j["choices"][0]["message"]; u = j["usage"]
    rec = dict(model="M4", pack=r["pack"], id=r["id"], arm=r["arm"], branch=r["branch"], pick=r["pick"], text=(m.get("content") or "").strip(),
               tokens=u["completion_tokens"], n_prompt_tokens=u["prompt_tokens"], ms=round((time.time() - t) * 1000), finish=j["choices"][0]["finish_reason"])
    open(AP, "a").write(json.dumps(rec, ensure_ascii=False) + "\n"); print("M4", r["arm"], r["id"], rec["tokens"], rec["finish"], round(rec["ms"] / 1000), "s", flush=True)
