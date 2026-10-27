#!/usr/bin/env python3
"""MOESCREEN (Kiln 2026-10-07): Anvil server-anchors.py with only instrumentation added: free random port (no shared port),
llama-server RSS sampled with ps every 250 ms (per-item and run peak), server --version, prefill tok/s, finish_reason and
reasoning-token count recorded in the trace. Prompt, body, sampler, max_tokens 450, server flags: unchanged.

Closed-book anchors for a local GGUF through llama-server (Anvil out-of-kit front; runs on the Mac mini under Kiln's heavy lock).

Same recipe as boar-eval harness/anchors.mjs (system prompt anchor.v1 = reference.v1 minus the web lines, user = the bare
question, no tools) and the app sampler of Kiln's serve-bench.py (temperature 0.7, top_k 40, top_p 0.95, min_p 0.05, seed 42),
max_tokens 450, thinking OFF (chat_template_kwargs enable_thinking=false; any <think>…</think> block is stripped and flagged).
Writes EvalTrace v1 (one per item) so harness/judge.mjs judges it like any run. Run every model, incl. the Qwen3-4B
control, through this script so the harness is identical.

Usage (mini):
  python3 server-anchors.py --name qwen3-4b --gguf <runner>/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf \
      --server <runner>/spikes/llama-b11010/build-cpu/bin/llama-server --questions <questions.public.jsonl> \
      --anchors-mjs <boar-eval/harness/anchors.mjs> --ids-file slice-ids.txt --out runs/<name>.traces.jsonl [--threads 4] [--ctx 4096]
Stdlib only. Resumable (items already in --out are skipped). Prints decode tok/s per item (desktop CPU, not a phone number).
"""
import argparse, hashlib, json, os, re, signal, subprocess, sys, time, urllib.request

ap = argparse.ArgumentParser()
for k in ("--name", "--gguf", "--server", "--questions", "--anchors-mjs", "--ids-file", "--out"): ap.add_argument(k, required=True)
ap.add_argument("--threads", default="4"); ap.add_argument("--ctx", default="4096"); ap.add_argument("--port", default="0")
a = ap.parse_args()
import socket, threading
if a.port == "0":
    _s = socket.socket(); _s.bind(("127.0.0.1", 0)); a.port = str(_s.getsockname()[1]); _s.close()
_v = subprocess.run([os.path.expanduser(a.server), "--version"], capture_output=True, text=True)
SERVER_VERSION = (_v.stdout + _v.stderr).strip().splitlines()[0]

src = open(os.path.expanduser(a.anchors_mjs)).read()
SYSTEM = re.search(r"export const ANCHOR_SYSTEM = `([\s\S]*?)`;", src).group(1)
psha = hashlib.sha256(SYSTEM.encode()).hexdigest()
ids = open(a.ids_file).read().strip().split(",")
qs = {}
for l in open(os.path.expanduser(a.questions)):
    if l.strip():
        q = json.loads(l); qs[q["id"]] = q
done = set()
if os.path.exists(a.out):
    done = {json.loads(l)["itemId"] for l in open(a.out) if l.strip()}
gguf = os.path.expanduser(a.gguf)
h = hashlib.sha256()
with open(gguf, "rb") as f:
    for b in iter(lambda: f.read(1 << 24), b""): h.update(b)
gsha = h.hexdigest()
print(f"{a.name}: {len(ids)} items ({len(done)} done) anchor.v1 sha {psha[:8]} gguf sha {gsha[:16]}", flush=True)

T_LAUNCH = time.time()
srv = subprocess.Popen([os.path.expanduser(a.server), "-m", gguf, "--port", a.port, "-t", a.threads, "-c", a.ctx, "-np", "1",
                        "--jinja", "--no-webui"], stdout=subprocess.DEVNULL, stderr=open(a.out + ".server.log", "w"))
