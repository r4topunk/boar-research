import json,sys
L=lambda f:{json.loads(l)['id']:json.loads(l) for l in open(f) if l.strip()}
a,b=L(sys.argv[1]),L(sys.argv[2]); ids=list(a)
f=lambda r,k:[c.get('chunkId') for c in r[k]]
print(len(ids), 'raw',sum(f(a[i],'rawFull')==f(b[i],'rawFull') for i in ids),'wide',sum(f(a[i],'wideFull')==f(b[i],'wideFull') for i in ids),
 'kept',sum(f(a[i],'keptFull')==f(b[i],'keptFull') for i in ids),'codes',sum(a[i]['reasonCodes']==b[i]['reasonCodes'] for i in ids))
