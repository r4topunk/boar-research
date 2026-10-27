import json,sqlite3,glob,numpy as np
Q=json.load(open('/tmp/rmaudit/out/qvec.json'))
P='<workspace>/shared-data/packs/v3proto/'
rng=np.random.default_rng(0)
for pack in ['boar-simplewiki-en','boar-firstaid-en','boar-factbook','boar-medlineplus-en']:
    db=sqlite3.connect('file:'+P+pack+'.sqlite?mode=ro',uri=True)
    lv=db.execute('select article_id,vec from lead_vecs order by article_id').fetchall()
    lids=np.array([r[0] for r in lv]); L=np.frombuffer(b''.join(r[1] for r in lv),dtype=np.int8).reshape(-1,384).astype(np.float32); L/=np.linalg.norm(L,axis=1,keepdims=True)
    n=db.execute('select max(rowid) from chunk_vecs').fetchone()[0]
    samp=db.execute('select vec from chunk_vecs order by random() limit 3000').fetchall()
    R=np.frombuffer(b''.join(r[0] for r in samp),dtype=np.int8).reshape(-1,384).astype(np.float32); R/=np.linalg.norm(R,axis=1,keepdims=True)
    out={}
    for grp in ['qa-cooking-se','qa-money-se','qa-travel-se','qa-bitcoin-se','boar-'+pack.split('boar-')[1]]:
        ids=[k for k in Q if k.startswith('st-'+grp)]
        t1=[];t2=[];rnd=[]
        for k in ids:
            q=np.array(Q[k]['raw'],dtype=np.float32); q/=np.linalg.norm(q)
            top=lids[np.argsort(-(L@q))[:50]].tolist()
            cv=db.execute(f"select v.vec from chunks c join chunk_vecs v on v.chunk_id=c.id where c.article_id in ({','.join('?'*len(top))})",top).fetchall()
            C=np.frombuffer(b''.join(r[0] for r in cv),dtype=np.int8).reshape(-1,384).astype(np.float32); C/=np.linalg.norm(C,axis=1,keepdims=True)
            cs=np.sort(C@q)[::-1]; t1.append(cs[0]); t2.append(cs[1]); rnd.extend((R@q).tolist())
        rnd=np.array(rnd)
        out[grp]=dict(n=len(ids),top1_med=round(float(np.median(t1)),3),top2_min=round(float(np.min(t2)),3),share_top2_ge055=round(float(np.mean(np.array(t2)>=0.55)),2),rand_med=round(float(np.median(rnd)),3),rand_p95=round(float(np.percentile(rnd,95)),3),rand_p99=round(float(np.percentile(rnd,99)),3))
    print(pack,json.dumps(out))
