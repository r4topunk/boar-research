"""Quick QFORM hit@kept for replay files (matrix.py gold rule). python3 -I qhit.py f1 [f2 ...]"""
import json, re, sys
Q = "<workspace>/rnd/research/coordinator/arms/qform/items/"
items = {json.loads(l)["id"]: json.loads(l) for l in open(Q + "qform.jsonl")}
facts = {f["fact_id"]: f for f in json.load(open(Q + "facts.json"))}
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()
def cid(c):
    m = re.search(r":(\d+)$", c["chunkId"]); return int(m.group(1)) if m else None
def hit(lst, f):
    q = norm(f["gold"]["quote"]); g = f["gold"]["merged_chunk_id"]
    return any(q in norm(c["title"] + " " + c["body"]) or cid(c) == g for c in lst)
def load(fn):
    out = {}
    for l in open(fn):
        r = json.loads(l); f = facts[items[r["id"]]["fact_id"]]; out[r["id"]] = (hit(r["keptFull"], f), hit(r["wideFull"], f), len(r["keptFull"]), r)
    return out
if __name__ == "__main__":
    for fn in sys.argv[1:]:
        d = load(fn); n = len(d)
        print(fn.split("/")[-1], "hit@kept", sum(v[0] for v in d.values()), "/", n, "mean kept", round(sum(v[2] for v in d.values()) / n, 2))
