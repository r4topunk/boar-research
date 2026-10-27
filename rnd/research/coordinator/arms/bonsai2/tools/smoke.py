#!/usr/bin/env python3
"""BONSAI2 S0 smoke: start one llama-server (port 8097), time load, send 5 plain questions,
record timings + RSS, stop the server. Usage:
  smoke.py <label> <server_bin> <model.gguf> <items.json> <out.jsonl> '<extra request json>' [extra server args...]
"""
import json, subprocess, sys, time, urllib.request, os, signal
label, binp, model, items_p, out_p, extra_req = sys.argv[1:7]
srv_args = sys.argv[7:]
PORT = 8097
cmd = [binp, "-m", model, "-c", "4096", "-t", "8", "--port", str(PORT), "--host", "127.0.0.1"] + srv_args
log = open(out_p + ".server.log", "w")
t0 = time.time()
p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
def get(path):
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}{path}", timeout=5) as r:
        return r.status, r.read()
load_s = None
while time.time() - t0 < 600:
    if p.poll() is not None: break
    try:
        st, _ = get("/health")
        if st == 200: load_s = time.time() - t0; break
    except Exception: pass
    time.sleep(0.25)
def rss_gb():
    o = subprocess.run(["ps", "-o", "rss=", "-p", str(p.pid)], capture_output=True, text=True).stdout.strip()
    return round(int(o) / 1024 / 1024, 3) if o else None
out = open(out_p, "w")
meta = {"label": label, "cmd": cmd, "load_s": load_s, "rss_gb_after_load": rss_gb() if load_s else None, "exit": p.poll()}
out.write(json.dumps({"meta": meta}) + "\n"); out.flush()
if load_s is not None:
    for it in json.load(open(items_p)):
        req = {"messages": [{"role": "user", "content": it["question"]}], "max_tokens": 256, "stream": False}
        req.update(json.loads(extra_req))
        t = time.time()
        try:
            r = urllib.request.Request(f"http://127.0.0.1:{PORT}/v1/chat/completions", data=json.dumps(req).encode(),
                                       headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(r, timeout=1800) as resp: body = json.loads(resp.read())
            err = None
        except Exception as e:
            body, err = None, repr(e)
        rec = {"id": it["id"], "request": req, "response": body, "error": err, "wall_s": round(time.time() - t, 2), "rss_gb": rss_gb()}
        out.write(json.dumps(rec) + "\n"); out.flush()
p.send_signal(signal.SIGTERM)
try: p.wait(30)
except Exception: p.kill()
print("done", label, "load_s", load_s)
