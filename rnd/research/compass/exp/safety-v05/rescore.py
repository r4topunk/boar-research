import json, glob, importlib.util, os
def load(mod, rules):
    spec = importlib.util.spec_from_file_location("sc"+mod, mod); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m, m.load(rules_path=rules, overlay_path="overlay.v0.4.json")
m4, S4 = load("safety_check.py", "rules.v0.4.json"); m5, S5 = load("safety_check.v0.5.py", "rules.v0.5.json")
B = "<workspace>/boar-eval/runs/night-2026-10-01/"
Q = {}
for f in ["<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "<workspace>/boar-eval/scorers/vendor/safety/track.v0.3.jsonl"]:
    for l in open(f): r = json.loads(l); Q[r["id"]] = r
changes = []; n = tot4 = tot5 = 0
for tf in sorted(glob.glob(B + "*.traces.jsonl")):
    run = os.path.basename(tf).replace(".traces.jsonl", "")
    for l in open(tf):
        t = json.loads(l); q = Q.get(t["itemId"])
        if not q or t["answer"].get("declined") or not (t["answer"].get("text") or "").strip(): continue
        r4 = m4.rules_for(q, S4); r5 = m5.rules_for(q, S5)
        if not r4: continue
        h4 = sorted({h["rule"] for h in m4.check(t["answer"]["text"], r4, S4)}); h5 = sorted({h["rule"] for h in m5.check(t["answer"]["text"], r5, S5)})
        n += 1; tot4 += bool(h4); tot5 += bool(h5)
        if h4 != h5: changes.append((run, t["itemId"], h4, h5))
print(f"answers checked {n}; unsafe v0.4 {tot4} → v0.5 {tot5}; changed verdicts {len(changes)}")
for c in changes: print("  ", c)
