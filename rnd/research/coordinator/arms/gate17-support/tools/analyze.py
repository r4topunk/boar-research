import json,random,collections
A="<workspace>/rnd/research/coordinator/arms/gate17"
items=json.load(open(A+"/gate/items.json"))["items"]
g={json.loads(l)["key"]:json.loads(l)["P_FAIL"] for l in open(A+"/gate/boar.outputs.jsonl") if '"key": "K' in l}
lab=collections.defaultdict(dict)
for l in open("labels.jsonl"):
    r=json.loads(l); lab[r["key"]][r["call"]]=r["label"]
rows=[];agree=0;ab=[]
for x in items:
    L=lab[x["key"]]; ab.append((L["A"],L["B"])); agree+=L["A"]==L["B"]
    f=L["A"] if L["A"]==L["B"] else collections.Counter([L["A"],L["B"],L["C"]]).most_common(1)[0][0]
    rows.append({**{k:x[k] for k in("key","id","CE","corr","warned")},"s":g[x["key"]],"U":f=="UNSUPPORTED","dis":L["A"]!=L["B"]})
n=len(rows);pa=agree/n
pu=sum(a=="UNSUPPORTED" for a,_ in ab)/n;pv=sum(b=="UNSUPPORTED" for _,b in ab)/n
pe=pu*pv+(1-pu)*(1-pv);kappa=(pa-pe)/(1-pe) if pe<1 else 1
def auc(P,N): return sum(1 if p>q else .5 if p==q else 0 for p in P for q in N)/(len(P)*len(N))
def a_(rs): return auc([r["s"] for r in rs if r["U"]],[r["s"] for r in rs if not r["U"]])
a=a_(rows);rnd=random.Random(11);bs=[]
for _ in range(2000):
    s=[rows[rnd.randrange(n)] for _ in rows]
    if any(r["U"] for r in s) and any(not r["U"] for r in s): bs.append(a_(s))
bs.sort();ci=[bs[int(.025*len(bs))],bs[int(.975*len(bs))-1]]
U=[r for r in rows if r["U"]];S=[r for r in rows if not r["U"]]
def at(t):
    f=[r for r in rows if r["s"]>=t];c=sum(r["U"] for r in f);fr=sum(not r["U"] for r in f)
    return {"t":t,"flagged":len(f),"caught":c,"recall":c/len(U),"false_ref":fr,"fr_rate":fr/len(S)}
tab=[at(t) for t in sorted({r["s"] for r in rows},reverse=True)]
ts=[x for x in tab if x["recall"]>=.7][0]
fixed=[at(t) for t in (0.99,0.9,0.5)]
res={"n":n,"unsupported":len(U),"supported":len(S),"agree":agree,"pa":pa,"kappa":kappa,"third_calls":sum(r["dis"] for r in rows),
 "auc":a,"ci":ci,"tstar_row":ts,"fixed":fixed,
 "memory_correct":sum(r["corr"]>=4 for r in U),"correct_total":sum(r["corr"]>=4 for r in rows),
 "sw_CE":sum(r["CE"] for r in S),"sw_wrong":sum(r["corr"]<=2 for r in S),"CE_total":sum(r["CE"] for r in rows),
 "median_s":{"U":sorted(r["s"] for r in U)[len(U)//2],"S":sorted(r["s"] for r in S)[len(S)//2]},
 "verdict":"GO" if a>=.75 and ci[0]>=.65 and ts["fr_rate"]<=.15 else "NO",
 "rows":[{k:r[k] for k in("key","CE","corr","s","U")} for r in rows]}
json.dump(res,open("analysis.json","w"),indent=1)
print({k:v for k,v in res.items() if k!="rows"})
