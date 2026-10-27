#!/usr/bin/env python3
"""LESPORT-L1 generation driver (criterion sha256 5756268c...). Runs on the mini under <runner>/bin/run-heavy.
Prompts: the 57 DEEPPAR-L1 rendered strings (sha-verified), no re-render. Engine: llama-omni fork llama-completion (CPU),
LES experts dir, bank 1280, lookahead prefetch, -t 4 -c 4096, one process per item (as S1), sampler of the control.
usage: python3 run_l1.py [N_ITEMS|all]   (resumable: appends to out/results.jsonl)"""
import json, os, subprocess, sys, time, threading, re, hashlib
H = os.path.expanduser("~"); D = f"{H}/boar/kiln/lesport-l1"; OUT = f"{D}/out"; os.makedirs(OUT, exist_ok=True)
REND = f"{H}/boar/kiln/deeppar-l1/out/rendered"
GGUF = f"{H}/boar/shared-models/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf"
BIN = f"{H}/boar/spikes/llama-omni/src/build-cpu/bin/llama-completion"
EXPERTS = f"{H}/boar/spikes/llama-omni/experts"
REQS = [json.loads(l)["id"] for l in open(f"{H}/boar/kiln/deeppar-l1/requests.jsonl") if l.strip()]
STOP = {"hit": None}; CUR = {"proc": None}
def log(*a):
    s = time.strftime("%H:%M:%S") + " " + " ".join(str(x) for x in a); print(s, flush=True)
    open(f"{OUT}/run.log", "a").write(s + "\n")
def free_gib(): st = os.statvfs("/"); return st.f_bavail * st.f_frsize / 2**30
def swap_mb():
    m = re.search(r"used = ([\d.,]+)M", subprocess.run(["sysctl", "-n", "vm.swapusage"], capture_output=True, text=True).stdout)
    return float(m.group(1).replace(",", ".")) if m else -1
def other_engine():
    ps = subprocess.run(["ps", "-axo", "args="], capture_output=True, text=True).stdout.splitlines()
    return [p for p in ps if re.search(r"llama-server|bmoe|llama-cli|llama-completion|llama-bench", p) and "port 8094" not in p and "grep" not in p and "lesport-l1" not in p and "run_l1.py" not in p and BIN not in p]
def watchdog():
    peak = 0
    while True:
        fg, sw = free_gib(), swap_mb(); peak = max(peak, sw)
        open(f"{OUT}/watch.txt", "w").write(f"{time.strftime('%H:%M:%S')} free={fg:.1f}GiB swap_used={sw:.0f}MB peak_swap={peak:.0f}MB\n")
        mn = f"{OUT}/watch.min"; 
        if fg < 25 or sw > 8192:
            STOP["hit"] = f"free={fg:.1f}GiB swap_used={sw:.0f}MB"; log("STOP RULE", STOP["hit"])
            p = CUR["proc"]
            if p and p.poll() is None: p.kill()
            return
        time.sleep(5)
def rss_gib(pid):
    try: return int(subprocess.check_output(["ps", "-o", "rss=", "-p", str(pid)]).split()[0]) / 2**20
    except Exception: return 0
class Peak(threading.Thread):
    def __init__(s, pid): super().__init__(daemon=True); s.pid = pid; s.max = 0; s.go = True
    def run(s):
        while s.go: s.max = max(s.max, rss_gib(s.pid)); time.sleep(2)
if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    sel = REQS if arg == "all" else REQS[:int(arg)]
    resf = f"{OUT}/results.jsonl"
    done = {json.loads(l)["id"] for l in open(resf) if l.strip()} if os.path.exists(resf) else set()
    log("items", len(sel), "done", len(done), f"free={free_gib():.1f}GiB swap={swap_mb():.0f}MB")
    oe = other_engine()
    if oe: raise SystemExit("other engine running: " + str(oe))
    threading.Thread(target=watchdog, daemon=True).start()
    env = dict(os.environ, LLAMA_MOE_LOOKAHEAD_PREFETCH="1")
    n_ok = 0; t_start = time.time()
    for k, iid in enumerate(sel):
        if iid in done: continue
        if STOP["hit"]: break
        f = f"{REND}/{iid}.txt"
        cmd = ["/usr/bin/time", "-l", BIN, "-m", GGUF, "--moe-experts", EXPERTS, "--moe-slot-bank", "1280", "--no-mmap",
               "-t", "4", "-c", "4096", "--temp", "0.7", "--top-k", "40", "--top-p", "0.95", "--min-p", "0.05", "--seed", "42",
               "-n", "512", "-f", f, "-no-cnv", "--no-display-prompt"]
        errf = f"{OUT}/{iid}.err"; t0 = time.time()
        pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=open(errf, "w"), env=env); CUR["proc"] = pr
        pk = Peak(pr.pid); pk.start()
        try: txt = pr.communicate(timeout=900)[0].decode("utf-8", "replace")
        except subprocess.TimeoutExpired: pr.kill(); txt = ""; log(iid, "TIMEOUT")
        pk.go = False; CUR["proc"] = None; wall = time.time() - t0
        err = open(errf).read()
        open(f"{OUT}/{iid}.raw.txt", "w").write(txt)
        def g(rx, s=err, i=1):
            m = re.search(rx, s); return float(m.group(i)) if m else None
        pe = re.search(r"prompt eval time =\s+([\d.]+) ms /\s+(\d+) tokens", err)
        ev = re.search(r"\n[^\n]*\beval time =\s+([\d.]+) ms /\s+(\d+) runs.*?([\d.]+) tokens per second", err.split("prompt eval time")[-1]) if pe else None
        row = dict(id=iid, rc=pr.returncode, text=txt, wall_s=round(wall, 2),
                   prefill_s=float(pe.group(1)) / 1000 if pe else None, n_prompt=int(pe.group(2)) if pe else None,
                   out_tokens=int(ev.group(2)) if ev else None, tok_s=float(ev.group(3)) if ev else None,
                   load_s=(g(r"load time =\s+([\d.]+) ms") or 0) / 1000,
                   rss_gib=(g(r"(\d+)\s+maximum resident set size") or 0) / 2**30, footprint_gib=(g(r"(\d+)\s+peak memory footprint") or 0) / 2**30,
                   rss_poll_gib=pk.max, prompt_sha=hashlib.sha256(open(f, "rb").read()).hexdigest())
        open(resf, "a").write(json.dumps(row, ensure_ascii=False) + "\n")
        log(iid, f"wall={wall:.1f}s rc={pr.returncode} n_prompt={row['n_prompt']} out={row['out_tokens']} tok_s={row['tok_s']} prefill_s={row['prefill_s']} rss={row['rss_gib']:.2f}", repr(txt[:60]))
        if pr.returncode != 0 or not txt.strip(): n_ok += 0
        if k + 1 == 3 or (k + 1) % 10 == 0: log(f"CHECKPOINT after {k+1}: elapsed {time.time()-t_start:.0f}s, s/item {(time.time()-t_start)/(k+1):.1f}, projected {(time.time()-t_start)/(k+1)*len(sel)/60:.0f} min")
    log("DONE STOP=" + str(STOP["hit"]), f"free={free_gib():.1f}GiB swap={swap_mb():.0f}MB")
