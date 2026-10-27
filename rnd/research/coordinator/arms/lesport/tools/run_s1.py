#!/usr/bin/env python3
"""LESPORT S1 (derived from run_s0.py; TAG env names outputs; env passes through) LESPORT S0 stage 3-4 runner (runs on the mini). usage: run_s0.py control|capped|uncapped [nprompts]"""
import sys, os, json, time, subprocess, glob, urllib.request, re, threading
H = os.path.expanduser("~"); R = H + "/boar/kiln/lesport-raw-s1"; os.makedirs(R, exist_ok=True)
MODEL = H + "/boar/shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf"
prompts = sorted(glob.glob(H + "/boar/kiln/deepspeed/prompts/*.rendered.txt"))
cfg = sys.argv[1]; TAG = os.environ.get("TAG", cfg); n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
def swap():
    o = subprocess.check_output(["sysctl", "-n", "vm.swapusage"]).decode()
    return float(re.search(r"used = ([\d.]+)M", o).group(1)) / 1024
def free_gib():
    s = os.statvfs("/"); return s.f_bavail * s.f_frsize / 2**30
def guard():
    if swap() > 8 or free_gib() < 25: raise SystemExit(f"KILL: swap {swap():.1f} free {free_gib():.1f}")
def rss_of(pid):
    try: return int(subprocess.check_output(["ps", "-o", "rss=", "-p", str(pid)]).split()[0]) / 2**20
    except Exception: return 0
class Peak(threading.Thread):
    def __init__(s, pid): super().__init__(daemon=True); s.pid = pid; s.max = 0; s.go = True
    def run(s):
        while s.go: s.max = max(s.max, rss_of(s.pid)); time.sleep(2)
out = {}
if cfg == "control":
    B = H + "/boar/spikes/llama-b11010/build-cpu/bin/llama-server"
    p = subprocess.Popen([B, "-m", MODEL, "-t", "4", "-c", "4096", "-np", "1", "--port", "8191", "--host", "127.0.0.1"],
                         stdout=open(R + "/control-server.log", "w"), stderr=subprocess.STDOUT)
    for _ in range(300):
        try: urllib.request.urlopen("http://127.0.0.1:8191/health", timeout=2).read(); break
        except Exception: time.sleep(2); guard()
    pk = Peak(p.pid); pk.start()
    for i, f in enumerate(prompts[:n]):
        guard(); pk.max = 0
        body = json.dumps({"prompt": open(f).read(), "n_predict": 128, "temperature": 0, "top_k": 1, "cache_prompt": False}).encode()
        r = json.load(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8191/completion", body, {"Content-Type": "application/json"}), timeout=900))
        t = r["timings"]; name = os.path.basename(f)[:2]
        open(f"{R}/control-{name}.txt", "w").write(r["content"])
        out[name] = dict(decode=t["predicted_per_second"], prefill=t["prompt_ms"] / 1000, foot=pk.max, ntok=r.get("tokens_predicted"))
        print(name, out[name], flush=True)
    pk.go = False; p.terminate(); p.wait()
else:
    B = H + "/boar/spikes/llama-omni/src/build-cpu/bin/llama-completion"
    extra = ["--moe-experts", H + "/boar/spikes/llama-omni/experts", "--moe-slot-bank", sys.argv[3]] if cfg.startswith("capped") else []
    mdl = MODEL if os.environ.get("FULLGGUF") else H + "/boar/spikes/llama-omni/stripped.gguf"
    for i, f in enumerate(prompts[:n]):
        guard(); name = os.path.basename(f)[:2]
        cmd = ["/usr/bin/time", "-l", B, "-m", mdl] + extra + ["-p", open(f).read(), "-n", "128", "-c", "4096", "-t", "4", "--temp", "0", "--top-k", "1", "-no-cnv", "--no-display-prompt"] + (["--no-mmap"] if os.environ.get("NOMMAP") else [])
        pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=open(f"{R}/{TAG}-{name}.err", "w"))
        pk = Peak(pr.pid); pk.start()
        txt = pr.communicate(timeout=1500)[0].decode(); pk.go = False
        err = open(f"{R}/{TAG}-{name}.err").read()
        open(f"{R}/{TAG}-{name}.txt", "w").write(txt)
        m = re.search(r"(\d+)\s+peak memory footprint", err); foot = int(m.group(1)) / 2**30 if m else 0
        pe = re.search(r"prompt eval time =\s+([\d.]+) ms", err); ev = re.search(r"eval time =.*?([\d.]+) tokens per second", err.split("prompt eval time")[-1]) if pe else None
        out[name] = dict(decode=float(ev.group(1)) if ev else 0, prefill=float(pe.group(1)) / 1000 if pe else 0, foot=foot, rssmax=(int(re.search(r"(\d+)\s+maximum resident set size",err).group(1))/2**30 if "maximum resident" in err else 0), rc=pr.returncode)
        print(name, out[name], flush=True)
json.dump(out, open(f"{R}/{TAG}.json", "w"))
