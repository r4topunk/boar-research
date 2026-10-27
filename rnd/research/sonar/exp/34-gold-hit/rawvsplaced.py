"""exp-34: gold Wikipedia article in the RAW retriever output (retrieve events) vs PLACED in the prompt (last sources
event with text), per kic trace file. Shows how many gold articles the grounding gates / compression drop."""
import json, re, sys, collections
O = "<workspace>/rnd/research/anvil/exp/oracle/"
gold = collections.defaultdict(set)
for l in open(O + "articles.jsonl"):
    a = json.loads(l)
    if a["kind"] == "wiki": gold[a["id"]].add(a["title"].lower())
for f in sys.argv[1:]:
    raw = placed = both = n = 0; dropped = []
    for l in open(f):
        r = json.loads(l); g = gold.get(r["itemId"])
        if not g: continue
        n += 1
        isw = lambda x: (x.get("source") or "Wikipedia").startswith("Wikipedia")
        rt = {x["title"].lower() for e in r["events"] if e.get("type") == "retrieve" for x in e.get("sources", []) if isw(x)}
        ev = [e for e in r["events"] if e.get("type") == "sources" and any(x.get("text") for x in e.get("sources", []))]
        pt = {x["title"].lower() for x in (ev[-1]["sources"] if ev else []) if isw(x)}
        a, b = bool(rt & g), bool(pt & g); raw += a; placed += b
        if a and not b: dropped.append((r["itemId"], [c for c in r["route"]["reasonCodes"] if c.startswith(("grounding:", "context:"))][:4]))
    print(f"== {f.split('/')[-1]}: wiki-gold items {n}; gold article in RAW retrieval {raw}; PLACED in prompt {placed}; dropped after retrieval {len(dropped)}")
    for d in dropped: print("   ", d)
