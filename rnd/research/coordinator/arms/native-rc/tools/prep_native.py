#!/usr/bin/env python3
"""NATIVE-RC label units (0 LLM), UXMATRIX protocol (uxmatrix/tools/prep.py construction): unit = (item, answer text exactly as shown, sources shown);
key = sha256([id, answer, sources])[:16]; sources = '[n] Title (cited)' + body, here the app's shown sources (ChatViewModel SourceGroups: one entry per
article, bodies joined '\\n…\\n', numbered as the shown answer cites them), answer = ChatScreen's display text (render step). Reversed copy for call B.
usage: python3 -I prep_native.py <render.jsonl> <out dir> <tag> [arms comma list] -> <out dir>/units.json + answers.json (key '<tag>|<state>|<id>',
state = 'on' for arms on/fb/fb2/probe, 'off' for arm off). Gold: v0.1 refs + public questions, or bench/selftest/<pack>."""
import json, sys, os, hashlib, re
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
src_fmt = lambda bl, cited: "\n\n".join(f"[{n+1}] {t}{' (cited)' if (n + 1) in cited else ''}\n{b}" for n, (t, b) in enumerate(bl)) or "(none)"
def build(render, tag, arms):
    units, ans = {}, {}
    for r in rd(render):
        if arms and r["arm"] not in arms: continue
        i = r["id"]; st = "off" if r["arm"] == "off" else "on"
        bl = [(s["title"], s["body"]) for s in r["sourcesShown"]]; cited = set(r["citedNums"])
        src = src_fmt(bl, cited)
        # reversed order, renumbered; the cited mark follows its passage
        rev = list(reversed(range(len(bl))))
        src_rev = "\n\n".join(f"[{n+1}] {bl[k][0]}{' (cited)' if (k + 1) in cited else ''}\n{bl[k][1]}" for n, k in enumerate(rev)) or "(none)"
        a = r["shownText"]
        key = hashlib.sha256(json.dumps([i, a, src]).encode()).hexdigest()[:16]
        G, q = gold(i)
        units[key] = dict(key=key, id=i, question=q["question"], gold=G, rubric=q["rubric"], answer=a, sources=src, sources_rev=src_rev, n_src=len(bl))
        ans[f"{tag}|{st}|{i}" if r["arm"] in ("on", "off") else f"{r['arm']}|on|{i}"] = dict(
            key=key, group=r["arm"], text=a, declined=False, shown=len(bl), cited=len(cited), citationsRaw=r["citationsRaw"],
            outTok=r.get("tokens_predicted"), totalMs=round(r["wall_s"] * 1000 + r.get("retrievalMs", 0)), stoppedLimit=bool(r.get("stopped_limit")), n_src=len(bl))
    return units, ans
if __name__ == "__main__":
    render, out, tag = sys.argv[1:4]; arms = set(sys.argv[4].split(",")) if len(sys.argv) > 4 else None
    units, ans = build(render, tag, arms); os.makedirs(out, exist_ok=True)
    json.dump(dict(units=list(units.values())), open(out + "/units.json", "w")); json.dump(ans, open(out + "/answers.json", "w"))
    print(f"answers {len(ans)} units {len(units)} (= exact A calls)")
