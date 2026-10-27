"""PACKROUTE-2 stage 0a: the claim 4B as a zero-shot pack classifier (criterion sha d67fd81c…; 0 judge / 0 paid; MacBook).
Run (nohup):  python3 -I classify.py [--wording v1|v2] [--aggregate-only]
- Starts the 4B llama-server (claim GGUF, CPU build b11010, the adapter's flags) unless a 4B job is running (then waits);
  never touches the :8094 detector. Stops the server it started.
- Prompt = system (role + installed non-kit packs from tools/pack_descriptions[.v2].json + none semantics + answer
  format) + user (the question). /v1/chat/completions, temperature 0, seed 42, max_tokens 16, cache_prompt false (cold).
- Resumable: items already in an output file are skipped.
- Outputs: runs/routes-st180[.v2].jsonl, runs/routes-v01[.v2].jsonl (public: id, label, choice, out, ms);
  blind/bench-v02/runs-packs/packroute2-v02[.v2].routes.jsonl (script-only: id, choice, ms ONLY);
  runs/routes-cached20[.v2].jsonl (prefix-cached latency on 20 public items + identity vs cold);
  aggregates/accuracy[.v2].json. Log (runs/classify[.v2].log): ids, choices, ms for public items; counts only for v0.2.
"""
import hashlib, json, os, re, sqlite3, subprocess, sys, time, urllib.request, statistics as stt
from collections import Counter, defaultdict

ROOT = "<workspace>"
ARM = f"{ROOT}/rnd/research/coordinator/arms/packroute2"; PR = f"{ROOT}/rnd/research/coordinator/arms/packroute"
B2 = f"{ROOT}/blind/bench-v02/runs-packs"
MODEL = f"{ROOT}/shared-models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf"
BIN = f"{ROOT}/spikes/llama-b11010-cpu/bin/llama-server"
PORT = 8137
FLAGS = ["-t", "4", "-tb", "4", "-c", "4096", "-ngl", "0", "-np", "1", "--jinja", "--no-webui", "--cache-ram", "0",
         "--reasoning-format", "deepseek", "--host", "127.0.0.1", "--port", str(PORT)]
SERVER_LOG = os.environ.get("PR2_SERVER_LOG", "/dev/null")  # llama-server log kept out of rnd/
PACKS = ["qa-travel-se", "qa-ethereum-se", "qa-bitcoin-se", "qa-health-se", "qa-outdoors-se",
         "boar-firstaid-en", "boar-medlineplus-en", "boar-factbook", "boar-simplewiki-en"]
SE = {p for p in PACKS if p.startswith("qa-")}

args = sys.argv[1:]
W = args[args.index("--wording") + 1] if "--wording" in args else "v1"
SUF = "" if W == "v1" else f".{W}"
DESC = f"{ARM}/tools/pack_descriptions{SUF}.json"
OUT_ST, OUT_V01 = f"{ARM}/runs/routes-st180{SUF}.jsonl", f"{ARM}/runs/routes-v01{SUF}.jsonl"
OUT_V02 = f"{B2}/packroute2-v02{SUF}.routes.jsonl"
OUT_C20 = f"{ARM}/runs/routes-cached20{SUF}.jsonl"
LOG = f"{ARM}/runs/classify{SUF}.log"
AGG = f"{ARM}/aggregates/accuracy{SUF}.json"
os.makedirs(f"{ARM}/runs", exist_ok=True); os.makedirs(f"{ARM}/aggregates", exist_ok=True); os.makedirs(B2, exist_ok=True)
logf = open(LOG, "a")
def log(m): logf.write(time.strftime("%H:%M:%S ") + m + "\n"); logf.flush()
load = lambda f: [json.loads(l) for l in open(f) if l.strip()]

# ------------------------------------------------------------------ prompt
D = json.load(open(DESC))
def pack_line(pid, v):
    if isinstance(v, str): return f"- {pid}: {v}"
    ex = "; ".join(f'"{e}"' for e in v["examples"])
    return f"- {pid}: {v['description']} Example questions: {ex}"
