# SFT4B TEACHER-PROBE: send the rendered engine messages to the deep tier (llama-server, Qwen3.6-35B-A3B, thinking ON by the
# template default) with the engine's sampler (samplerFor: 0.7/40/0.95/0.05, seed 42), max_tokens 1200, no prompt cache.
# Resumable: skips xids already in <out>. usage: python tp_gen.py <port> <contexts.jsonl> <out.jsonl>
import json, os, re, sys, time, urllib.request
port, P, O = sys.argv[1], sys.argv[2], sys.argv[3]
def post(path, body):
    r = urllib.request.Request(f"http://127.0.0.1:{port}{path}", json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=1800).read())
done = {json.loads(l)["xid"] for l in open(O)} if os.path.exists(O) else set()
rows = [json.loads(l) for l in open(P)]
for i, r in enumerate(rows):
    if r["xid"] in done: continue
    t = time.time()
    res = post("/v1/chat/completions", {"messages": r["messages"], "stream": False, "max_tokens": 1200, "temperature": 0.7, "top_k": 40,
                                        "top_p": 0.95, "min_p": 0.05, "seed": 42, "cache_prompt": False})
    wall = time.time() - t
    ch = res["choices"][0]; msg = ch["message"]
    content = msg.get("content") or ""; reasoning = msg.get("reasoning_content") or ""
    m = re.search(r"<think>(.*?)</think>", content, re.S)
    if m: reasoning = reasoning or m.group(1)
    visible = re.sub(r"<think>.*?(</think>|$)", "", content, flags=re.S).strip()
    rt = len(post("/tokenize", {"content": reasoning})["tokens"]) if reasoning else 0
    with open(O, "a") as f:
        f.write(json.dumps({"xid": r["xid"], "content": visible, "reasoning": reasoning, "reasoning_tokens": rt, "finish_reason": ch.get("finish_reason"),
                            "completion_tokens": (res.get("usage") or {}).get("completion_tokens"), "prompt_tokens": (res.get("usage") or {}).get("prompt_tokens"),
                            "timings": res.get("timings"), "wall": round(wall, 2)}, ensure_ascii=False) + "\n")
    print(f"{time.strftime('%T')} {i+1}/{len(rows)} {r['xid']} wall={wall:.0f}s rt={rt} fin={ch.get('finish_reason')} words={len(visible.split())}", flush=True)
print("ALLDONE", flush=True)
