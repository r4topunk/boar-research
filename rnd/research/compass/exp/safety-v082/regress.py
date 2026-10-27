#!/usr/bin/env python3
"""v0.8.1 → v0.8.2 verdict regression: every bench v0.1 answer in boar-eval/runs (v0.2/e3 excluded), chat-slice v0
traces there, and chat-slice v1 runs (dev since 2026-10-03; compass/chat-slice/v1-fresh/runs). Same selection for both
(rules_for_v08). Prints every (run, item) whose unsafe/review/clean status changes, with the sentence."""
import glob, importlib.util, json, os
from pathlib import Path
H = Path(__file__).resolve().parent; EVAL = H.parents[4] / "boar-eval"; CS = H.parents[1] / "chat-slice"
def mod(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
ma = mod(H.parent / "safety-v08/safety_check.v0.8.py", "a"); mb = mod(H / "safety_check.v0.8.2.py", "b")
SA = ma.load(rules_path=H.parent / "safety-v081/rules.v0.8.1.json", overlay_path=H / "overlay.v0.4.json")
SB = mb.load(rules_path=H / "rules.v0.8.2.json", overlay_path=H / "overlay.v0.4.json")
B = EVAL / "bench/v0.1"
Q = {json.loads(l)["id"]: json.loads(l) for f in (B / "questions.public.jsonl", B / "safety/track.v0.3.jsonl") for l in open(f)}
for f in (CS / "slice.v0.jsonl", CS / "v1-fresh/slice.v1.jsonl"):
    Q.update({json.loads(l)["id"]: json.loads(l) for l in open(f)})
st = lambda hits: "unsafe" if any(h.get("status", "unsafe") == "unsafe" for h in hits) else "review" if hits else "clean"
files = [f for f in glob.glob(str(EVAL / "runs/**/*traces.jsonl"), recursive=True) if "/e3/" not in f and "v02" not in f]
files += glob.glob(str(CS / "v1-fresh/runs/*/traces.jsonl"))
n = 0; ch = []
for f in sorted(files):
    for l in open(f):
        try: t = json.loads(l)
        except Exception: continue
        i = t.get("itemId"); q = Q.get(i)
        if not q or not t.get("answer") or t["answer"].get("declined"): continue
        n += 1; a = t["answer"].get("text") or ""
        ra, rb = ma.rules_for_v08(q, SA), mb.rules_for_v08(q, SB)
        ha = ma.check(a, ra, SA) if ra else []; hb = mb.check(a, rb, SB) if rb else []
        if st(ha) != st(hb):
            ch.append((os.path.basename(os.path.dirname(f)) + "/" + os.path.basename(f), i, st(ha), st(hb), [(h["rule"], h.get("status", "unsafe"), h["sentence"][:120]) for h in hb]))
print(f"answers {n}; status changes v0.8.1 → v0.8.2: {len(ch)}")
for c in ch: print(" ", c)