SYSTEM = ("You route questions for an offline research assistant. Its base library (travel guides and crypto documents) is "
          "always searched. These extra knowledge packs are installed:\n"
          + "\n".join(pack_line(p, D["packs"][p]) for p in PACKS)
          + f"\n- none: {D['none']}\n\n"
          "Choose the one pack most likely to hold the answer to the user's question. "
          "Reply with exactly one pack id or none, and nothing else.")
PROMPT_SHA = hashlib.sha256(SYSTEM.encode()).hexdigest()
VALID = set(PACKS) | {"none"}
def parse(out):
    s = out.strip().strip("`\"'*. \n").strip().lower()
    return s if s in VALID else "invalid"

# ------------------------------------------------------------------ server
def pg(pat):
    r = subprocess.run(["pgrep", "-fl", pat], capture_output=True, text=True); return [l for l in r.stdout.splitlines() if l.strip()]
def other_4b_jobs(own_pid=None):
    jobs = [l for l in pg("llama-server.*Qwen3-4B") if not own_pid or not l.startswith(f"{own_pid} ")]
    return jobs + pg("adapter.ts")
def http(path, body=None, timeout=600):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r: return json.loads(r.read())
proc = None
def start_server():
    global proc
    while other_4b_jobs():
        log("a 4B job is running; waiting 60 s"); time.sleep(60)
    proc = subprocess.Popen([BIN, "-m", MODEL, *FLAGS], stdout=open(SERVER_LOG, "a"), stderr=subprocess.STDOUT)
    t0 = time.time()
    while True:
        if proc.poll() is not None: log("FATAL llama-server exited during load"); sys.exit(1)
        try:
            if http("/health", timeout=5).get("status") == "ok": break
        except Exception: pass
        if time.time() - t0 > 600: proc.kill(); log("FATAL server not healthy"); sys.exit(1)
        time.sleep(1)
    log(f"server up pid {proc.pid} in {time.time() - t0:.1f}s")
def stop_server():
    if proc and proc.poll() is None: proc.terminate(); proc.wait(timeout=60); log("server stopped")

def classify(q, cache):
    body = {"messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": q}], "stream": False,
            "max_tokens": 16, "temperature": 0, "seed": 42, "cache_prompt": cache}
    t = time.perf_counter(); r = http("/v1/chat/completions", body); ms = (time.perf_counter() - t) * 1000
    out = r["choices"][0]["message"].get("content") or ""; tm = r.get("timings", {})
    return out, round(ms, 1), {"prompt_n": tm.get("prompt_n"), "prompt_ms": round(tm.get("prompt_ms", 0), 1), "predicted_n": tm.get("predicted_n")}

# ------------------------------------------------------------------ items
st = load(f"{PR}/runs/st180.questions.jsonl")
v01 = load(f"{ROOT}/boar-eval/bench/v0.1/questions.public.jsonl")
def run_set(items, out, public, label=None):
    done = {x["id"] for x in load(out)} if os.path.exists(out) else set()
    todo = [it for it in items if it["id"] not in done]
    if not todo: return
    with open(out, "a") as f:
        for it in todo:
            o, ms, tm = classify(it["question"], False); c = parse(o)
            if public:
                f.write(json.dumps({"id": it["id"], **({"label": label(it)} if label else {}), "choice": c, "out": o, "ms": ms, **tm}) + "\n")
                log(f"{it['id']} {c} {ms}")
            else:
                f.write(json.dumps({"id": it["id"], "choice": c, "ms": ms}) + "\n")
            f.flush()
    if not public: log(f"v0.2 batch done: {len(todo)} items")

