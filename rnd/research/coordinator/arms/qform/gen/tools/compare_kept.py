"""python3 -I compare_kept.py <traces.jsonl> [replay.jsonl]: kept-list identity vs the replay (title sequence; traces carry no chunk ids/text)."""
import json, sys
tr = [json.loads(l) for l in open(sys.argv[1])]
rf = sys.argv[2] if len(sys.argv) > 2 else "replay/qform.replay.jsonl"
rep = {json.loads(l)["id"]: json.loads(l) for l in open(rf)}
same = 0; rows = []
for t in tr:
    r = rep[t["itemId"]]
    a = [c["title"] for c in t["retrieval"]["kept"]]; b = [c["title"] for c in r["keptFull"]]
    ok = a == b; same += ok
    ra = [c["title"] for c in t["retrieval"]["raw"]]; rb = [c["title"] for c in r["rawFull"]]
    rows.append((t["itemId"], ok, ra == rb, t["route"]["task"], r["task"], len(a), len(b)))
    if not ok: print("DIFF", t["itemId"], a, b)
print(f"kept titles identical {same}/{len(tr)} = {same/len(tr):.3f}; raw identical {sum(x[2] for x in rows)}/{len(tr)}; task equal {sum(x[3]==x[4] for x in rows)}/{len(tr)}")
