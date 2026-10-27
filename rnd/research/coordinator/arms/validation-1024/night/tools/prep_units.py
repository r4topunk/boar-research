#!/usr/bin/env python3
"""Label units for the UXMATRIX protocol (0 LLM), generic over runs. Same unit/sources construction as uxmatrix/tools/prep.py (Context blocks of the generation
prompt(s), '[n] Title (cited)', reversed copy for call B; unit key = sha256(id, answer text, sources)[:16]; identical units share one label).
usage: python3 -I prep_units.py <out dir> <tag>=<run dir> [<tag>=<run dir> ...]
  run dir = a dir of group dirs (<group>/traces.jsonl + prompts.jsonl), e.g. night/fetched/v2-s/out or uxmatrix/gen/succinct.
  group 'NN-on...' / 'on...' -> state on, else off. Writes <out dir>/units.json + answers.json (key '<tag>|<state>|<id>').
Gold: st-<pack>-NNN -> boar-eval/bench/selftest/<pack>/{refs/refs.jsonl answer, questions.jsonl rubric}; else bench/v0.1 (refs + questions.public)."""
import json, glob, os, sys, hashlib, re
BE = "<workspace>/boar-eval/bench/"
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
REF, Q = {}, {}
for r in rd(BE + "v0.1/refs/refs.jsonl"): REF[r["id"]] = r["answer"]
for r in rd(BE + "v0.1/questions.public.jsonl"): Q[r["id"]] = r
def gold(i):
    m = re.match(r"st-(.+)-\d{3}$", i)
    if m and i not in Q:
        p = m.group(1)
        for r in rd(f"{BE}selftest/{p}/refs/refs.jsonl"): REF[r["id"]] = r["answer"]
        for r in rd(f"{BE}selftest/{p}/questions.jsonl"): Q[r["id"]] = r
    return REF[i], Q[i]
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
def build(runs):
    units, ans = {}, {}
    for tag, rdir in runs:
        for d in sorted(glob.glob(f"{rdir}/*/")):
            g = os.path.basename(d.rstrip("/")); tf = d + "traces.jsonl"
            if not os.path.exists(tf) or not os.path.exists(d + "prompts.jsonl"): continue
            gg = re.sub(r"^\d\d-", "", g); st = "on" if gg.startswith("on") else "off"; PR = {}
            for p in rd(d + "prompts.jsonl"): PR.setdefault(p["itemId"], []).append(p)
            for t in rd(tf):
                i = t["itemId"]; a = t["answer"]; cited = set(a.get("cited") or [])
                bl = blocks(PR.get(i, []))
                src = "\n\n".join(f"[{n+1}] {ti}{' (cited)' if ti in cited else ''}\n{b}" for n, (ti, b) in enumerate(bl)) or "(none)"
                src_rev = "\n\n".join(f"[{n+1}] {ti}{' (cited)' if ti in cited else ''}\n{b}" for n, (ti, b) in enumerate(bl[::-1])) or "(none)"
                key = hashlib.sha256(json.dumps([i, a["text"], src]).encode()).hexdigest()[:16]
                G, q = gold(i)
                units[key] = dict(key=key, id=i, question=q["question"], gold=G, rubric=q["rubric"], answer=a["text"], sources=src, sources_rev=src_rev, n_src=len(bl))
                ans[f"{tag}|{st}|{i}"] = dict(key=key, group=gg, text=a["text"], declined=bool(a.get("declined")), shown=len(a.get("shown") or []), cited=len(cited),
                                              outTok=t["timing"].get("outputTokens"), totalMs=t["timing"].get("totalMs"), host=t["runtime"]["host"], n_src=len(bl))
    return units, ans
if __name__ == "__main__":
    out = sys.argv[1]; runs = [a.split("=", 1) for a in sys.argv[2:]]
    units, ans = build(runs); os.makedirs(out, exist_ok=True)
    json.dump(dict(units=list(units.values())), open(out + "/units.json", "w")); json.dump(ans, open(out + "/answers.json", "w"))
    print(f"answers {len(ans)} units {len(units)} (= exact A calls)")
