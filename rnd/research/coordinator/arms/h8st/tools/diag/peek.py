import json, sqlite3, subprocess, os, collections, random
exec(open('diag137.py').read().split('res = []')[0])
R=[x for x in json.load(open('diag137.json')) if not x['S_kept_ST2']]
random.seed(7); sample=random.sample(R,14)
for x in sample:
    db=sqlite3.connect(f"file:{pub(x['pack'])}?mode=ro",uri=True); c=x['best']['chunk']
    aid,s,e=db.execute("select article_id,start,end from chunks where id=?",(c,)).fetchone()
    t,bid,off,ln=db.execute("select title,block_id,off,len from articles where id=?",(aid,)).fetchone()
    z=db.execute("select zdata from blocks where id=?",(bid,)).fetchone()[0]
    txt=subprocess.run(["zstd","-dc"],input=bytes(z),capture_output=True,check=True).stdout[off:off+ln].decode()
    nch=db.execute("select count(*) from chunks where article_id=?",(aid,)).fetchone()[0]
    pos=[r[0] for r in db.execute("select id from chunks where article_id=? order by start",(aid,))].index(c)
    print('\n##',x['id'],x['best']['cls'],'rank',x['best']['bm25_rank'],'idxcov',x['best']['idx_cov'],'pos',pos,'/',nch,'art_in_raw',x['art_in_raw'])
    print('Q:',x['query']); print('ART:',t); print('CHUNK:',js_slice(txt,s,e).strip()[:260].replace('\n',' | '))
