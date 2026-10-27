#!/usr/bin/env python3
"""UXMATRIX label units (0 LLM). python3 -I prep.py [modes...] -> ../judge/units.json (+ ../judge/answers.json: per (mode,state,id) -> unit key)
Reads gen/<mode>/<group>/{traces,prompts}.jsonl. Sources shown = Context blocks of the generation prompt(s) (criterion); unit key = sha256(id, answer text, sources)."""
import json, glob, os, sys, hashlib, re
U = "<workspace>/rnd/research/coordinator/arms/uxmatrix"; BE = "<workspace>/boar-eval/bench/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
IT = {x["id"]: x for x in json.load(open(U + "/items.json"))["items"]}
REF, Q = {}, {}
for r in rd(BE + "v0.1/refs/refs.jsonl"): REF[r["id"]] = r["answer"]
for r in rd(BE + "v0.1/questions.public.jsonl"): Q[r["id"]] = r
for p in ("qa-cooking-se", "qa-money-se"):
    for r in rd(f"{BE}selftest/{p}/refs/refs.jsonl"): REF[r["id"]] = r["answer"]
    for r in rd(f"{BE}selftest/{p}/questions.jsonl"): Q[r["id"]] = r
def blocks(prompts):
    seen, out = set(), []
    for p in prompts:
        for m in p["messages"]:
            if m["role"] != "system" or "\nContext:\n" not in m["content"]: continue
            ctx = m["content"].split("\nContext:\n", 1)[1]
            for b in re.split(r"\n\n(?=\[\d+\] )", ctx.strip()):
                mm = re.match(r"\[\d+\] ([^\n]*)\n?(.*)", b, re.S)
                if not mm: continue
                t, body = mm.group(1).strip(), mm.group(2).strip()
                if (t, body) in seen: continue
                seen.add((t, body)); out.append((t, body))
    return out
modes = sys.argv[1:] or ["succinct", "detailed", "deep"]
units = {}; ans = {}
old = json.load(open(U + "/judge/answers.json")) if os.path.exists(U + "/judge/answers.json") else {}
for mode in modes:
    for d in sorted(glob.glob(f"{U}/gen/{mode}/*/")):
        g = os.path.basename(d.rstrip("/")); tf = d + "traces.jsonl"
        if not os.path.exists(tf) or not os.path.exists(d + "prompts.jsonl"): continue
        st = "on" if g == "on" else "off"; PR = {}
        for p in rd(d + "prompts.jsonl"): PR.setdefault(p["itemId"], []).append(p)
        for t in rd(tf):
            i = t["itemId"]; a = t["answer"]; cited = set(a.get("cited") or [])
            bl = blocks(PR.get(i, []))
            src = "\n\n".join(f"[{n+1}] {ti}{' (cited)' if ti in cited else ''}\n{b}" for n, (ti, b) in enumerate(bl)) or "(none)"
            src_rev = "\n\n".join(f"[{n+1}] {ti}{' (cited)' if ti in cited else ''}\n{b}" for n, (ti, b) in enumerate(bl[::-1])) or "(none)"
            key = hashlib.sha256(json.dumps([i, a["text"], src]).encode()).hexdigest()[:16]
            units[key] = dict(key=key, id=i, question=Q[i]["question"], gold=REF[i], rubric=Q[i]["rubric"], answer=a["text"], sources=src, sources_rev=src_rev, n_src=len(bl))
            ans[f"{mode}|{st}|{i}"] = dict(key=key, group=g, cls=IT[i]["cls"], text=a["text"], declined=bool(a.get("declined")), shown=len(a.get("shown") or []), cited=len(cited),
                                          outTok=t["timing"].get("outputTokens"), totalMs=t["timing"].get("totalMs"), host=t["runtime"]["host"], reason=t["route"]["reasonCodes"], n_src=len(bl))
old.update(ans); os.makedirs(U + "/judge", exist_ok=True)
uo = json.load(open(U + "/judge/units.json"))["units"] if os.path.exists(U + "/judge/units.json") else []
um = {u["key"]: u for u in uo}; um.update(units)
json.dump(dict(units=list(um.values())), open(U + "/judge/units.json", "w")); json.dump(old, open(U + "/judge/answers.json", "w"))
print("answers", len(old), "units", len(um))
