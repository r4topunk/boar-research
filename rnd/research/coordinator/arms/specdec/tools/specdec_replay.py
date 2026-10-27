#!/usr/bin/env python3
"""SPECDEC replay (runs ON the Mac mini, inside the heavy lock). One llama-server per config, sequential requests.
usage: specdec_replay.py PROMPTS.jsonl OUTDIR CONFIG [CONFIG ...]
CONFIG = name:mode:draft:nmax   mode = samp|greedy|greedylp (greedy + top-2 logprobs per token, for the tie analysis) ; draft = none|q06|q15 ; nmax = 0|4|8   (+ optional :pmin)
Request body = what the be-ship server backend sends (runner/server.ts requestFor): messages, max_tokens = nPredict(512)+thinkingBudget(256)
because enableThinking is null (engine default), temperature 0.7 top_k 40 top_p 0.95 min_p 0.05 seed 44, cache_prompt false.
greedy mode = same but temperature 0 (identity gate G1 'greedy')."""
import json, os, subprocess, sys, time, threading, urllib.request, signal

SRV = os.path.expanduser("<runner>/spikes/llama-b11010/build-cpu/bin/llama-server")
TARGET = os.path.expanduser(os.environ.get("SPECDEC_TARGET", "<runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf"))  # override only for the c-measurement (draft alone)
DRAFTS = {"q06": os.path.expanduser("<runner>/kiln/specdec/Qwen3-0.6B-Q8_0.gguf"),
          "q15": os.path.expanduser("<runner>/shared-models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf")}
PORT = 8187
MAX_TOKENS = 512 + 256

def rss_kb(pid):
    try: return int(subprocess.check_output(["ps", "-o", "rss=", "-p", str(pid)]).strip())
    except Exception: return 0

def run_config(name, mode, draft, nmax, pmin, prompts, outdir):
    args = [SRV, "-m", TARGET, "-t", "4", "-tb", "4", "-c", "4096", "-ngl", "0", "-np", "1", "--jinja", "--no-webui", "--cache-ram", "0",
            "--reasoning-format", "deepseek", "--host", "127.0.0.1", "--port", str(PORT)]
    if draft != "none":
        args += ["-md", DRAFTS[draft], "--spec-type", "draft-simple", "--spec-draft-n-max", str(nmax), "--spec-draft-n-min", "0"]
        if pmin is not None: args += ["--spec-draft-p-min", str(pmin)]
    log = open(f"{outdir}/{name}.server.log", "w"); log.write(" ".join(args) + "\n"); log.flush()
    p = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT)
    base = f"http://127.0.0.1:{PORT}"
    t0 = time.time(); ok = False
    try:
        while time.time() - t0 < 300:
            if p.poll() is not None: break
            try:
                if urllib.request.urlopen(base + "/health", timeout=2).status == 200: ok = True; break
            except Exception: time.sleep(0.5)
        if not ok:
            return {"name": name, "error": "server did not become healthy (exit=%s), see %s.server.log" % (p.poll(), name)}
        load_s = time.time() - t0
        idle_rss = rss_kb(p.pid); peak = [idle_rss]; stop = [False]
        def poll():
            while not stop[0]:
                peak[0] = max(peak[0], rss_kb(p.pid)); time.sleep(0.25)
        th = threading.Thread(target=poll, daemon=True); th.start()
        rows = []
        for pr in prompts:
            body = {"messages": pr["messages"], "stream": False, "max_tokens": MAX_TOKENS, "temperature": 0.7 if mode == "samp" else 0.0,
                    **({"logprobs": True, "top_logprobs": 2} if mode == "greedylp" else {}),
                    "top_k": 40, "top_p": 0.95, "min_p": 0.05, "seed": 44, "cache_prompt": False}
            req = urllib.request.Request(base + "/v1/chat/completions", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            s = time.time()
            r = json.load(urllib.request.urlopen(req, timeout=900))
            wall = time.time() - s
            m = r["choices"][0]["message"]; t = r.get("timings", {})
            rows.append({"itemId": pr["itemId"], "text": m.get("content") or "", "reasoning": m.get("reasoning_content") or "",
                         "finish": r["choices"][0].get("finish_reason"), "wall_s": wall,
                         "prompt_n": t.get("prompt_n"), "prompt_ms": t.get("prompt_ms"), "predicted_n": t.get("predicted_n"),
                         "predicted_ms": t.get("predicted_ms"), "predicted_per_second": t.get("predicted_per_second"),
                         "draft_n": t.get("draft_n"), "draft_n_accepted": t.get("draft_n_accepted"),
                         **({"lp": [[x["token"], x["logprob"]] + [y["logprob"] for y in x.get("top_logprobs", [])[1:2]] + [[y["token"] for y in x.get("top_logprobs", [])[:2]]]
                             for x in (r["choices"][0].get("logprobs") or {}).get("content", [])]} if mode == "greedylp" else {})})
        stop[0] = True; th.join(timeout=1)
        with open(f"{outdir}/{name}.jsonl", "w") as f:
            for x in rows: f.write(json.dumps(x) + "\n")
        return {"name": name, "mode": mode, "draft": draft, "nmax": nmax, "pmin": pmin, "load_s": load_s, "idle_rss_mb": idle_rss / 1024,
                "peak_rss_mb": peak[0] / 1024, "n": len(rows), "ok": True}
    finally:
        # stop THIS server by pid (then verify the port is free)
        p.send_signal(signal.SIGTERM)
        try: p.wait(timeout=20)
        except Exception: p.kill(); p.wait()
        log.close()

if __name__ == "__main__":
    prompts = [json.loads(l) for l in open(sys.argv[1])]
    outdir = sys.argv[2]; os.makedirs(outdir, exist_ok=True)
    summ = open(f"{outdir}/summary.jsonl", "a")
    only = os.environ.get("SPECDEC_LIMIT")
    if only: prompts = prompts[:int(only)]
    for c in sys.argv[3:]:
        f = c.split(":"); name, mode, draft, nmax = f[0], f[1], f[2], int(f[3]); pmin = float(f[4]) if len(f) > 4 else None
        r = run_config(name, mode, draft, nmax, pmin, prompts, outdir)
        summ.write(json.dumps(r) + "\n"); summ.flush(); print(json.dumps(r), flush=True)
