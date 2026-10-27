#!/usr/bin/env python3
"""PACKPROOF label units (0 LLM). python3 -I prep.py -> ../judge/units.json + ../judge/answers.json (per state|id -> unit key + UX fields)
Same unit/sources construction as uxmatrix/tools/prep.py (Context blocks of the generation prompt, '[n] Title (cited)'); unit key = sha256(id, answer text, sources)."""
import json, glob, os, hashlib, re
P = "<workspace>/rnd/research/coordinator/arms/packproof"; BE = "<workspace>/boar-eval/bench/selftest/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
IT = {x["id"]: x for x in json.load(open(P + "/in/items.json"))["items"]}
REF, Q = {}, {}
for p in json.load(open(P + "/in/items.json"))["packs"]:
    for r in rd(f"{BE}{p}/refs/refs.jsonl"): REF[r["id"]] = r["answer"]
    for r in rd(f"{BE}{p}/questions.jsonl"): Q[r["id"]] = r
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
units, ans = {}, {}
for d in sorted(glob.glob(f"{P}/gen/*/")):
    g = os.path.basename(d.rstrip("/")); tf = d + "traces.jsonl"
    if g.startswith("ident5") or not os.path.exists(d + "STATUS") or "DONE" not in open(d + "STATUS").read() or "placeholder" in open(d + "STATUS").read() or not os.path.exists(tf): continue
    st = "on" if g.startswith("on-") else "off"; PR = {}
    for p in rd(d + "prompts.jsonl"): PR.setdefault(p["itemId"], []).append(p)
    for t in rd(tf):
        i = t["itemId"]; a = t["answer"]; cited = set(a.get("cited") or [])
        bl = blocks(PR.get(i, []))
        src = "\n\n".join(f"[{n+1}] {ti}{' (cited)' if ti in cited else ''}\n{b}" for n, (ti, b) in enumerate(bl)) or "(none)"
        src_rev = "\n\n".join(f"[{n+1}] {ti}{' (cited)' if ti in cited else ''}\n{b}" for n, (ti, b) in enumerate(bl[::-1])) or "(none)"
        key = hashlib.sha256(json.dumps([i, a["text"], src]).encode()).hexdigest()[:16]
        units[key] = dict(key=key, id=i, question=Q[i]["question"], gold=REF[i], rubric=Q[i]["rubric"], answer=a["text"], sources=src, sources_rev=src_rev, n_src=len(bl))
        ans[f"{st}|{i}"] = dict(key=key, group=g, pack=IT[i]["pack"], text=a["text"], declined=bool(a.get("declined")), shown=a.get("shown") or [], cited=sorted(cited),
                                raw=[(k["title"], k["source"]) for k in t["retrieval"]["raw"]], kept=[(k["title"], k["source"]) for k in t["retrieval"]["kept"]],
                                outTok=t["timing"].get("outputTokens"), totalMs=t["timing"].get("totalMs"), host=t["runtime"]["host"], reason=t["route"]["reasonCodes"], n_src=len(bl))
os.makedirs(P + "/judge", exist_ok=True)
json.dump(dict(units=list(units.values())), open(P + "/judge/units.json", "w")); json.dump(ans, open(P + "/judge/answers.json", "w"))
print("answers", len(ans), "units", len(units))
