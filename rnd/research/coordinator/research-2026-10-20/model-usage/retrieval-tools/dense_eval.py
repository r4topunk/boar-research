import json,sqlite3,glob,ast,sys
import numpy as np
Q=json.load(open('/tmp/rmaudit/out/qvec.json'))
P='<workspace>/shared-data/packs/'
packfile=lambda p: (P+'v3proto/'+p+'.sqlite') if glob.glob(P+'v3proto/'+p+'.sqlite') else glob.glob(P+'*/'+p+'.sqlite')[0]
def lit(x): return x if isinstance(x,(list,dict)) else ast.literal_eval(x)
rows=[]
for f in sorted(glob.glob('<workspace>/rnd/research/packs/selftest/*.jsonl')):
    items=[json.loads(l) for l in open(f)]
    pack=items[0]['pack']; db=sqlite3.connect('file:'+packfile(pack)+'?mode=ro',uri=True)
    lv=db.execute('select article_id,vec from lead_vecs order by article_id').fetchall()
    lids=np.array([r[0] for r in lv]); L=np.frombuffer(b''.join(r[1] for r in lv),dtype=np.int8).reshape(-1,384).astype(np.float32)
    L/=np.linalg.norm(L,axis=1,keepdims=True)+1e-9
    hascv=db.execute("select 1 from sqlite_master where name='chunk_vecs'").fetchone() is not None
    for it in items:
        facts=lit(it['in_pack_facts']); src=lit(it['source']); gold_a=src['article_id']
        gold_chunks=set()
        for fa in facts:
            ch=[r[0] for r in db.execute('select id from chunks where article_id=? order by id',(fa.get('article',gold_a),))]
            if fa['chunk_index']<len(ch): gold_chunks.add(ch[fa['chunk_index']])
        rec={'id':it['id'],'pack':pack}
        for mode in('raw','inst'):
            q=np.array(Q[it['id']][mode],dtype=np.float32); q/=np.linalg.norm(q)
            s=L@q; order=np.argsort(-s,kind='stable')
            pos=np.where(lids[order]==gold_a)[0]
            rec[mode+'_lead_rank']=int(pos[0])+1 if len(pos) else None
            rec[mode+'_lead_cos']=float(s[lids==gold_a][0]) if (lids==gold_a).any() else None
            if hascv:
                top=lids[order[:50]].tolist()
                cv=db.execute(f"select c.id,v.vec from chunks c join chunk_vecs v on v.chunk_id=c.id where c.article_id in ({','.join('?'*len(top))})",top).fetchall()
                C=np.frombuffer(b''.join(r[1] for r in cv),dtype=np.int8).reshape(-1,384).astype(np.float32); C/=np.linalg.norm(C,axis=1,keepdims=True)+1e-9
                cs=C@q; cid=np.array([r[0] for r in cv]); o=np.argsort(-cs,kind='stable')
                kept=[(int(cid[i]),float(cs[i])) for i in o if cs[i]>=0.55][:12]
                keptids=[k for k,_ in kept]
                gr=[keptids.index(g)+1 for g in gold_chunks if g in keptids]
                rec[mode+'_gold_in_dense12']=bool(gr); rec[mode+'_gold_best_rank']=min(gr) if gr else None
                rec[mode+'_gold_in_top2']=bool(gr and min(gr)<=2)
                rec[mode+'_nkept']=len(kept)
                # gold chunk cosine (any gold chunk, max)
                gc=[]
                for g in gold_chunks:
                    v=db.execute('select vec from chunk_vecs where chunk_id=?',(g,)).fetchone()
                    if v: x=np.frombuffer(v[0],dtype=np.int8).astype(np.float32); gc.append(float(x@q/np.linalg.norm(x)))
                rec[mode+'_gold_cos']=max(gc) if gc else None
                rec[mode+'_top1_cos']=kept[0][1] if kept else float(cs[o[0]])
        rows.append(rec)
json.dump(rows,open('/tmp/rmaudit/out/dense_eval.json','w'))
import collections
by=collections.defaultdict(list)
for r in rows: by[r['pack']].append(r); by['ALL'].append(r)
def m(xs): xs=[x for x in xs if x is not None]; return (sum(xs)/len(xs)) if xs else float('nan')
print('pack n | lead@1 raw/inst | lead@50 raw/inst | dense12 raw/inst | top2 raw/inst | goldcos raw/inst | top1cos raw/inst | nkept raw/inst')
for p,rs in by.items():
    f=lambda k:[r.get(k) for r in rs]
    a1=[ (r['raw_lead_rank']==1, r['inst_lead_rank']==1) for r in rs]
    a50=[ (r['raw_lead_rank'] is not None and r['raw_lead_rank']<=50, r['inst_lead_rank'] is not None and r['inst_lead_rank']<=50) for r in rs]
    print(p,len(rs),'|',sum(x for x,_ in a1),sum(y for _,y in a1),'|',sum(x for x,_ in a50),sum(y for _,y in a50),'|',
      sum(bool(x) for x in f('raw_gold_in_dense12')),sum(bool(x) for x in f('inst_gold_in_dense12')),'|',
      sum(bool(x) for x in f('raw_gold_in_top2')),sum(bool(x) for x in f('inst_gold_in_top2')),'|',
      round(m(f('raw_gold_cos')),3),round(m(f('inst_gold_cos')),3),'|',round(m(f('raw_top1_cos')),3),round(m(f('inst_top1_cos')),3),'|',round(m(f('raw_nkept')),1),round(m(f('inst_nkept')),1))
