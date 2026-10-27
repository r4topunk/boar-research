import json,sys,statistics
pre=sys.argv[1]
def load(p):
    d={}
    for l in open(p):
        r=json.loads(l); d[r["itemId"]]=sum(e["ms"] for e in r["events"] if e.get("type")=="retrieve" and "ms" in e)
    return d
def agg(tag):
    runs=[load(f"{pre}-{tag}{i}.jsonl") for i in (1,2,3)]
    return {i:min(r[i] for r in runs) for i in runs[0]}, [round(statistics.median(r.values()),1) for r in runs]
b,br=agg("base"); s,sr=agg("sel")
print("per-run p50 base",br,"sel",sr)
print("p50 of per-item min-of-3: base",round(statistics.median(b.values()),1),"sel",round(statistics.median(s.values()),1),"ratio",round(statistics.median(s.values())/statistics.median(b.values()),3))
print("ratio of per-run p50s:",[round(x/y,3) for x,y in zip(sr,br)])
