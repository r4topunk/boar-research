import json,sqlite3,re,unicodedata
from compression import zstd
B='<workspace>/rnd/research/'
rd=lambda f:[json.loads(l) for l in open(f) if l.strip()]
def n2(x):
    x=unicodedata.normalize('NFKC',x or '').lower().replace('’',"'")
    return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9]+',' ',x)).strip()
PK={'boar-firstaid-en':'<workspace>/shared-data/packs/v3proto/boar-firstaid-en.sqlite','boar-medlineplus-en':'<workspace>/shared-data/packs/v3proto/boar-medlineplus-en.sqlite'}
out={}
for pack,path in PK.items():
    c=sqlite3.connect(f'file:{path}?mode=ro',uri=True)
    for st in rd(B+f'packs/selftest/{pack}.jsonl'):
        aid=st['source']['article_id']
        a=c.execute('select block_id,off,len,title from articles where id=?',(aid,)).fetchone()
        blk=zstd.decompress(c.execute('select zdata from blocks where id=?',(a[0],)).fetchone()[0])
        raw=blk[a[1]:a[1]+a[2]]; text=raw.decode('utf8')
        qs=[n2(f['quote']) for f in st['in_pack_facts']]
        fc=[];allc=[]
        for cid,s,e in c.execute('select id,start,end from chunks where article_id=? order by start',(aid,)):
            t1=text[s:e]; t2=raw[s:e].decode('utf8','ignore')
            allc.append(cid)
            for t in (t1,t2):
                if any(q and q in n2(t) for q in qs): fc.append(cid); break
        out[st['id']]=dict(pack=pack,aid=aid,title=a[3],article_chunks=allc,fact_chunks=sorted(set(fc)),nq=len(qs))
json.dump(out,open('factchunks.json','w'),indent=1)
for i,x in out.items(): print(i[3:],x['aid'],len(x['article_chunks']),'fact chunks',x['fact_chunks'])
