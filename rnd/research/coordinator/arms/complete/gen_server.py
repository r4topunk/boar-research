#!/usr/bin/env python3
"""COMPLETE (Kiln): DEEPREAD gen_server.py with max_tokens 512 -> 700 (only change; prompt change lives in requests.jsonl).
Original doc: DEEPREAD (Kiln): deep35 R450 generation through llama-server (b11010 build), same flags as the desktop-node
--backend server (-t 4 -tb 4 -c 4096 -ngl 0 -np 1 --jinja --no-webui --cache-ram 0 --reasoning-format deepseek),
same sampler as the 4B R450 oracle run (0.7/40/0.95/0.05, seed 42, max_tokens 512), thinking off
(chat_template_kwargs.enable_thinking=false). RSS of llama-server sampled with ps every 250 ms.
Writes EvalTrace rows (gen_oracle.mts shape) for harness/judge.mjs. Resumes on rerun.
usage: python3 gen_server.py requests.jsonl out.traces.jsonl"""
import json, os, socket, subprocess, sys, threading, time, urllib.request, datetime

REQ, OUT = sys.argv[1], sys.argv[2]
GGUF = os.path.expanduser("<runner>/shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf")
BIN = os.path.expanduser("<runner>/spikes/llama-b11010/build-cpu/bin/llama-server")
NAME, VARIANT, THREADS = "deep35-complete", "R450", 4
SAMPLER = {"temperature": 0.7, "top_k": 40, "top_p": 0.95, "min_p": 0.05, "seed": 42}

s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
args = [BIN, "-m", GGUF, "-t", str(THREADS), "-tb", str(THREADS), "-c", "4096", "-ngl", "0", "-np", "1", "--jinja", "--no-webui",
        "--cache-ram", "0", "--reasoning-format", "deepseek", "--host", "127.0.0.1", "--port", str(port)]
