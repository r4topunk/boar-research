"""T1 paired compare (0 LLM). python3 -I t1/compare.py
Reads aggregates/matrix.json (baseline rows) is not row-level, so this recomputes hit@kept per item with matrix.py's rule
for the baseline and the terms replay, then pairs by fact per form (bootstrap B 2000, seed 11)."""
import json, os, random, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
items = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "items/qform.jsonl"))}
facts = {f["fact_id"]: f for f in json.load(open(os.path.join(ROOT, "items/facts.json")))}

def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()
def cid(c):
    m = re.search(r":(\d+)$", c["chunkId"]); return int(m.group(1)) if m else None
def hit(lst, qn, gc):
    return any(qn in norm(c["title"] + " " + c["body"]) or cid(c) == gc for c in lst)
def load(p):
    return {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, p)) if l.strip()}

base, terms = load("replay/qform.replay.jsonl"), load("t1/terms.replay.jsonl")
FN = {0: "F0 base", 1: "F1 entity-free", 2: "F2 keywords", 3: "F3 situational", 4: "F4 typos", 5: "F5 yes/no true",
      6: "F6 false premise", 7: "F7 comparison", 8: "F8 follow-up"}
out, L = {}, ["| form | original hit@kept | terms hit@kept | delta pts [95% CI] | raw orig -> terms | kept empty orig -> terms |", "|---|---|---|---|---|---|"]
for k in range(9):
    ids = sorted(i for i, it in items.items() if it["form"] == k)
    a, b, ra, rb, ea, eb = [], [], 0, 0, 0, 0
    for i in ids:
        f = facts[items[i]["fact_id"]]; qn = norm(f["gold"]["quote"]); gc = f["gold"]["merged_chunk_id"]
        a.append(int(hit(base[i]["keptFull"], qn, gc))); b.append(int(hit(terms[i]["keptFull"], qn, gc)))
        ra += hit(base[i]["rawFull"], qn, gc); rb += hit(terms[i]["rawFull"], qn, gc)
        ea += not base[i]["keptFull"]; eb += not terms[i]["keptFull"]
    n = len(ids); d = [y - x for x, y in zip(a, b)]
    rng = random.Random(11); bs = sorted(sum(rng.choice(d) for _ in range(n)) / n for _ in range(2000))
    m, lo, hi = sum(d) / n, bs[50], bs[1949]
    out[k] = {"n": n, "orig": sum(a), "terms": sum(b), "delta": m, "ci": [lo, hi], "gained": sum(x == 1 for x in d), "lost": sum(x == -1 for x in d)}
    L.append(f"| {FN[k]} | {sum(a)}/{n} ({100*sum(a)/n:.0f} %) | {sum(b)}/{n} ({100*sum(b)/n:.0f} %) | {100*m:+.0f} [{100*lo:+.0f}, {100*hi:+.0f}] (gained {out[k]['gained']}, lost {out[k]['lost']}) | {ra} -> {rb} | {ea} -> {eb} |")
json.dump(out, open(os.path.join(ROOT, "t1/compare.json"), "w"), indent=1)
open(os.path.join(ROOT, "t1/compare.md"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
