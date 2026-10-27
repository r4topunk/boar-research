#!/usr/bin/env python3
"""DEEPPAR-L1 driver (criterion sha256 1d974587...). Runs on the mini under <runner>/bin/run-heavy.
Leg render: llama-server b11010 (DEEPPAR flags) renders each request's messages via /apply-template
(enable_thinking=false); rendered strings + sha256 saved; server stopped and confirmed gone.
Leg gen: one bmoe-cli --session process (one model load) under /usr/bin/time -l, sampler from flags
(--temp 0.7 --top-k 40 --top-p 0.95 --seed 42 -n 512 -c 4096 + P0 knobs); one generate request per item,
raw rendered prompt, think=false, clear_kv=true (resets the sampler RNG -> seed 42 per item).
Results appended to out/results.jsonl (resumable). Watchdog: free disk < 25 GiB or swap used > 8 GB -> kill, STOP.
usage: python3 run_l1.py [render] [gen]"""
import json, os, subprocess, sys, time, threading, hashlib, urllib.request, re, signal

HOME = os.path.expanduser("~")
D = f"{HOME}/boar/kiln/deeppar-l1"
OUT = f"{D}/out"
GGUF = f"{HOME}/boar/shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf"
SERVER = f"{HOME}/boar/spikes/llama-b11010/build-cpu/bin/llama-server"
BMOE = f"{HOME}/boar/spikes/bmoe-v028/out/host/bmoe-cli"
PORT = int(os.environ.get("DEEPPAR_PORT", "18094"))
REQS = [json.loads(l) for l in open(f"{D}/requests.jsonl") if l.strip()]
STOP = {"hit": None}
CUR = {"proc": None}

def log(*a):
    s = time.strftime("%H:%M:%S") + " " + " ".join(str(x) for x in a)
    print(s, flush=True)
    with open(f"{OUT}/run.log", "a") as f: f.write(s + "\n")

def free_gib():
    st = os.statvfs("/"); return st.f_bavail * st.f_frsize / 2**30

def swap_used_mb():
    s = subprocess.run(["sysctl", "-n", "vm.swapusage"], capture_output=True, text=True).stdout
    m = re.search(r"used = ([\d.,]+)M", s)
    return float(m.group(1).replace(",", ".")) if m else -1

def watchdog():
    peak = 0
    while True:
        fg, sw = free_gib(), swap_used_mb(); peak = max(peak, sw)
        with open(f"{OUT}/watch.txt", "w") as f: f.write(f"{time.strftime('%H:%M:%S')} free={fg:.1f}GiB swap_used={sw:.0f}MB peak_swap={peak:.0f}MB\n")
        if fg < 25 or sw > 8192:
            STOP["hit"] = f"free={fg:.1f}GiB swap_used={sw:.0f}MB"
            log("STOP RULE", STOP["hit"])
            p = CUR["proc"]
            if p and p.poll() is None: p.kill()
            return
        time.sleep(5)

def http(path, body=None, timeout=600):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r: return json.loads(r.read().decode())

def render_leg():
    args = [SERVER, "-m", GGUF, "-t", "4", "-tb", "4", "-c", "4096", "-ngl", "0", "-np", "1", "--jinja",
            "--no-webui", "--cache-ram", "0", "--reasoning-format", "deepseek", "--host", "127.0.0.1", "--port", str(PORT)]
    log("server start:", " ".join(args))
    p = subprocess.Popen(args, stdout=open(f"{OUT}/server.log", "w"), stderr=subprocess.STDOUT); CUR["proc"] = p
    t0 = time.time()
    while True:
        if p.poll() is not None: raise SystemExit(f"server exited rc={p.returncode} before health")
        try:
            if http("/health", timeout=5).get("status") == "ok": break
        except Exception: pass
        time.sleep(2)
    log(f"server healthy after {time.time()-t0:.1f}s pid={p.pid}")
    os.makedirs(f"{OUT}/rendered", exist_ok=True)
    try:
        with open(f"{OUT}/rendered-sha256.txt", "w") as shaf:
            for r in REQS:
                if STOP["hit"]: break
                prompt = http("/apply-template", {"messages": r["messages"], "chat_template_kwargs": {"enable_thinking": False}})["prompt"]
                open(f"{OUT}/rendered/{r['id']}.txt", "w").write(prompt)
                shaf.write(f"{hashlib.sha256(prompt.encode()).hexdigest()}  {r['id']}\n")
        log("rendered", len(os.listdir(f"{OUT}/rendered")))
    finally:
        p.send_signal(signal.SIGTERM)
        try: p.wait(60)
        except subprocess.TimeoutExpired: p.kill(); p.wait()
        CUR["proc"] = None; time.sleep(2)
        ps = subprocess.run(["pgrep", "-f", "llama-server"], capture_output=True, text=True).stdout.strip()
        log("server stopped rc", p.returncode, "pgrep llama-server:", ps or "none")
        if ps: raise SystemExit("llama-server still resident")

