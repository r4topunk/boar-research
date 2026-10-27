#!/usr/bin/env python3
"""v0.8.6 → v0.8.7 re-score of every non-held-out answer we have (coordinator 2026-10-03): boar-eval/runs (v0.2/e3
held-out excluded), Kiln runs, chat-slice v1 dev runs, Sonar's experiment traces; plus the 60 first-aid card texts.
Only under-triage verdicts can change (new PT/ES doctor wording). Prints every status change per run.
Blindness: items whose id is not in a dev file (v0.1 public/safety, chat-slice v0/v1) or Sonar's repro set (r2-*, rep-*)
are treated as blind-derived: only run, id, language, rule and status are printed, never question or answer text."""
import glob, importlib.util, json, os, re
from collections import Counter, defaultdict
from pathlib import Path
H = Path(__file__).resolve().parent; RND = H.parents[2]; BOAR = RND.parents[1]; EVAL = BOAR / "boar-eval"; CS = RND / "compass/chat-slice"
def mod(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
ma = mod(H.parent / "safety-v086/safety_check.v0.8.6.py", "a"); mb = mod(H / "safety_check.v0.8.7.py", "b")
SA = ma.load(rules_path=H.parent / "safety-v086/rules.v0.8.6.json", overlay_path=H / "overlay.v0.4.json")
SB = mb.load(rules_path=H / "rules.v0.8.7.json", overlay_path=H / "overlay.v0.4.json")
B = EVAL / "bench/v0.1"
Q = {json.loads(l)["id"]: json.loads(l) for f in (B / "questions.public.jsonl", B / "safety/track.v0.3.jsonl") for l in open(f)}
for f in (CS / "slice.v0.jsonl", CS / "v1-fresh/slice.v1.jsonl", CS / "v2-fresh/slice.v2.jsonl"):
    Q.update({json.loads(l)["id"]: json.loads(l) for l in open(f)})
dev = lambda i: i in Q or re.match(r"^(r2|rep|cp)-|^pd-2[3-8]$", i or "")  # Sonar 2026-10-03: cp-*, pd-23..28 = his own probes
st = lambda hs: "unsafe" if any(h.get("status", "unsafe") == "unsafe" for h in hs) else "review" if hs else "clean"
files = [f for f in glob.glob(str(EVAL / "runs/**/*traces.jsonl"), recursive=True) if "/e3/" not in f and "v02" not in f]
files += glob.glob(str(CS / "v1-fresh/runs/*/traces.jsonl")) + glob.glob(str(CS / "v2-fresh/runs/*/traces.jsonl"))
files += glob.glob(str(RND / "sonar/exp/**/*traces.jsonl"), recursive=True)
files = sorted(set(files))
n = Counter(); ch = defaultdict(list)
for f in files:
    for l in open(f):
        try: t = json.loads(l)
        except Exception: continue
        i = t.get("itemId"); a = (t.get("answer") or {})
        if not i or a.get("declined") or not a.get("text"): continue
        q = Q.get(i) or {"id": i, "question": t.get("question") or ""}
        lang = mb.lang_of(a["text"]); n["answers"] += 1; n[lang] += 1
        ra, rb = ma.rules_for_v085(q, SA), mb.rules_for_v085(q, SB)
        if not rb: continue
        n["with_rules"] += 1
        ha, hb = (ma.check(a["text"], ra, SA) if ra else []), mb.check(a["text"], rb, SB)
        x, y = st(ha), st(hb)
        if x != y:
            new = [(h["rule"], h.get("status", "unsafe")) + ((h["sentence"][:160],) if dev(i) else ()) for h in hb if (h["rule"], h.get("status")) not in {(g["rule"], g.get("status")) for g in ha}]
            ch[os.path.relpath(f, BOAR)].append((i, lang, x, y, "dev" if dev(i) else "BLIND-DERIVED (ids only)", new))
D = json.load(open(H.parent / "first-aid-cards/cards.json")); cards = []; ncard = 0
for c in D["cards"]:
    for lg, L in c["langs"].items():
        txt = "\n".join([L["title"]] + [s["text"] for s in L["steps"] + c.get("alt_steps", {}).get(lg, [])] + [L["call"]["text"]])
        rb = sorted(set(c.get("rules", [])) | set(mb.rules_by_topic(c["topic"][lg], SB)))
        hb = mb.check(txt, rb, SB); ncard += 1
        if hb: cards.append((c["id"], lg, [(h["rule"], h.get("status", "unsafe"), h["sentence"][:120]) for h in hb]))
print(f"answers {n['answers']} (en {n['en']}, pt {n['pt']}, es {n['es']}, und {n['und']}); with a rule {n['with_rules']}; runs with a change {len(ch)}; changes {sum(map(len, ch.values()))}")
for f, rows in ch.items():
    print("==", f)
    for r in rows: print("  ", r)
print(f"card texts {ncard}: {'all clean' if not cards else cards}")
