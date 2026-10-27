import sys,re,sqlite3
from compression import zstd
pk,f,q,rx=sys.argv[1:5]
db=sqlite3.connect(f"file:{f}?mode=ro",uri=True)
for (rid,) in db.execute("select rowid from fts where fts match ? order by rank limit 300",(q,)):
    a,s,e=db.execute("select article_id,start,end from chunks where id=?",(rid,)).fetchone()
    b,off,ln,t=db.execute("select block_id,off,len,title from articles where id=?",(a,)).fetchone()
    txt=zstd.decompress(db.execute("select zdata from blocks where id=?",(b,)).fetchone()[0])[off:off+ln].decode("utf-8","replace")[s:e]
    m=re.search(rx,txt,re.I)
    if m: print(t,'|',re.sub(r'\s+',' ',txt[max(0,m.start()-200):m.end()+200])); print('--')
