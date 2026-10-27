#!/usr/bin/env python3
"""v0.8.2 → v0.8.3 verdict regression, same pool as v0.8.2 (all v0.1 runs, chat-slice v0, chat-slice v1 dev runs), plus
the 14 first-aid cards (all languages, alternative steps included). Prints every status change."""
import glob, importlib.util, json, os
from pathlib import Path
H = Path(__file__).resolve().parent; EVAL = H.parents[4] / "boar-eval"; CS = H.parents[1] / "chat-slice"
s = importlib.util.spec_from_file_location("c", H / "safety_check.v0.8.2.py"); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
SA = m.load(rules_path=H.parent / "safety-v082/rules.v0.8.2.json", overlay_path=H / "overlay.v0.4.json")
SB = m.load(rules_path=H / "rules.v0.8.3.json", overlay_path=H / "overlay.v0.4.json")
B = EVAL / "bench/v0.1"
Q = {json.loads(l)["id"]: json.loads(l) for f in (B / "questions.public.jsonl", B / "safety/track.v0.3.jsonl") for l in open(f)}
for f in (CS / "slice.v0.jsonl", CS / "v1-fresh/slice.v1.jsonl"):
    Q.update({json.loads(l)["id"]: json.loads(l) for l in open(f)})
st = lambda hs: "unsafe" if any(h.get("status", "unsafe") == "unsafe" for h in hs) else "review" if hs else "clean"
files = [f for f in glob.glob(str(EVAL / "runs/**/*traces.jsonl"), recursive=True) if "/e3/" not in f and "v02" not in f] + glob.glob(str(CS / "v1-fresh/runs/*/traces.jsonl"))
n = 0; ch = []
for f in sorted(files):
    for l in open(f):
        try: t = json.loads(l)
        except Exception: continue
        q = Q.get(t.get("itemId"))
        if not q or not t.get("answer") or t["answer"].get("declined"): continue
        n += 1; a = t["answer"].get("text") or ""
        ra, rb = m.rules_for_v08(q, SA), m.rules_for_v08(q, SB)
        x, y = st(m.check(a, ra, SA) if ra else []), st(m.check(a, rb, SB) if rb else [])
        if x != y: ch.append((os.path.relpath(f, EVAL / "runs"), t["itemId"], x, y))
D = json.load(open(H.parent / "first-aid-cards/cards.json")); cards = 0
for c in D["cards"]:
    for lang, L in c["langs"].items():
        txt = "\n".join([L["title"]] + [s["text"] for s in L["steps"] + c.get("alt_steps", {}).get(lang, [])] + [L["call"]["text"]])
        rb = sorted(set(c.get("rules", [])) | set(m.rules_by_topic(c["topic"][lang], SB))); cards += 1
        hb = m.check(txt, rb, SB)
        if hb: ch.append(("card", c["id"] + "/" + lang, "clean", st(hb), [(h["rule"], h.get("status", "unsafe"), h["sentence"][:80]) for h in hb]))
print(f"answers {n}, card texts {cards}; status changes v0.8.2 → v0.8.3: {len(ch)}")
for c in ch: print(" ", c)
