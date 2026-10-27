"""CRYPTOSEL L0 (deterministic, stub LLM): python3 l0.py base.traces sel.traces [more sel.traces for latency] 
Reports gold-fact hits on the 3 targets, changed items (and whether crypto-routed), goldhit-sent loss on crypto-routed items, retrieve p50."""
import json,re,sys,statistics
A=sys.argv[1]; B=sys.argv[2]
HERE="<workspace>/rnd/research/coordinator/arms/cryptosel/"
gold=json.load(open(HERE+"gold-facts.json"))
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
def hit(i,ctx):
    cg=grams(W(ctx))
    for alt in gold[i]:
        if "regex" in alt:
            if re.search(alt["regex"],ctx): return True
        else:
            g=grams(W(alt["sentence"]))
            if g and len(g&cg)/len(g)>=0.6: return True
    return False
CR=re.compile(r"^(Ethereum EIPs/ERCs|Ethereum specs|Bitcoin BIPs|ethereum\.org)")
a=load(A); b=load(B)
print("== gold fact in context (base -> sel)")
gain=lose=0
for i in ("vit-cry-002","vit-cry-003","vit-cry-009"):
    x,y=hit(i,a[i]["ctx"]),hit(i,b[i]["ctx"]); gain+=(not x and y); lose+=(x and not y); print(f"  {i}: {x} -> {y}")
print(f"  gained {gain}/3, lost {lose}")
ch=[i for i in a if a[i]["ctx"]!=b[i]["ctx"]]
cr=lambda d,i: any(CR.match(s["title"]) for s in d[i]["src"])
print("== changed contexts:",len(ch),[(i,"crypto-routed" if (cr(a,i) or cr(b,i)) else "NON-CRYPTO") for i in ch])
cri=[i for i in a if cr(a,i)]
print("== crypto-routed items (base):",len(cri),cri)
# goldhit sentence metric (Sonar) on v0.1 items, crypto-routed ones
O="<workspace>/rnd/research/anvil/exp/oracle/"
R={json.loads(l)["id"]:json.loads(l)["passages"] for l in open(O+"ctx-R450.jsonl")}
def sent(i,ctx):
    if not R.get(i): return None
    cg=grams(W(ctx)); ss=[x for p in R[i][:3] for x in re.split(r"(?<=[.!?])\s+",p["text"]) if len(W(x))>=8]
    return max((len(grams(W(x))&cg)/max(1,len(grams(W(x)))) for x in ss),default=0.0)>=0.6
lost=[i for i in cri if sent(i,a[i]["ctx"]) and not sent(i,b[i]["ctx"])]
print("== crypto-routed items losing a goldhit gold sentence:",lost, "| goldhit-sent hits base/sel on crypto-routed:",sum(1 for i in cri if sent(i,a[i]["ctx"])),sum(1 for i in cri if sent(i,b[i]["ctx"])))
# gold-fact check for crypto-routed items where the 4-gram fact of the base context vanished: sentences of base ctx sources from spec pages kept?
def p50(paths):
    return statistics.median([min(load(p)[i]["ms"] for p in paths) for i in a])
if len(sys.argv)>3:
    k=sys.argv[3:]; 
    ba=[A]+[x for x in k if x.startswith("base:")]; 
print("== retrieve ms p50 (median over items of the per-item retrieve ms)")
print("   base",round(statistics.median([a[i]["ms"] for i in a]),1),"sel",round(statistics.median([b[i]["ms"] for i in b]),1),"ratio",round(statistics.median([b[i]["ms"] for i in b])/statistics.median([a[i]["ms"] for i in a]),3))