def main_run():
    log(f"start wording {W} prompt sha {PROMPT_SHA}")
    start_server()
    try:
        http("/v1/chat/completions", {"messages": [{"role": "user", "content": "Say ok."}], "max_tokens": 2, "temperature": 0, "cache_prompt": False})  # warm-up (not counted)
        run_set(st, OUT_ST, True, label=lambda it: it["pack"])
        run_set(v01, OUT_V01, True)
        v02 = load(f"{ROOT}/blind/bench-v02/live/v0.2/questions.v02-new.jsonl")  # script-only
        run_set(v02, OUT_V02, False); del v02
        if not (os.path.exists(OUT_C20) and len(load(OUT_C20)) >= 20):
            cold = {x["id"]: x for x in load(OUT_ST)}
            pick = [it for p in PACKS for it in [x for x in st if x["pack"] == p][:2]] + v01[:2]
            classify("What is the capital of France?", True)  # primes the cached prefix (not counted)
            with open(OUT_C20, "w") as f:
                for it in pick:
                    o, ms, tm = classify(it["question"], True); c = parse(o)
                    ref = cold.get(it["id"]) or next((x for x in load(OUT_V01) if x["id"] == it["id"]), None)
                    f.write(json.dumps({"id": it["id"], "choice": c, "cold_choice": ref["choice"], "same": c == ref["choice"], "ms": ms, "cold_ms": ref["ms"], **tm}) + "\n")
                    log(f"cached {it['id']} {c} {ms}")
    finally:
        stop_server()

# ------------------------------------------------------------------ kit `none` set (step0.py G1_none logic, recomputed)
_LIB = re.compile(r"^[^:]{2,40}:\s+")
bare = lambda t: _LIB.sub("", str(t or ""))
def pub(p): return f"{ROOT}/shared-data/packs/{'wave2' if p in ('boar-factbook', 'boar-simplewiki-en') else 'wave1'}/{p}.sqlite"
dbs = {p: sqlite3.connect(f"file:{pub(p)}?mode=ro", uri=True) for p in PACKS}
def gold_in_wave(g):
    t = bare(g.partition("#")[0])
    for db in dbs.values():
        if db.execute("SELECT 1 FROM articles WHERE title = ? COLLATE NOCASE LIMIT 1", (t,)).fetchone(): return True
        try:
            if db.execute("SELECT 1 FROM redirects WHERE title = ? COLLATE NOCASE LIMIT 1", (t,)).fetchone(): return True
        except sqlite3.Error: pass
    return False
def nowave(runf, goldf):
    seen, router = Counter(), {}
    for l in load(runf):
        if l["mode"] == "router" and l["id"] not in router: router[l["id"]] = l
    G = {k: v for k, v in json.load(open(goldf)).items() if isinstance(v, list) and v}
    return [i for i in sorted(G) if i in router and router[i].get("route") and not any(gold_in_wave(g) for g in G[i])]

def p(xs, q):
    xs = sorted(x for x in xs if x is not None)
    if not xs: return None
    return round(stt.median(xs), 1) if q == 50 else round(xs[min(len(xs) - 1, int(round(q / 100 * (len(xs) - 1))))], 1)

