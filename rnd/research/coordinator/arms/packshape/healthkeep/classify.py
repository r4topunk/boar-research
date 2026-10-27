import json,re
rd=lambda f:[json.loads(l) for l in open(f) if l.strip()]
FC=json.load(open('factchunks.json')); Q={}
for pk in ('boar-firstaid-en','boar-medlineplus-en'):
    for st in rd(f'<workspace>/rnd/research/packs/selftest/{pk}.jsonl'): Q[st['id']]=st
res={}
for r in rd('hk2.jsonl'):
    i=r['id']; fc=FC[i]; pk=fc['pack']
    F={f'pack:local-{pk}:{n}' for n in fc['fact_chunks']}; A={f'pack:local-{pk}:{n}' for n in fc['article_chunks']}
    codes=r['reasonCodes']
    def cv(k):
        for c in codes:
            if c.startswith('HK:'+k+':'): return [x for x in c[len('HK:'+k+':'):].split('|') if x]
        return []
    ids=lambda k:[c['chunkId'] for c in r[k]]
    raw,wide,kept=ids('rawFull'),ids('wideFull'),ids('keptFull')
    health='grounding:health-strict' in codes
    m=re.search(r'detector:p=([\d.]+)',' '.join(codes)); p=float(m.group(1)) if m else None
    fire='detector:fire' in codes
    hdrop=set(cv('drop'))|set(cv('x1drop'))|set(cv('densedrop'))|set(cv('sedrop'))
    appended=set(re.findall(r'headpass:(?:dense:|selead:)?add:(\S+)',' '.join(codes)))|set(cv('x1all'))|set(cv('denseall'))
    bud=set(re.findall(r'headpass:budget:dropped:(\S+)',' '.join(codes)))
    dc=cv('densecand')
    rank=[k+1 for k,c in enumerate(dc) if c in F]
    wr=[k+1 for k,c in enumerate(wide) if c in F]
    pre=set(cv('pre'))
    topic=cv('topic') if health else None
    cls=None
    if F&set(kept): cls='OK'
    elif health and F&hdrop: cls='B'
    elif F&bud: cls='E'
    elif F&set(raw+list(appended)): cls='A'
    elif F&set(wide): cls='D'
    elif F&set(dc): cls='C2'
    else: cls='C1'
    own_raw=bool(A&set(raw)); own_wide=bool(A&set(wide)); own_kept=bool(A&set(kept))
    why=[c[7:] for c in codes if c.startswith('HK:why:')]
    res[i]=dict(cls=cls,p=p,fire=fire,health=health,topic=topic,nkept=len(kept),rank=rank,wr=wr,own_raw=own_raw,own_wide=own_wide,own_kept=own_kept,fact_in=dict(raw=sorted(F&set(raw)),wide=sorted(F&set(wide)),pre=sorted(F&pre),app=sorted(F&appended),bud=sorted(F&bud),hdrop=sorted(F&hdrop)),q=Q[i]['question'],cat=Q[i]['category'],own_title=Q[i]['source']['title'],codes=[c for c in codes if not c.startswith('HK:')])
json.dump(res,open('classes.json','w'),indent=1)
import collections
for pk in ('boar-firstaid-en','boar-medlineplus-en'):
    print(pk,collections.Counter(v['cls'] for k,v in res.items() if pk in k))
    for k,v in res.items():
        if pk in k: print(' ',k[-3:],v['cls'],'p=%s'%v['p'],'fire' if v['fire'] else '    ','H' if v['health'] else ' ','topic',v['topic'],'kept',v['nkept'],'rank',v['rank'][:3],'widepos',v['wr'],'ownraw/wide/kept',int(v['own_raw']),int(v['own_wide']),int(v['own_kept']),{a:b for a,b in v['fact_in'].items() if b and a!='raw'} if v['cls']!='OK' else '')
