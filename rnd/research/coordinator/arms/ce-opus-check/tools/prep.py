#!/usr/bin/env python3
"""Builds the CEOPUS sets (0 calls). python3 -I prep.py"""
import json,os
A='<workspace>/rnd/research/coordinator/arms'; O=A+'/ce-opus-check/in'
c=json.load(open(A+'/lp-screens/control/aggregates/lpctl-K0-screen-s42.json'))['items']
g=json.load(open(A+'/greedy/aggregates/greedy-K0-screen-s42.json'))['items']
ids=open(A+'/lp-screens/screen-K0.ids').read().split()
ctl=[i for i in ids if c[i]['CE']]; chg=[i for i in ids if g[i]['text']!=c[i]['text']]
v01=set(open(A+'/litepacks/data/v01-57.ids').read().split())
unit=lambda i:'v01' if i in v01 else ('qa-cooking-se' if i.startswith('st-qa-cooking-se-') else 'qa-money-se')
for tag,sel,tr in (('ctl',ctl,A+'/lp-screens/control/traces/lpctl-K0-screen-s42.traces.jsonl'),('greedy',chg,A+'/greedy/traces/greedy-K0-screen-s42.traces.jsonl')):
    rows=[json.loads(l) for l in open(tr) if l.strip()]
    for u in ('v01','qa-cooking-se','qa-money-se'):
        s=[i for i in sel if unit(i)==u]
        if not s: continue
        open(f'{O}/{tag}-{u}.ids','w').write('\n'.join(s)+'\n')
        with open(f'{O}/{tag}-{u}.traces.jsonl','w') as f:
            for r in rows:
                if r['itemId'] in s: f.write(json.dumps(r,ensure_ascii=False)+'\n')
        print(tag,u,len(s))
print(len(ctl),len(chg),'calls',2*(len(ctl)+len(chg)))