log_path = OUT.replace(".jsonl", "") + ".server.log"
logf = open(log_path, "w"); logf.write(" ".join(args) + "\n"); logf.flush()
version = subprocess.run([BIN, "--version"], capture_output=True, text=True)
version = (version.stdout + version.stderr).strip().splitlines()[0]
t0 = time.time()
proc = subprocess.Popen(args, stdout=logf, stderr=subprocess.STDOUT)
base = f"http://127.0.0.1:{port}"
try:
    while True:
        if proc.poll() is not None: sys.exit(f"llama-server exited during load, see {log_path}")
        if time.time() - t0 > 600: sys.exit("not healthy after 600 s")
        try:
            if urllib.request.urlopen(base + "/health", timeout=2).status == 200: break
        except Exception: pass
        time.sleep(0.1)
    load_ms = round((time.time() - t0) * 1000)

    peak = {"run": 0, "win": 0, "idle": 0}
    stop_flag = threading.Event()
    def rss_kb():
        try: return int(subprocess.run(["ps", "-o", "rss=", "-p", str(proc.pid)], capture_output=True, text=True).stdout.strip() or 0)
        except Exception: return 0
    def sampler():
        while not stop_flag.is_set():
            kb = rss_kb(); peak["run"] = max(peak["run"], kb); peak["win"] = max(peak["win"], kb); time.sleep(0.25)
    peak["idle"] = rss_kb()
    threading.Thread(target=sampler, daemon=True).start()

    reqs = [json.loads(l) for l in open(REQ) if l.strip()]
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)["itemId"] for l in open(OUT) if l.strip()}
    for r in reqs:
        if r["id"] in done: continue
        body = {"messages": r["messages"], "stream": True, "max_tokens": 700, **SAMPLER, "cache_prompt": False,
                "chat_template_kwargs": {"enable_thinking": False}}
        req = urllib.request.Request(base + "/v1/chat/completions", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        peak["win"] = 0
        ts = time.time(); first = None; content = []; reasoning = 0; timings = None; finish = None; err = None
        try:
            with urllib.request.urlopen(req, timeout=900) as resp:
                for raw in resp:
                    line = raw.decode("utf-8", "replace").strip()
                    if not line.startswith("data:"): continue
                    data = line[5:].strip()
                    if data == "[DONE]": break
                    d = json.loads(data)
                    if d.get("timings"): timings = d["timings"]
                    for ch in d.get("choices", []):
                        dl = ch.get("delta", {}) or {}
                        if dl.get("reasoning_content"): reasoning += 1
                        if dl.get("content"):
                            if first is None and dl["content"].strip(): first = time.time()
                            content.append(dl["content"])
                        if ch.get("finish_reason"): finish = ch["finish_reason"]
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
        total = time.time() - ts
        text = "".join(content).strip()
        import re; text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()
        tm = timings or {}
        trace = {"protocol": "1.0.0", "runId": f"oracle-{NAME}-{VARIANT}", "itemId": r["id"], "question": r["question"],
            "engine": {"commit": "0cfd4a77-prompt", "arm": f"oracle-{VARIANT}-{NAME}", "dirty": False},
            "runtime": {"adapter": "oracle-reader-server", "backend": "llama-server", "host": f"Mac mini M-series CPU x{THREADS} (llama-server)",
                        "model": NAME, "sampler": SAMPLER,
                        "versions": {"prompt": "engine fast-tier prompt from and-qwen-s44 dump + COMPLETE instruction (prompt-diff.txt)", "ctx": f"ctx-{VARIANT}.jsonl", "llama-server": version,
                                     "model.sha256": "96b9c0af5c77a4ecaabe3983175112b5ece763261c1ece12b2494b692a70dad7"}},
            "config": {"commit": "0cfd4a77", "arm": f"oracle-{VARIANT}-{NAME}", "modelId": "qwen3.6-35b-a3b-ud-q2kxl", "settings": {}, "kit": [], "device": None},
            "route": {"task": None, "tier": "deep", "outcome": "answered", "reasonCodes": [f"oracle:{VARIANT}", f"oracle:passages-{r['nPassages']}"],
                      "finishReason": finish},
            "retrieval": {"raw": [], "kept": r["kept"], "dropped": []},
            "answer": {"text": text, "cited": [], "shown": [], "declined": False, "weakSources": False, "warnings": []},
            "timing": {"ttftMs": round((first - ts) * 1000) if first else None, "totalMs": round(total * 1000), "retrievalMs": None,
                       "prefillMs": tm.get("prompt_ms"), "prefillTokPerSec": tm.get("prompt_per_second"), "decodeTokPerSec": tm.get("predicted_per_second"),
                       "decodeMs": tm.get("predicted_ms"), "promptTokens": tm.get("prompt_n"), "outputTokens": tm.get("predicted_n"),
                       "reasoningTokens": reasoning, "modelLoadMs": load_ms},
            "resources": {"peakRssMb": round(peak["win"] / 1024), "idleRssMb": round(peak["idle"] / 1024)},
            "events": [], "error": err or (None if text else "empty-answer"), "createdAt": datetime.datetime.utcnow().isoformat() + "Z"}
        with open(OUT, "a") as f: f.write(json.dumps(trace) + "\n")
        print(r["id"], r["nPassages"], f"{total:.1f}s", f"pp={tm.get('prompt_n')}@{tm.get('prompt_per_second') or 0:.1f}",
              f"tg={tm.get('predicted_n')}@{tm.get('predicted_per_second') or 0:.2f}", f"rssMB={round(peak['win']/1024)}", f"think={reasoning}",
              text[:70].replace("\n", " "), flush=True)
    stop_flag.set()
    print(f"RUN DONE load_ms={load_ms} idle_rss_mb={round(peak['idle']/1024)} peak_rss_mb={round(peak['run']/1024)}", flush=True)
finally:
    proc.terminate()
    try: proc.wait(10)
    except Exception: proc.kill()
