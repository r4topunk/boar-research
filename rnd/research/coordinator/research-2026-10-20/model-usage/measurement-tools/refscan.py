import json,glob,re,collections
A='<workspace>/rnd/research/coordinator/arms'
RX=re.compile(r"(i (do not|don't) know|i'?m not sure|i cannot answer|i can'?t answer|not enough information|couldn'?t find|could not find|no (reliable )?information|(do|does)n'?t (contain|mention|say|cover)|(do|does) not (contain|mention|say|cover)|unable to (find|answer|confirm))",re.I)
T={}
for f in glob.glob(A+'/*/traces/*.jsonl'):
    try:
        for l in open(f):
            t=json.loads(l); txt=(t.get('answer') or {}).get('text') or ''
            T[(t.get('runId'),t.get('itemId'))]=(txt,bool((t.get('answer') or {}).get('declined')))
    except Exception as e: pass
res=collections.defaultdict(list); seen=set()
for f in glob.glob(A+'/*/judgments/*.judgments.jsonl'):
    for l in open(f):
        try: r=json.loads(l)
        except: continue
        if not r.get('ok') or r.get('floorScored'): continue
        k=(r.get('runId'),r['queryId'])
        if k not in T: continue
        txt,d=T[k]
        if len(txt)<400 and RX.search(txt):
            res[(k,txt[:160],d)].append((r['mapped']['boar']['correctness'],r.get('judgeVersion')))
corrs=[]
for (k,txt,d),v in sorted(res.items()):
    m=sum(c for c,_ in v)/len(v); corrs.append(m)
print('refusal-like judged answers',len(res),'mean corr',sum(corrs)/len(corrs) if corrs else None,'share <=1.5',sum(c<=1.5 for c in corrs)/max(1,len(corrs)))
print(collections.Counter(round(c*2)/2 for c in corrs))
for (k,txt,d),v in list(sorted(res.items()))[:25]: print(k[0][:30],k[1],'decl',d,[c for c,_ in v],v[0][1],'|',txt.replace('\n',' '))
