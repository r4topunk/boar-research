import json,sys
def load(f): return {json.loads(l)['id']:json.loads(l) for l in open(f)}
for name in ['packread','v01']:
    A=load(f'{sys.argv[1]}/{name}.jsonl'); B=load(f'{sys.argv[2]}/{name}.jsonl')
    ch=[i for i in A if A[i]['sources']!=B[i]['sources']]
    rawch=[i for i in A if [x['title'] for x in A[i]['raw']]!=[x['title'] for x in B[i]['raw']]]
    hs=lambda r:'grounding:health-strict' in r.get('codes',[])
    newh=[i for i in A if hs(B[i]) and not hs(A[i])]
    qch=[i for i in A if A[i]['query']!=B[i]['query']]
    ms=lambda D:sorted(x['ms'] or 0 for x in D.values())
    import statistics
    print(f"{name}: n={len(A)} sources-changed={len(ch)} raw-changed={len(rawch)} query-changed={len(qch)} newly-health={len(newh)} health-items={sum(hs(B[i]) for i in B)} p50ms {statistics.median(ms(A)):.0f}->{statistics.median(ms(B)):.0f} max {max(ms(A)):.0f}->{max(ms(B)):.0f}")
    for i in ch: print('   ',i,'|',A[i]['query'][:60] if A[i]['query'] else None,'->',B[i]['query'][:60] if B[i]['query'] else None,'\n      ',A[i]['sources'],'\n    ->',B[i]['sources'])
