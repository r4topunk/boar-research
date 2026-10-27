import json,sys,collections
S=sys.argv[1]; runs=sys.argv[2:]
pool=json.load(open(S+'/pool.json')); lex={o['id']:o['lex'] for o in json.load(open(S+'/lex.json'))}
def grp(p):
    s=p['src'][0]
    if p['history']: return 'multi-turn'
    if s.startswith('night'): return 'night'
    return {'compass-eval':'compass','compass-ptmirror':'pt-mirror'}.get(s, s)
def lang(p): 
    t=p['msg'].lower()
    return 'pt/es' if any(w in t for w in ' meu minha você não está ele ela mi tiene qué hago está muy '.split()) else 'en'
dets={'lex':lambda i:lex[i]}
for r in runs:
    if r.startswith('lex|'): continue
    name,_,th=r.partition('@'); th=float(th or 0.5)
    rows={json.loads(l)['id']:json.loads(l) for l in open(f'{S}/runs/{name}.jsonl')}
    if 'pE' in next(iter(rows.values())):
        dets[r]=(lambda rows,th: lambda i: (lambda x: x['pE']/max(1e-12,x['pE']+x['pS']+x['pA'])>=th)(rows[i]))(rows,th)
    else:
        dets[r]=(lambda rows,th: lambda i: rows[i]['score'] is None or rows[i]['score']>=th)(rows,th)
for r in runs:
    if r.startswith('lex|'): dets[r]=(lambda g: lambda i: lex[i] or g(i))(dets[r[4:]])
print(f"{'detector':22}{'recall E':>12}{'FP NOT':>10}{'FP hardneg':>12}{'HINFO fire':>11}  recall by group / FP by group")
for n,f in dets.items():
    E=[p for p in pool if p['label']=='EMERGENCY']; N=[p for p in pool if p['label']=='NOT']; H=[p for p in pool if p['label']=='HEALTH_INFO']
    hn=[p for p in N if p.get('hard_neg')]
    rg=collections.defaultdict(lambda:[0,0]); fg=collections.defaultdict(lambda:[0,0])
    for p in E: rg[grp(p)][0]+=f(p['id']); rg[grp(p)][1]+=1
    for p in N: fg[grp(p)][0]+=f(p['id']); fg[grp(p)][1]+=1
    print(f"{n:22}{sum(f(p['id']) for p in E):>5}/{len(E):<6}{sum(f(p['id']) for p in N):>4}/{len(N):<5}{sum(f(p['id']) for p in hn):>5}/{len(hn):<6}{sum(f(p['id']) for p in H):>4}/{len(H):<5}  R "+' '.join(f"{k}:{a}/{b}" for k,(a,b) in sorted(rg.items()))+" | FP "+' '.join(f"{k}:{a}/{b}" for k,(a,b) in sorted(fg.items()) if a))