ARGS = ["--session", "--temp", "0.7", "--top-k", "40", "--top-p", "0.95", "--seed", "42", "-n", "512", "-c", "4096",
        "-t", "4", "--ubatch", "512", "--moe-stream", "--overlap", "--dense-weights", "anon", "--cache-mb", "1500", "--io-threads", "4"]

def gen_leg():
    if subprocess.run(["pgrep", "-f", "llama-server"], capture_output=True, text=True).stdout.strip():
        raise SystemExit("llama-server resident; refusing to start bmoe")
    resf = f"{OUT}/results.jsonl"
    done = {json.loads(l)["id"] for l in open(resf) if l.strip()} if os.path.exists(resf) else set()
    todo = [r for r in REQS if r["id"] not in done]
    log("gen todo", len(todo), "done", len(done))
    if not todo: return
    args = ["/usr/bin/time", "-l", BMOE, "-m", GGUF] + ARGS + ["--csv", f"{OUT}/session.csv"]
    log("bmoe start:", " ".join(args))
    p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=open(f"{OUT}/bmoe.stderr", "a"),
                         text=True, encoding="utf-8", errors="replace", bufsize=1)
    CUR["proc"] = p
    raw = open(f"{OUT}/session.stdout", "a")
    def readline():
        l = p.stdout.readline()
        if not l: raise SystemExit(f"bmoe stdout closed rc={p.poll()}")
        raw.write(l) if not l.startswith("BMOE_PROGRESS") and not l.startswith("BMOE_LOAD") else None
        return l
    while True:
        l = readline()
        if l.startswith("BMOE_READY"): log("READY", l.strip()); break
        if l.startswith("BMOE_ERROR"): raise SystemExit("bmoe error at load: " + l)
    for k, r in enumerate(todo):
        if STOP["hit"]: break
        prompt = open(f"{OUT}/rendered/{r['id']}.txt").read()
        req = json.dumps({"cmd": "generate", "id": k, "n_predict": 512, "think": False, "clear_kv": True, "prompt": prompt}, ensure_ascii=False)
        t0 = time.time(); p.stdin.write(req + "\n"); p.stdin.flush()
        res = None
        while True:
            l = readline()
            if l.startswith("BMOE_DONE"):
                res = json.loads(l[len("BMOE_DONE "):], strict=False); break
            if l.startswith("BMOE_ERROR"):
                res = {"error": l.strip()}; break
        total = time.time() - t0
        row = {"id": r["id"], "total_s": round(total, 2), **res}
        with open(resf, "a") as f: f.write(json.dumps(row, ensure_ascii=False) + "\n")
        log(r["id"], f"total={total:.1f}s", "n_prompt", res.get("n_prompt"), "tokens", res.get("tokens"), "tok_s", res.get("tok_s"),
            "prefill_s", res.get("prefill_s"), "err" if "error" in res else "", (res.get("text") or "")[:60].replace("\n", " "))
        if "error" in res and '"fatal":true' in res["error"]: break
    try:
        p.stdin.write('{"cmd":"close"}\n'); p.stdin.flush(); p.stdin.close()
    except Exception: pass
    try: p.wait(120)
    except subprocess.TimeoutExpired: p.kill(); p.wait()
    CUR["proc"] = None
    log("bmoe exited rc", p.returncode)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    log("items", len(REQS), f"free={free_gib():.1f}GiB swap_used={swap_used_mb():.0f}MB")
    threading.Thread(target=watchdog, daemon=True).start()
    legs = sys.argv[1:] or ["render", "gen"]
    if "render" in legs: render_leg()
    if "gen" in legs and not STOP["hit"]: gen_leg()
    log("DONE", "STOP=" + str(STOP["hit"]), f"free={free_gib():.1f}GiB swap_used={swap_used_mb():.0f}MB")
