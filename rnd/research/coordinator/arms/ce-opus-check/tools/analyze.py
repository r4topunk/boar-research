#!/usr/bin/env python3
"""CEOPUS analysis (0 calls). python3 -I analyze.py"""
import json,glob
A='<workspace>/rnd/research/coordinator/arms'; C=A+'/ce-opus-check'
W="Not found in this phone's offline library. From the model's memory, may be wrong:"
ctl=json.load(open(A+'/lp-screens/control/aggregates/lpctl-K0-screen-s42.json'))['items']
gr=json.load(open(A+'/greedy/aggregates/greedy-K0-screen-s42.json'))['items']
ids=open(A+'/lp-screens/screen-K0.ids').read().split(); prob=ids[:27]
op={}
for tag in('ctl','greedy'):
    by={}
    for f in glob.glob(f'{C}/out/{tag}-*.judgments.jsonl'):
        for l in open(f):
            r=json.loads(l)
            if r.get('ok'): by.setdefault(r['queryId'],{})[r['order']]=r['mapped']['boar']['correctness']
    op[tag]={i:sum(v.values())/2 for i,v in by.items() if len(v)==2}
def lab(it,corr): return (not it['declined']) and corr<=1.5
rows=[]  # (src,id,hCE,oCE,hUW,oUW,hcorr,ocorr)
for tag,src in(('ctl',ctl),('greedy',gr)):
    for i,oc in op[tag].items():
        it=src[i]; w=it['text'].startswith(W); h=it['CE']; o=lab(it,oc)
        rows.append((tag,i,h,o,h and not w,o and not w,it['corr'],oc))
def stats(sel,hi,oi):
    n=len(sel); a=sum(r[hi]==r[oi] for r in sel); po=a/n
    ph=sum(r[hi] for r in sel)/n; pq=sum(r[oi] for r in sel)/n; pe=ph*pq+(1-ph)*(1-pq)
    k=(po-pe)/(1-pe) if pe<1 else float('nan')
    return dict(n=n,agree=a,rate=round(po,3),kappa=round(k,3),haikuCE=sum(r[hi] for r in sel),opusCE=sum(r[oi] for r in sel),hCE_oNot=sum(r[hi] and not r[oi] for r in sel),oCE_hNot=sum(r[oi] and not r[hi] for r in sel))
out={'n_answers':len(rows),'opus_calls':2*len(rows)}
for nm,sel in(('all',rows),('ctl',[r for r in rows if r[0]=='ctl']),('greedy',[r for r in rows if r[0]=='greedy'])):
    out[nm]=dict(CE=stats(sel,2,3),CE_unwarned=stats(sel,4,5))
d=[r[7]-r[6] for r in rows]; out['corr']=dict(MAE=round(sum(abs(x) for x in d)/len(d),3),mean_opus_minus_haiku=round(sum(d)/len(d),3))
def gcl(i,t):  # greedy label under opus (own if changed else control)
    return lab(gr[i],op['greedy'][i]) if i in op['greedy'] else (lab(ctl[i],op['ctl'][i]) if i in op['ctl'] else None)
fixO=[i for i in prob if i in op['ctl'] and lab(ctl[i],op['ctl'][i]) and gcl(i,0) is False]
fixO2=[i for i in prob if ctl[i]['CE'] and gcl(i,0) is False]
fixH=[i for i in prob if ctl[i]['CE'] and not gr[i]['CE']]
out['greedy_fixed']=dict(haiku=fixH,opus_primary=fixO,opus_secondary=fixO2)
out['flag_judge_sensitive']=out['all']['CE']['rate']<0.80
json.dump(out,open(C+'/ceopus.json','w'),indent=1); print(json.dumps(out,indent=1))
