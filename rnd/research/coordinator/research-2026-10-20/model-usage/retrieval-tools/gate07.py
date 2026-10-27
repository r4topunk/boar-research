import json,sqlite3,numpy as np
Q=json.load(open('/tmp/rmaudit/out/qvec.json'))
P='<workspace>/shared-data/packs/v3proto/'
for pack in ['boar-simplewiki-en','boar-firstaid-en']:
    db=sqlite3.connect('file:'+P+pack+'.sqlite?mode=ro',uri=True)
    lv=db.execute('select article_id,vec from lead_vecs order by article_id').fetchall()
    lids=np.array([r[0] for r in lv]); L=np.frombuffer(b''.join(r[1] for r in lv),dtype=np.int8).reshape(-1,384).astype(np.float32); L/=np.linalg.norm(L,axis=1,keepdims=True)
    res={}
    for grp in ['qa-cooking-se','qa-money-se','qa-travel-se','qa-bitcoin-se','qa-ethereum-se','qa-outdoors-se','qa-health-se',pack]:
        ids=[k for k in Q if k.startswith('st-'+grp)]; c2=[]
        for k in ids:
            q=np.array(Q[k]['raw'],dtype=np.float32); q/=np.linalg.norm(q)
            top=lids[np.argsort(-(L@q))[:50]].tolist()
            cv=db.execute(f"select v.vec from chunks c join chunk_vecs v on v.chunk_id=c.id where c.article_id in ({','.join('?'*len(top))})",top).fetchall()
            C=np.frombuffer(b''.join(r[0] for r in cv),dtype=np.int8).reshape(-1,384).astype(np.float32); C/=np.linalg.norm(C,axis=1,keepdims=True)
            cs=np.sort(C@q)[::-1]; c2+= [cs[0],cs[1]]
        c2=np.array(c2); res[grp]=dict(top2_ge055=round(float((c2>=0.55).mean()),2),top2_ge07=round(float((c2>=0.70).mean()),2),med=round(float(np.median(c2)),3))
    print(pack,json.dumps(res))
