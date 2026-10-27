#!/usr/bin/env python3
"""v0.7 → v0.8 verdict regression on every bench v0.1 answer in boar-eval/runs (v0.2 / e3 excluded) + chat-slice traces.
Selection: v0.7 = rules_for_v06(question); v0.8 = rules_for_v08 (same explicit mapping; topic over all user turns).
Prints every (run, item) whose unsafe/review status changes, with the sentence, for hand triage."""
import glob, importlib.util, json, os, sys
from pathlib import Path
H = Path(__file__).resolve().parent; EVAL = H.parents[4] / "boar-eval"
def mod(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
m7 = mod(H.parent / "safety-v07/safety_check.v0.7.py", "s7"); m8 = mod(H / "safety_check.v0.8.py", "s8")
S7 = m7.load(rules_path=H.parent / "safety-v07/rules.v0.7.json", overlay_path=H / "overlay.v0.4.json")
S8 = m8.load(rules_path=H / "rules.v0.8.json", overlay_path=H / "overlay.v0.4.json")
B = EVAL / "bench/v0.1"
Q = {json.loads(l)["id"]: json.loads(l) for f in (B / "questions.public.jsonl", B / "safety/track.v0.3.jsonl") for l in open(f)}
CS = {json.loads(l)["id"]: json.loads(l) for l in open(H.parents[1] / "chat-slice/slice.v0.jsonl")}
def status(hits):
    return ("unsafe" if any(h.get("status", "unsafe") == "unsafe" for h in hits) else "review" if hits else "clean")
files = [f for f in glob.glob(str(EVAL / "runs/**/*traces.jsonl"), recursive=True) if "/e3/" not in f and "v02" not in f]
n = sel7 = sel8 = 0; changes = []
for f in sorted(files):
    for l in open(f):
        try: t = json.loads(l)
        except Exception: continue
        i = t.get("itemId"); q = Q.get(i) or CS.get(i)
        if not q or (i in CS and "chat-slice" not in f) or t.get("answer") is None or t["answer"].get("declined"): continue
        a = t["answer"].get("text") or ""; n += 1
        r7, r8 = m7.rules_for_v06(q, S7), m8.rules_for_v08(q, S8)
        sel7 += bool(r7); sel8 += bool(r8)
        h7, h8 = m7.check(a, r7, S7) if r7 else [], m8.check(a, r8, S8) if r8 else []
        if status(h7) != status(h8):
            changes.append((os.path.relpath(f, EVAL / "runs"), i, status(h7), status(h8), [(h["rule"], h["status"] if "status" in h else "unsafe", h["sentence"][:140]) for h in h8 if h not in h7]))
print(f"answers {n}; with rules v0.7 {sel7} → v0.8 {sel8}; status changes {len(changes)}")
for c in changes: print(" ", c)
