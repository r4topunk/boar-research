#!/usr/bin/env python3
"""DEEPSPEED driver (criterion sha256 c2e101d3...). Runs on the mini under <runner>/bin/run-heavy.
For each item (10 DEEPPAR rendered prompts, raw -p), configs K0..K4 back to back, each a fresh
bmoe-cli process under /usr/bin/time -l. Watchdog: free disk < 25 GiB or swap used > 8 GB -> kill, STOP."""
import os, subprocess, sys, time, threading, re

HOME = os.path.expanduser("~")
D = f"{HOME}/boar/kiln/deepspeed"
OUT = f"{D}/out"
GGUF = f"{HOME}/boar/shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf"
BMOE = f"{HOME}/boar/spikes/bmoe-v028/out/host/bmoe-cli"
ITEMS = sorted(f[:-len(".rendered.txt")] for f in os.listdir(f"{D}/prompts") if f.endswith(".rendered.txt"))
BASE = ["-n", "128", "-c", "4096", "-t", "4", "--ubatch", "512", "--moe-stream", "--overlap",
        "--dense-weights", "anon", "--cache-mb", "1500", "--io-threads", "4"]
CONFIGS = [("K0", []), ("K1", ["--ngram"]), ("K2", ["--ngram", "--draft", "6"]),
           ("K3", ["--prefetch", "2"]), ("K4", ["--ngram", "--prefetch", "2"])]
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
    peak = 0.0; n = 0
    while True:
        fg, sw = free_gib(), swap_used_mb(); peak = max(peak, sw); n += 1
        if n % 60 == 0: log(f"watchdog free={fg:.1f}GiB swap_used={sw:.0f}MB swap_peak={peak:.0f}MB")
        if fg < 25 or sw > 8192:
            STOP["hit"] = f"free={fg:.1f}GiB swap_used={sw:.0f}MB"
            log("STOP RULE", STOP["hit"])
            p = CUR["proc"]
            if p and p.poll() is None: p.kill()
            return
        time.sleep(5)

def other_engine():
    ps = subprocess.run(["pgrep", "-fl", "llama-server|llama-cli|bmoe-cli"], capture_output=True, text=True).stdout.strip()
    return ps

def run(tag, prompt, knobs):
    args = ["/usr/bin/time", "-l", BMOE, "-m", GGUF, "-p", prompt] + BASE + knobs + ["--csv", f"{OUT}/{tag}.csv"]
    log(tag, "start", " ".join(a for a in args if a != prompt), "(-p <rendered>)")
    with open(f"{OUT}/{tag}.stdout", "w") as so, open(f"{OUT}/{tag}.stderr", "w") as se:
        t = time.time()
        p = subprocess.Popen(args, stdout=so, stderr=se); CUR["proc"] = p
        rc = p.wait(); CUR["proc"] = None
    log(tag, f"rc={rc} wall={time.time()-t:.1f}s free={free_gib():.1f}GiB swap_used={swap_used_mb():.0f}MB")
    return rc

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    oe = other_engine()
    log("items", ITEMS, f"free={free_gib():.1f}GiB swap_used={swap_used_mb():.0f}MB other_engine={oe or 'none'}")
    if oe: log("STOP: other engine running"); sys.exit(3)
    threading.Thread(target=watchdog, daemon=True).start()
    only = sys.argv[1:]  # optional: list of tags to (re)run, e.g. 03-...__K1
    for it in ITEMS:
        prompt = open(f"{D}/prompts/{it}.rendered.txt").read()
        for k, knobs in CONFIGS:
            if STOP["hit"]: break
            tag = f"{it}__{k}"
            if only and tag not in only: continue
            run(tag, prompt, knobs)
    log("DONE", "STOP=" + str(STOP["hit"]), f"free={free_gib():.1f}GiB swap_used={swap_used_mb():.0f}MB")
