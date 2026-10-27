"""Answer-style L1 read: ratio, correctness, labels, output tokens (+ phone s at 5 tok/s), safety v0.8.11, key rv2-diag items."""
import json, sys, statistics as st, importlib.util
D="<workspace>/rnd/research/anvil/exp/answer-style/"; S11="<workspace>/rnd/research/compass/exp/safety-v0811/"
spec=importlib.util.spec_from_file_location("sc",S11+"safety_check.v0.8.11.py"); sc=importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
S=sc.load(rules_path=S11+"rules.v0.8.11.json", overlay_path=S11+"overlay.v0.4.json")
qs={json.loads(l)['id']:json.loads(l) for l in open('<workspace>/boar-eval/bench/v0.1/questions.public.jsonl')}
seeds=sys.argv[1:] or ['42']
rub=lambda d: st.mean([d['correctness'],d['completeness'],d['usefulness']])
def load(v):
    J={};T={}
    for s in seeds:
        for l in open(f"{D}runs/{v}-s{s}.judgments.jsonl"):
            r=json.loads(l)
            if r.get('ok'): J.setdefault(r['queryId'],[]).append(r['mapped'])
        for l in open(f"{D}runs/{v}-s{s}.traces.jsonl"):
            t=json.loads(l); T.setdefault(t['itemId'],[]).append(t)
    return J,T
res={}
for v in ['S0','S2','S3']:
    try: J,T=load(v)
    except FileNotFoundError: continue
    ids=sorted(J)
    b=sum(st.mean(rub(m['boar']) for m in J[i]) for i in ids); rf=sum(st.mean(rub(m['ref']) for m in J[i]) for i in ids)
    corr={i:st.mean(m['boar']['correctness'] for m in J[i]) for i in ids}
    toks=[t['timing']['outputTokens'] for i in T for t in T[i]]
    unsafe=[]
    for i in T:
        rules=sc.rules_for_v085(qs[i],S) if i in qs else []
        for t in T[i]:
            hits=sc.check(t['answer']['text'],rules,S) if rules else []
            if any((h.get('status') if isinstance(h,dict) else None)=='unsafe' or (isinstance(h,dict) and h.get('severity')=='unsafe') for h in hits): unsafe.append(i)
            elif hits and not isinstance(hits[0],dict): unsafe.append(f"{i}?")
    res[v]=dict(ids=ids,ratio=b/rf,corr=st.mean(corr.values()),pas=sum(c>=4 for c in corr.values()),cw=sum(c<=2 for c in corr.values()),tok50=st.median(toks),tokm=st.mean(toks),unsafe=sorted(set(unsafe)),J=J,T=T)
    print(f"{v}: n={len(ids)} ratio {b/rf:.3f} correctness {res[v]['corr']:.2f} pass/cw {res[v]['pas']}/{res[v]['cw']} out-tokens p50 {res[v]['tok50']:.0f} mean {res[v]['tokm']:.0f} (phone @5 tok/s p50 {res[v]['tok50']/5:.0f}s) unsafe(v0.8.11) {res[v]['unsafe']}")
if 'S0' in res:
    for v in ['S2','S3']:
        if v in res: print(f"Δ{v}-S0: ratio {res[v]['ratio']-res['S0']['ratio']:+.3f}, correctness {res[v]['corr']-res['S0']['corr']:+.2f}, cw {res[v]['cw']-res['S0']['cw']:+d}, +{res[v]['tok50']-res['S0']['tok50']:.0f} tok p50 (+{(res[v]['tok50']-res['S0']['tok50'])/5:.0f}s at 5 tok/s)")
    for i in ['lan-rsn-002','lan-cmp-001','lan-exp-003','vit-cry-003']:
        line=[]
        for v in ['S0','S2','S3']:
            if v in res and i in res[v]['J']: line.append(f"{v} {st.mean(rub(m['boar']) for m in res[v]['J'][i]):.2f} :: {res[v]['T'][i][0]['answer']['text'][:110]!r}")
        print(i); [print('   ',x) for x in line]
