import json,glob,sys,math
A='<workspace>/rnd/research/coordinator/arms'
def load_j(pattern):
    by={}
    for f in glob.glob(pattern):
        for l in open(f):
            if not l.strip(): continue
            r=json.loads(l)
            if r.get('ok'): by.setdefault(r['queryId'],{})[r['order']]=r['mapped']['boar']['correctness']
    return by
def items(tr, jpat, ctl=None):
    T={json.loads(l)['itemId']:json.loads(l) for l in open(tr)}
    J=load_j(jpat); out={}
    for i,t in T.items():
        txt=t['answer']['text']; d=bool(t['answer'].get('declined'))
        if ctl and ctl[i]['text']==txt: c=ctl[i]['corr']; src='ctl'
        else:
            o=J.get(i,{}); 
            if len(o)!=2: out[i]=None; continue
            c=(o['boarA']+o['boarB'])/2; src='own'
        out[i]=dict(text=txt,corr=c,CE=(not d and c<=1.5),declined=d,src=src)
    return out
arm,K,run=sys.argv[1:4]
ctl=items(f'{A}/lp-screens/control/traces/lpctl-{K}-screen-s42.traces.jsonl', f'{A}/lp-screens/control/judgments/lpctl-{K}-screen-s42-*.judgments.jsonl')
cand=items(f'{A}/{arm}/traces/{run}.traces.jsonl', f'{A}/{arm}/judgments/{run}-*.judgments.jsonl', ctl)
sc=json.load(open(f'{A}/lp-screens/screen-{K}.json'))
P,S=sc['problems'],sc['sentinels']
ctlce=[i for i in P if ctl[i]['CE']]
fixed=[i for i in ctlce if not cand[i]['CE']]
worse=[i for i in S if cand[i]['corr']<=ctl[i]['corr']-1 or (cand[i]['CE'] and not ctl[i]['CE']) or (cand[i]['declined'] and not ctl[i]['declined'])]
chg=sum(cand[i]['text']!=ctl[i]['text'] for i in P+S)
print(run,'ctlCE',len(ctlce),'fixed',len(fixed),fixed,'worse',worse,'changed',chg,'candCE',sum(cand[i]['CE'] for i in P+S),'ctlCEall',sum(ctl[i]['CE'] for i in P+S))
# null-ish: fixes among changed vs unchanged
print('  changed problem CE items', sum(1 for i in ctlce if cand[i]['text']!=ctl[i]['text']))
