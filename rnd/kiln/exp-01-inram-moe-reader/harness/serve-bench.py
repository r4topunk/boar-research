#!/usr/bin/env python3
"""Replay the captured app contexts to one model through llama-server and record speed, memory and answers.

Runs on the Mac mini inside ONE heavy-queue job per model (see run-model.sh). Stdlib only.

Per model:
  1. sha256 of the GGUF must match the pinned value (refuses otherwise).
  2. llama-server (CPU build, -t 4, -ngl 0, -c 4096, --jinja) is started under /usr/bin/time -l; its RSS is also
     sampled every 0.25 s with ps (peak RSS during the run).
  3. One warm-up request (the first captured context, discarded), then every captured context in order.
     Each request: the exact messages the app built, max_tokens = the app's nPredict (512), sampling = the app/runner
     defaults (temp 0.7, top_k 40, top_p 0.95, min_p 0.05, seed 42), enable_thinking=false, cache_prompt=false
     (full prefill every time, so dense and hybrid models pay the same prompt cost; see README).
  4. Load gate: before each request wait until the 1-min load average is < 8 (max 10 min); if the load was > 12 at
     the start or end of a request the sample is flagged and re-measured once (the re-run replaces it).
  5. Questions the app answers without the LLM (instant tier) are copied as-is, route=no-llm, identical for all models.

Usage: python3 serve-bench.py --model-id ID --gguf PATH --sha256 HEX --server BIN --captures a.jsonl,b.jsonl --out rows.jsonl
"""
import argparse, hashlib, json, os, re, signal, subprocess, sys, threading, time, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("--model-id", required=True)
ap.add_argument("--gguf", required=True)
ap.add_argument("--sha256", required=True)
ap.add_argument("--server", required=True)
ap.add_argument("--captures", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--port", type=int, default=18123)
ap.add_argument("--threads", type=int, default=4)
ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--no-think", action="store_true", default=True)
# extra llama-server args, e.g. --server-arg=--cache-ram --server-arg=0 (memory probe without the server prompt cache)
ap.add_argument("--server-arg", action="append", default=[])
a = ap.parse_args()

LOAD_START_MAX, LOAD_FLAG = 8.0, 12.0
SAMPLING = {"temperature": 0.7, "top_k": 40, "top_p": 0.95, "min_p": 0.05, "seed": 42}


def log(*x):
    print(time.strftime("%H:%M:%S"), *x, flush=True)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


got = sha256(a.gguf)
if got != a.sha256:
    sys.exit(f"sha256 mismatch for {a.gguf}: expected {a.sha256}, got {got}")
log("sha256 ok", os.path.basename(a.gguf))

rows_in = []
for f in a.captures.split(","):
    for line in open(f):
        r = json.loads(line)
        rows_in.append((os.path.basename(f).replace(".jsonl", ""), r))
if a.limit:
    rows_in = rows_in[: a.limit]

# ---- server
time_log = a.out + ".time.txt"
server_log = a.out + ".server.log"
cmd = ["/usr/bin/time", "-l", "-o", time_log, a.server, "-m", a.gguf, "-t", str(a.threads), "-tb", str(a.threads),
       "-c", "4096", "-ngl", "0", "-np", "1", "--jinja", "--port", str(a.port), "--no-webui",
       "--reasoning-format", "deepseek", *a.server_arg]
srv = subprocess.Popen(cmd, stdout=open(server_log, "w"), stderr=subprocess.STDOUT)
base = f"http://127.0.0.1:{a.port}"
t0 = time.time()
while True:
    try:
        urllib.request.urlopen(base + "/health", timeout=2)
        break
    except Exception:
        if srv.poll() is not None:
            sys.exit(f"llama-server exited early, see {server_log}")
        if time.time() - t0 > 600:
            sys.exit("llama-server did not become healthy in 600 s")
        time.sleep(1)
load_s = time.time() - t0
log(f"server healthy after {load_s:.1f} s")

# child pid of /usr/bin/time = llama-server
def server_pid():
    out = subprocess.run(["pgrep", "-P", str(srv.pid)], capture_output=True, text=True).stdout.split()
    return int(out[0]) if out else srv.pid

spid = server_pid()
peak_rss_kb = 0
stop = threading.Event()

def sampler():
    global peak_rss_kb
    while not stop.is_set():
        o = subprocess.run(["ps", "-o", "rss=", "-p", str(spid)], capture_output=True, text=True).stdout.strip()
        if o:
            peak_rss_kb = max(peak_rss_kb, int(o))
        time.sleep(0.25)

threading.Thread(target=sampler, daemon=True).start()

THINK = re.compile(r"<think>.*?</think>\s*", re.S)


def chat(messages, n_predict):
    body = {"messages": messages, "max_tokens": n_predict, "stream": True, "cache_prompt": False,
            "chat_template_kwargs": {"enable_thinking": False} if a.no_think else {}, **SAMPLING}
    req = urllib.request.Request(base + "/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    start = time.perf_counter()
    first_any = first_answer = None
    content, reasoning, timings = [], [], {}
    with urllib.request.urlopen(req, timeout=900) as resp:
        for raw in resp:
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            ev = json.loads(data)
            if ev.get("timings"):
                timings = ev["timings"]
            for ch in ev.get("choices", []):
                d = ch.get("delta") or {}
                if d.get("reasoning_content"):
                    first_any = first_any or time.perf_counter()
                    reasoning.append(d["reasoning_content"])
                if d.get("content"):
                    first_any = first_any or time.perf_counter()
                    content.append(d["content"])
                    if first_answer is None and "".join(content).strip() and not "".join(content).lstrip().startswith("<think>"):
                        first_answer = time.perf_counter()
                    elif first_answer is None and "</think>" in "".join(content) and THINK.sub("", "".join(content)).strip():
                        first_answer = time.perf_counter()
    end = time.perf_counter()
    text = "".join(content)
    inline_think = "<think>" in text
    return {
        "answer": THINK.sub("", text).strip(),
        "reasoning": "".join(reasoning) + ("".join(THINK.findall(text)) if inline_think else ""),
        "inlineThink": inline_think,
        "ttftMs": round(((first_answer or end) - start) * 1000, 1),
        "firstTokenMs": round(((first_any or end) - start) * 1000, 1),
        "totalMs": round((end - start) * 1000, 1),
        "timings": timings,
    }


def gate():
    waited = 0
    while os.getloadavg()[0] >= LOAD_START_MAX and waited < 600:
        time.sleep(10)
        waited += 10
    return waited


def run_one(msgs, n_predict):
    waited = gate()
    l0 = os.getloadavg()[0]
    r = chat(msgs, n_predict)
    l1 = os.getloadavg()[0]
    r.update({"loadStart": round(l0, 2), "loadEnd": round(l1, 2), "gateWaitS": waited,
              "contaminated": l0 > LOAD_FLAG or l1 > LOAD_FLAG})
    return r


out = open(a.out, "w")
llm_items = [(s, r) for s, r in rows_in if r.get("kilnCaptured")]
if llm_items:
    s, r = llm_items[0]
    log("warm-up with", r["queryId"])
    run_one(r["kilnCaptured"][0]["messages"], r["kilnCaptured"][0]["nPredict"])

for s, r in rows_in:
    base_row = {"model": a.model_id, "set": s, "queryId": r["queryId"], "category": r.get("category"),
                "query": r.get("query"), "answerTier": r.get("answerTier")}
    cap = r.get("kilnCaptured") or []
    if not cap:
        out.write(json.dumps({**base_row, "route": "no-llm", "answer": r.get("answer", "")}) + "\n")
        continue
    c = cap[0]
    res = run_one(c["messages"], c["nPredict"])
    rerun = False
    if res["contaminated"]:
        log(r["queryId"], "contaminated (load", res["loadStart"], res["loadEnd"], ") -> re-measure")
        res2 = run_one(c["messages"], c["nPredict"])
        res2["remeasuredFrom"] = {k: res[k] for k in ("loadStart", "loadEnd", "ttftMs", "totalMs")}
        res, rerun = res2, True
    t = res["timings"]
    row = {**base_row, "route": "llm", **{k: v for k, v in res.items() if k != "timings"},
           "promptN": t.get("prompt_n"), "promptMs": t.get("prompt_ms"), "prefillTokPerS": t.get("prompt_per_second"),
           "predictedN": t.get("predicted_n"), "decodeTokPerS": t.get("predicted_per_second"), "rerun": rerun,
           "extraCalls": len(cap) - 1}
    out.write(json.dumps(row) + "\n")
    out.flush()
    log(f"{r['queryId']} ttft={row['ttftMs']:.0f}ms prompt={row['promptN']} pp={row['prefillTokPerS'] or 0:.1f} "
        f"tg={row['decodeTokPerS'] or 0:.1f} n={row['predictedN']} load={row['loadStart']}/{row['loadEnd']}")

stop.set()
srv.send_signal(signal.SIGINT)
try:
    srv.wait(timeout=60)
except subprocess.TimeoutExpired:
    srv.kill()
time.sleep(1)
tl = open(time_log).read() if os.path.exists(time_log) else ""
def grab(label):
    m = re.search(r"(\d+)\s+" + label, tl)
    return int(m.group(1)) if m else None
meta = {"model": a.model_id, "gguf": os.path.basename(a.gguf), "sha256": got, "serverLoadS": round(load_s, 1),
        "peakRssSampledBytes": peak_rss_kb * 1024, "maxRssBytes": grab("maximum resident set size"),
        "peakFootprintBytes": grab("peak memory footprint"), "threads": a.threads, "server": a.server,
        "sampling": SAMPLING, "noThink": a.no_think, "cachePrompt": False, "serverArgs": a.server_arg, "finishedAt": time.strftime("%F %T")}
json.dump(meta, open(a.out + ".meta.json", "w"), indent=1)
log("meta", json.dumps(meta))
