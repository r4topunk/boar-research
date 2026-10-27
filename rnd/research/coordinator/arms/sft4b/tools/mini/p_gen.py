# SFT4B parity: send the parity prompts to a running llama-server (greedy, seed 42, <= 200 tokens, no prompt cache) or to MLX.
# usage: python p_gen.py server <port> <prompts.jsonl> <n> <out.jsonl>
#        python p_gen.py mlx <model dir> <adapter dir|-> <prompts.jsonl> <n> <out.jsonl>
import json, sys, time, urllib.request
def post(port, path, body):
    r = urllib.request.Request(f"http://127.0.0.1:{port}{path}", json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=900).read())
mode = sys.argv[1]
if mode == "server":
    port, P, n, O = sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
    rows = [json.loads(l) for l in open(P)][:n]
    with open(O, "w") as f:
        for r in rows:
            tpl = post(port, "/apply-template", {"messages": r["messages"]})["prompt"]
            t = time.time()
            res = post(port, "/completion", {"prompt": tpl, "n_predict": 200, "temperature": 0, "top_k": 1, "seed": 42, "cache_prompt": False, "return_tokens": True})
            f.write(json.dumps({"pid": r["pid"], "template": tpl, "text": res["content"], "tokens": res.get("tokens"),
                                "timings": res.get("timings"), "wall": time.time() - t}, ensure_ascii=False) + "\n"); f.flush()
else:
    from mlx_lm import load, generate
    from mlx_lm.sample_utils import make_sampler
    M, A, P, n, O = sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), sys.argv[6]
    model, tok = load(M, adapter_path=None if A == "-" else A)
    rows = [json.loads(l) for l in open(P)][:n]
    with open(O, "w") as f:
        for r in rows:
            tpl = tok.apply_chat_template(r["messages"], tokenize=False, add_generation_prompt=True)
            t = time.time()
            text = generate(model, tok, tpl, max_tokens=200, sampler=make_sampler(temp=0.0))
            f.write(json.dumps({"pid": r["pid"], "template": tpl, "text": text, "tokens": tok.encode(text, add_special_tokens=False), "wall": time.time() - t}, ensure_ascii=False) + "\n"); f.flush()
