import json,glob
A='<workspace>/rnd/research/coordinator/arms'; LP=A+'/litepacks'
rd=lambda f:[json.loads(l) for l in open(f) if l.strip()]
def traces(a):
    out={}
    for f in sorted(glob.glob(f"{LP}/traces/lp-{a}-*-s42.traces.jsonl")):
        if 'smoke' in f: continue
        for t in rd(f): out[t['itemId']]=t
    return out
def judg(a):
    by={}
    for f in sorted(glob.glob(f"{LP}/judgments/lp-{a}-*.judgments.jsonl")):
        for r in rd(f):
            if r.get('ok') is True: by.setdefault(r['queryId'],{})[r['order']]=r['mapped']['boar']['correctness']
    return {q:sum(v.values())/2 for q,v in by.items() if len(v)==2}
TR={a:traces(a) for a in ('K0','K1')}; JR={a:judg(a) for a in ('K0','K1')}
def mbcorr(a,i): 
    return JR['K0'][i] if (a=='K0' or TR[a][i]['answer']['text']==TR['K0'][i]['answer']['text']) else JR[a][i]
for K in ('K0','K1'):
    sc=json.load(open(f'{A}/lp-screens/screen-{K}.json')); P=sc['problems']
    ctl=json.load(open(f'{A}/lp-screens/control/aggregates/lpctl-{K}-screen-s42.json'))['items']
    ch=[i for i in P if ctl[i]['text']!=TR[K][i]['answer']['text']]
    same=[i for i in P if i not in ch]
    print(K,'problems',len(P),'mini text changed',len(ch),'-> mini not CE among changed',sum(not ctl[i]['CE'] for i in ch),'| unchanged',len(same),'-> mini not CE (pure judge re-draw)',sum(not ctl[i]['CE'] for i in same))
