import json, sys
R=json.load(open("rows.json")); P=json.load(open("emb_p.json"))
for f in sys.argv[1:]:
    L=json.load(open(f)); print("==",f)
    for pre in (0.0,0.2,0.3):
        def fire(r): return P[r["id"]]>=pre and L[r["id"]]=="yes"
        for s in ("train","dev"):
            S=[r for r in R if r["set"]==s]
            print(f"  prefilter {pre}: {s:5} crisis {sum(fire(r) for r in S if r['y'])}/{sum(r['y'] for r in S)}  decoys fired {sum(fire(r) for r in S if not r['y'])}/{sum(1-r['y'] for r in S)}")
        N=[r for r in R if r["set"] in ("eval","faqa")]
        print(f"  prefilter {pre}: neg632 fired {sum(fire(r) for r in N)}  LLM calls on neg632 {sum(P[r['id']]>=pre for r in N)}")
    print("  misses (dev):",[r["q"][:60] for r in R if r["set"]=="dev" and r["y"] and L[r["id"]]!="yes"])
    print("  decoy fires (train+dev):",[r["q"][:60] for r in R if r["set"] in ("train","dev") and not r["y"] and L[r["id"]]=="yes"])
    print("  neg fires:",[r["q"][:70] for r in R if r["set"] in ("eval","faqa") and L[r["id"]]=="yes"][:12])
