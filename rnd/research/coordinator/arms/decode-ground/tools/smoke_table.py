#!/usr/bin/env python3
"""DG smoke table (0 LLM). Usage: python3 -I smoke_table.py <runs/traces dir> <run name>... (first = B). Markdown to stdout.
loop = a word 6-gram occurring >= 3 times, or output tokens >= n_predict (512); cjk = answers with CJK characters (CAD tail-token artefact);
diff-vs-S = answers whose text differs from arm S on the same item (copy-bias / CAD effect beyond selection)."""
import json, re, sys
d, runs = sys.argv[1], sys.argv[2:]
load = lambda r: {json.loads(l)["itemId"]: json.loads(l) for l in open(f"{d}/{r}.traces.jsonl")}
T = {r: load(r) for r in runs}; B = T[runs[0]]; S = next((T[r] for r in runs if r.startswith("dg-S-")), None)
def loop(t):
    w = t["answer"]["text"].split(); g = [" ".join(w[i:i + 6]) for i in range(len(w) - 5)]
    return (max((g.count(x) for x in set(g)), default=0) >= 3) or (t["timing"]["outputTokens"] or 0) >= 512
print("| run | non-empty | loops | NO_EVIDENCE | selected in dropped | selected in kept | CJK answers | diff vs B | diff vs S | mean out tok | mean totalMs | totalMs / B |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
bms = sum(t["timing"]["totalMs"] for t in B.values()) / len(B)
for r in runs:
    ts = list(T[r].values()); sel = [(t["retrieval"].get("dg") or {}).get("select") for t in ts]
    ne = sum(1 for s in sel if s and s.get("choice") == 0); dr = sum(1 for s in sel if s and s.get("inDropped")); kp = sum(1 for s in sel if s and s.get("inKept"))
    ms = sum(t["timing"]["totalMs"] for t in ts) / len(ts); ot = sum(t["timing"]["outputTokens"] or 0 for t in ts) / len(ts)
    dB = sum(1 for t in ts if t["answer"]["text"] != B[t["itemId"]]["answer"]["text"]); dS = sum(1 for t in ts if S and t["answer"]["text"] != S[t["itemId"]]["answer"]["text"])
    cjk = sum(1 for t in ts if re.search(r"[぀-ヿ一-鿿]", t["answer"]["text"]))
    print(f"| {r} | {sum(1 for t in ts if t['answer']['text'].strip())}/{len(ts)} | {sum(map(loop, ts))} | {ne} | {dr} | {kp} | {cjk} | {dB} | {dS if S else '-'} | {ot:.1f} | {ms:.0f} | {ms / bms:.2f} |")
