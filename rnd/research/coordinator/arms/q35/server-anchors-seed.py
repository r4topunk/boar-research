#!/usr/bin/env python3
"""Closed-book anchors for a local GGUF through llama-server (Anvil out-of-kit front; runs on the Mac mini under Kiln's heavy lock).

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
ap.add_argument("--seed", type=int, default=42); ap.add_argument("--threads", default="4"); ap.add_argument("--ctx", default="4096"); ap.add_argument("--port", default="18431")
a = ap.parse_args()

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

srv = subprocess.Popen([os.path.expanduser(a.server), "-m", gguf, "--port", a.port, "-t", a.threads, "-c", a.ctx, "-np", "1",
                        "--jinja", "--no-webui"], stdout=subprocess.DEVNULL, stderr=open(a.out + ".server.log", "w"))
base = f"http://127.0.0.1:{a.port}"
try:
    for _ in range(600):
        try:
            if json.load(urllib.request.urlopen(base + "/health", timeout=2)).get("status") == "ok": break
        except Exception: time.sleep(1)
    else: sys.exit("server did not come up")
    for i in ids:
        if i in done or i not in qs: continue
        q = qs[i]
        body = {"messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": q["question"]}], "max_tokens": 450,
                "temperature": 0.7, "top_k": 40, "top_p": 0.95, "min_p": 0.05, "seed": a.seed, "cache_prompt": False,
                "chat_template_kwargs": {"enable_thinking": False}}
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
                             "versions": {"prompt": "anchor.v1", "promptSha256": psha, "gguf": os.path.basename(gguf), "gguf.sha256": gsha, "server": a.server}},
                 "config": {"commit": "n/a-anchor", "arm": f"anchor-local-{a.name}", "modelId": a.name,
                            "settings": {"promptVersion": "anchor.v1", "tools": [], "web": False, "thinking": False}, "kit": [], "device": None},
                 "route": {"task": None, "tier": None, "outcome": "answered", "reasonCodes": []},
                 "retrieval": {"raw": [], "kept": [], "dropped": []},
                 "answer": {"text": raw.strip(), "cited": [], "shown": [], "declined": False, "weakSources": False, "warnings": warn},
                 "timing": {"ttftMs": None, "totalMs": round(wall * 1000), "retrievalMs": None, "prefillMs": tim.get("prompt_ms"),
                            "decodeTokPerSec": tim.get("predicted_per_second"), "promptTokens": tim.get("prompt_n"), "outputTokens": tim.get("predicted_n")},
                 "resources": None, "events": [], "error": None if raw.strip() else "empty-answer", "createdAt": time.strftime("%Y-%m-%dT%H:%M:%S")}
        with open(a.out, "a") as f: f.write(json.dumps(trace, ensure_ascii=False) + "\n")
        print(f"{i} {wall:.1f}s decode {tim.get('predicted_per_second', 0):.1f} tok/s {'EMPTY ' if not raw.strip() else ''}{' '.join(warn)} {raw.strip()[:60]!r}", flush=True)
finally:
    srv.send_signal(signal.SIGTERM); srv.wait(timeout=30)