base = f"http://127.0.0.1:{a.port}"
try:
    for _ in range(600):
        try:
            if json.load(urllib.request.urlopen(base + "/health", timeout=2)).get("status") == "ok": break
        except Exception: time.sleep(1)
    else: sys.exit("server did not come up")
    load_s = time.time() - T_LAUNCH
    peak = {"run": 0, "win": 0}; stop_flag = threading.Event()
    def rss_kb():
        try: return int(subprocess.run(["ps", "-o", "rss=", "-p", str(srv.pid)], capture_output=True, text=True).stdout.strip() or 0)
        except Exception: return 0
    def sampler():
        while not stop_flag.is_set():
            kb = rss_kb(); peak["run"] = max(peak["run"], kb); peak["win"] = max(peak["win"], kb); time.sleep(0.25)
    idle_kb = rss_kb(); threading.Thread(target=sampler, daemon=True).start()
    print(f"server up port {a.port} load {load_s:.1f}s idle_rss_mb {idle_kb//1024} version {SERVER_VERSION}", flush=True)
    for i in ids:
        if i in done or i not in qs: continue
        q = qs[i]
        body = {"messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": q["question"]}], "max_tokens": 450,
                "temperature": 0.7, "top_k": 40, "top_p": 0.95, "min_p": 0.05, "seed": 42, "cache_prompt": False,
                "chat_template_kwargs": {"enable_thinking": False}}
        peak["win"] = 0
        t0 = time.time()
        r = json.load(urllib.request.urlopen(urllib.request.Request(base + "/v1/chat/completions", data=json.dumps(body).encode(),
                                             headers={"content-type": "application/json"}), timeout=900))
        wall = time.time() - t0
        msg = r["choices"][0]["message"]; raw = (msg.get("content") or "")
        warn = []
        if "<think>" in raw or msg.get("reasoning_content"):
            warn.append("thinking-present"); raw = re.sub(r"<think>[\s\S]*?</think>", "", raw)
        tim = r.get("timings", {})
        trace = {"protocol": "1.0.0", "runId": f"outofkit-server-{a.name}", "itemId": i, "question": q["question"],
                 "engine": {"commit": "n/a-anchor", "arm": f"anchor-local-{a.name}", "dirty": False},
                 "runtime": {"adapter": "local-anchor-server", "host": os.uname().nodename, "model": a.name,
                             "sampler": {k: body[k] for k in ("temperature", "top_k", "top_p", "min_p", "seed")},
                             "versions": {"prompt": "anchor.v1", "promptSha256": psha, "llama-server": SERVER_VERSION, "gguf": os.path.basename(gguf), "gguf.sha256": gsha, "server": a.server}},
                 "config": {"commit": "n/a-anchor", "arm": f"anchor-local-{a.name}", "modelId": a.name,
                            "settings": {"promptVersion": "anchor.v1", "tools": [], "web": False, "thinking": False}, "kit": [], "device": None},
                 "route": {"task": None, "tier": None, "outcome": "answered", "reasonCodes": [], "finishReason": r["choices"][0].get("finish_reason")},
                 "retrieval": {"raw": [], "kept": [], "dropped": []},
                 "answer": {"text": raw.strip(), "cited": [], "shown": [], "declined": False, "weakSources": False, "warnings": warn},
                 "timing": {"ttftMs": None, "totalMs": round(wall * 1000), "retrievalMs": None, "prefillMs": tim.get("prompt_ms"),
                            "prefillTokPerSec": tim.get("prompt_per_second"), "decodeMs": tim.get("predicted_ms"), "decodeTokPerSec": tim.get("predicted_per_second"), "reasoningChars": len(msg.get("reasoning_content") or ""), "modelLoadMs": round(load_s * 1000), "promptTokens": tim.get("prompt_n"), "outputTokens": tim.get("predicted_n")},
                 "resources": {"peakRssMb": round(peak["win"] / 1024), "idleRssMb": round(idle_kb / 1024)}, "events": [], "error": None if raw.strip() else "empty-answer", "createdAt": time.strftime("%Y-%m-%dT%H:%M:%S")}
        with open(a.out, "a") as f: f.write(json.dumps(trace, ensure_ascii=False) + "\n")
        print(f"{i} {wall:.1f}s pp {tim.get('prompt_n')}@{tim.get('prompt_per_second', 0):.1f} tg {tim.get('predicted_n')}@{tim.get('predicted_per_second', 0):.2f} tok/s rssMB {round(peak['win']/1024)} fin {r['choices'][0].get('finish_reason')} {'EMPTY ' if not raw.strip() else ''}{' '.join(warn)} {raw.strip()[:60]!r}", flush=True)
    stop_flag.set(); print(f"RUN DONE peak_rss_mb {round(peak['run']/1024)}", flush=True)
finally:
    srv.send_signal(signal.SIGTERM); srv.wait(timeout=30)