def aggregate():
    S = load(OUT_ST); V1 = {x["id"]: x for x in load(OUT_V01)}
    V2 = {x["id"]: x for x in load(OUT_V02)} if os.path.exists(OUT_V02) else {}  # script-only: ids/choices/ms
    nw1 = nowave(f"{PR}/runs/all9-v01.jsonl", f"{ROOT}/boar-eval/bench/v0.1/gold/sources.json")
    nw2 = nowave(f"{B2}/packroute-all9-v02.jsonl", f"{ROOT}/boar-eval/bench/v0.2/gold/sources.json")
    own = sum(x["choice"] == x["label"] for x in S)
    fam = {f: {"n": sum(1 for x in S if (x["label"] in SE) == (f == "SE")),
               "own": sum(x["choice"] == x["label"] for x in S if (x["label"] in SE) == (f == "SE"))} for f in ("SE", "topic")}
    for f in fam.values(): f["acc"] = round(f["own"] / f["n"], 3)
    per = {pk: {"own": sum(x["choice"] == pk for x in S if x["label"] == pk), "n": sum(x["label"] == pk for x in S)} for pk in PACKS}
    conf = {pk: dict(Counter(x["choice"] for x in S if x["label"] == pk).most_common()) for pk in PACKS}
    none1 = sum(V1[i]["choice"] == "none" for i in nw1 if i in V1); none2 = sum(V2[i]["choice"] == "none" for i in nw2 if i in V2)
    picked_kit = dict(Counter([V1[i]["choice"] for i in nw1 if i in V1 and V1[i]["choice"] != "none"] +
                              [V2[i]["choice"] for i in nw2 if i in V2 and V2[i]["choice"] != "none"]).most_common())
    inv = {"st180": sum(x["choice"] == "invalid" for x in S), "v01": sum(x["choice"] == "invalid" for x in V1.values()),
           "v02": sum(x["choice"] == "invalid" for x in V2.values())}
    cold_ms = [x["ms"] for x in S] + [x["ms"] for x in V1.values()] + [x["ms"] for x in V2.values()]
    C = load(OUT_C20) if os.path.exists(OUT_C20) else []
    out = {"criterion_sha256": "d67fd81c4b58ff150fd8f893d53bf90d3e7e030ebd3a513e9f6e8cb2a00c9d05", "wording": W,
           "descriptions_file": os.path.basename(DESC), "descriptions_sha256": hashlib.sha256(open(DESC, "rb").read()).hexdigest(),
           "prompt_sha256": PROMPT_SHA, "prompt_system_chars": len(SYSTEM),
           "model": os.path.basename(MODEL), "model_sha256": MODEL_SHA, "server": {"bin": BIN, "flags": FLAGS,
           "request": {"endpoint": "/v1/chat/completions", "temperature": 0, "seed": 42, "max_tokens": 16, "cache_prompt": "false (cold); true only for routes-cached20"}},
           "st180": {"n": len(S), "own": own, "acc": round(own / len(S), 3), "family": fam, "per_pack": per, "confusion": conf,
                     "choice_dist": dict(Counter(x["choice"] for x in S).most_common())},
           "kit_none": {"v01_ids": nw1, "v01_n": len(nw1), "v01_none": none1, "v02_n": len(nw2), "v02_none": none2,
                        "none": none1 + none2, "n": len(nw1) + len(nw2), "picked": picked_kit},
           "route_dist": {"v01": {"n": len(V1), **dict(Counter(x["choice"] for x in V1.values()).most_common())},
                          "v02": {"n": len(V2), **dict(Counter(x["choice"] for x in V2.values()).most_common())}},
           "invalid": inv,
           "ms": {"cold_all": {"n": len(cold_ms), "p50": p(cold_ms, 50), "p90": p(cold_ms, 90)},
                  "cold_prompt_ms_st180": {"p50": p([x["prompt_ms"] for x in S], 50)},
                  "cached20": {"n": len(C), "p50": p([x["ms"] for x in C], 50), "p90": p([x["ms"] for x in C], 90),
                               "cold_same_items_p50": p([x["cold_ms"] for x in C], 50),
                               "prompt_n_p50": p([x["prompt_n"] for x in C], 50), "same_choice": f"{sum(x['same'] for x in C)}/{len(C)}"}},
           }
    g_items = own >= 153; g_none = (none1 + none2) >= 21
    out["G1"] = {"own": f"{own}/180", "need_own": 153, "none": f"{none1 + none2}/{len(nw1) + len(nw2)}", "need_none": 21,
                 "pass": bool(g_items and g_none)}
    json.dump(out, open(AGG, "w"), indent=1)
    log(f"aggregate: own {own}/180, none {none1 + none2}/{len(nw1) + len(nw2)}, invalid {inv}, G1 {'PASS' if out['G1']['pass'] else 'FAIL'}")
    return out

def sha(f):
    h = hashlib.sha256()
    with open(f, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""): h.update(b)
    return h.hexdigest()
MODEL_SHA = sha(MODEL)
if "--aggregate-only" not in args: main_run()
o = aggregate()
print(json.dumps({"G1": o["G1"], "family": o["st180"]["family"], "invalid": o["invalid"], "ms": o["ms"]}))
