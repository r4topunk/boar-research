"""TRAVELSEL L0 (deterministic, stub LLM): python3 l0.py base.traces sel.traces
Gold-fact hits on the 3 targets (frozen gold-facts.json), changed items (and whether travel-routed = a Wikivoyage source in either context),
goldhit-sent loss on travel-routed items, venue/GPS items identical (context + route), retrieve p50."""
import json,re,sys,statistics
A=sys.argv[1]; B=sys.argv[2]
HERE="<workspace>/rnd/research/coordinator/arms/travelsel/"
gold=json.load(open(HERE+"gold-facts.json")); gold.pop("note")
SUPP=json.load(open(HERE+"gold-facts-supplement.json")) if len(sys.argv)>3 and sys.argv[3]=="supp" else {}
SUPP.pop("note",None)
W=lambda s: re.findall(r"\w+", s.lower())
def grams(ws,n=4): return {tuple(ws[i:i+n]) for i in range(len(ws)-n+1)}
def load(p):
    d={}
    for l in open(p):
        r=json.loads(l); ev=[e for e in r["events"] if e.get("type")=="sources" and any(x.get("text") for x in e.get("sources",[]))]
        src=ev[-1]["sources"] if ev else []
        ctx="\n\n".join(f"{x['title']}\n{x.get('text') or ''}" for x in src)
        ms=[e["ms"] for e in r["events"] if e.get("type")=="retrieve" and "ms" in e]
        d[r["itemId"]]=dict(ctx=ctx,src=src,ms=sum(ms),codes=r["route"].get("reasonCodes",[]),q=r["question"])
    return d
def hit(g,i,ctx):
    cg=grams(W(ctx))
    for alt in g[i]:
        if "regex" in alt:
            if re.search(alt["regex"],ctx): return True
        else:
            x=grams(W(alt["sentence"]))
            if x and len(x&cg)/len(x)>=0.6: return True
    return False
WV=re.compile(r"^Wikivoyage:")
a=load(A); b=load(B)
for lab,g in (("frozen gold",gold),("supplement (post-hoc, non-gating)",SUPP)):
    if not g: continue
    print("== gold fact in context, base -> sel:",lab)
    gain=lose=0
    for i in g:
        x,y=hit(g,i,a[i]["ctx"]),hit(g,i,b[i]["ctx"]); gain+=(not x and y); lose+=(x and not y); print(f"  {i}: {x} -> {y}")
        for k,alt in enumerate(g[i]): print("      alt",k,hit({i:[alt]},i,a[i]["ctx"]),"->",hit({i:[alt]},i,b[i]["ctx"]))
    print(f"  gained {gain}/{len(g)}, lost {lose}")
tr=lambda d,i: any(WV.match(s["title"]) for s in d[i]["src"])
ch=[i for i in a if a[i]["ctx"]!=b[i]["ctx"]]
print("== changed contexts:",len(ch),[(i,"travel-routed" if (tr(a,i) or tr(b,i)) else "NON-TRAVEL") for i in ch])
tri=[i for i in a if tr(a,i)]
print("== travel-routed items (base):",len(tri))
O="<workspace>/rnd/research/anvil/exp/oracle/"
R={json.loads(l)["id"]:json.loads(l)["passages"] for l in open(O+"ctx-R450.jsonl")}
def sent(i,ctx):
    if not R.get(i): return None
    cg=grams(W(ctx)); ss=[x for p in R[i][:3] for x in re.split(r"(?<=[.!?])\s+",p["text"]) if len(W(x))>=8]
    return max((len(grams(W(x))&cg)/max(1,len(grams(W(x)))) for x in ss),default=0.0)>=0.6
lost=[i for i in tri if sent(i,a[i]["ctx"]) and not sent(i,b[i]["ctx"])]
print("== travel-routed items losing a goldhit gold sentence:",lost,"| goldhit-sent hits base/sel on travel-routed:",sum(1 for i in tri if sent(i,a[i]["ctx"])),sum(1 for i in tri if sent(i,b[i]["ctx"])))
V=["food-001","food-002","food-006","vx-003","vx-004","vx-005"]
print("== venue items (6) identical context+route:",[ (i, a[i]["ctx"]==b[i]["ctx"] and a[i]["codes"]==b[i]["codes"]) for i in V])
ma=statistics.median([a[i]["ms"] for i in a]); mb=statistics.median([b[i]["ms"] for i in b])
print("== retrieve ms p50 base",round(ma,1),"sel",round(mb,1),"ratio",round(mb/ma,3))
