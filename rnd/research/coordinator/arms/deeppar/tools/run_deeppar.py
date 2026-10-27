#!/usr/bin/env python3
"""DEEPPAR driver (criterion sha256 98028c0d...). Runs on the mini under <runner>/bin/run-heavy.
Leg 1: llama-server b11010 renders each item's messages (/apply-template, enable_thinking=false) and
completes the rendered string greedily (n_predict 64). Server is then stopped.
Leg 2: bmoe-cli v0.28.0 gets the same rendered string raw (-p, no --chatml/--no-think), -n 64.
Side: item 00 with --chatml --no-think on the P0-style probe text, -n 1 (prompt count only).
A watchdog enforces the stop rules (free disk < 25 GiB or swap used > 8 GB -> kill engine, mark STOP)."""
import json, os, subprocess, sys, time, threading, hashlib, urllib.request, re, signal

HOME = os.path.expanduser("~")
D = f"{HOME}/boar/kiln/deeppar"
OUT = f"{D}/out"
GGUF = f"{HOME}/boar/shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf"
SERVER = f"{HOME}/boar/spikes/llama-b11010/build-cpu/bin/llama-server"
BMOE = f"{HOME}/boar/spikes/bmoe-v028/out/host/bmoe-cli"
PORT = int(os.environ.get("DEEPPAR_PORT", "18093"))
ITEMS = sorted(f[:-5] for f in os.listdir(f"{D}/prompts") if f.endswith(".json"))
STOP = {"hit": None}
CUR = {"proc": None}

def log(*a):
    s = time.strftime("%H:%M:%S") + " " + " ".join(str(x) for x in a)
    print(s, flush=True)
    with open(f"{OUT}/run.log", "a") as f: f.write(s + "\n")

def free_gib():
    st = os.statvfs("/")
    return st.f_bavail * st.f_frsize / 2**30

def swap_used_mb():
    s = subprocess.run(["sysctl", "-n", "vm.swapusage"], capture_output=True, text=True).stdout
    m = re.search(r"used = ([\d.,]+)M", s)
    return float(m.group(1).replace(",", ".")) if m else -1

def watchdog():
    while True:
        fg, sw = free_gib(), swap_used_mb()
        if fg < 25 or sw > 8192:
            STOP["hit"] = f"free={fg:.1f}GiB swap_used={sw:.0f}MB"
            log("STOP RULE", STOP["hit"])
            p = CUR["proc"]
            if p and p.poll() is None: p.kill()
            return
        time.sleep(5)

def http(path, body=None, timeout=1800):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}",
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def server_leg():
    args = [SERVER, "-m", GGUF, "-t", "4", "-tb", "4", "-c", "4096", "-ngl", "0", "-np", "1", "--jinja",
            "--no-webui", "--cache-ram", "0", "--reasoning-format", "deepseek", "--host", "127.0.0.1", "--port", str(PORT)]
    log("server start:", " ".join(args))
    lf = open(f"{OUT}/server.log", "w")
    p = subprocess.Popen(args, stdout=lf, stderr=subprocess.STDOUT)
    CUR["proc"] = p
    t0 = time.time()
    while True:
        if p.poll() is not None: raise SystemExit(f"server exited rc={p.returncode} before health")
        try:
            if http("/health", timeout=5).get("status") == "ok": break
        except Exception: pass
        time.sleep(2)
    log(f"server healthy after {time.time()-t0:.1f}s pid={p.pid}")
    try:
        for it in ITEMS:
            if STOP["hit"]: break
            msgs = json.load(open(f"{D}/prompts/{it}.json"))["messages"]
            r = http("/apply-template", {"messages": msgs, "chat_template_kwargs": {"enable_thinking": False}})
            prompt = r["prompt"]
            open(f"{OUT}/{it}.rendered.txt", "w").write(prompt)
            t = time.time()
            c = http("/completion", {"prompt": prompt, "temperature": 0, "n_predict": 64, "cache_prompt": False,
                                     "return_tokens": True, "n_probs": 0})
            c["_wall_s"] = time.time() - t
            json.dump(c, open(f"{OUT}/{it}.server.json", "w"), indent=1)
            tm = c.get("timings", {})
            log(it, "server prompt_n", tm.get("prompt_n"), "pred_n", tm.get("predicted_n"),
                f"tok/s {tm.get('predicted_per_second', 0):.2f}", "sha12", hashlib.sha256(prompt.encode()).hexdigest()[:12])
    finally:
        p.send_signal(signal.SIGTERM)
        try: p.wait(60)
        except subprocess.TimeoutExpired: p.kill(); p.wait()
        CUR["proc"] = None
        time.sleep(2)
        ps = subprocess.run(["pgrep", "-f", "llama-server"], capture_output=True, text=True).stdout.strip()
        log("server stopped rc", p.returncode, "pgrep llama-server:", ps or "none")

KNOBS = ["-n", "64", "-c", "4096", "-t", "4", "--ubatch", "512", "--moe-stream", "--overlap", "--dense-weights", "anon",
         "--cache-mb", "1500", "--io-threads", "4"]

def bmoe_run(tag, prompt, extra, knobs=KNOBS):
    args = ["/usr/bin/time", "-l", BMOE, "-m", GGUF, "-p", prompt] + extra + knobs + ["--csv", f"{OUT}/{tag}.csv"]
    log(tag, "bmoe start", " ".join(a for a in args if a != prompt), "(-p <rendered>)")
    with open(f"{OUT}/{tag}.bmoe.stdout", "w") as so, open(f"{OUT}/{tag}.bmoe.stderr", "w") as se:
        t = time.time()
        p = subprocess.Popen(args, stdout=so, stderr=se)
        CUR["proc"] = p
        rc = p.wait()
        CUR["proc"] = None
    log(tag, f"bmoe rc={rc} wall={time.time()-t:.1f}s")
    return rc

def bmoe_leg():
    for it in ITEMS:
        if STOP["hit"]: break
        fp = f"{OUT}/{it}.rendered.txt"
        if not os.path.exists(fp): log(it, "no rendered prompt; skipped"); continue
        bmoe_run(it, open(fp).read(), [])

def side():
    if STOP["hit"]: return
    txt = open(f"{D}/probe-00-lan-exp-001.txt").read()
    k = list(KNOBS); k[1] = "1"
    bmoe_run("side-00-chatml", txt, ["--chatml", "--no-think"], k)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    log("items", ITEMS, f"free={free_gib():.1f}GiB swap_used={swap_used_mb():.0f}MB")
    threading.Thread(target=watchdog, daemon=True).start()
    legs = sys.argv[1:] or ["server", "bmoe", "side"]
    if "server" in legs: server_leg()
    if "bmoe" in legs: bmoe_leg()
    if "side" in legs: side()
    log("DONE", "STOP=" + str(STOP["hit"]), f"free={free_gib():.1f}GiB swap_used={swap_used_mb():.0f}MB")
