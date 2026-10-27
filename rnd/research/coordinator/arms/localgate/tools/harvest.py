#!/usr/bin/env python3
"""LOCALGATE harvest: rebuild the exact jev request bodies of wikifull_gate.py (A0, shard 07) and packcond_p1.py by running
their own planning code with the network disabled, and keep only requests whose response is already cached.
Writes per-decision records (state text + jev probability) to blind/localgate/ (never printed, never in git).
Prints counts only. 0 network calls: urllib is patched to raise; cache misses get a -1 sentinel.

usage: harvest.py wikifull vpara|v02   |   harvest.py packcond
"""
import sys, os, json, hashlib, threading, urllib.request
sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/wikisection/tools")
sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/wikifull/tools")
sys.path.insert(0, "<workspace>/rnd/research/coordinator/arms/packcond/tools")
import section_gate as sg

def _no_net(*a, **k): raise RuntimeError("network disabled in LOCALGATE harvest")
urllib.request.urlopen = _no_net
os.environ["VERCEL_AI_GATEWAY"] = "offline-dummy"; os.environ.pop("AI_GATEWAY_API_KEY", None)
OUTD = "<private held-out dir>"; os.makedirs(OUTD, exist_ok=True)
SCRATCH = "<scratch>"; os.makedirs(SCRATCH, exist_ok=True)
lock = threading.Lock(); seen = set(); stats = dict(hit=0, miss=0, records=0)

def h(body): return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
def sentinel(body): return {"answers": {k: {"type": "boolean", "probability": -1.0} for k in body["questions"]}}

def emit(fh, src, setn, body, res):
    st = body["state"]; key = h(body); recs = []
    for qn, ans in res["answers"].items():
        if "probability" not in ans: continue
        if "chunks" not in st:
            typ = qn; text = st["text"]
        else:
            pre, k = qn.split("_", 1)
            if pre == "sup": continue
            typ = {"has": "has_fact", "quo": "quote_supports"}[pre]; text = st["chunks"][k]
        recs.append(dict(rid=f"{key[:16]}:{qn}", src=src, set=setn, type=typ,
                         state=dict(rationale_1=st["rationale_1"], rationale_2=st["rationale_2"], text=text), jev_p=ans["probability"]))
    with lock:
        if key in seen: return
        seen.add(key)
        for r in recs: fh.write(json.dumps(r, ensure_ascii=False) + "\n"); stats["records"] += 1

def run_wikifull(setn):
    import wikifull_gate as wg
    wg.OUT = SCRATCH
    fh = open(f"{OUTD}/harvest-wikifull-{setn}.jsonl", "w"); tl = threading.local()
    class J:
        def __getattr__(s, n): return getattr(json, n)
        def dumps(s, obj, **kw):
            if isinstance(obj, dict) and "questions" in obj and "state" in obj: tl.body = obj
            return json.dumps(obj, **kw)
        def load(s, f, **kw):
            r = json.load(f, **kw); b = getattr(tl, "body", None)
            if b is not None and isinstance(r, dict) and "answers" in r:
                tl.body = None; stats["hit"] += 1; emit(fh, "wikifull", setn, b, r)
            return r
    wg.json = J()
    def fake_call(body, key, cd): stats["miss"] += 1; return sentinel(body), False
    sg.call = fake_call
    sys.argv = ["wikifull_gate.py", "--set", setn, "--workers", "1"]
    devnull = open(os.devnull, "w"); so = sys.stdout; sys.stdout = devnull
    try: wg.main()
    finally: sys.stdout = so
    fh.close()

def run_packcond():
    import packcond_p1 as pc
    pc.OUT = SCRATCH
    fh = open(f"{OUTD}/harvest-packcond.jsonl", "w")
    def fake_call(body, key, cd):
        p = os.path.join(cd, h(body) + ".json")
        if os.path.exists(p):
            r = json.load(open(p)); stats["hit"] += 1
            emit(fh, "packcond", os.path.basename(os.path.dirname(cd)) + "@" + cd.split("/blind/")[1].split("/")[0], body, r); return r, True
        stats["miss"] += 1; return sentinel(body), False
    sg.call = fake_call
    sys.argv = ["packcond_p1.py", "--workers", "1"]
    devnull = open(os.devnull, "w"); so = sys.stdout; sys.stdout = devnull
    try: pc.main()
    finally: sys.stdout = so
    fh.close()

def run_wsec(mod, setn):
    import builtins
    m = __import__(mod)
    def safe_open(f, mode="r", *a, **k):
        if "w" in mode and "/aggregates/" in str(f): f = os.path.join(SCRATCH, os.path.basename(str(f)))
        return builtins.open(f, mode, *a, **k)
    m.open = safe_open; sg.open = safe_open
    tag = "section" if mod == "section_gate" else "anywhere"
    fh = open(f"{OUTD}/harvest-{tag}-{setn}.jsonl", "w")
    def fake_call(body, key, cd):
        p = os.path.join(cd, h(body) + ".json")
        if os.path.exists(p):
            r = json.load(open(p)); stats["hit"] += 1; emit(fh, "wikisection", setn, body, r); return r, True
        stats["miss"] += 1; return sentinel(body), False
    sg.call = fake_call
    sys.argv = [mod + ".py", "--set", setn, "--workers", "1"]
    devnull = open(os.devnull, "w"); so = sys.stdout; sys.stdout = devnull
    try: m.main()
    finally: sys.stdout = so
    fh.close()

if __name__ == "__main__":
    if sys.argv[1] in ("section_gate", "anywhere_gate"): run_wsec(sys.argv[1], sys.argv[2]); tag = sys.argv[1] + "-" + sys.argv[2]
    elif sys.argv[1] == "wikifull": run_wikifull(sys.argv[2]); tag = "wikifull-" + sys.argv[2]
    else: run_packcond(); tag = "packcond"
    print(tag, json.dumps(stats))
